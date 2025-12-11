# AML Knowledge Base Setup Guide

This guide explains how to set up and use Weaviate knowledge bases with the AML Advisory Agent system.

## Overview

The AML advisor integrates with Weaviate to provide each specialist agent access to domain-specific knowledge bases. Each of the 5 AML categories can have its own dedicated Weaviate collection:

1. **CDD Red Flags** → `aml_cdd_redflags`
2. **Regulatory Updates** → `aml_regulations`
3. **SAR Filing** → `aml_sar_guidelines`
4. **Policy Review** → `aml_policies`
5. **Scenario Testing** → `aml_case_studies`

## Architecture

```
User Query
    ↓
Router Agent (determines relevant specialists)
    ↓
Specialist Agents (each with dedicated knowledge base)
    ├─ CDD Agent → searches aml_cdd_redflags collection
    ├─ Regulatory Agent → searches aml_regulations collection
    ├─ SAR Agent → searches aml_sar_guidelines collection
    ├─ Policy Agent → searches aml_policies collection
    └─ Scenario Agent → searches aml_case_studies collection
    ↓
Synthesis Agent (combines all insights)
    ↓
Final Report
```

## Configuration

### 1. Environment Variables

Ensure your `.env` file has Weaviate credentials:

```bash
# Weaviate Configuration
WEAVIATE_HTTP_HOST="your-instance.weaviate.cloud"
WEAVIATE_GRPC_HOST="grpc-your-instance.weaviate.cloud"
WEAVIATE_API_KEY="your-api-key"
WEAVIATE_HTTP_PORT="443"
WEAVIATE_GRPC_PORT="443"
WEAVIATE_HTTP_SECURE="true"
WEAVIATE_GRPC_SECURE="true"

# Embedding Model (for vectorization)
EMBEDDING_BASE_URL="https://your-embedding-service.com"
EMBEDDING_API_KEY="your-embedding-key"

# OpenAI-compatible LLM
OPENAI_BASE_URL="https://generativelanguage.googleapis.com/v1beta/openai/"
OPENAI_API_KEY="your-openai-key"

# LangFuse (for observability)
LANGFUSE_SECRET_KEY="sk-lf-..."
LANGFUSE_PUBLIC_KEY="pk-lf-..."
LANGFUSE_HOST="https://us.cloud.langfuse.com"
```

### 2. Default Collection Names

The system uses these default collection names (defined in `aml_advisor.py`):

```python
KNOWLEDGE_BASE_COLLECTIONS = {
    AMLCategory.CDD_RED_FLAGS: "aml_cdd_redflags",
    AMLCategory.REGULATORY_UPDATES: "aml_regulations",
    AMLCategory.SAR_FILING: "aml_sar_guidelines",
    AMLCategory.POLICY_REVIEW: "aml_policies",
    AMLCategory.SCENARIO_TESTING: "aml_case_studies",
}
```

### 3. Custom Collection Names

You can override these at runtime using the `--collection` flag:

```bash
uv run --env-file .env src/2_frameworks/2_multi_agent/aml_advisor.py \
    --query "Your query here" \
    --collection cdd_red_flags=my_custom_cdd_collection \
    --collection sar_filing=my_sar_collection
```

## Usage Examples

### Example 1: Basic Usage with Default Collections

```bash
uv run --env-file .env src/2_frameworks/2_multi_agent/aml_advisor.py \
    --query "What are the key CDD red flags for cryptocurrency customers?"
```

This will:
- Use default collection names from `KNOWLEDGE_BASE_COLLECTIONS`
- Route to CDD specialist
- Search `aml_cdd_redflags` collection
- Generate comprehensive report

### Example 2: Custom Collections

```bash
uv run --env-file .env src/2_frameworks/2_multi_agent/aml_advisor.py \
    --query "Help me draft a SAR for structured deposits" \
    --collection sar_filing=company_sar_templates \
    --collection cdd_red_flags=company_cdd_guidelines
```

This overrides:
- SAR filing collection → `company_sar_templates`
- CDD red flags collection → `company_cdd_guidelines`

### Example 3: Using Single Collection for All Categories

If you have one comprehensive AML knowledge base:

```bash
uv run --env-file .env src/2_frameworks/2_multi_agent/aml_advisor.py \
    --query "Analyze our AML policy for gaps" \
    --collection cdd_red_flags=aml_master_kb \
    --collection regulatory_updates=aml_master_kb \
    --collection sar_filing=aml_master_kb \
    --collection policy_review=aml_master_kb \
    --collection scenario_testing=aml_master_kb
```

