# AML Advisory Agent - Quick Start Guide

Get your AML advisory agent up and running in 5 minutes!

## 🚀 Quick Start

### 1. Launch the Gradio Interface

```bash
cd /Users/267958742/Documents/GitHub/agent-bootcamp
uv run --env-file .env gradio src/2_frameworks/2_multi_agent/aml_advisor_gradio.py
```

### 2. Access the Interface

The terminal will show:
```
Running on local URL:  http://127.0.0.1:7860
Running on public URL: https://xxxxx.gradio.live
```

**Open either URL in your browser** to start chatting with the AML advisor!

### 3. Try Example Queries

Click any example or type your own:

- "What are the key CDD red flags for cryptocurrency customers?"
- "Help me draft a SAR for structured deposits"
- "What are the latest FinCEN guidance updates?"
- "Review our customer onboarding process for AML gaps"
- "How should we handle a customer with sudden 500% transaction increase?"

## 📋 Prerequisites

### Required Environment Variables

Ensure your `.env` file has these configured:

```bash
# OpenAI-compatible LLM (required)
OPENAI_BASE_URL="https://generativelanguage.googleapis.com/v1beta/openai/"
OPENAI_API_KEY="your-api-key"

# Weaviate (required for knowledge base)
WEAVIATE_HTTP_HOST="your-instance.weaviate.cloud"
WEAVIATE_GRPC_HOST="grpc-your-instance.weaviate.cloud"
WEAVIATE_API_KEY="your-api-key"
WEAVIATE_HTTP_PORT="443"
WEAVIATE_GRPC_PORT="443"
WEAVIATE_HTTP_SECURE="true"
WEAVIATE_GRPC_SECURE="true"

# Embedding Model (required for search)
EMBEDDING_BASE_URL="your-embedding-service"
EMBEDDING_API_KEY="your-embedding-key"

# LangFuse (optional but recommended for observability)
LANGFUSE_SECRET_KEY="sk-lf-..."
LANGFUSE_PUBLIC_KEY="pk-lf-..."
LANGFUSE_HOST="https://us.cloud.langfuse.com"
```

### Verify Setup

```bash
uv run --env-file .env pytest -sv tests/tool_tests/test_integration.py
```

## 🎯 How It Works

### Architecture

```
You (Chat Interface)
    ↓
Main AML Advisor Agent
    ↓
Consults Specialist Agents (as needed)
    ├─ CDD Specialist → searches aml_cdd_redflags
    ├─ Regulatory Specialist → searches aml_regulations
    ├─ SAR Specialist → searches aml_sar_guidelines
    ├─ Policy Specialist → searches aml_policies
    └─ Scenario Specialist → searches aml_case_studies
    ↓
Synthesized Response (streamed to you)
```

### What Happens When You Ask a Question?

1. **Main Agent** receives your query
2. **Determines** which specialist(s) to consult
3. **Specialists** search their knowledge bases
4. **Synthesizes** insights into actionable advice
5. **Streams** response to you in real-time

All interactions are traced in LangFuse for transparency!

## 🔧 Customization

### Using Your Own Knowledge Bases

The system uses these default Weaviate collections:

- `aml_cdd_redflags` - CDD guidelines
- `aml_regulations` - Regulatory documents
- `aml_sar_guidelines` - SAR procedures
- `aml_policies` - Policy templates
- `aml_case_studies` - Scenario examples

**To use your own collections**, edit `aml_advisor_gradio.py`:

```python
KNOWLEDGE_BASE_COLLECTIONS = {
    AMLCategory.CDD_RED_FLAGS: "your_cdd_collection",
    AMLCategory.REGULATORY_UPDATES: "your_regulations_collection",
    # ... etc
}
```

### Using a Single Collection for All

If you have one comprehensive AML knowledge base:

```python
KNOWLEDGE_BASE_COLLECTIONS = {
    AMLCategory.CDD_RED_FLAGS: "aml_master_kb",
    AMLCategory.REGULATORY_UPDATES: "aml_master_kb",
    AMLCategory.SAR_FILING: "aml_master_kb",
    AMLCategory.POLICY_REVIEW: "aml_master_kb",
    AMLCategory.SCENARIO_TESTING: "aml_master_kb",
}
```

## 💡 Usage Tips

### For Best Results

1. **Be Specific**: "CDD red flags for crypto customers" vs "tell me about CDD"
2. **Provide Context**: Mention industry, jurisdiction, or specific concerns
3. **Ask Follow-ups**: The agent maintains conversation context
4. **Check Sources**: Agent cites regulations and references

### Example Conversation Flow

