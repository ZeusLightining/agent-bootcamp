# AML Advisory Multi-Agent System

A sophisticated multi-agent system for Anti-Money Laundering (AML) compliance advisory, built using the OpenAI Agents SDK and fan-out pattern principles.

## Overview

This system provides expert AML advisory services across five specialized domains:

1. **Customer Due Diligence (CDD)** - Red flags and risk assessment
2. **Regulatory Updates** - Compliance changes and impact analysis
3. **SAR Filing** - Suspicious Activity Report drafting assistance
4. **Policy Review** - Gap analysis and improvement recommendations
5. **Scenario Testing** - Hypothetical scenario guidance

## Architecture

```
User Query
    ↓
Router Agent (determines which specialists to consult)
    ↓
Specialist Agents (parallel processing)
    ├─ CDD Red Flags Agent
    ├─ Regulatory Updates Agent
    ├─ SAR Filing Agent
    ├─ Policy Review Agent
    └─ Scenario Testing Agent
    ↓
Synthesis Agent (combines insights)
    ↓
Final Advisory Report
```

### Key Design Principles

- **Intelligent Routing**: Router agent analyzes queries to determine relevant specialists
- **Parallel Processing**: Multiple specialists work concurrently for efficiency
- **Expert Synthesis**: Senior advisor synthesizes insights into actionable advice
- **Observability**: Full Langfuse tracing for transparency and debugging

## Installation & Setup

### 1. Prerequisites

Ensure you have the agent-bootcamp environment set up:

```bash
cd /Users/267958742/Documents/GitHub/agent-bootcamp
```

### 2. Configure Environment

```bash
# Copy example env file if not already done
cp .env.example .env

# Edit .env and add your API keys:
# - OPENAI_API_KEY (or compatible API)
# - LANGFUSE_SECRET_KEY
# - LANGFUSE_PUBLIC_KEY
```

### 3. Verify Setup

```bash
uv run --env-file .env pytest -sv tests/tool_tests/test_integration.py
```

## Usage

### Interactive Chat Interface (Recommended)

Launch the Gradio web interface for interactive chat with the AML advisor:

```bash
uv run --env-file .env gradio src/2_frameworks/2_multi_agent/aml_advisor_gradio.py
```

This will:
- Start a local web server with chat interface
- Generate a public `gradio.live` URL for sharing
- Provide real-time streaming responses
- Show agent reasoning and tool usage
- Trace all interactions in LangFuse

**Access the interface:**
1. Open the local URL (e.g., `http://127.0.0.1:7860`)
2. Or use the public `gradio.live` URL for remote access

### Command-Line Interface

For batch processing or scripted usage:

```bash
uv run --env-file .env src/2_frameworks/2_multi_agent/aml_advisor.py \
    --query "What are the key CDD red flags for a high-risk customer in the cryptocurrency sector?" \
    --documents_dir ./aml_documents \
    --output_report aml_advice.md
```

### Command-Line Arguments

- `--query` (required): Your AML advisory question
- `--documents_dir` (optional): Directory containing AML documents (default: `./aml_documents`)
- `--output_report` (optional): Output file path (default: `aml_advice.md`)
- `--collection` (optional): Custom Weaviate collection mapping (can be used multiple times)

### Example Queries

#### 1. Customer Due Diligence

```bash
uv run --env-file .env src/2_frameworks/2_multi_agent/aml_advisor.py \
    --query "What are the key red flags to look for when conducting CDD on a new customer in the real estate sector?" \
    --output_report cdd_analysis.md
```

#### 2. Regulatory Updates

```bash
uv run --env-file .env src/2_frameworks/2_multi_agent/aml_advisor.py \
    --query "What are the latest changes to AML regulations in the European Union and how do they impact our current processes?" \
    --output_report regulatory_update.md
```

#### 3. SAR Filing

```bash
uv run --env-file .env src/2_frameworks/2_multi_agent/aml_advisor.py \
    --query "Help me draft a Suspicious Activity Report for a customer making multiple structured deposits just below the reporting threshold" \
    --output_report sar_draft.md
```

#### 4. Policy Review

```bash
uv run --env-file .env src/2_frameworks/2_multi_agent/aml_advisor.py \
    --query "Analyze our current AML policy and identify any gaps or areas for improvement based on FATF recommendations" \
    --documents_dir ./company_policies \
    --output_report policy_review.md
```

#### 5. Scenario Testing

```bash
uv run --env-file .env src/2_frameworks/2_multi_agent/aml_advisor.py \
    --query "A customer suddenly increases transaction volume by 500% with no clear business justification. How should we handle this?" \
    --output_report scenario_guidance.md
```

## Document Preparation

### Supported Formats

- `.txt` - Plain text documents
- `.md` - Markdown documents
- `.json` - JSON structured data

### Document Organization

Create an `aml_documents` directory with your reference materials:

```
aml_documents/
├── policies/
│   ├── aml_policy_2024.txt
│   └── kyc_procedures.md
├── regulations/
│   ├── bsa_requirements.txt
│   └── fatf_guidelines.md
├── case_studies/
│   └── previous_sars.txt
└── training/
    └── red_flags_guide.txt
```

