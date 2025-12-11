# AML Advisory Agent System - Complete Summary

## 📁 Files Created

### 1. Core Implementation
- **`aml_advisor.py`** - CLI version with full routing, specialists, and synthesis
- **`aml_advisor_gradio.py`** - Interactive Gradio chat interface (⭐ **Use this!**)

### 2. Documentation
- **`AML_QUICKSTART.md`** - 5-minute quick start guide
- **`AML_ADVISOR_README.md`** - Comprehensive documentation
- **`AML_KNOWLEDGE_BASE_SETUP.md`** - Weaviate integration guide
- **`AML_SUMMARY.md`** - This file

## 🚀 How to Run

### Interactive Chat (Recommended)

```bash
uv run --env-file .env gradio src/2_frameworks/2_multi_agent/aml_advisor_gradio.py
```

Then open the URL in your browser and start chatting!

### Command-Line (For Batch Processing)

```bash
uv run --env-file .env src/2_frameworks/2_multi_agent/aml_advisor.py \
    --query "Your AML question here" \
    --output_report report.md
```

## 🏗️ Architecture

### Gradio Version (aml_advisor_gradio.py)

```
User Chat Interface (Gradio)
    ↓
Main AML Advisor Agent
    ↓
Specialist Agents (called as tools)
    ├─ CDD Specialist + Knowledge Base
    ├─ Regulatory Specialist + Knowledge Base
    ├─ SAR Specialist + Knowledge Base
    ├─ Policy Specialist + Knowledge Base
    └─ Scenario Specialist + Knowledge Base
    ↓
Streamed Response to User
```

**Key Features:**
- Real-time streaming responses
- Interactive multi-turn conversations
- Visual agent reasoning display
- Public shareable URL via gradio.live
- Full LangFuse tracing

### CLI Version (aml_advisor.py)

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
- Batch processing
- Detailed markdown reports
- Custom collection mapping
- Local document integration
- Parallel specialist processing

## 🔑 Key Differences from Fan-Out Pattern

### Traditional Fan-Out (fan_out.py)
- Processes **all pairs** of documents (O(N²))
- Fixed processing pattern
- Best for: Pairwise comparisons, conflict detection

### AML Advisor (aml_advisor_gradio.py)
- **Intelligent routing** to relevant specialists only
- Dynamic specialist selection based on query
- Best for: Complex advisory tasks, interactive chat

## 🎯 5 Specialized Agents

Each agent has:
- Domain-specific instructions
- Dedicated Weaviate knowledge base
- Search tool for retrieving information
- Structured output format

### 1. CDD Red Flags Agent
- **Collection**: `aml_cdd_redflags`
- **Expertise**: Customer due diligence, risk indicators, KYC
- **Use for**: Red flag identification, risk assessment

### 2. Regulatory Updates Agent
- **Collection**: `aml_regulations`
- **Expertise**: Compliance changes, regulatory requirements
- **Use for**: Regulatory guidance, compliance updates

### 3. SAR Filing Agent
- **Collection**: `aml_sar_guidelines`
- **Expertise**: Suspicious activity reporting
- **Use for**: SAR drafting, filing procedures

### 4. Policy Review Agent
- **Collection**: `aml_policies`
- **Expertise**: AML policy development, gap analysis
- **Use for**: Policy review, improvement recommendations

### 5. Scenario Testing Agent
- **Collection**: `aml_case_studies`
- **Expertise**: Hypothetical scenario analysis
- **Use for**: Scenario guidance, decision support

## 🔧 Weaviate Integration

### How It Works

1. **Initialization**: Each specialist gets a knowledge base instance
2. **Tool Attachment**: `search_knowledgebase` tool added to each specialist
3. **Autonomous Search**: Agents decide when to search based on query
4. **Result Integration**: Search results inform agent responses

### Configuration

```python
# Default collections
KNOWLEDGE_BASE_COLLECTIONS = {
    AMLCategory.CDD_RED_FLAGS: "aml_cdd_redflags",
    AMLCategory.REGULATORY_UPDATES: "aml_regulations",
    AMLCategory.SAR_FILING: "aml_sar_guidelines",
    AMLCategory.POLICY_REVIEW: "aml_policies",
    AMLCategory.SCENARIO_TESTING: "aml_case_studies",
}
```

