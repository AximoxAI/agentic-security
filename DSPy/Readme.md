# Healthcare Database Query System with DSPy

A natural language query system for healthcare patient data using DSPy framework, LLM-powered SQL generation, and SQLite database.

## Overview

This system allows users to query patient healthcare data using natural language queries. It leverages the DSPy framework with LLM-powered SQL generation to translate natural language into structured database queries, making healthcare data more accessible without requiring SQL knowledge.

## Features

- **Natural Language Processing**: Query patient data using plain English
- **LLM-Powered SQL Generation**: Automatically converts natural language to SQL queries
- **Flexible Database Querying**: Support for complex queries through generated SQL
- **Structured Output**: Returns formatted patient information with key details
- **SQLite Integration**: Efficient local database storage and querying

## Key Components

### 1. TextToSql Class (DSPy Signature)
- **Purpose**: Defines the signature for converting natural language queries into SQL queries
- **Inputs**: Natural language query and database schema context
- **Output**: Generated SQL query string

### 2. HealthcareDBTool Class
- **Purpose**: Handles LLM-powered SQL generation and database operations
- **Key Methods**:
  - `get_schema_context()`: Provides database schema information for context
  - `generate_sql_query()`: Uses LLM to convert natural language to SQL
  - `execute_sql_query()`: Executes generated SQL queries safely
  - `search_patients_with_llm()`: Complete pipeline for LLM-based patient search

### 3. PatientSearchModule Class
- **Purpose**: DSPy module that orchestrates the complete search process
- **Key Methods**:
  - `forward()`: Main processing pipeline that generates SQL and formats results

### 4. Database Schema
The system works with a `patients` table containing:
- **Name** (TEXT): Patient's full name
- **Medical Condition** (TEXT): Patient's medical condition (Cancer, Diabetes, Hypertension, Asthma, Arthritis)
- **Medication** (TEXT): Prescribed medication
- **Test Results** (TEXT): Test results (Normal, Abnormal, Inconclusive)
- **Age** (INTEGER): Patient's age
- **Gender** (TEXT): Patient's gender (Male, Female)
- **Date of Admission** (TEXT): Date of admission in YYYY-MM-DD format


## Example Queries and Results

The system can handle complex natural language queries:

```python
test_queries = [
    "Find patients with abnormal test results in 2024",
    "List all cancer patients above age 40", 
    "Who was admitted for diabetes in 2022?",
    "List female patients whose test results are abnormal",
    "Show me all patients with hypertension who are male",
    "Find patients admitted between 2021 and 2023 with normal test results"
]
```

### Sample Output

```
Query: List all cancer patients above age 40
----------------------------------------
Generated SQL: SELECT * FROM patients 
WHERE "Medical Condition" = 'Cancer' 
AND Age > 40 
LIMIT 100;

Found patients:
1. adrIENNE bEll - Cancer (Age: 43, Gender: Female, Test Results: Abnormal, Admission: 2022-09-19)
2. ChRISTopher BerG - Cancer (Age: 58, Gender: Female, Test Results: Inconclusive, Admission: 2021-05-23)
3. mIchElLe daniELs - Cancer (Age: 72, Gender: Male, Test Results: Normal, Admission: 2020-04-19)
...
```

## Technical Implementation

### LLM-Powered SQL Generation
The system uses a sophisticated approach:
- **Schema Context**: Provides detailed database schema information to the LLM
- **Natural Language Processing**: LLM understands complex queries and relationships
- **SQL Generation**: Produces syntactically correct SQL with proper column quoting
- **Safety Features**: Automatic LIMIT clause addition to prevent excessive results

### Query Processing Features
- **Case-insensitive matching**: Uses LOWER() for string comparisons
- **Partial matching**: Supports LIKE with wildcards
- **Date extraction**: Uses strftime() for date-based queries
- **Column name handling**: Properly quotes column names with spaces
- **Error handling**: Comprehensive error management for database operations

### Database Schema Context
The system provides rich context to the LLM including:
- Complete table schema with column types
- Important notes about column naming conventions
- SQL best practices for the specific schema
- Performance optimization guidelines

## Error Handling and Safety

- **SQL Injection Prevention**: Uses parameterized queries and LLM-generated SQL
- **Result Limiting**: Automatic LIMIT clauses prevent excessive data retrieval
- **Database Error Handling**: Comprehensive exception handling for database operations
- **Query Validation**: Clean-up and validation of generated SQL queries

## Advantages Over Traditional Approaches

1. **Flexibility**: Can handle complex, multi-condition queries naturally
2. **Scalability**: LLM can adapt to new query patterns without code changes
3. **User-Friendly**: No SQL knowledge required from end users
4. **Maintainable**: Schema changes can be handled by updating context information
5. **Extensible**: Easy to add new query capabilities through prompt engineering

## Limitations

- **LLM Dependency**: Requires API access to language models
- **Cost Considerations**: API calls for each query may incur costs
- **Response Time**: LLM processing adds latency compared to direct SQL
- **Data Privacy**: Queries are processed by external LLM services
- **Schema Dependency**: Changes in database schema require context updates

## Future Enhancements

- **Query Optimization**: Cache common SQL patterns to reduce LLM calls
- **Local LLM Support**: Integration with local language models for privacy
- **Advanced Analytics**: Support for aggregation and statistical queries
- **Multi-table Joins**: Expand to support complex multi-table relationships
- **Query History**: Store and learn from previous successful queries
- **Web Interface**: Browser-based interface for easier access
- **Real-time Updates**: Support for live database updates and notifications