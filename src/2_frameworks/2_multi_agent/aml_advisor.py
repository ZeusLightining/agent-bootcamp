"""AML Advisory Multi-Agent System.

This system provides specialized AML (Anti-Money Laundering) advisory services
across five key areas:
1. Customer Due Diligence (CDD) Red Flags
2. Regulatory Updates Analysis
3. SAR Filing Assistance
4. Policy Review & Gap Analysis
5. Scenario Testing & Guidance

Usage:
    uv run --env-file .env src/2_frameworks/2_multi_agent/aml_advisor.py \
        --query "Analyze CDD red flags for a high-risk customer" \
        --documents_dir ./aml_documents \
        --output_report aml_advice.md

Architecture:
    Router Agent → Specialized Agents → Synthesis Agent → Final Report
"""

import argparse
import asyncio
import contextlib
import json
import sys
from enum import Enum
from pathlib import Path
from typing import Any

import agents
import openai
import pydantic
from dotenv import load_dotenv

from src.utils import (
    AsyncWeaviateKnowledgeBase,
    Configs,
    get_weaviate_async_client,
    set_up_logging,
    setup_langfuse_tracer,
)
from src.utils.async_utils import gather_with_progress, rate_limited
from src.utils.langfuse.shared_client import langfuse_client


# Load environment variables
load_dotenv(verbose=True)


class AMLCategory(str, Enum):
    """AML advisory categories."""

    CDD_RED_FLAGS = "cdd_red_flags"
    REGULATORY_UPDATES = "regulatory_updates"
    SAR_FILING = "sar_filing"
    POLICY_REVIEW = "policy_review"
    SCENARIO_TESTING = "scenario_testing"


# Model configuration
AGENT_LLM_NAMES = {
    "router": "gemini-2.5-flash",
    "specialist": "gemini-2.5-pro",
    "synthesizer": "gemini-2.5-pro",
}

MAX_CONCURRENCY = {"specialist": 3, "synthesizer": 1}
MAX_GENERATED_TOKENS = {"router": 8192, "specialist": 32768, "synthesizer": 32768}

# Knowledge base collection names for different AML domains
# You can customize these based on your Weaviate collections
KNOWLEDGE_BASE_COLLECTIONS = {
    AMLCategory.CDD_RED_FLAGS: "aml_cdd_redflags",  # CDD guidelines and red flags
    AMLCategory.REGULATORY_UPDATES: "aml_regulations",  # Regulatory documents
    AMLCategory.SAR_FILING: "aml_sar_guidelines",  # SAR filing procedures
    AMLCategory.POLICY_REVIEW: "aml_policies",  # Policy templates and standards
    AMLCategory.SCENARIO_TESTING: "aml_case_studies",  # Case studies and scenarios
}


class Document(pydantic.BaseModel):
    """AML document structure."""

    filename: str
    content: str
    document_type: str | None = None
    metadata: dict[str, Any] = pydantic.Field(default_factory=dict)


class QueryRouting(pydantic.BaseModel):
    """Router decision on which specialists to engage."""

    primary_category: AMLCategory
    secondary_categories: list[AMLCategory] = pydantic.Field(default_factory=list)
    reasoning: str
    key_aspects: list[str] = pydantic.Field(
        description="Key aspects to focus on in the analysis"
    )


class SpecialistAnalysis(pydantic.BaseModel):
    """Analysis from a specialist agent."""

    category: AMLCategory
    key_findings: list[str]
    recommendations: list[str]
    risk_assessment: str
    regulatory_references: list[str] = pydantic.Field(default_factory=list)
    confidence_level: str = pydantic.Field(
        description="High, Medium, or Low confidence in the analysis"
    )


class SARDraft(pydantic.BaseModel):
    """Suspicious Activity Report draft."""

    narrative: str
    suspicious_indicators: list[str]
    timeline_of_events: list[str]
    supporting_documentation: list[str]
    regulatory_compliance_notes: str


class PolicyGapAnalysis(pydantic.BaseModel):
    """Policy review and gap analysis."""

    current_strengths: list[str]
    identified_gaps: list[str]
    improvement_recommendations: list[str]
    industry_best_practices: list[str]
    priority_actions: list[str]


class ScenarioGuidance(pydantic.BaseModel):
    """Scenario testing guidance."""

    scenario_summary: str
    recommended_actions: list[str]
    escalation_criteria: list[str]
    documentation_requirements: list[str]
    regulatory_considerations: list[str]