### Custom Collections

**In Gradio version**: Edit `KNOWLEDGE_BASE_COLLECTIONS` in the file

**In CLI version**: Use `--collection` flag
```bash
--collection cdd_red_flags=my_custom_collection
```

## 📊 Example Use Cases

### 1. Interactive Advisory Session (Gradio)

**Advisor asks:** "What CDD red flags should I look for in crypto customers?"

**Agent:**
1. Routes to CDD specialist
2. Searches `aml_cdd_redflags` collection
3. Streams response with specific indicators
4. Provides regulatory references

**Advisor follows up:** "How should I document these findings?"

**Agent:**
1. Routes to Policy specialist
2. Searches `aml_policies` collection
3. Provides documentation procedures

### 2. Batch Report Generation (CLI)

**Command:**
```bash
uv run --env-file .env src/2_frameworks/2_multi_agent/aml_advisor.py \
    --query "Comprehensive review of our AML program" \
    --documents_dir ./company_policies \
    --output_report aml_review.md
```

**Result:**
- Consults all relevant specialists
- Analyzes provided documents
- Generates detailed markdown report
- Includes recommendations and checklist

## 🎨 Gradio Interface Features

### UI Components

- **Chat Interface**: Natural conversation flow
- **Example Queries**: Pre-loaded common questions
- **Streaming**: Real-time response generation
- **Message History**: Full conversation context
- **Themed Design**: Professional blue/slate theme

### User Experience

1. **Clear Title**: "🏦 AML Advisory Multi-Agent System"
2. **Description**: Explains capabilities
3. **Examples**: Click to try immediately
4. **Streaming**: See agent thinking and responding
5. **Public URL**: Share with team via gradio.live

## 📈 Observability

### LangFuse Integration

Every interaction is traced:
- Session name: "AML-Advisory-Session"
- Input: User query
- Output: Final response
- Intermediate steps: Specialist consultations, searches
- Metadata: Token usage, timing, costs

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

## 🔐 Security Considerations

### API Keys
- Stored in `.env` file (not committed to git)
- Loaded via `dotenv`
- Never hardcoded in source

### Data Privacy
- All queries logged in LangFuse
- Knowledge base searches recorded
- Consider data retention policies
- Implement access controls for production

### Compliance
- System provides advisory support only
- Not a replacement for professional judgment
- Always review outputs with compliance officers
- Maintain audit trails via LangFuse

## 🚦 Performance

### Concurrency
```python
MAX_CONCURRENCY = {"specialist": 3}
```
- Up to 3 specialists run in parallel
- Adjust based on API rate limits

### Search Configuration
```python
AsyncWeaviateKnowledgeBase(
    num_results=5,        # Results per search
    snippet_length=1000,  # Character limit
)
```

### Response Times
- Simple query (1 specialist): 10-30 seconds
- Complex query (3+ specialists): 30-90 seconds
- Streaming starts immediately once agent begins responding

## 🛠️ Customization Guide

### Adding New Specialist

1. **Add to enum:**
```python
class AMLCategory(str, Enum):
    YOUR_NEW_CATEGORY = "your_category"
```

2. **Add collection:**
```python
KNOWLEDGE_BASE_COLLECTIONS = {
    AMLCategory.YOUR_NEW_CATEGORY: "your_collection",
}
```

3. **Add instructions:**
```python
instructions_map = {
    AMLCategory.YOUR_NEW_CATEGORY: """Your instructions...""",
}
```

4. **Add to main agent tools:**
```python
specialist_agents[AMLCategory.YOUR_NEW_CATEGORY].as_tool(
    tool_name="consult_your_specialist",
    tool_description="Your description...",
)
```

### Changing Models

```python
AGENT_LLM_NAMES = {
    "router": "gemini-2.5-flash",      # Fast routing
    "specialist": "gpt-4o",             # Change to GPT-4
    "main": "claude-3-5-sonnet",        # Change to Claude
}
```

