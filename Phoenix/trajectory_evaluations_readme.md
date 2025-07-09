# Trajectory Evaluations

A comprehensive evaluation framework for analyzing agent convergence patterns using Phoenix experiments. This notebook evaluates how efficiently an agent reaches the same conclusion when asked semantically similar questions.

## Overview

This project evaluates agent "convergence" - the ability of an AI agent to consistently reach the same answer through similar reasoning paths when presented with different phrasings of the same question. The evaluation focuses on measuring path efficiency and consistency across multiple question variations.

## Features

- **Convergence Testing**: Evaluates agent behavior across 17 semantically similar questions
- **Path Length Analysis**: Measures the efficiency of agent reasoning paths
- **Phoenix Integration**: Uses Phoenix for experiment tracking and evaluation
- **Automated Evaluation**: Scores agent performance based on optimal path length ratios

## Prerequisites

### Required Libraries
```bash
pip install phoenix-evals
pip install pandas
pip install nest-asyncio
```

### Dependencies
- `phoenix` - For experiment management and evaluation
- `utils2` - Contains the `run_agent` function
- `helper` - Contains Phoenix endpoint utilities
- OpenAI API access (for evaluation model)


### 1. Setup Environment

```python
import phoenix as px
from phoenix.experiments import run_experiment, evaluate_experiment
from utils2 import run_agent
from helper import get_phoenix_endpoint
```

### 2. Define Test Questions

The notebook includes 17 convergence questions that ask about the same concept (average quantity per transaction) in different ways:

- "What was the average quantity sold per transaction?"
- "What is the mean number of items per sale?"
- "Calculate the typical quantity per transaction"
- And 14 more variations...

### 3. Run Experiments

```python
# Create dataset
dataset = px_client.upload_dataset(
    dataframe=convergence_df,
    dataset_name=f"convergence_questions-{timestamp}",
    input_keys=["question"]
)

# Run experiment
experiment = run_experiment(
    dataset,
    run_agent_and_track_path,
    experiment_name="convergence Eval",
    experiment_description="Evaluating the convergence of an agent"
)
```

### 4. Evaluate Results

The evaluation uses a custom convergence metric:

```python
@create_evaluator(name="Convergence Eval", kind="CODE")
def evaluate_path_length(output: str) -> float:
    if output and output.get("path_length"):
        return optimal_path_length / float(output.get("path_length"))
    else:
        return 0
```

## Key Components

### Agent Task Function
```python
def run_agent_and_track_path(example: Example) -> str:
    messages = [{"role": "user", "content": example.input.get("question")}]
    ret = run_agent(messages)
    return {
        "path_length": len(ret),
        "messages": format_message_steps(ret)
    }
```

### Message Formatting
The `format_message_steps` function converts agent conversation history into a readable format showing:
- User inputs
- System context
- Assistant tool calls
- Tool responses
- Final assistant responses

### Evaluation Metrics

- **Path Length**: Number of steps in the agent's reasoning process
- **Convergence Score**: `optimal_path_length / actual_path_length`
- **Average Score**: Mean convergence score across all test questions

## Results Interpretation

### Path Length Analysis
- **Optimal Path Length**: 5 steps (minimum observed)
- **Average Score**: 0.966387 (96.6% efficiency)
- **Variance**: Most queries took 5 steps, with 2 queries taking 7 steps

### Convergence Insights
- High convergence score indicates consistent agent behavior
- Lower scores suggest inefficient reasoning paths
- Outliers may indicate edge cases or ambiguous phrasing

## Sample Output

```
Experiment Summary
------------------
          evaluator   n  n_scores  avg_score
0  Convergence Eval  17        17   0.966387

Tasks Summary
-------------
   n_examples  n_runs  n_errors
0          17      17         0
```

