# AML Advisory Agent - Architecture Diagram

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    AML ADVISORY SYSTEM                          │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              Gradio Web Interface                        │  │
│  │  • Chat UI                                               │  │
│  │  • Streaming responses                                   │  │
│  │  • Public URL sharing                                    │  │
│  └──────────────────────────────────────────────────────────┘  │
│                            ↓                                    │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │           Main AML Advisor Agent                         │  │
│  │  Model: gemini-2.5-pro                                   │  │
│  │  Role: Orchestrate specialists, synthesize advice        │  │
│  └──────────────────────────────────────────────────────────┘  │
│                            ↓                                    │
│         ┌──────────────────┴──────────────────┐                │
│         │    Consults Specialists (as tools)  │                │
│         └──────────────────┬──────────────────┘                │
│                            ↓                                    │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              5 SPECIALIST AGENTS                        │   │
│  │                                                         │   │
│  │  ┌──────────────────┐  ┌──────────────────┐           │   │
│  │  │ CDD Specialist   │  │ Regulatory       │           │   │
│  │  │ gemini-2.5-pro   │  │ Specialist       │           │   │
│  │  │                  │  │ gemini-2.5-pro   │           │   │
│  │  │ Tool:            │  │                  │           │   │
│  │  │ search_cdd       │  │ Tool:            │           │   │
│  │  │                  │  │ search_regulatory│           │   │
│  │  └────────┬─────────┘  └────────┬─────────┘           │   │
│  │           ↓                     ↓                      │   │
│  │  ┌──────────────────┐  ┌──────────────────┐           │   │
│  │  │ SAR Specialist   │  │ Policy           │           │   │
│  │  │ gemini-2.5-pro   │  │ Specialist       │           │   │
│  │  │                  │  │ gemini-2.5-pro   │           │   │
│  │  │ Tool:            │  │                  │           │   │
│  │  │ search_sar       │  │ Tool:            │           │   │
│  │  │                  │  │ search_policy    │           │   │
│  │  └────────┬─────────┘  └────────┬─────────┘           │   │
│  │           ↓                     ↓                      │   │
│  │  ┌──────────────────┐                                 │   │
│  │  │ Scenario         │                                 │   │
│  │  │ Specialist       │                                 │   │
│  │  │ gemini-2.5-pro   │                                 │   │
│  │  │                  │                                 │   │
│  │  │ Tool:            │                                 │   │
│  │  │ search_scenario  │                                 │   │
│  │  └────────┬─────────┘                                 │   │
│  └───────────┼─────────────────────────────────────────┘   │
│              ↓                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         WEAVIATE KNOWLEDGE BASES                     │  │
│  │                                                      │  │
│  │  ┌──────────────────┐  ┌──────────────────┐        │  │
│  │  │ aml_cdd_redflags │  │ aml_regulations  │        │  │
│  │  │ • Red flags      │  │ • FinCEN rules   │        │  │
│  │  │ • Risk factors   │  │ • FATF guidance  │        │  │
│  │  │ • KYC procedures │  │ • BSA/AML regs   │        │  │
│  │  └──────────────────┘  └──────────────────┘        │  │
│  │                                                      │  │
│  │  ┌──────────────────┐  ┌──────────────────┐        │  │
│  │  │ aml_sar_         │  │ aml_policies     │        │  │
│  │  │ guidelines       │  │ • Templates      │        │  │
│  │  │ • SAR templates  │  │ • Best practices │        │  │
│  │  │ • Filing rules   │  │ • Standards      │        │  │
│  │  └──────────────────┘  └──────────────────┘        │  │
│  │                                                      │  │
│  │  ┌──────────────────┐                               │  │
│  │  │ aml_case_studies │                               │  │
│  │  │ • Scenarios      │                               │  │
│  │  │ • Case examples  │                               │  │
│  │  └──────────────────┘                               │  │
│  └──────────────────────────────────────────────────────┘  │
│                            ↓                                │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              LANGFUSE OBSERVABILITY                  │  │
│  │  • Trace all interactions                            │  │
│  │  • Monitor token usage                               │  │
│  │  • Debug agent decisions                             │  │
│  │  • Track costs                                       │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Interaction Flow

### Example: "What are CDD red flags for crypto customers?"