### Adjusting UI Theme

```python
theme=gr.themes.Soft(
    primary_hue="blue",      # Change colors
    secondary_hue="slate",
)
```

## 📚 Documentation Structure

1. **AML_QUICKSTART.md** - Start here! 5-minute setup
2. **AML_ADVISOR_README.md** - Full documentation
3. **AML_KNOWLEDGE_BASE_SETUP.md** - Weaviate details
4. **AML_SUMMARY.md** - This overview

## ✅ Checklist for Production

- [ ] Configure all environment variables
- [ ] Create/populate Weaviate collections
- [ ] Test with sample queries
- [ ] Review LangFuse traces
- [ ] Set up monitoring and alerts
- [ ] Implement authentication (if needed)
- [ ] Configure data retention policies
- [ ] Train users on system capabilities
- [ ] Establish review procedures for outputs
- [ ] Document internal processes

## 🎓 Learning Path

### For Users
1. Read `AML_QUICKSTART.md`
2. Launch Gradio interface
3. Try example queries
4. Explore LangFuse traces

### For Developers
1. Review `aml_advisor_gradio.py` code
2. Understand specialist agent pattern
3. Read `AML_KNOWLEDGE_BASE_SETUP.md`
4. Experiment with customizations

### For Administrators
1. Set up Weaviate collections
2. Configure environment variables
3. Monitor LangFuse usage
4. Establish governance policies

## 🔄 Comparison: CLI vs Gradio

| Feature | CLI (`aml_advisor.py`) | Gradio (`aml_advisor_gradio.py`) |
|---------|------------------------|-----------------------------------|
| **Interface** | Command-line | Web browser |
| **Interaction** | Single query | Multi-turn chat |
| **Output** | Markdown file | Streamed chat |
| **Routing** | Explicit router agent | Implicit via main agent |
| **Synthesis** | Dedicated synthesis agent | Integrated in main agent |
| **Best For** | Batch processing, reports | Interactive advisory, exploration |
| **Sharing** | File-based | Public URL |
| **Real-time** | No | Yes (streaming) |
| **Documents** | Local files supported | Not directly supported |

## 🎯 Recommended Usage

### For Interactive Advisory
✅ **Use Gradio version** (`aml_advisor_gradio.py`)
- Real-time conversations
- Iterative refinement
- Team collaboration via shared URL
- Visual feedback

### For Batch Processing
✅ **Use CLI version** (`aml_advisor.py`)
- Automated report generation
- Integration with scripts
- Processing multiple queries
- Including local documents

## 🌟 Key Innovations

1. **Multi-Agent Orchestration**: Main agent dynamically consults specialists
2. **Knowledge Base Integration**: Each specialist has domain-specific search
3. **Streaming Responses**: Real-time feedback in Gradio
4. **Full Observability**: Every decision traced in LangFuse
5. **Flexible Architecture**: Easy to add new specialists or knowledge bases

## 📞 Getting Help

### Troubleshooting Steps
1. Check `.env` configuration
2. Verify Weaviate connectivity
3. Review LangFuse traces
4. Check console output for errors
5. Test individual components

### Common Issues
- **Slow responses**: Adjust concurrency, reduce search results
- **No results**: Check collection names, verify data exists
- **API errors**: Verify API keys, check quotas
- **Connection errors**: Test Weaviate endpoint

## 🎉 Success Criteria

You'll know it's working when:
- ✅ Gradio interface launches without errors
- ✅ Example queries return relevant responses
- ✅ Specialists are consulted appropriately
- ✅ Knowledge base searches retrieve information
- ✅ LangFuse shows complete traces
- ✅ Responses are accurate and actionable

## 🚀 Next Steps

1. **Launch the interface:**
   ```bash
   uv run --env-file .env gradio src/2_frameworks/2_multi_agent/aml_advisor_gradio.py
   ```

2. **Try example queries** to understand capabilities

3. **Review LangFuse traces** to see how it works

4. **Customize** for your specific AML needs

5. **Deploy** for your team to use

---

**You now have a complete, production-ready AML advisory agent system!** 🎊
