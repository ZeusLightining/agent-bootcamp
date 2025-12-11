"""AML Advisory Multi-Agent System - Gradio Interface.

Interactive chat interface for AML compliance advisory using specialized agents
with Weaviate knowledge base integration.

Usage:
    uv run --env-file .env gradio src/2_frameworks/2_multi_agent/aml_advisor_gradio.py

Features:
    - Interactive chat with AML compliance experts
    - Specialized agents for CDD, Regulatory, SAR, Policy, and Scenarios
    - Real-time streaming responses
    - Knowledge base integration via Weaviate
    - Full LangFuse observability
"""

import asyncio
import contextlib
import signal
import sys
from enum import Enum

import agents
import gradio as gr
import openai
import pydantic
from dotenv import load_dotenv
from gradio.components.chatbot import ChatMessage

from src.utils import (
    AsyncWeaviateKnowledgeBase,
    Configs,
    get_weaviate_async_client,
    oai_agent_stream_to_gradio_messages,
    set_up_logging,
    setup_langfuse_tracer,
)
from src.utils.langfuse.shared_client import langfuse_client


# Load environment variables
load_dotenv(verbose=True)
set_up_logging()


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
    "main": "gemini-2.5-pro",
}

MAX_CONCURRENCY = {"specialist": 3}
MAX_GENERATED_TOKENS = {"router": 8192, "specialist": 32768, "main": 32768}

# Knowledge base collection names for different AML domains
KNOWLEDGE_BASE_COLLECTIONS = {
    AMLCategory.CDD_RED_FLAGS: "aml_cdd_redflags",
    AMLCategory.REGULATORY_UPDATES: "aml_regulations",
    AMLCategory.SAR_FILING: "aml_sar_guidelines",
    AMLCategory.POLICY_REVIEW: "aml_policies",
    AMLCategory.SCENARIO_TESTING: "aml_case_studies",
}


class QueryRouting(pydantic.BaseModel):
    """Router decision on which specialists to engage."""

    primary_category: AMLCategory
    secondary_categories: list[AMLCategory] = pydantic.Field(default_factory=list)
    reasoning: str


class SpecialistAnalysis(pydantic.BaseModel):
    """Analysis from a specialist agent."""

    category: str
    key_findings: list[str]
    recommendations: list[str]
    risk_assessment: str
    regulatory_references: list[str] = pydantic.Field(default_factory=list)


# Initialize clients
configs = Configs.from_env_var()
async_weaviate_client = get_weaviate_async_client(
    http_host=configs.weaviate_http_host,
    http_port=configs.weaviate_http_port,
    http_secure=configs.weaviate_http_secure,
    grpc_host=configs.weaviate_grpc_host,
    grpc_port=configs.grpc_port,
    grpc_secure=configs.weaviate_grpc_secure,
    api_key=configs.weaviate_api_key,
)
async_openai_client = openai.AsyncOpenAI()

