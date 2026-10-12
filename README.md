# Data Analyst Copilot 🤖📊

An AI-powered data analysis assistant that translates natural-language questions into Python Pandas code, executes the generated code against a dataset, and returns results and visualizations.

The project combines **multi-agent orchestration, Retrieval-Augmented Generation (RAG), vector search, and Python code execution** to create a practical workflow for interacting with structured data using natural language.

## 🚀 Project Overview

Data Analyst Copilot allows users to ask questions about a sales dataset without manually writing Pandas code.

For example:

* What is the total cost for each country?
* Which product categories generate the highest total cost?
* How many orders belong to each customer type?
* Plot the total cost over time.

The system interprets the question, retrieves relevant dataset documentation, generates Python code, executes it, and displays the results.

## ✨ Key Features

* **Natural Language Queries:** Ask data analysis questions in English or Arabic.
* **Multi-Agent Architecture:** Use specialized CrewAI agents for business context generation, query understanding, retrieval-count extraction, and Python code generation.
* **Dataset Documentation:** Generate structured documentation describing column names, data types, unique values, observed categories, and potential business meanings.
* **Retrieval-Augmented Generation (RAG):** Retrieve relevant column documentation to provide context for downstream agents.
* **Semantic Search:** Use sentence embeddings and ChromaDB to retrieve documentation based on semantic similarity.
* **Automated Pandas Code Generation:** Generate Python code tailored to the user's question and the available dataset.
* **Code Execution:** Run the generated code against a copy of the dataset and capture printed output and execution errors.
* **Data Visualization:** Generate charts using Matplotlib when requested.
* **Streamlit Interface:** Interact with the assistant through a simple web application.
* **Transparent Workflow:** Inspect the interpreted question, generated code, retrieved documentation, and analysis results.

## 🏗️ Architecture

The project follows a multi-stage workflow:

1. **Dataset Loading:** Load the Excel dataset using Pandas and extract column metadata.
2. **Business Context Generation:** A CrewAI agent creates structured documentation for the dataset, including column descriptions and observed categorical values.
3. **Query Understanding:** An agent translates the user's question into a structured plan containing the corrected question, required columns, calculation, and clarification status.
4. **Retrieval Count Extraction:** A specialized agent extracts the number of required columns to guide document retrieval.
5. **Document Retrieval:** The RAG component embeds the query plan and retrieves relevant documentation chunks from ChromaDB.
6. **Code Generation:** A Python code-generation agent produces Pandas code using the retrieved context.
7. **Code Execution:** The generated code runs against a copy of the dataset, with standard output and errors captured.
8. **Result Presentation:** The application displays the results, generated code, retrieved documentation, and any charts.

### Workflow Diagram

```text
             User Question
                   |
                   v
          Query Understanding
                   |
                   v
          Retrieval Count Agent
                   |
                   v
          Semantic Document Search
             (RAG + ChromaDB)
                   |
                   v
          Python Code Generation
                   |
                   v
          Code Execution (Pandas)
                   |
                   v
        Results + Code + Visualizations
                   |
                   v
             Streamlit UI
```

Dataset documentation is prepared separately by the Business Context Architect agent and supplied to the retrieval pipeline.

## 🧠 Multi-Agent System

The project uses specialized agents, each responsible for a specific task.

| Agent                               | Responsibility                                                                      |
| ----------------------------------- | ----------------------------------------------------------------------------------- |
| Business Context Architect          | Documents dataset columns and their potential business meanings.                    |
| Query Understanding Specialist      | Identifies required columns, metrics, aggregations, filters, and calculation logic. |
| Retrieval Count Extractor           | Extracts the number of required columns to guide document retrieval.                |
| Python Data Analysis Code Generator | Generates executable Pandas code to answer the user's question.                     |

The agents are orchestrated using CrewAI crews with sequential task execution where appropriate.

## 🛠️ Tech Stack

* **Python** — Core application logic.
* **Pandas** — Data loading, transformation, aggregation, and analysis.
* **CrewAI** — Multi-agent orchestration.
* **Gemini** — Language model used by the agents.
* **Sentence Transformers** — Text embedding generation using `all-MiniLM-L6-v2`.
* **ChromaDB** — Vector storage and semantic retrieval.
* **Matplotlib** — Data visualization.
* **Streamlit** — Interactive web interface.
* **openpyxl** — Excel file support for Pandas.