**You:** "What are CDD red flags for cryptocurrency customers?"

**Agent:** *Consults CDD specialist, searches knowledge base*
- Lists specific red flags
- Explains risk factors
- Provides regulatory references

**You:** "How should we document these findings?"

**Agent:** *Consults Policy specialist*
- Recommends documentation procedures
- Suggests templates
- Outlines retention requirements

**You:** "Draft a SAR narrative for a customer exhibiting these red flags"

**Agent:** *Consults SAR specialist*
- Provides SAR template
- Includes required elements
- Suggests supporting documentation

## 📊 Monitoring

### LangFuse Observability

Every interaction is traced in LangFuse:

1. Go to https://cloud.langfuse.com
2. Find your session under "AML-Advisory-Session"
3. View:
   - Which specialists were consulted
   - What searches were performed
   - Retrieved knowledge base results
   - Token usage and costs
   - Full reasoning traces

### Console Output

Watch the terminal for:
```
✓ CDD Red Flags specialist initialized
✓ Regulatory Updates specialist initialized
✓ SAR Filing specialist initialized
✓ Policy Review specialist initialized
✓ Scenario Testing specialist initialized

Running on local URL:  http://127.0.0.1:7860
```

## 🛠️ Troubleshooting

### "Connection Error" on Launch

**Check:**
1. `.env` file exists and has correct API keys
2. Weaviate instance is accessible
3. No firewall blocking connections

**Test Weaviate connection:**
```bash
curl -H "Authorization: Bearer YOUR_API_KEY" \
  https://your-instance.weaviate.cloud/v1/.well-known/ready
```

### "Collection Not Found" Warning

The system will fall back to default collection (`enwiki_20250520`).

**To fix:**
- Create the missing collections in Weaviate, OR
- Update `KNOWLEDGE_BASE_COLLECTIONS` to use existing collections

### Slow Responses

**Possible causes:**
1. Large knowledge base searches
2. Multiple specialists being consulted
3. API rate limits

**Solutions:**
- Reduce `num_results` in knowledge base config
- Decrease `snippet_length`
- Check API rate limits

### No Streaming / Delayed Output

This is normal! The agent:
1. Thinks and plans (may take 5-10 seconds)
2. Searches knowledge bases
3. Then streams the response

Watch for "thinking" indicators in the UI.

## 🎓 Learning Resources

### Understanding the Code

1. **Main Agent** (`aml_advisor_gradio.py`): Orchestrates everything
2. **Specialist Agents**: Domain experts with knowledge base access
3. **Knowledge Bases**: Weaviate collections with AML content
4. **Streaming**: Real-time response delivery via Gradio

### Key Files

- `aml_advisor_gradio.py` - Gradio interface (this is what you run)
- `aml_advisor.py` - CLI version for batch processing
- `AML_ADVISOR_README.md` - Comprehensive documentation
- `AML_KNOWLEDGE_BASE_SETUP.md` - Weaviate setup guide

## 🚦 Next Steps

### For Development

1. **Customize Specialists**: Edit instructions in `create_specialist_agent()`
2. **Add New Categories**: Extend `AMLCategory` enum
3. **Adjust Models**: Change `AGENT_LLM_NAMES` for different LLMs
4. **Modify UI**: Customize Gradio theme and layout

### For Production

1. **Secure API Keys**: Use proper secrets management
2. **Set Up Monitoring**: Configure LangFuse alerts
3. **Add Authentication**: Protect the Gradio interface
4. **Scale Infrastructure**: Consider load balancing for multiple users
5. **Backup Data**: Regular Weaviate backups

## 📞 Support

### Common Issues

- **API Errors**: Check API keys and quotas
- **Slow Performance**: Adjust concurrency and search parameters
- **Wrong Answers**: Review knowledge base content quality
- **Missing Features**: Check if specialist has appropriate tools

### Getting Help

1. Check LangFuse traces for detailed execution logs
2. Review console output for errors
3. Test individual components separately
4. Verify environment variables

## ⚠️ Important Notes

### Compliance Disclaimer

This system provides **advisory support** but should not replace:
- Professional legal advice
- Compliance officer judgment
- Regulatory consultation
- Internal review processes

**Always have qualified compliance professionals review outputs before implementation.**

### Data Privacy

- Queries and responses are logged in LangFuse
- Knowledge base searches are recorded
- Ensure compliance with your data handling policies
- Consider data retention and privacy requirements

## 🎉 You're Ready!

Start the interface and begin chatting with your AML advisor:

```bash
uv run --env-file .env gradio src/2_frameworks/2_multi_agent/aml_advisor_gradio.py
```

**Happy advising! 🏦**
