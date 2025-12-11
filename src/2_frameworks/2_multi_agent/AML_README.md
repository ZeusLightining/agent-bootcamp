# 🏦 AML Advisory Multi-Agent System

**Complete AI-powered AML compliance advisory with interactive chat interface**

Built using OpenAI Agents SDK, Weaviate knowledge bases, and Gradio for a production-ready AML advisory system.

---

## 🚀 Quick Start (5 Minutes)

### 1. Launch the Interface

```bash
cd /Users/267958742/Documents/GitHub/agent-bootcamp
uv run --env-file .env gradio src/2_frameworks/2_multi_agent/aml_advisor_gradio.py
```

### 2. Open in Browser

```
Running on local URL:  http://127.0.0.1:7860
Running on public URL: https://xxxxx.gradio.live
```

### 3. Start Chatting!

Try these example queries:
- "What are the key CDD red flags for cryptocurrency customers?"
- "Help me draft a SAR for structured deposits"
- "What are the latest FinCEN guidance updates?"

**That's it!** You now have an interactive AML advisor.

---

## 📁 Files Overview

| File | Purpose | When to Use |
|------|---------|-------------|
| **`aml_advisor_gradio.py`** | Interactive chat interface | ⭐ **Start here!** Daily advisory work |
| **`aml_advisor.py`** | Command-line batch processor | Automated reports, scripts |
| **`test_aml_setup.py`** | Setup verification script | Before first run |
| **`AML_QUICKSTART.md`** | 5-minute getting started guide | First-time setup |
| **`AML_ADVISOR_README.md`** | Complete documentation | Deep dive into features |
| **`AML_KNOWLEDGE_BASE_SETUP.md`** | Weaviate configuration guide | Setting up knowledge bases |
| **`AML_ARCHITECTURE.md`** | System architecture diagrams | Understanding the design |
| **`AML_SUMMARY.md`** | Complete system overview | High-level understanding |

---

## 🎯 What Does It Do?

### 5 Specialized AML Advisors

1. **🔍 CDD Red Flags Specialist**
   - Customer due diligence analysis
   - Risk indicator identification
   - KYC compliance guidance

2. **📋 Regulatory Updates Specialist**
   - Latest regulatory changes
   - Compliance requirements
   - Jurisdictional guidance

3. **📝 SAR Filing Specialist**
   - Suspicious activity report drafting
   - Filing procedures
   - Regulatory compliance

4. **📊 Policy Review Specialist**
   - AML policy analysis
   - Gap identification
   - Improvement recommendations

5. **🎯 Scenario Testing Specialist**
   - Hypothetical scenario analysis
   - Decision support
   - Action recommendations

### How It Works

```
You ask a question
    ↓
Main AML Advisor analyzes your query
    ↓
Consults relevant specialist(s)
    ↓
Each specialist searches their knowledge base
    ↓
Synthesizes insights into actionable advice
    ↓
Streams response to you in real-time
```

---

## 🔧 Setup Requirements

### Environment Variables

Your `.env` file needs:

```bash
# Required: OpenAI-compatible LLM
OPENAI_BASE_URL="https://generativelanguage.googleapis.com/v1beta/openai/"
OPENAI_API_KEY="your-api-key"

# Required: Weaviate
WEAVIATE_HTTP_HOST="your-instance.weaviate.cloud"
WEAVIATE_GRPC_HOST="grpc-your-instance.weaviate.cloud"
WEAVIATE_API_KEY="your-api-key"
WEAVIATE_HTTP_PORT="443"
WEAVIATE_GRPC_PORT="443"
WEAVIATE_HTTP_SECURE="true"
WEAVIATE_GRPC_SECURE="true"

# Required: Embeddings
EMBEDDING_BASE_URL="your-embedding-service"
EMBEDDING_API_KEY="your-embedding-key"

# Optional but recommended: LangFuse
LANGFUSE_SECRET_KEY="sk-lf-..."
LANGFUSE_PUBLIC_KEY="pk-lf-..."
LANGFUSE_HOST="https://us.cloud.langfuse.com"
```

### Verify Setup

```bash
# Test your configuration
uv run --env-file .env python src/2_frameworks/2_multi_agent/test_aml_setup.py
```

---

## 💡 Usage Examples

### Interactive Chat (Gradio)

**Launch:**
```bash
uv run --env-file .env gradio src/2_frameworks/2_multi_agent/aml_advisor_gradio.py
```

**Example conversation:**

> **You:** What are CDD red flags for cryptocurrency customers?
> 
> **Agent:** *[Consults CDD specialist, searches knowledge base]*
> 
> Based on current AML guidelines, key red flags for cryptocurrency customers include:
> 1. Frequent large transactions with no clear business purpose...
> 2. Use of multiple wallets or exchanges...
> [continues with detailed analysis]

> **You:** How should I document these findings?
>
> **Agent:** *[Consults Policy specialist]*
>
> For documenting CDD findings on cryptocurrency customers, follow these procedures:
> 1. Create a comprehensive customer risk profile...
> [continues with documentation guidance]

### Command-Line (Batch Processing)

```bash
# Generate a comprehensive report
uv run --env-file .env src/2_frameworks/2_multi_agent/aml_advisor.py \
    --query "Comprehensive AML policy review" \
    --documents_dir ./company_policies \
    --output_report aml_review.md
```

---

## 🏗️ Architecture

### Gradio Version (Recommended)