## 📁 Project Structure

```text
Data-Analyst-Copilot/
│
├── app.py                  # Streamlit application
├── main.py                 # Command-line interface (if retained)
├── data.py                 # Dataset loading and metadata extraction
├── agents.py               # CrewAI agent definitions
├── tasks.py                # CrewAI task definitions
├── crews.py                # Crew orchestration
├── pipeline.py             # Main analysis pipeline
├── RAG.py                  # Embeddings, vector storage, retrieval
├── tools.py                # Custom CrewAI tools
├── dataset_context.txt     # Structured dataset documentation
├── requirements.txt        # Python dependencies
├── .gitignore              # Files excluded from Git
└── README.md               # Project documentation
```

*The file structure above is illustrative. Adjust filenames to match the files actually present in your repository.*

## 📊 Example Use Case

**Question:**

```text
What is the total cost for each country?
```

**Expected analytical approach:**

1. Identify `CustCountry` as the grouping column.
2. Identify `Total Cost` as the numerical measure.
3. Group the dataset by country.
4. Sum `Total Cost` for each country.
5. Display the resulting table.

Illustrative Pandas logic:

```python
result = (
    df.groupby("CustCountry")["Total Cost"]
      .sum()
      .sort_values(ascending=False)
)

print(result)
```

The application generates code dynamically according to the user's question rather than relying on this fixed example.

## 🔍 Why RAG?

Dataset column names alone do not always provide enough information to interpret business questions correctly.

For example, a column such as `Total Cost` may represent a line-item amount, net sales, or another financial measure. Its exact business definition should be verified rather than assumed.

The RAG component retrieves relevant documentation to help the code-generation agent:

* Use the exact column names available in the dataset.
* Understand the documented meaning of relevant columns.
* Reduce unsupported assumptions about business logic.
* Focus on the context most relevant to the user's question.

The current implementation uses an in-memory ChromaDB collection, so embeddings and stored documents are recreated when the RAG module initializes.

## ⚠️ Current Limitations

* The current implementation is designed around a specific sales dataset and may require adjustments for other datasets.
* Generated code can contain errors and is not guaranteed to produce correct results for every question.
* Business definitions and financial formulas must be verified against the actual data and documented business rules.
* Semantic retrieval quality depends on the dataset documentation and embedding model.
* The current vector database is in-memory rather than persistent.
* The application executes LLM-generated Python code. This approach is **not safe for untrusted input or public deployment without proper code isolation and execution controls**.
* API access, model availability, and model-specific configuration can affect execution.

## 🔮 Potential Future Improvements

* Support uploading CSV and Excel files directly through the interface.
* Add dataset profiling and automated data-quality checks.
* Validate generated code before execution.
* Implement sandboxed code execution with resource limits.
* Add SQL-based analysis as an alternative execution backend.
* Improve retrieval using metadata filters and more advanced retrieval strategies.
* Add unit tests and evaluation datasets to measure code correctness and answer accuracy.
* Support persistent vector storage and dataset-specific indexing.
* Improve error handling and allow controlled code regeneration after execution failures.

## 🎯 Learning Objectives

This project provides hands-on experience with:

* Building multi-agent AI workflows using CrewAI.
* Implementing a basic Retrieval-Augmented Generation pipeline.
* Generating and querying text embeddings.
* Using ChromaDB for semantic document retrieval.
* Integrating LLMs into data analysis workflows.
* Generating and executing Pandas code dynamically.
* Building an interactive data application with Streamlit.
* Connecting natural-language interfaces to structured datasets.

## 👨‍💻 Author

**YOUR NAME**

Aspiring Data Analyst interested in Python, SQL, business intelligence, and practical applications of Generative AI in data analytics.

* GitHub: https://github.com/YOUR_USERNAME
* LinkedIn: https://www.linkedin.com/in/YOUR_PROFILE/

---

*Built as a practical project exploring how multi-agent systems and retrieval-augmented generation can simplify data analysis through natural language.*