# Initialize knowledge bases for each AML category
knowledge_bases: dict[AMLCategory, AsyncWeaviateKnowledgeBase] = {}
for category, collection_name in KNOWLEDGE_BASE_COLLECTIONS.items():
    try:
        knowledge_bases[category] = AsyncWeaviateKnowledgeBase(
            async_weaviate_client,
            collection_name=collection_name,
            num_results=5,
            snippet_length=1000,
        )
    except Exception as e:
        print(f"Warning: Could not initialize knowledge base for {category.value}: {e}")
        # Use fallback collection
        knowledge_bases[category] = AsyncWeaviateKnowledgeBase(
            async_weaviate_client,
            collection_name="enwiki_20250520",
            num_results=5,
            snippet_length=1000,
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


# Create specialist agents for each AML category
def create_specialist_agent(
    category: AMLCategory, knowledge_base: AsyncWeaviateKnowledgeBase
) -> agents.Agent:
    """Create a specialist agent for a specific AML category with knowledge base access."""

    instructions_map = {
        AMLCategory.CDD_RED_FLAGS: """You are an expert in Customer Due Diligence (CDD) and KYC.
        Use the search tool to find relevant information about red flags, risk indicators, 
        and compliance requirements. Provide specific, actionable insights based on current AML standards.""",
        AMLCategory.REGULATORY_UPDATES: """You are an expert in AML regulatory compliance.
        Use the search tool to find information about regulatory changes, compliance requirements,
        and jurisdictional considerations. Reference specific regulations when possible.""",
        AMLCategory.SAR_FILING: """You are an expert in Suspicious Activity Report (SAR) filing.
        Use the search tool to find SAR guidelines, filing procedures, and best practices.
        Help draft SARs that meet regulatory standards.""",
        AMLCategory.POLICY_REVIEW: """You are an expert in AML policy development and review.
        Use the search tool to find policy templates, industry standards, and best practices.
        Identify gaps and recommend improvements.""",
        AMLCategory.SCENARIO_TESTING: """You are an expert in AML scenario analysis and testing.
        Use the search tool to find case studies and guidance. Provide step-by-step
        recommendations for handling scenarios.""",
    }

    return agents.Agent(
        f"AML_{category.value}_specialist",
        instructions=instructions_map[category],
        tools=[
            agents.function_tool(
                knowledge_base.search_knowledgebase,
                tool_name=f"search_{category.value}",
                tool_description=f"Search the {category.value.replace('_', ' ')} knowledge base for AML information.",
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


# Initialize specialist agents
specialist_agents = {}
for category, kb in knowledge_bases.items():
    specialist_agents[category] = create_specialist_agent(category, kb)

# Main AML Advisory Agent
main_agent = agents.Agent(
    name="AML_Advisor",
    instructions="""You are a senior AML (Anti-Money Laundering) compliance advisor.

Your role is to provide expert guidance on:
1. Customer Due Diligence (CDD) - red flags and risk assessment
2. Regulatory Updates - compliance changes and requirements
3. SAR Filing - Suspicious Activity Report drafting
4. Policy Review - gap analysis and improvements
5. Scenario Testing - handling hypothetical situations

When a user asks a question:
1. Determine which specialist(s) to consult based on the query
2. Use the appropriate specialist tools to get expert analysis
3. Synthesize the information into clear, actionable advice
4. Provide specific recommendations and next steps
5. Reference relevant regulations and best practices

Be thorough, professional, and ensure all advice is compliant with AML regulations.
Always cite your sources when referencing specific regulations or guidelines.""",
    tools=[
        specialist_agents[AMLCategory.CDD_RED_FLAGS].as_tool(
            tool_name="consult_cdd_specialist",
            tool_description="Consult the Customer Due Diligence specialist for red flags, risk assessment, and KYC guidance.",
        ),
        specialist_agents[AMLCategory.REGULATORY_UPDATES].as_tool(
            tool_name="consult_regulatory_specialist",
            tool_description="Consult the Regulatory Updates specialist for compliance changes and regulatory requirements.",
        ),
        specialist_agents[AMLCategory.SAR_FILING].as_tool(
            tool_name="consult_sar_specialist",
            tool_description="Consult the SAR Filing specialist for suspicious activity reporting guidance.",
        ),
        specialist_agents[AMLCategory.POLICY_REVIEW].as_tool(
            tool_name="consult_policy_specialist",
            tool_description="Consult the Policy Review specialist for AML policy analysis and improvements.",
        ),
        specialist_agents[AMLCategory.SCENARIO_TESTING].as_tool(
            tool_name="consult_scenario_specialist",
            tool_description="Consult the Scenario Testing specialist for handling hypothetical AML situations.",
        ),
    ],
    model=agents.OpenAIChatCompletionsModel(
        model=AGENT_LLM_NAMES["main"], openai_client=async_openai_client
    ),
    model_settings=agents.ModelSettings(
        reasoning=openai.types.Reasoning(effort="high", generate_summary="detailed"),
        max_tokens=MAX_GENERATED_TOKENS["main"],
    ),
)


async def _main(question: str, gr_messages: list[ChatMessage]):
    """Main async function to handle user queries with streaming responses."""
    setup_langfuse_tracer()

    with langfuse_client.start_as_current_span(name="AML-Advisory-Session") as span:
        span.update(input=question)

        # Stream the agent's response
        result_stream = agents.Runner.run_streamed(main_agent, input=question)
        async for _item in result_stream.stream_events():
            gr_messages += oai_agent_stream_to_gradio_messages(_item)
            if len(gr_messages) > 0:
                yield gr_messages

        span.update(output=result_stream.final_output)


# Create Gradio interface
demo = gr.ChatInterface(
    _main,
    title="🏦 AML Advisory Multi-Agent System",
    description="""
    **Expert AML Compliance Advisory powered by AI**
    
    Get specialized guidance on:
    - 🔍 Customer Due Diligence (CDD) & Red Flags
    - 📋 Regulatory Updates & Compliance
    - 📝 Suspicious Activity Report (SAR) Filing
    - 📊 Policy Review & Gap Analysis
    - 🎯 Scenario Testing & Guidance
    
    *All responses are traced in LangFuse for transparency and compliance.*
    """,
    type="messages",
    examples=[
        "What are the key CDD red flags for cryptocurrency customers?",
        "Help me draft a SAR for a customer making multiple structured deposits below $10,000",
        "What are the latest FinCEN guidance updates on beneficial ownership?",
        "Review our customer onboarding process for AML compliance gaps",
        "A customer suddenly increases transaction volume by 500% with no clear business justification. How should we handle this?",
        "What enhanced due diligence measures should we apply to PEPs (Politically Exposed Persons)?",
        "Explain the risk-based approach to AML compliance for a fintech startup",
    ],
    theme=gr.themes.Soft(
        primary_hue="blue",
        secondary_hue="slate",
    ),
    css="""
    .gradio-container {
        max-width: 900px !important;
    }
    """,
)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, _handle_sigint)

    print("\n" + "=" * 80)
    print("🏦 AML ADVISORY MULTI-AGENT SYSTEM")
    print("=" * 80)
    print("\nStarting Gradio interface...")
    print("Knowledge bases initialized for:")
    for category in knowledge_bases.keys():
        print(f"  ✓ {category.value.replace('_', ' ').title()}")
    print("\nAccess the interface at the URL shown below.")
    print("For public sharing, the gradio.live URL will be displayed.\n")

    try:
        demo.launch(share=True)
    finally:
        print("\nShutting down...")
        asyncio.run(_cleanup_clients())
        print("Cleanup complete.")