class SynthesizedAdvice(pydantic.BaseModel):
    """Final synthesized advice from all specialists."""

    executive_summary: str
    detailed_analysis: str
    actionable_recommendations: list[str]
    risk_mitigation_strategies: list[str]
    compliance_checklist: list[str]
    next_steps: list[str]
    specialist_analyses: list[SpecialistAnalysis]


# Initialize clients
configs = Configs.from_env_var()
async_weaviate_client = get_weaviate_async_client(
    http_host=configs.weaviate_http_host,
    http_port=configs.weaviate_http_port,
    http_secure=configs.weaviate_http_secure,
    grpc_host=configs.weaviate_grpc_host,
    grpc_port=configs.weaviate_grpc_port,
    grpc_secure=configs.weaviate_grpc_secure,
    api_key=configs.weaviate_api_key,
)
async_openai_client = openai.AsyncOpenAI()

# Initialize knowledge bases for each AML category
knowledge_bases: dict[AMLCategory, AsyncWeaviateKnowledgeBase] = {}
for category, collection_name in KNOWLEDGE_BASE_COLLECTIONS.items():
    knowledge_bases[category] = AsyncWeaviateKnowledgeBase(
        async_weaviate_client,
        collection_name=collection_name,
        num_results=5,  # Number of search results per query
        snippet_length=1000,  # Length of text snippets
    )


async def _cleanup_clients() -> None:
    """Close async clients."""
    await async_weaviate_client.close()
    await async_openai_client.close()


def _handle_sigint(signum: int, frame: object) -> None:
    """Handle SIGINT signal to gracefully shutdown."""
    with contextlib.suppress(Exception):
        asyncio.get_event_loop().run_until_complete(_cleanup_clients())
    sys.exit(0)


# Router Agent
router_agent = agents.Agent(
    "AML Query Router",
    instructions="""You are an expert AML advisor router. Analyze the user's query and determine:
    1. The primary AML category it falls under
    2. Any secondary categories that should be consulted
    3. Key aspects to focus on
    
    Categories:
    - cdd_red_flags: Customer Due Diligence red flags and risk indicators
    - regulatory_updates: Changes in AML regulations and compliance requirements
    - sar_filing: Suspicious Activity Report drafting and filing
    - policy_review: AML policy analysis and gap identification
    - scenario_testing: Hypothetical scenario analysis and guidance
    
    Be thorough in identifying all relevant categories.""",
    output_type=QueryRouting,
    model=agents.OpenAIChatCompletionsModel(
        model=AGENT_LLM_NAMES["router"], openai_client=async_openai_client
    ),
    model_settings=agents.ModelSettings(
        max_tokens=MAX_GENERATED_TOKENS["router"],
    ),
)


# Specialist Agents
def create_specialist_agent(
    category: AMLCategory, knowledge_base: AsyncWeaviateKnowledgeBase
) -> agents.Agent:
    """Create a specialist agent for a specific AML category with knowledge base access."""

    instructions_map = {
        AMLCategory.CDD_RED_FLAGS: """You are an expert in Customer Due Diligence (CDD) and KYC (Know Your Customer).
        Analyze the provided documents and query to identify:
        - Red flags and suspicious indicators
        - Risk classification factors
        - Enhanced due diligence triggers
        - Regulatory compliance requirements
        - Best practices for customer verification
        
        Provide specific, actionable insights based on current AML standards.""",
        AMLCategory.REGULATORY_UPDATES: """You are an expert in AML regulatory compliance.
        Analyze the provided documents and query to identify:
        - Recent regulatory changes and updates
        - Impact on current processes
        - Implementation requirements
        - Compliance deadlines
        - Jurisdictional considerations
        
        Reference specific regulations (e.g., BSA, FinCEN, FATF guidelines).""",
        AMLCategory.SAR_FILING: """You are an expert in Suspicious Activity Report (SAR) filing.
        Analyze the provided information to help draft a SAR that:
        - Clearly describes suspicious activity
        - Includes all required elements
        - Meets regulatory standards
        - Provides sufficient detail for investigators
        - Maintains confidentiality requirements
        
        Follow FinCEN SAR guidelines and best practices.""",
        AMLCategory.POLICY_REVIEW: """You are an expert in AML policy development and review.
        Analyze the provided policy documents to:
        - Identify gaps and weaknesses
        - Compare against industry standards
        - Recommend improvements
        - Ensure regulatory alignment
        - Suggest implementation strategies
        
        Reference FATF recommendations and industry best practices.""",
        AMLCategory.SCENARIO_TESTING: """You are an expert in AML scenario analysis and testing.
        Analyze the provided scenario to:
        - Assess risk levels
        - Recommend appropriate actions
        - Identify escalation triggers
        - Outline documentation requirements
        - Consider regulatory obligations
        
        Provide step-by-step guidance for handling the scenario.""",
    }

    return agents.Agent(
        f"AML Specialist: {category.value}",
        instructions=instructions_map[category],
        output_type=SpecialistAnalysis,
        tools=[
            agents.function_tool(
                knowledge_base.search_knowledgebase,
                tool_name=f"search_{category.value}",
                tool_description=f"Search the {category.value.replace('_', ' ')} knowledge base for relevant AML information, regulations, guidelines, and best practices.",
            )
        ],
        model=agents.OpenAIChatCompletionsModel(
            model=AGENT_LLM_NAMES["specialist"], openai_client=async_openai_client
        ),
        model_settings=agents.ModelSettings(
            reasoning=openai.types.Reasoning(
                effort="high", generate_summary="detailed"
            ),
            max_tokens=MAX_GENERATED_TOKENS["specialist"],
        ),
    )


