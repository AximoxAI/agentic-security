# Phoenix Tracing Agent

A comprehensive AI-powered sales data analysis agent with Phoenix tracing capabilities. This project implements an intelligent agent that can query, analyze, and visualize sales data from the Store Sales Price Elasticity Promotions dataset using OpenAI's GPT models with full observability through Phoenix tracing.

## Features

- **SQL Query Generation**: Automatically generates SQL queries based on natural language prompts
- **Data Analysis**: AI-powered analysis of sales data with insights extraction
- **Data Visualization**: Generates Python code for creating charts and visualizations
- **Phoenix Tracing**: Complete observability with OpenTelemetry integration - **KEY FEATURE**
- **Multi-tool Agent**: Intelligent routing between different analysis tools

##  How Phoenix Tracing Works

This project implements **comprehensive distributed tracing** using Phoenix and OpenTelemetry to provide complete visibility into your AI agent's execution:

### Tracing Architecture
```
User Query
    ↓
🔍 Main Span (AgentRun) - Traces entire conversation
    ↓
🔍 Router Span (router_call) - Traces decision making
    ↓
🔍 Tool Spans - Traces individual tool execution
    ↓
🔍 Chain Spans - Traces sub-operations within tools
    ↓
Real-time Dashboard Visualization
```

### What Gets Traced
- **Every OpenAI API call** (automatically instrumented)
- **Agent decision-making process** (router spans)
- **Tool executions** (data lookup, analysis, visualization)
- **SQL query execution** (custom spans)
- **Data processing steps** (chain spans)
- **Input/output data** at each step
- **Performance metrics** and timing
- **Error states** and exceptions

## Installation

1. Clone the repository or download the notebook
2. Install required dependencies:

```bash
pip install openai pandas duckdb phoenix-arize pydantic jupyter
pip install openinference-instrumentation-openai opentelemetry-api
```

3. Set up your OpenAI API key:
   - Create a `helper.py` file with a `get_openai_api_key()` function
   - Or set the `OPENAI_API_KEY` environment variable

## Dataset

The agent works with the `Store_Sales_Price_Elasticity_Promotions_Data.parquet` file, which should contain sales transaction data with columns for:
- Store information
- Product SKUs
- Sales amounts
- Dates
- Promotional data

## Usage

### Starting Phoenix Tracing

```python
import phoenix as px
from phoenix.otel import register

# Launch Phoenix app
session = px.launch_app()

# Register tracer
tracer_provider = register(
    project_name="tracing_agent",
    endpoint="http://localhost:6006/v1/traces"
)
```

### Running the Agent

```python
# Simple query
result = start_main_span([{
    "role": "user", 
    "content": "Which stores did the best in 2021?"
}])

# Complex analysis with visualization
result = start_main_span([{
    "role": "user", 
    "content": "Show me the code for graph of sales by store in Nov 2021, and tell me what trends you see."
}])
```

## 🔧 Tracing Implementation Details

### 1. Phoenix Setup & Registration
```python
# Launch Phoenix dashboard
session = px.launch_app()  # Starts local dashboard at localhost:6006

# Register OpenTelemetry tracer
tracer_provider = register(
    project_name="tracing_agent",
    endpoint="http://localhost:6006/v1/traces"
)

# Auto-instrument OpenAI calls
OpenAIInstrumentor().instrument(tracer_provider=tracer_provider)
```

### 2. Tracing Decorators in Action

#### **@tracer.tool() Decorator**
```python
@tracer.tool()  # 🔍 Creates tool-level spans
def lookup_sales_data(prompt: str) -> str:
    # This entire function execution is traced
    # Input: prompt string
    # Output: SQL results
    pass
```

#### **@tracer.chain() Decorator**
```python
@tracer.chain()  # 🔍 Creates chain-level spans
def extract_chart_config(data: str, visualization_goal: str) -> str:
    # Traces sub-operations within tools
    # Shows data flow between components
    pass
```

#### **Manual Span Creation**
```python
with tracer.start_as_current_span(
    "execute_sql_query",
    openinference_span_kind="chain"
) as span:
    span.set_input(sql_query)          # 🔍 Logs input data
    result = duckdb.sql(sql_query).df()
    span.set_output(value=str(result))  # 🔍 Logs output data
    span.set_status(StatusCode.OK)      # 🔍 Sets success status
```

### 3. Span Hierarchy Example

When you ask "Which stores did the best in 2021?":

```
🔍 AgentRun (agent)
  ├── 🔍 router_call (chain)
  │   ├── Input: User query
  │   ├── Output: Tool selection decision
  │   └── OpenAI API call (auto-instrumented)
  ├── 🔍 lookup_sales_data (tool)
  │   ├── Input: "Which stores did the best in 2021?"
  │   ├── 🔍 SQL Generation (OpenAI call)
  │   ├── 🔍 execute_sql_query (chain)
  │   │   ├── Input: Generated SQL
  │   │   └── Output: Query results
  │   └── Output: Formatted data
  └── 🔍 router_call (chain)
      ├── Input: Results + user query
      ├── OpenAI API call (auto-instrumented)
      └── Output: Final answer
```

