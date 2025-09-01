#!/usr/bin/env python
# coding: utf-8

from openai import OpenAI
import pandas as pd
import json
import duckdb
from pydantic import BaseModel, Field

from DSPy.helper import get_openai_api_key, get_phoenix_endpoint

import phoenix as px
from phoenix.otel import register
from openinference.instrumentation.openai import OpenAIInstrumentor
from opentelemetry.trace import StatusCode
from openinference.instrumentation import TracerProvider

# Initialize OpenAI client and Phoenix tracer
openai_api_key = get_openai_api_key()
client = OpenAI(api_key=openai_api_key)
MODEL = "gpt-4o-mini"
PROJECT_NAME = "evaluating-agent"

tracer_provider = register(
    project_name=PROJECT_NAME,
    endpoint=get_phoenix_endpoint() + "v1/traces"
)

OpenAIInstrumentor().instrument(tracer_provider=tracer_provider)
tracer = tracer_provider.get_tracer(__name__)

# File path
TRANSACTION_DATA_FILE_PATH = '/Users/priyanka./Documents/ai-agents/Phoenix/Store_Sales_Price_Elasticity_Promotions_Data.parquet'

# SQL Prompt Template
SQL_GENERATION_PROMPT = """
Generate an SQL query based on a prompt. Do not reply with anything besides the SQL query.
The prompt is : {prompt}
The availabe columns are: {columns}
The table name is: {table_name}
"""

def generate_sql_query(prompt: str, columns: list, table_name: str) -> str:
    formatted_prompt = SQL_GENERATION_PROMPT.format(prompt=prompt, columns=columns, table_name=table_name)
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": formatted_prompt}],
    )
    return response.choices[0].message.content

@tracer.tool()
def lookup_sales_data(prompt: str) -> str:
    try:
        table_name = "sales"
        df = pd.read_parquet(TRANSACTION_DATA_FILE_PATH)
        duckdb.sql(f"CREATE TABLE IF NOT EXISTS {table_name} AS SELECT * FROM df")
        sql_query = generate_sql_query(prompt, df.columns, table_name).strip().replace("```sql", "").replace("```", "")
        with tracer.start_as_current_span("execute_sql_query", openinference_span_kind="chain") as span:
            span.set_input(sql_query)
            result = duckdb.sql(sql_query).df()
            span.set_output(value=str(result))
            span.set_status(StatusCode.OK)
        return result.to_string()
    except Exception as e:
        return f"Error accessing data: {str(e)}"

DATA_ANALYSIS_PROMPT = """
Analyse the following data:{data}
Your job is to answer the following question:{prompt}
"""

@tracer.tool()
def analyze_sales_data(prompt: str, data: str) -> str:
    formatted_prompt = DATA_ANALYSIS_PROMPT.format(data=data, prompt=prompt)
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": formatted_prompt}]
    )
    analysis = response.choices[0].message.content
    return analysis if analysis else "No analysis could be generated"

CHART_CONFIGURATION_PROMPT = """
Generate a chart configuration based on this data:{data}
The goal is to show:{visualization_goal}
"""

class VisualizationConfig(BaseModel):
    chart_type: str = Field(..., description="Type of chart to generate")
    x_axis: str = Field(..., description="Name of the x-axis column")
    y_axis: str = Field(..., description="Name of the y-axis column")
    title: str = Field(..., description="Title of the chart")

@tracer.chain()
def extract_chart_config(data: str, visualization_goal: str) -> str:
    formatted_prompt = CHART_CONFIGURATION_PROMPT.format(data=data, visualization_goal=visualization_goal)
    response = client.beta.chat.completions.parse(
        model=MODEL,
        messages=[{"role": "user", "content": formatted_prompt}],
        response_format=VisualizationConfig
    )
    try:
        content = response.choices[0].message.content
        return {
            "chart_type": content.chart_type,
            "x_axis": content.x_axis,
            "y_axis": content.y_axis,
            "title": content.title,
            "data": data
        }
    except Exception:
        return {
            "chart_type": "line",
            "x_axis": "date",
            "y_axis": "value",
            "title": visualization_goal,
            "data": data
        }

CREATE_CHART_PROMPT = """
Write python code to create a chart based on the following configuration.
Only return the code, no other text.
config:{config}
"""

@tracer.chain()
def create_chart(config: dict) -> str:
    formatted_prompt = CREATE_CHART_PROMPT.format(config=config)
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": formatted_prompt}],
    )
    code = response.choices[0].message.content.replace("```python", "").replace("```", "").strip()
    return code

@tracer.tool()
def generate_visualization(data: str, visualization_goal: str) -> str:
    config = extract_chart_config(data, visualization_goal)
    code = create_chart(config)
    return code

tools = [
    {
        "type": "function",
        "function": {
            "name": "lookup_sales_data",
            "description": "Look up data from Store Sales Price Elasticity Promotions dataset",
            "parameters": {
                "type": "object",
                "properties": {
                    "prompt": {"type": "string", "description": "The unchanged prompt that the user provided."}
                },
                "required": ["prompt"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "analyze_sales_data",
            "description": "Analyze sales data to extract insights",
            "parameters": {
                "type": "object",
                "properties": {
                    "data": {"type": "string", "description": "The lookup_sales_data tool's output."},
                    "prompt": {"type": "string", "description": "The unchanged prompt that the user provided."}
                },
                "required": ["data", "prompt"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "generate_visualization",
            "description": "Generate Python code to create data visualizations",
            "parameters": {
                "type": "object",
                "properties": {
                    "data": {"type": "string", "description": "The lookup_sales_data tool's output."},
                    "visualization_goal": {"type": "string", "description": "The goal of the visualization."}
                },
                "required": ["data", "visualization_goal"]
            }
        }
    }
]

tool_implementations = {
    "lookup_sales_data": lookup_sales_data,
    "analyze_sales_data": analyze_sales_data,
    "generate_visualization": generate_visualization
}

@tracer.chain()
def handle_tool_calls(tool_calls, messages):
    for tool_call in tool_calls:
        function = tool_implementations[tool_call.function.name]
        function_args = json.loads(tool_call.function.arguments)
        result = function(**function_args)
        messages.append({"role": "tool", "content": result, "tool_call_id": tool_call.id})
    return messages

SYSTEM_PROMPT = """
You are a helpful assistant that can answer questions about the Store Sales Price Elasticity Promotions dataset.
"""

def run_agent(messages):
    if isinstance(messages, str):
        messages = [{"role": "user", "content": messages}]
    if not any(isinstance(message, dict) and message.get("role") == "system" for message in messages):
        messages.append({"role": "system", "content": SYSTEM_PROMPT})
    while True:
        with tracer.start_as_current_span("router_call", openinference_span_kind="chain") as span:
            span.set_input(value=messages)
            response = client.chat.completions.create(
                model=MODEL,
                messages=messages,
                tools=tools,
            )
            messages.append(response.choices[0].message)
            tool_calls = response.choices[0].message.tool_calls
            span.set_status(StatusCode.OK)
        if tool_calls:
            messages = handle_tool_calls(tool_calls, messages)
            span.set_output(value=tool_calls)
        else:
            span.set_output(value=response.choices[0].message.content)
            return response.choices[0].message.content

def start_main_span(messages):
    with tracer.start_as_current_span("AgentRun", openinference_span_kind="agent") as span:
        span.set_input(value=messages)
        ret = run_agent(messages)
        span.set_output(value=ret)
        span.set_status(StatusCode.OK)
        return ret