# Synthesis Agent
synthesis_agent = agents.Agent(
    "AML Advisory Synthesizer",
    instructions="""You are a senior AML compliance advisor. Synthesize the analyses from specialist agents into:
    1. Executive summary for quick decision-making
    2. Detailed analysis combining all specialist insights
    3. Prioritized, actionable recommendations
    4. Risk mitigation strategies
    5. Compliance checklist
    6. Clear next steps
    
    Ensure the advice is:
    - Practical and implementable
    - Compliant with regulations
    - Risk-based and proportionate
    - Clear and well-structured
    
    Highlight any conflicting recommendations and provide guidance on resolution.""",
    output_type=SynthesizedAdvice,
    model=agents.OpenAIChatCompletionsModel(
        model=AGENT_LLM_NAMES["synthesizer"], openai_client=async_openai_client
    ),
    model_settings=agents.ModelSettings(
        reasoning=openai.types.Reasoning(effort="high", generate_summary="detailed"),
        max_tokens=MAX_GENERATED_TOKENS["synthesizer"],
    ),
)


async def route_query(user_query: str) -> QueryRouting:
    """Route the user query to appropriate specialist categories."""
    with langfuse_client.start_as_current_observation(name="Route Query") as span:
        try:
            result = await agents.Runner.run(router_agent, input=user_query)
            routing = result.final_output_as(QueryRouting)
            span.update(input=user_query, output=routing)
            return routing
        except agents.AgentsException as e:
            print(f"Routing error: {e}")
            raise


async def analyze_with_specialist(
    category: AMLCategory, user_query: str, documents: list[Document], key_aspects: list[str]
) -> SpecialistAnalysis | None:
    """Get analysis from a specialist agent with knowledge base access."""
    knowledge_base = knowledge_bases.get(category)
    if not knowledge_base:
        print(f"Warning: No knowledge base configured for {category.value}")
        # Create a basic knowledge base with default collection if not configured
        knowledge_base = AsyncWeaviateKnowledgeBase(
            async_weaviate_client,
            collection_name="enwiki_20250520",  # Fallback to default collection
        )
    
    specialist = create_specialist_agent(category, knowledge_base)

    # Prepare context
    context = {
        "query": user_query,
        "key_aspects": key_aspects,
        "documents": [
            {
                "filename": doc.filename,
                "content": doc.content[:5000],  # Limit content length
                "type": doc.document_type,
            }
            for doc in documents
        ],
    }

    with langfuse_client.start_as_current_observation(
        name=f"Specialist Analysis: {category.value}"
    ) as span:
        try:
            result = await agents.Runner.run(
                specialist, input=json.dumps(context, indent=2)
            )
            analysis = result.final_output_as(SpecialistAnalysis)
            analysis.category = category
            span.update(input=context, output=analysis)
            return analysis
        except agents.AgentsException as e:
            print(f"Specialist error ({category.value}): {e}")
            return None


async def process_specialists(
    routing: QueryRouting, user_query: str, documents: list[Document]
) -> list[SpecialistAnalysis]:
    """Process all relevant specialist agents in parallel."""
    categories = [routing.primary_category] + routing.secondary_categories

    semaphore = asyncio.Semaphore(MAX_CONCURRENCY["specialist"])
    coros = [
        rate_limited(
            lambda cat=cat: analyze_with_specialist(
                cat, user_query, documents, routing.key_aspects
            ),
            semaphore,
        )
        for cat in categories
    ]

    results = await gather_with_progress(coros, "Consulting specialists...")
    return [r for r in results if r is not None]


