# LLM Integration Instructions

## Overview
The `app/core/init_llm.py` module provides a standardized way to initialize OpenAI's ChatGPT for AI-powered features within the CA Verified AI Layer Backend.

## Environment Setup
Add the following environment variables to your `.env` file:

```env
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4                    # Optional, defaults to gpt-4
OPENAI_TEMPERATURE=0.5               # Optional, defaults to 0.5
```

## Usage Pattern

### Basic Usage
```python
from app.core.init_llm import make_llm

# Initialize with defaults
llm = make_llm()

# Or with custom parameters
llm = make_llm(
    model="gpt-4-turbo",
    temperature=0.3,
    max_retries=3
)
```

### Integration in API Routes
```python
from fastapi import APIRouter, Depends
from app.core.init_llm import make_llm
from app.core.tenant_context import get_tenant_context, TenantContext

router = APIRouter()

@router.post("/ai/reconcile")
async def ai_reconcile_transactions(
    data: ReconciliationRequest,
    context: TenantContext = Depends(get_tenant_context),
):
    llm = make_llm()
    
    # Use LLM for intelligent reconciliation
    prompt = f"Analyze these transactions for reconciliation: {data.transactions}"
    response = llm.invoke(prompt)
    
    return {"ai_analysis": response.content}
```

### AI-Powered Features Implementation

#### 1. Reconciliation Intelligence
```python
from app.core.init_llm import make_llm

def ai_reconciliation_analysis(vouchers, bank_statements):
    llm = make_llm(temperature=0.2)  # Lower temperature for consistency
    
    prompt = f"""
    Analyze these financial records for reconciliation:
    Vouchers: {vouchers}
    Bank Statements: {bank_statements}
    
    Identify potential matches and provide confidence scores.
    """
    
    return llm.invoke(prompt)
```

#### 2. Financial Anomaly Detection
```python
def detect_financial_anomalies(transactions):
    llm = make_llm(temperature=0.1)  # Very low temperature for accuracy
    
    prompt = f"""
    Review these transactions for anomalies:
    {transactions}
    
    Flag any suspicious patterns, unusual amounts, or data inconsistencies.
    """
    
    return llm.invoke(prompt)
```

## Best Practices

1. **Environment Variables**: Always use environment variables for API keys
2. **Temperature Settings**: 
   - Use 0.1-0.2 for financial analysis (consistency)
   - Use 0.5-0.7 for creative tasks (reporting)
3. **Error Handling**: Wrap LLM calls in try-catch blocks
4. **Tenant Context**: Always respect multi-tenant data isolation
5. **Cost Management**: Use appropriate models (gpt-4 for complex, gpt-3.5-turbo for simple tasks)

## Dependencies
- `langchain-openai`: LangChain's OpenAI integration
- `python-dotenv`: Environment variable management
- `openai`: OpenAI API client (installed via langchain-openai)

## Security Considerations
- Never log or expose API keys
- Validate all inputs before sending to LLM
- Implement rate limiting for LLM endpoints
- Ensure tenant data isolation in AI prompts