### 4. What You See in Phoenix Dashboard

#### **Real-time Trace Visualization**
- **Timeline view**: See execution flow and timing
- **Span details**: Input/output data for each step
- **Performance metrics**: Latency, token usage, costs
- **Error tracking**: Failed operations and stack traces

#### **Span Attributes Tracked**
- `openinference_span_kind`: agent|tool|chain
- `input.value`: Input data to each operation
- `output.value`: Output data from each operation
- `llm.model_name`: OpenAI model used
- `llm.token_count`: Token usage per call
- `status`: Success/failure status

### 5. Advanced Tracing Features

#### **Automatic OpenAI Instrumentation**
```python
# Every OpenAI call is automatically traced with:
# - Model name and parameters
# - Input prompts and system messages
# - Response content and metadata
# - Token counts and costs
# - Latency and performance metrics
```

#### **Custom Span Kinds**
- `agent`: Top-level agent execution
- `tool`: Individual tool calls
- `chain`: Sub-operations and data processing
- `retrieval`: Data lookup operations (auto-detected)
- `llm`: Language model calls (auto-detected)

### 1. Data Lookup (`lookup_sales_data`)
- Converts natural language queries to SQL
- Executes queries against the parquet dataset
- Returns formatted results

### 2. Data Analysis (`analyze_sales_data`)
- AI-powered analysis of retrieved data
- Extracts insights and trends
- Provides business intelligence

### 3. Visualization (`generate_visualization`)
- Creates chart configurations based on data
- Generates Python code for visualizations
- Supports multiple chart types

## Architecture

```
User Query → Router → Tool Selection → Execution → Response
     ↓           ↓          ↓            ↓         ↓
🔍 Phoenix Tracing Captures Everything (OpenTelemetry)
     ↓           ↓          ↓            ↓         ↓
Real-time Observability Dashboard (localhost:6006)
```

**🔍 Tracing Flow:**
1. **Main Span** (`AgentRun`) - Wraps entire conversation
2. **Router Spans** (`router_call`) - Decision-making process
3. **Tool Spans** - Individual tool executions
4. **Chain Spans** - Sub-operations within tools
5. **LLM Spans** - All OpenAI API calls (auto-instrumented)

## 📊 Phoenix Dashboard Deep Dive

Access the Phoenix dashboard at `http://localhost:6006/` to view:

### **Trace Timeline**
- **Visual execution flow** of your entire agent run
- **Nested span hierarchy** showing parent-child relationships
- **Duration bars** for performance analysis
- **Color-coded span types** (agent, tool, chain, llm)

### **Span Details Panel**
- **Input/Output data** for every operation
- **Metadata and attributes** (model names, token counts)
- **Performance metrics** (latency, memory usage)
- **Error states** and exception details

### **Analytics Views**
- **Token usage patterns** across different operations
- **Performance bottlenecks** and slow operations
- **Error rates** and failure patterns
- **Cost tracking** for OpenAI API usage

### **Search and Filtering**
- **Filter by span kind** (agent, tool, chain, llm)
- **Search by input/output content**
- **Filter by status** (success, error)
- **Time range selection**

## 🔍 Tracing in Practice: Step-by-Step Example

Let's trace what happens when you ask: **"Which stores did the best in 2021?"**

### Step 1: Main Span Creation
```python
# 🔍 Creates top-level "AgentRun" span
with tracer.start_as_current_span("AgentRun", openinference_span_kind="agent") as span:
    span.set_input(value="Which stores did the best in 2021?")
    # ... agent execution ...
    span.set_output(value="Store 2970: $84,454.33, Store 3300: $63,205.33...")
```

### Step 2: Router Decision Tracing
```python
# 🔍 Creates "router_call" span to trace decision-making
with tracer.start_as_current_span("router_call", openinference_span_kind="chain") as span:
    span.set_input(value=messages)
    # OpenAI call to determine which tool to use (auto-traced)
    response = client.chat.completions.create(...)
    span.set_output(value=tool_calls)  # Decision: use lookup_sales_data
```

### Step 3: Tool Execution Tracing
```python
# 🔍 @tracer.tool() decorator creates tool span
@tracer.tool()
def lookup_sales_data(prompt: str) -> str:
    # This entire function is wrapped in a span
    # Input: "Which stores did the best in 2021?"
    
    # Sub-operation: SQL generation (OpenAI call - auto-traced)
    sql_query = generate_sql_query(prompt, columns, table_name)
    
    # Sub-operation: SQL execution (manual span)
    with tracer.start_as_current_span("execute_sql_query") as span:
        span.set_input(sql_query)
        result = duckdb.sql(sql_query).df()
        span.set_output(value=str(result))
    
    # Output: Formatted sales data
    return result.to_string()
```

### Step 4: What Phoenix Captures