### Document Naming Conventions

Use prefixes to help the system categorize documents:

- `policy_*.txt` - Internal policies
- `regulation_*.txt` - Regulatory documents
- `case_*.txt` - Case studies
- `guidance_*.txt` - Guidance materials

## Output Report Structure

The generated markdown report includes:

1. **Executive Summary** - Quick overview for decision-makers
2. **Query Routing** - How the query was categorized
3. **Detailed Analysis** - Comprehensive analysis from all specialists
4. **Actionable Recommendations** - Prioritized action items
5. **Risk Mitigation Strategies** - Specific risk controls
6. **Compliance Checklist** - Items to verify
7. **Next Steps** - Clear action plan
8. **Specialist Analyses** - Individual expert insights

## Advanced Usage

### Customizing Specialist Agents

You can modify specialist instructions in the code:

```python
# In aml_advisor.py, find the create_specialist_agent function
instructions_map = {
    AMLCategory.CDD_RED_FLAGS: """Your custom instructions here...""",
    # ... other categories
}
```

### Adjusting Concurrency

Control how many specialists run in parallel:

```python
MAX_CONCURRENCY = {
    "specialist": 3,  # Increase for faster processing (watch API limits)
    "synthesizer": 1
}
```

### Model Selection

Change models based on your needs:

```python
AGENT_LLM_NAMES = {
    "router": "gemini-2.5-flash",      # Fast routing
    "specialist": "gemini-2.5-pro",     # Deep analysis
    "synthesizer": "gemini-2.5-pro",    # Quality synthesis
}
```

## How It Differs from Simple Fan-Out

### Traditional Fan-Out (fan_out.py)
- Processes **all pairs** of documents (O(N²))
- Fixed processing pattern
- Best for pairwise comparisons

### AML Advisor (aml_advisor.py)
- **Intelligent routing** to relevant specialists only
- Dynamic specialist selection based on query
- Best for complex advisory tasks with multiple domains

## Performance Considerations

### API Costs

- **Router**: Fast, cheap model (gemini-2.5-flash)
- **Specialists**: High-quality model (gemini-2.5-pro) - only invoked when needed
- **Synthesizer**: High-quality model for final output

**Cost Optimization Tips:**
1. Limit document content to relevant sections
2. Use specific queries to reduce specialist invocations
3. Adjust concurrency based on API rate limits

### Processing Time

Typical processing times:
- Simple query (1 specialist): 10-30 seconds
- Complex query (3+ specialists): 30-90 seconds
- With large documents: Add 10-30 seconds

## Observability with Langfuse

All agent interactions are traced in Langfuse:

1. **Router decisions** - See why specialists were selected
2. **Specialist analyses** - Review individual expert outputs
3. **Synthesis process** - Understand how advice was combined
4. **Token usage** - Monitor costs

Access your traces at: https://cloud.langfuse.com

## Troubleshooting

### "No documents loaded" Warning

This is normal if you don't have a documents directory. The system will still provide advice based on the query and the agents' training data.

### Specialist Errors

If a specialist fails, the system continues with other specialists. Check Langfuse traces for details.

### API Rate Limits

Reduce `MAX_CONCURRENCY["specialist"]` if you hit rate limits:

```python
MAX_CONCURRENCY = {"specialist": 1, "synthesizer": 1}
```

### Memory Issues

If processing large documents, limit content:

```python
# In analyze_with_specialist function
"content": doc.content[:5000],  # Adjust this limit
```

## Extending the System

### Adding New Specialist Categories

1. Add to `AMLCategory` enum:
```python
class AMLCategory(str, Enum):
    YOUR_NEW_CATEGORY = "your_new_category"
```

2. Add instructions in `create_specialist_agent`:
```python
instructions_map = {
    AMLCategory.YOUR_NEW_CATEGORY: """Your instructions...""",
}
```

3. Update router agent instructions to include the new category

### Adding Custom Output Types

Create specialized Pydantic models for specific outputs:

```python
class CustomAnalysis(pydantic.BaseModel):
    your_field: str
    another_field: list[str]
```

Then use it as the `output_type` for your specialist agent.

## Best Practices

1. **Be Specific**: More specific queries get better routing and analysis
2. **Provide Context**: Include relevant documents for better advice
3. **Review Traces**: Use Langfuse to understand agent reasoning
4. **Iterate**: Refine queries based on initial results
5. **Validate**: Always have human experts review critical compliance advice

## Compliance Disclaimer

⚠️ **Important**: This system provides advisory support but should not replace:
- Professional legal advice
- Compliance officer judgment
- Regulatory consultation
- Internal review processes

Always have qualified compliance professionals review outputs before implementation.

## Examples in Action

See the `examples/` directory for:
- Sample queries and outputs
- Document templates
- Integration examples
- Custom specialist configurations

## Support & Contribution

For issues or enhancements:
1. Check Langfuse traces for debugging
2. Review specialist outputs individually
3. Adjust model parameters if needed
4. Consult the main agent-bootcamp README

## License

Same as agent-bootcamp repository.