```
Step 1: User Query
┌─────────────────────────────────────┐
│ User types in Gradio chat:          │
│ "What are CDD red flags for         │
│  cryptocurrency customers?"         │
└─────────────────────────────────────┘
                ↓
Step 2: Main Agent Receives Query
┌─────────────────────────────────────┐
│ Main AML Advisor Agent:             │
│ • Analyzes query                    │
│ • Determines CDD specialist needed  │
│ • Decides to consult specialist     │
└─────────────────────────────────────┘
                ↓
Step 3: Consult CDD Specialist
┌─────────────────────────────────────┐
│ Main Agent calls:                   │
│ consult_cdd_specialist(             │
│   "CDD red flags for crypto"        │
│ )                                   │
└─────────────────────────────────────┘
                ↓
Step 4: CDD Specialist Processes
┌─────────────────────────────────────┐
│ CDD Specialist Agent:               │
│ • Receives query                    │
│ • Decides to search knowledge base  │
│ • Calls search_cdd_red_flags tool   │
└─────────────────────────────────────┘
                ↓
Step 5: Knowledge Base Search
┌─────────────────────────────────────┐
│ Weaviate Search:                    │
│ • Collection: aml_cdd_redflags      │
│ • Query: "cryptocurrency red flags" │
│ • Returns: Top 5 relevant docs      │
│ • Snippet length: 1000 chars each   │
└─────────────────────────────────────┘
                ↓
Step 6: Specialist Analysis
┌─────────────────────────────────────┐
│ CDD Specialist:                     │
│ • Analyzes search results           │
│ • Identifies key red flags          │
│ • Provides recommendations          │
│ • Cites regulatory references       │
│ • Returns structured analysis       │
└─────────────────────────────────────┘
                ↓
Step 7: Main Agent Synthesis
┌─────────────────────────────────────┐
│ Main AML Advisor:                   │
│ • Receives specialist analysis      │
│ • Synthesizes into clear advice     │
│ • Formats for user consumption      │
│ • Streams response to Gradio        │
└─────────────────────────────────────┘
                ↓
Step 8: User Sees Response
┌─────────────────────────────────────┐
│ Gradio Interface:                   │
│ • Displays streaming response       │
│ • Shows agent reasoning (optional)  │
│ • User can ask follow-up questions  │
└─────────────────────────────────────┘
                ↓
Step 9: LangFuse Logging
┌─────────────────────────────────────┐
│ LangFuse records:                   │
│ • Full conversation trace           │
│ • Specialist consultations          │
│ • Knowledge base searches           │
│ • Token usage and costs             │
│ • Timing information                │
└─────────────────────────────────────┘
```

## Multi-Turn Conversation Flow

```
Turn 1: Initial Query
User: "What are CDD red flags for crypto?"
  ↓
Main Agent → CDD Specialist → Knowledge Base
  ↓
Response: [List of red flags with explanations]

Turn 2: Follow-up Question
User: "How should I document these findings?"
  ↓
Main Agent → Policy Specialist → Knowledge Base
  ↓
Response: [Documentation procedures and templates]

Turn 3: Specific Action
User: "Draft a SAR narrative for a customer showing these flags"
  ↓
Main Agent → SAR Specialist + CDD Specialist → Knowledge Bases
  ↓
Response: [SAR template with specific narrative]
```

## Component Responsibilities

### Main AML Advisor Agent
```
┌─────────────────────────────────────┐
│ Responsibilities:                   │
│ • Understand user intent            │
│ • Route to appropriate specialists  │
│ • Synthesize specialist insights    │
│ • Maintain conversation context     │
│ • Stream responses to user          │
│                                     │
│ Tools Available:                    │
│ • consult_cdd_specialist           │
│ • consult_regulatory_specialist    │
│ • consult_sar_specialist           │
│ • consult_policy_specialist        │
│ • consult_scenario_specialist      │
└─────────────────────────────────────┘
```

### Specialist Agents (5 total)
```
┌─────────────────────────────────────┐
│ Each Specialist:                    │
│ • Domain expert in specific area    │
│ • Has dedicated knowledge base      │
│ • Autonomous search decisions       │
│ • Structured output format          │
│ • Cites sources and regulations     │
│                                     │
│ Tool Available:                     │
│ • search_[category]_knowledge_base │
└─────────────────────────────────────┘
```

### Knowledge Bases
```
┌─────────────────────────────────────┐
│ Each Weaviate Collection:           │
│ • Domain-specific AML content       │
│ • Vectorized for semantic search    │
│ • Hybrid search (keyword + vector)  │
│ • Returns top-k relevant docs       │
│ • Configurable result count         │
└─────────────────────────────────────┘
```

## Data Flow

```
User Input (Text)
    ↓
Main Agent (Reasoning)
    ↓
Specialist Selection (Tool Call)
    ↓
Specialist Agent (Analysis)
    ↓
Knowledge Base Query (Vector Search)
    ↓
Search Results (Top-k Documents)
    ↓
Specialist Analysis (Structured Output)
    ↓
Main Agent Synthesis (Natural Language)
    ↓
Streaming Response (Real-time)
    ↓
User Interface (Gradio)
    ↓
LangFuse (Logging & Observability)
```