```json
{
  "trace_id": "abc123...",
  "spans": [
    {
      "span_id": "main_001",
      "name": "AgentRun",
      "kind": "agent",
      "input": "Which stores did the best in 2021?",
      "output": "Store 2970: $84,454.33...",
      "duration_ms": 2847,
      "children": ["router_001", "tool_001", "router_002"]
    },
    {
      "span_id": "router_001", 
      "name": "router_call",
      "kind": "chain",
      "input": [{"role": "user", "content": "Which stores..."}],
      "output": "lookup_sales_data tool selected",
      "duration_ms": 423,
      "llm_calls": 1
    },
    {
      "span_id": "tool_001",
      "name": "lookup_sales_data", 
      "kind": "tool",
      "input": "Which stores did the best in 2021?",
      "output": "Store data table with rankings",
      "duration_ms": 1891,
      "children": ["sql_gen_001", "sql_exec_001"]
    }
  ]
}
```

## Key Components

- **Router Logic**: Intelligent tool selection based on user queries (🔍 **traced**)
- **SQL Generation**: Dynamic query creation using OpenAI (🔍 **auto-traced**)
- **Tracing Decorators**: `@tracer.tool()` and `@tracer.chain()` for observability
- **Error Handling**: Comprehensive error management for data operations (🔍 **error states traced**)

## Configuration

### Model Settings
```python
MODEL = "gpt-4o-mini"  # OpenAI model
PROJECT_NAME = "tracing_agent"  # Phoenix project name (🔍 appears in dashboard)
```

### Tracing Configuration
```python
# 🔍 OpenTelemetry endpoint - where traces are sent
PHOENIX_ENDPOINT = "http://localhost:6006/v1/traces"

# 🔍 Automatic instrumentation setup
OpenAIInstrumentor().instrument(tracer_provider=tracer_provider)
```

### File Paths
```python
TRANSACTION_DATA_FILE_PATH = 'Store_Sales_Price_Elasticity_Promotions_Data.parquet'
```

## Example Queries

- "Which stores did the best in 2021?"
- "Show me sales trends for store 1320 in November 2021"
- "Create a bar chart of sales by product SKU"
- "Analyze the impact of promotions on sales"
- "What are the top performing products?"

## Tracing Features

### 🔍 **Complete Observability**
- **Span Hierarchy**: Nested spans showing parent-child relationships
- **Input/Output Tracking**: Complete data flow visibility at every step
- **Error Monitoring**: Status tracking and error capture with stack traces
- **Performance Metrics**: Execution time, token usage, and resource consumption

### 🔍 **Automatic Instrumentation**
- **OpenAI API Calls**: Every LLM call automatically traced with prompts, responses, and metadata
- **Token Counting**: Automatic tracking of input/output tokens and costs
- **Model Metadata**: Model names, parameters, and configuration captured

### 🔍 **Custom Span Creation**
- **Manual Spans**: Create spans for specific operations with custom attributes
- **Span Kinds**: Different types (agent, tool, chain, llm) for better organization
- **Status Tracking**: Success/failure states with detailed error information

### 🔍 **Real-time Dashboard**
- **Live Updates**: See traces as they happen in real-time
- **Interactive Timeline**: Drill down into specific spans and operations
- **Search & Filter**: Find specific traces by content, status, or timeframe
- **Performance Analysis**: Identify bottlenecks and optimization opportunities

## Troubleshooting

### Common Issues

1. **🔍 Phoenix Connection**: 
   - Ensure Phoenix is running on localhost:6006
   - Check that `px.launch_app()` completed successfully
   - Verify traces are being sent to the correct endpoint

2. **🔍 Missing Traces**:
   - Confirm `OpenAIInstrumentor().instrument()` was called
   - Check that tracer decorators (`@tracer.tool()`, `@tracer.chain()`) are applied
   - Verify the tracer provider is registered correctly

3. **🔍 Incomplete Span Data**:
   - Ensure `span.set_input()` and `span.set_output()` are called
   - Check that spans are properly closed (use context managers)
   - Verify span status is set correctly

4. **API Key**: Verify OpenAI API key is correctly configured
5. **Dataset**: Check that the parquet file exists and is accessible
6. **Dependencies**: Ensure all required packages are installed

### Debug Mode

Enable detailed logging by checking the Phoenix dashboard for:
- **🔍 Trace timeline** - Visual execution flow
- **🔍 Span details** - Input/output data and metadata
- **🔍 Error states** - Failed operations and exception details
- **🔍 Performance metrics** - Slow operations and bottlenecks

## Security Considerations

- Store API keys securely
- Validate SQL queries before execution
- Sanitize user inputs
- Review generated code before execution

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is provided as-is for educational and development purposes.

## Support

For issues with:
- Phoenix tracing: Check the [Phoenix documentation](https://docs.arize.com/phoenix)
- OpenAI API: Refer to [OpenAI documentation](https://platform.openai.com/docs)
- Dataset issues: Ensure proper parquet file format and structure

## Acknowledgments

- Phoenix by Arize AI for observability
- OpenAI for language model capabilities
- DuckDB for efficient data processing