### Example 4: With Local Documents

Combine knowledge base search with local documents:

```bash
uv run --env-file .env src/2_frameworks/2_multi_agent/aml_advisor.py \
    --query "Review our customer onboarding process for AML compliance" \
    --documents_dir ./company_policies \
    --collection policy_review=aml_best_practices \
    --output_report policy_review_report.md
```

## How Knowledge Bases Are Used

### 1. Specialist Agent Tool

Each specialist agent gets a `search_knowledgebase` tool:

```python
tools=[
    agents.function_tool(
        knowledge_base.search_knowledgebase,
        tool_name=f"search_{category.value}",
        tool_description=f"Search the {category.value} knowledge base..."
    )
]
```

### 2. Agent Workflow

When a specialist agent is invoked:

1. **Receives query** and context from router
2. **Decides to search** knowledge base (autonomous decision)
3. **Calls search tool** with relevant keywords
4. **Receives results** (top 5 by default, 1000 char snippets)
5. **Analyzes results** and generates specialist analysis
6. **Returns structured output** with findings and recommendations

### 3. Search Configuration

You can customize search behavior by modifying the initialization:

```python
knowledge_bases[category] = AsyncWeaviateKnowledgeBase(
    async_weaviate_client,
    collection_name=collection_name,
    num_results=5,        # Number of results to return
    snippet_length=1000,  # Character length of text snippets
    max_concurrency=3,    # Max concurrent searches
)
```

## Creating Weaviate Collections

### Collection Schema Requirements

Your Weaviate collections should have these properties:

```json
{
  "class": "AmlCddRedflags",
  "properties": [
    {
      "name": "title",
      "dataType": ["text"],
      "description": "Document title"
    },
    {
      "name": "section",
      "dataType": ["text"],
      "description": "Section or category (optional)"
    },
    {
      "name": "text",
      "dataType": ["text"],
      "description": "Main content text"
    }
  ],
  "vectorizer": "text2vec-openai"  // or your chosen vectorizer
}
```

### Sample Data Structure

```json
{
  "title": "High-Risk Customer Indicators",
  "section": "Cryptocurrency",
  "text": "Customers operating in cryptocurrency exchanges should be subject to enhanced due diligence. Red flags include: 1) Frequent large transactions with no clear business purpose, 2) Use of multiple wallets or exchanges, 3) Transactions to/from high-risk jurisdictions..."
}
```

### Populating Collections

#### Option 1: Using Weaviate Client

```python
import weaviate
from weaviate.util import generate_uuid5

client = weaviate.Client(
    url="https://your-instance.weaviate.cloud",
    auth_client_secret=weaviate.AuthApiKey(api_key="your-key"),
)

# Add documents
documents = [
    {
        "title": "CDD Red Flags - Cryptocurrency",
        "section": "High-Risk Industries",
        "text": "Your content here..."
    },
    # ... more documents
]

for doc in documents:
    client.data_object.create(
        data_object=doc,
        class_name="AmlCddRedflags",
        uuid=generate_uuid5(doc)
    )
```

#### Option 2: Batch Import

```python
with client.batch as batch:
    batch.batch_size = 100
    for doc in documents:
        batch.add_data_object(
            data_object=doc,
            class_name="AmlCddRedflags"
        )
```

## Recommended Knowledge Base Content

### 1. CDD Red Flags Collection (`aml_cdd_redflags`)

- Industry-specific red flag indicators
- Risk assessment criteria
- Enhanced due diligence triggers
- Customer risk classification guidelines
- Beneficial ownership verification procedures
- PEP (Politically Exposed Person) screening guidelines

### 2. Regulatory Updates Collection (`aml_regulations`)

- FinCEN guidance documents
- FATF recommendations
- BSA/AML regulations by jurisdiction
- Regulatory advisory notices
- Compliance deadline calendars
- Enforcement action summaries

### 3. SAR Filing Collection (`aml_sar_guidelines`)

- SAR narrative templates
- Suspicious activity type definitions
- Filing procedures and timelines
- Required documentation checklists
- Case study examples
- Common filing mistakes to avoid

### 4. Policy Review Collection (`aml_policies`)

- Model AML policy templates
- Industry best practice documents
- Internal control frameworks
- Training program guidelines
- Audit and testing procedures
- Third-party risk management policies

### 5. Scenario Testing Collection (`aml_case_studies`)

- Real-world case studies (anonymized)
- Scenario testing templates
- Decision tree frameworks
- Escalation procedures
- Documentation examples
- Lessons learned from investigations

## Advanced Configuration

### Customizing Search Parameters