## Parallel Processing

When multiple specialists are needed:

```
User: "Comprehensive AML review"
    ↓
Main Agent decides to consult multiple specialists
    ↓
┌─────────────┬─────────────┬─────────────┐
│             │             │             │
CDD           Regulatory    Policy
Specialist    Specialist    Specialist
│             │             │
↓             ↓             ↓
Search KB     Search KB     Search KB
│             │             │
↓             ↓             ↓
Analysis      Analysis      Analysis
│             │             │
└─────────────┴─────────────┴─────────────┘
                    ↓
            Main Agent Synthesis
                    ↓
            Combined Response
```

## Technology Stack

```
┌─────────────────────────────────────────────┐
│ Frontend                                    │
│ • Gradio (Web UI)                          │
│ • Streaming chat interface                 │
│ • Public URL sharing                       │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│ Agent Framework                             │
│ • OpenAI Agents SDK                        │
│ • Multi-agent orchestration                │
│ • Tool calling                             │
│ • Streaming responses                      │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│ LLM Provider                                │
│ • Gemini 2.5 Flash (routing, specialists)  │
│ • Gemini 2.5 Pro (main agent)              │
│ • OpenAI-compatible API                    │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│ Knowledge Base                              │
│ • Weaviate (Vector database)               │
│ • Hybrid search (keyword + semantic)       │
│ • 5 domain-specific collections            │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│ Observability                               │
│ • LangFuse (Tracing & monitoring)          │
│ • Token usage tracking                     │
│ • Cost analysis                            │
└─────────────────────────────────────────────┘
```

## Deployment Architecture

```
┌─────────────────────────────────────────────┐
│ User's Browser                              │
│ • Accesses gradio.live URL                 │
│ • Interactive chat interface               │
└─────────────────────────────────────────────┘
                    ↓ HTTPS
┌─────────────────────────────────────────────┐
│ Gradio Server (Local or Cloud)             │
│ • Runs aml_advisor_gradio.py               │
│ • Handles WebSocket connections            │
│ • Streams responses                        │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│ Agent Runtime                               │
│ • Python async event loop                  │
│ • Manages agent lifecycle                  │
│ • Coordinates specialists                  │
└─────────────────────────────────────────────┘
         ↓                    ↓
┌──────────────────┐  ┌──────────────────┐
│ LLM API          │  │ Weaviate Cloud   │
│ (Gemini/OpenAI)  │  │ (Knowledge Base) │
└──────────────────┘  └──────────────────┘
         ↓
┌─────────────────────────────────────────────┐
│ LangFuse Cloud                              │
│ • Receives traces                          │
│ • Stores analytics                         │
└─────────────────────────────────────────────┘
```

## Security Architecture

```
┌─────────────────────────────────────────────┐
│ Environment Variables (.env)                │
│ • OPENAI_API_KEY                           │
│ • WEAVIATE_API_KEY                         │
│ • LANGFUSE_SECRET_KEY                      │
│ • Not committed to git                     │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│ Application Layer                           │
│ • Loads secrets via dotenv                 │
│ • No hardcoded credentials                 │
│ • Secure client initialization             │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│ External Services                           │
│ • HTTPS/TLS for all connections            │
│ • API key authentication                   │
│ • Rate limiting                            │
└─────────────────────────────────────────────┘
```

## Scalability Considerations

```
Current: Single Instance
┌─────────────────────────────────────┐
│ 1 Gradio Server                     │
│ • Handles multiple users            │
│ • Async processing                  │
│ • Concurrent specialist calls       │
└─────────────────────────────────────┘

Future: Multi-Instance
┌─────────────────────────────────────┐
│ Load Balancer                       │
│   ↓         ↓         ↓            │
│ Server 1  Server 2  Server 3       │
│   ↓         ↓         ↓            │
│ Shared Weaviate & LangFuse         │
└─────────────────────────────────────┘
```

## Cost Structure

```
Per Query Costs:

Main Agent (gemini-2.5-pro)
├─ Input tokens: ~500-1000
└─ Output tokens: ~500-2000

Specialist Agents (gemini-2.5-pro each)
├─ Input tokens: ~1000-2000 per specialist
├─ Output tokens: ~500-1000 per specialist
└─ Number consulted: 1-3 typically

Knowledge Base Searches
├─ Weaviate queries: ~5 results per search
├─ Embedding API calls: 1 per search
└─ Number of searches: 1-5 per query

Total per query: ~$0.05-0.20 (estimated)
```

---

This architecture provides:
- ✅ Modular design
- ✅ Scalable components
- ✅ Full observability
- ✅ Secure credential management
- ✅ Flexible knowledge base integration
- ✅ Real-time user experience