async def synthesize_advice(
    user_query: str, routing: QueryRouting, analyses: list[SpecialistAnalysis]
) -> SynthesizedAdvice:
    """Synthesize specialist analyses into final advice."""
    synthesis_input = {
        "user_query": user_query,
        "routing_decision": routing.model_dump(),
        "specialist_analyses": [a.model_dump() for a in analyses],
    }

    with langfuse_client.start_as_current_observation(name="Synthesize Advice") as span:
        try:
            result = await agents.Runner.run(
                synthesis_agent, input=json.dumps(synthesis_input, indent=2)
            )
            advice = result.final_output_as(SynthesizedAdvice)
            advice.specialist_analyses = analyses
            span.update(input=synthesis_input, output=advice)
            return advice
        except agents.AgentsException as e:
            print(f"Synthesis error: {e}")
            raise


def load_documents(documents_dir: Path) -> list[Document]:
    """Load AML documents from directory."""
    documents = []

    if not documents_dir.exists():
        print(f"Warning: Documents directory not found: {documents_dir}")
        return documents

    for file_path in documents_dir.glob("**/*.txt"):
        try:
            content = file_path.read_text(encoding="utf-8")
            documents.append(
                Document(
                    filename=file_path.name,
                    content=content,
                    document_type=file_path.stem.split("_")[0]
                    if "_" in file_path.stem
                    else None,
                    metadata={"path": str(file_path)},
                )
            )
        except Exception as e:
            print(f"Error loading {file_path}: {e}")

    # Also support JSON and MD files
    for ext in ["*.json", "*.md"]:
        for file_path in documents_dir.glob(f"**/{ext}"):
            try:
                content = file_path.read_text(encoding="utf-8")
                documents.append(
                    Document(
                        filename=file_path.name,
                        content=content,
                        document_type=file_path.suffix[1:],
                        metadata={"path": str(file_path)},
                    )
                )
            except Exception as e:
                print(f"Error loading {file_path}: {e}")

    return documents


def generate_report(advice: SynthesizedAdvice, routing: QueryRouting) -> str:
    """Generate markdown report from synthesized advice."""
    report = f"""# AML Advisory Report

## Executive Summary

{advice.executive_summary}

---

## Query Routing

**Primary Category:** {routing.primary_category.value}

**Secondary Categories:** {', '.join(c.value for c in routing.secondary_categories) if routing.secondary_categories else 'None'}

**Routing Reasoning:** {routing.reasoning}

**Key Aspects Analyzed:**
{chr(10).join(f'- {aspect}' for aspect in routing.key_aspects)}

---

## Detailed Analysis

{advice.detailed_analysis}

---

## Actionable Recommendations

{chr(10).join(f'{i+1}. {rec}' for i, rec in enumerate(advice.actionable_recommendations))}

---

## Risk Mitigation Strategies

{chr(10).join(f'- {strategy}' for strategy in advice.risk_mitigation_strategies)}

---

## Compliance Checklist

{chr(10).join(f'- [ ] {item}' for item in advice.compliance_checklist)}

---

## Next Steps

{chr(10).join(f'{i+1}. {step}' for i, step in enumerate(advice.next_steps))}

---

## Specialist Analyses

"""

    for analysis in advice.specialist_analyses:
        report += f"""
### {analysis.category.value.replace('_', ' ').title()}

**Confidence Level:** {analysis.confidence_level}

**Risk Assessment:** {analysis.risk_assessment}

**Key Findings:**
{chr(10).join(f'- {finding}' for finding in analysis.key_findings)}

**Recommendations:**
{chr(10).join(f'- {rec}' for rec in analysis.recommendations)}

**Regulatory References:**
{chr(10).join(f'- {ref}' for ref in analysis.regulatory_references) if analysis.regulatory_references else '- None provided'}

---
"""

    return report