```
Gradio Chat Interface
    ↓
Main AML Advisor Agent (gemini-2.5-pro)
    ↓
Specialist Agents (as tools)
    ├─ CDD Specialist → aml_cdd_redflags
    ├─ Regulatory Specialist → aml_regulations
    ├─ SAR Specialist → aml_sar_guidelines
    ├─ Policy Specialist → aml_policies
    └─ Scenario Specialist → aml_case_studies
    ↓
Weaviate Knowledge Bases
    ↓
LangFuse Observability
```

**Key Features:**
- ✅ Real-time streaming responses
- ✅ Multi-turn conversations
- ✅ Public URL sharing (gradio.live)
- ✅ Visual agent reasoning
- ✅ Full LangFuse tracing

### CLI Version

```
User Query
    ↓
Router Agent (determines specialists)
    ↓
Specialist Agents (parallel processing)
    ↓
Synthesis Agent (combines insights)
    ↓
Markdown Report
```

**Key Features:**
- ✅ Batch processing
- ✅ Detailed reports
- ✅ Local document integration
- ✅ Scriptable

---

## 🎨 Customization

### Using Your Own Knowledge Bases

Edit `KNOWLEDGE_BASE_COLLECTIONS` in `aml_advisor_gradio.py`:

```python
KNOWLEDGE_BASE_COLLECTIONS = {
    AMLCategory.CDD_RED_FLAGS: "your_cdd_collection",
    AMLCategory.REGULATORY_UPDATES: "your_regulations_collection",
    AMLCategory.SAR_FILING: "your_sar_collection",
    AMLCategory.POLICY_REVIEW: "your_policies_collection",
    AMLCategory.SCENARIO_TESTING: "your_scenarios_collection",
}
```

### Using a Single Collection

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

### Changing Models

```python
AGENT_LLM_NAMES = {
    "specialist": "gpt-4o",           # Use GPT-4
    "main": "claude-3-5-sonnet",      # Use Claude
}
```

---

## 📊 Monitoring & Observability

### LangFuse Integration

Every interaction is traced:
- Session name: "AML-Advisory-Session"
- Specialist consultations
- Knowledge base searches
- Token usage and costs
- Full reasoning traces

**Access:** https://cloud.langfuse.com

### Console Output

```
🏦 AML ADVISORY MULTI-AGENT SYSTEM
================================================================================

Starting Gradio interface...
Knowledge bases initialized for:
  ✓ Cdd Red Flags
  ✓ Regulatory Updates
  ✓ Sar Filing
  ✓ Policy Review
  ✓ Scenario Testing

Running on local URL:  http://127.0.0.1:7860
Running on public URL: https://xxxxx.gradio.live
```

---

## 🔍 How It Compares to Fan-Out

### Traditional Fan-Out (`fan_out.py`)
- Processes **all pairs** of documents (O(N²))
- Fixed processing pattern
- Best for: Pairwise comparisons, conflict detection

### AML Advisor (`aml_advisor_gradio.py`)
- **Intelligent routing** to relevant specialists only
- Dynamic specialist selection based on query
- Best for: Complex advisory tasks, interactive chat

**Key Innovation:** Instead of processing all combinations, the main agent intelligently decides which specialists to consult based on the user's query.

---

## 🛠️ Troubleshooting

### "Connection Error"

**Check:**
1. `.env` file has correct API keys
2. Weaviate instance is accessible
3. Run test script: `uv run --env-file .env python src/2_frameworks/2_multi_agent/test_aml_setup.py`

### "Collection Not Found"

**Solution:**
- System will fall back to default collection
- Create AML-specific collections (see `AML_KNOWLEDGE_BASE_SETUP.md`)
- Or edit `KNOWLEDGE_BASE_COLLECTIONS` to use existing collections

### Slow Responses

**Normal behavior:**
- Agent thinks and plans (5-10 seconds)
- Searches knowledge bases
- Then streams response

**To optimize:**
- Reduce `num_results` in knowledge base config
- Decrease `snippet_length`
- Lower `MAX_CONCURRENCY`

---

## 📚 Documentation Guide

**Start here:**
1. **`AML_QUICKSTART.md`** - Get running in 5 minutes

**For users:**
2. **`AML_ADVISOR_README.md`** - Complete feature documentation
3. **`AML_SUMMARY.md`** - System overview

**For developers:**
4. **`AML_ARCHITECTURE.md`** - Technical architecture
5. **`AML_KNOWLEDGE_BASE_SETUP.md`** - Weaviate setup

**For testing:**
6. **`test_aml_setup.py`** - Verify configuration

---

## ⚠️ Important Notes

### Compliance Disclaimer

This system provides **advisory support** but should not replace:
- Professional legal advice
- Compliance officer judgment
- Regulatory consultation
- Internal review processes

**Always have qualified compliance professionals review outputs.**

### Data Privacy

- Queries and responses are logged in LangFuse
- Knowledge base searches are recorded
- Ensure compliance with your data handling policies

---

## 🎯 Next Steps

### 1. Quick Test
```bash
uv run --env-file .env python src/2_frameworks/2_multi_agent/test_aml_setup.py
```

### 2. Launch Interface
```bash
uv run --env-file .env gradio src/2_frameworks/2_multi_agent/aml_advisor_gradio.py
```

### 3. Try Examples
- Click example queries in the interface
- Ask follow-up questions
- Review LangFuse traces

### 4. Customize
- Add your knowledge bases
- Adjust specialist instructions
- Modify UI theme

### 5. Deploy
- Set up authentication
- Configure monitoring
- Train your team

---

## 🎉 You're Ready!

Launch the interface and start getting expert AML advice:

```bash
uv run --env-file .env gradio src/2_frameworks/2_multi_agent/aml_advisor_gradio.py
```

**Questions?** Check the documentation files or review LangFuse traces for detailed execution logs.

**Happy advising! 🏦**