Edit the agent creation in `aml_advisor.py`:

```python
# For more comprehensive searches
knowledge_bases[category] = AsyncWeaviateKnowledgeBase(
    async_weaviate_client,
    collection_name=collection_name,
    num_results=10,       # More results
    snippet_length=2000,  # Longer snippets
    max_concurrency=5,    # Higher concurrency
)
```

### Using Different Embedding Models

Specify in the knowledge base initialization:

```python
knowledge_bases[category] = AsyncWeaviateKnowledgeBase(
    async_weaviate_client,
    collection_name=collection_name,
    embedding_model_name="text-embedding-3-large",
    embedding_api_key=os.getenv("OPENAI_API_KEY"),
    embedding_base_url="https://api.openai.com/v1",
)
```

### Fallback Behavior

If a collection doesn't exist, the system falls back to a default collection:

```python
if not knowledge_base:
    print(f"Warning: No knowledge base configured for {category.value}")
    knowledge_base = AsyncWeaviateKnowledgeBase(
        async_weaviate_client,
        collection_name="enwiki_20250520",  # Fallback
    )
```

## Monitoring and Debugging

### 1. LangFuse Tracing

All knowledge base searches are traced in LangFuse:

- View search queries made by each specialist
- See retrieved results and relevance
- Monitor token usage and costs
- Debug agent decision-making

### 2. Console Output

The system prints useful information:

```
Using collection 'my_cdd_kb' for cdd_red_flags
Loading documents from: ./aml_documents
Loaded 5 document(s)

Routing query to appropriate specialists...
Primary category: cdd_red_flags
Secondary categories: regulatory_updates
Reasoning: Query requires CDD analysis with regulatory context

Consulting specialists...
[████████████████████] 2/2 specialists completed

Synthesizing final advice...
Report generated: aml_advice.md
```

### 3. Error Handling

If a specialist fails:
- Error is logged
- Other specialists continue
- Synthesis proceeds with available analyses
- Check LangFuse for detailed error traces

## Performance Optimization

### 1. Concurrency Control

Adjust based on your API limits:

```python
MAX_CONCURRENCY = {
    "specialist": 3,  # Number of specialists running in parallel
    "synthesizer": 1
}
```

### 2. Content Limiting

Large documents are truncated:

```python
"content": doc.content[:5000],  # Limit to 5000 chars
```

### 3. Search Result Caching

Consider implementing caching for repeated queries:

```python
from functools import lru_cache

@lru_cache(maxsize=100)
async def cached_search(keyword: str):
    return await knowledge_base.search_knowledgebase(keyword)
```

## Troubleshooting

### Issue: "Weaviate is not ready (HTTP 503)"

**Solution**: Check Weaviate instance status and credentials

```bash
# Test connection
curl -H "Authorization: Bearer YOUR_API_KEY" \
  https://your-instance.weaviate.cloud/v1/.well-known/ready
```

### Issue: "No results found"

**Possible causes**:
1. Collection doesn't exist
2. Collection is empty
3. Query doesn't match content
4. Vectorization issues

**Solution**: Verify collection and test search:

```python
collection = client.collections.get("aml_cdd_redflags")
response = collection.query.hybrid("cryptocurrency red flags", limit=5)
print(response.objects)
```

### Issue: "Collection not found"

**Solution**: Create the collection or use `--collection` flag to specify existing one

### Issue: High API costs

**Solutions**:
1. Reduce `num_results` per search
2. Decrease `snippet_length`
3. Lower `MAX_CONCURRENCY`
4. Use cheaper embedding models
5. Implement result caching

## Best Practices

1. **Organize by Domain**: Keep collections focused on specific AML areas
2. **Update Regularly**: Keep regulatory content current
3. **Quality Over Quantity**: Well-curated content > large volumes
4. **Test Searches**: Verify retrieval quality before production use
5. **Monitor Costs**: Track API usage via LangFuse
6. **Version Control**: Tag collections with version/date
7. **Access Control**: Secure sensitive AML data appropriately
8. **Backup Data**: Regular backups of Weaviate collections

## Next Steps

1. **Create Collections**: Set up Weaviate collections for your AML domains
2. **Populate Data**: Import your AML knowledge base content
3. **Test Queries**: Run sample queries to verify retrieval
4. **Monitor Performance**: Use LangFuse to optimize
5. **Iterate**: Refine based on agent performance and user feedback

## Support

For issues:
- Check LangFuse traces for detailed execution logs
- Review Weaviate logs for connection/search issues
- Verify environment variables are set correctly
- Test individual components (router, specialists, synthesis) separately