async def main(
    user_query: str,
    documents_dir: Path,
    output_report: Path,
    collection_names: dict[str, str] | None = None,
):
    """Main execution flow.
    
    Parameters
    ----------
    user_query : str
        The AML advisory question
    documents_dir : Path
        Directory containing additional AML documents
    output_report : Path
        Path to save the output report
    collection_names : dict[str, str] | None
        Optional mapping of category names to Weaviate collection names.
        Example: {"cdd_red_flags": "my_cdd_collection", "sar_filing": "my_sar_collection"}
    """
    # Update knowledge base collections if custom ones provided
    if collection_names:
        for category_name, collection_name in collection_names.items():
            try:
                category = AMLCategory(category_name)
                knowledge_bases[category] = AsyncWeaviateKnowledgeBase(
                    async_weaviate_client,
                    collection_name=collection_name,
                    num_results=5,
                    snippet_length=1000,
                )
                print(f"Using collection '{collection_name}' for {category_name}")
            except ValueError:
                print(f"Warning: Unknown category '{category_name}', skipping")
    
    print(f"\n{'='*80}")
    print("AML ADVISORY MULTI-AGENT SYSTEM")
    print(f"{'='*80}\n")

    # Load documents
    print(f"Loading documents from: {documents_dir}")
    documents = load_documents(documents_dir)
    print(f"Loaded {len(documents)} document(s)\n")

    if not documents:
        print("Warning: No documents loaded. Proceeding with query-only analysis.\n")

    # Route query
    print("Routing query to appropriate specialists...")
    with langfuse_client.start_as_current_span(name="AML Advisory Session") as session:
        routing = await route_query(user_query)
        print(f"Primary category: {routing.primary_category.value}")
        if routing.secondary_categories:
            print(
                f"Secondary categories: {', '.join(c.value for c in routing.secondary_categories)}"
            )
        print(f"Reasoning: {routing.reasoning}\n")

        # Get specialist analyses
        analyses = await process_specialists(routing, user_query, documents)
        print(f"\nReceived {len(analyses)} specialist analysis/analyses\n")

        # Synthesize advice
        print("Synthesizing final advice...")
        advice = await synthesize_advice(user_query, routing, analyses)

        session.update(
            input={"query": user_query, "num_documents": len(documents)},
            output=advice.model_dump(),
        )

    # Generate report
    report = generate_report(advice, routing)
    output_report.write_text(report, encoding="utf-8")

    print(f"\n{'='*80}")
    print(f"Report generated: {output_report}")
    print(f"{'='*80}\n")

    # Print executive summary
    print("EXECUTIVE SUMMARY:")
    print(advice.executive_summary)
    print()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="AML Advisory Multi-Agent System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  # Basic usage with default collections
  uv run --env-file .env src/2_frameworks/2_multi_agent/aml_advisor.py \
      --query "What are CDD red flags for cryptocurrency customers?"
  
  # With custom collection for CDD
  uv run --env-file .env src/2_frameworks/2_multi_agent/aml_advisor.py \
      --query "Analyze SAR filing requirements" \
      --collection cdd_red_flags=my_cdd_kb \
      --collection sar_filing=my_sar_kb
  
  # With local documents
  uv run --env-file .env src/2_frameworks/2_multi_agent/aml_advisor.py \
      --query "Review our AML policy" \
      --documents_dir ./company_policies
        """,
    )
    parser.add_argument(
        "--query",
        required=True,
        help="AML advisory query",
    )
    parser.add_argument(
        "--documents_dir",
        type=Path,
        default=Path("./aml_documents"),
        help="Directory containing AML documents",
    )
    parser.add_argument(
        "--output_report",
        type=Path,
        default=Path("aml_advice.md"),
        help="Output report file path",
    )
    parser.add_argument(
        "--collection",
        action="append",
        dest="collections",
        help="Specify custom Weaviate collection for a category. Format: category=collection_name. "
        "Can be used multiple times. Categories: cdd_red_flags, regulatory_updates, sar_filing, policy_review, scenario_testing",
    )

    args = parser.parse_args()

    # Parse collection mappings
    collection_names = None
    if args.collections:
        collection_names = {}
        for mapping in args.collections:
            if "=" in mapping:
                category, collection = mapping.split("=", 1)
                collection_names[category.strip()] = collection.strip()
            else:
                print(f"Warning: Invalid collection mapping '{mapping}', expected format: category=collection_name")

    set_up_logging()
    setup_langfuse_tracer()

    # Register signal handler for graceful shutdown
    import signal
    signal.signal(signal.SIGINT, _handle_sigint)

    try:
        asyncio.run(main(args.query, args.documents_dir, args.output_report, collection_names))
    finally:
        # Cleanup on exit
        asyncio.run(_cleanup_clients())
