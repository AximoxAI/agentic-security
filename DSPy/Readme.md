# Healthcare Database Query System with DSPy

A natural language query system for healthcare patient data using DSPy framework and SQLite database.

## Overview

This system allows users to query patient healthcare data using natural language queries. It leverages the DSPy framework to parse user queries and translate them into structured database searches, making healthcare data more accessible without requiring SQL knowledge.

## Features

- **Natural Language Processing**: Query patient data using plain English
- **Flexible Filtering**: Search by medical condition, age, gender, test results, and admission year
- **Structured Output**: Returns formatted patient information with key details
- **SQLite Integration**: Efficient local database storage and querying

## Key Components

### 1. HealthcareDBTool Class
- **Purpose**: Handles database operations and query construction
- **Key Methods**:
  - `build_where_clause()`: Constructs SQL WHERE clauses from filters
  - `search_patients()`: Executes database queries with optional filters

### 2. PatientSearchModule Class
- **Purpose**: DSPy module that processes natural language queries
- **Key Methods**:
  - `forward()`: Main processing pipeline
  - `_parse_query()`: Extracts parameters from natural language using regex

### 3. Query Parameters Supported
- **condition**: Medical conditions (cancer, diabetes, hypertension, asthma, arthritis)
- **year**: Admission year (format: 2019-2024)
- **age_min**: Minimum age threshold
- **gender**: Patient gender (male/female)
- **test_result**: Test result status (normal/abnormal)

## Usage Procedure

### Step 1: Data Preparation
The system loads healthcare data from CSV and preprocesses it by:
- Reading the CSV file using pandas
- Removing unnecessary columns (Billing Amount, Room Number, Insurance Provider, Doctor, Hospital)
- Converting to SQLite database for efficient querying

### Step 2: Database Creation
```python
df = create_data()
db_path = 'healthcare.db'
conn = sqlite3.connect(db_path)
df.to_sql('patients', conn, if_exists='replace', index=False)
```

### Step 3: Query Processing Pipeline
1. **Input**: Natural language query (e.g., "Find patients with abnormal results in 2024")
2. **Parsing**: Extract parameters using regex patterns
3. **Database Query**: Build and execute SQL query with extracted filters
4. **Output**: Formatted patient information

### Step 4: Results Formatting
Results include:
- Patient name
- Medical condition
- Age and gender
- Test results
- Admission date

## Example Queries

The system can handle queries like:

```python
test_queries = [
    "Find patients with abnormal results in 2024",
    "List all cancer patients above age 40", 
    "Who was admitted for diabetes in 2022?",
    "List female patients whose test results are abnormal"
]
```

## Sample Output

```
Query: List all cancer patients above age 40
----------------------------------------
Found patients:
1. adrIENNE bEll - Cancer (Age: 43, Gender: Female, Test Results: Abnormal, Admission: 2022-09-19)
2. ChRISTopher BerG - Cancer (Age: 58, Gender: Female, Test Results: Inconclusive, Admission: 2021-05-23)
...
```

## Technical Implementation

### Query Parsing Strategy
The system uses regex patterns to extract:
- **Years**: `\b(20\d{2})\b` pattern
- **Ages**: `above age (\d+)|age (\d+)` pattern  
- **Conditions**: Direct string matching against known conditions
- **Gender/Results**: Keyword-based detection

### Database Schema
The SQLite database contains a `patients` table with columns:
- Name, Medical Condition, Medication
- Test Results, Age, Gender
- Date of Admission

## Configuration

Set up your OpenAI API key in `helper.py`:
```python
openai_api_key = "your-api-key-here"
```

Configure DSPy with your preferred language model:
```python
dspy.settings.configure(lm=dspy.LM("openai/gpt-4o-mini"))
```

## Limitations

- Query parsing relies on simple regex patterns
- Limited to predefined medical conditions
- Requires specific date formats and keywords
- No fuzzy matching for patient names or conditions

## Future Enhancements

- Advanced NLP for better query understanding
- Support for more complex queries and conditions
- Integration with medical ontologies
- Enhanced error handling and validation
- Web interface for easier access
