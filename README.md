# Data Analyst Copilot 🤖📊

> A multi-agent, RAG-based assistant that turns natural-language questions (English or Arabic, even messy ones) into Pandas code, executes it against a dataset, and returns results and charts.

---

## 01. Project Identity

| Field | Details |
|---|---|
| **Project Name** | Data Analyst Copilot |
| **Track** | Generative AI / Data Analytics |
| **Project Type** | Final Project |
| **Status** | Completed (prototype, not production-ready) |
| **Author** | Abdelrahman — Data Analyst |
| **Repository** | `[https://github.com/abdelrahmanheiba48/Data-Analyst-Copilot]` |
| **Live Demo** | Local reproducible run (Streamlit) |


### Executive Summary

Data Analyst Copilot lets users ask questions about a sales dataset without writing Pandas code. Four specialized CrewAI agents interpret the question, plan the required columns and calculation, and generate Python code. A ChromaDB-backed RAG layer supplies only the relevant column documentation as context. The code is executed on a copy of the dataset, and results, generated code, retrieved context, and charts are shown in a Streamlit app. The system is a working prototype; it has no automated test suite or measured accuracy benchmark yet (see Section 11).

---

## 02. Context & Motivation

**Background.** Business users often need quick answers from tabular data (e.g. "total cost per country") but cannot write Pandas, and their questions are frequently ambiguous, misspelled, or logically flawed.

**Motivation.** LLMs can write Pandas code, but column names alone rarely carry business meaning (does `Total Cost` mean net sales, or a line-item amount?). Feeding the full dataset documentation to the model on every call is wasteful and noisy. This project addresses both problems with a query-cleaning agent and column-level retrieval.

**Track alignment.** The project combines multi-agent orchestration (CrewAI), embeddings and vector search (Sentence Transformers, ChromaDB), LLM integration (Gemini), data analysis (Pandas, Matplotlib), and an interactive interface (Streamlit).

---

## 03. Problem Definition

**Problem statement.** Given a tabular dataset *D* and a free-form user question *q* (possibly containing syntax or logic errors), produce executable Pandas code that answers *q*, run it, and present the output together with the evidence used to produce it.

| Stakeholder | Need | Current bottleneck |
|---|---|---|
| Business user | Get answers from data in plain language | Cannot write Pandas/SQL |
| Analyst | Speed up repetitive aggregation questions | Boilerplate code for every question |
| Reviewer | Verify how an answer was produced | Opaque LLM output |

### Assumptions vs. Verified Facts

| Category | Statement | Status |
|---|---|---|
| Assumption | The dataset is a single Excel sales table with a consistent schema | Domain assumption |
| Assumption | Business definitions in `dataset_context.txt` match the real business rules | Must be verified by a domain owner |
| Assumption | Gemini remains available and behaves consistently across runs | Not guaranteed |
| Verified | The pipeline runs end-to-end locally and shows question, code, retrieved docs, and output | Manual run via Streamlit |

---

## 04. Objectives & Success Criteria

**Primary objective:** answer natural-language data questions through generated, inspectable Pandas code.

**Engineering objectives**
1. **Transparency:** expose the interpreted question, retrieved documentation, generated code, and output.
2. **Context efficiency:** retrieve only the column documentation relevant to the question.
3. **Robustness to messy input:** correct or clarify flawed user questions before code generation.
4. **Modularity:** keep agents, tasks, crews, retrieval, and pipeline in separate modules.

**Success criteria (current):** the app answers the documented example questions (totals per country, orders per customer type, cost over time) and shows its full reasoning chain. Quantitative accuracy criteria are not yet defined (see Limitations).

---

## 05. Requirements

| ID | Requirement | Implementation | Verification | Status |
|---|---|---|---|---|
| FR-01 | Load the Excel dataset and extract column metadata | `data.py` | Manual run | Complete |
| FR-02 | Generate structured per-column documentation | Business Context Architect agent (`agents.py`, `tasks.py`, `crews.py`) → `dataset_context.txt` | Manual inspection of the text file | Complete |
| FR-03 | Interpret and correct the user question | Query Understanding Specialist | Manual run | Complete |
| FR-04 | Determine how many columns are needed | Retrieval Count Extractor | Manual run | Complete |
| FR-05 | Retrieve relevant column chunks semantically | `RAG.py` (MiniLM + ChromaDB) | Manual inspection of retrieved chunks in UI | Complete |
| FR-06 | Generate and execute Pandas code, capturing stdout and errors | Code Generator agent, `pipeline.py` | Manual run | Complete |
| FR-07 | Show results, code, docs, and charts | `app.py` (Streamlit) | Manual run | Complete |

**Non-functional constraints**
- **Security:** executes LLM-generated code without sandboxing, so it is for trusted local use only.
- **Dependencies:** requires Gemini API access.
- **Out of scope:** multi-dataset support, persistent vector storage, authentication, public deployment.

---

## 06. System Overview

The system has two phases: an **offline preparation phase** and an **online question-answering phase**.

**Preparation (once per dataset)**
1. The *Business Context Architect* creates a summary text file (`dataset_context.txt`) where each chunk describes one column.
2. The file is chunked, embedded with `all-MiniLM-L6-v2`, and stored in ChromaDB.

**Question answering (per query)**
1. The user's input (which may contain syntax and logic issues) goes to the *Query Understanding Specialist*, which returns a valid question, the needed columns, the calculation, and a clarification status.
2. The *Retrieval Count Extractor* determines how many columns (chunks) are needed.
3. The RAG component retrieves that many relevant chunks from ChromaDB.
4. The *Code Generator* receives the original question, the corrected question, and the retrieved chunks, then writes Pandas code.
5. The code runs on a copy of the dataset; output and errors are captured.
6. Streamlit displays the results, code, retrieved documentation, and charts.

```text
 [Offline] Dataset ──► Business Context Architect ──► dataset_context.txt
                                                          │ chunk (1 per column) + embed
                                                          ▼
                                                  ChromaDB (in-memory)

 [Online]  User Question
                │
                ▼
        Query Understanding Agent
   (corrected question + columns + calculation)
                │
                ▼
        Retrieval Count Agent
                │
                ▼
        Semantic Retrieval  ◄──── ChromaDB
                │
                ▼
        Code Generation Agent
   (user question + corrected question + chunks)
                │
                ▼
        Code Execution (Pandas, dataset copy)
                │
                ▼
        Results + Code + Charts ──► Streamlit UI
```

### 📄 Original Design Chart (PDF)

The original hand-drawn design notes and workflow chart that this project was built from are included in the repository:
<img width="1068" height="804" alt="image" src="https://github.com/user-attachments/assets/142477a2-afaa-4189-a7e9-69ecfc7ae254" />

---

## 07. Architecture

### Multi-Agent Design

| Agent | Responsibility | Input | Output |
|---|---|---|---|
| Business Context Architect | Documents each column and its potential business meaning | Dataset metadata, observed categories | `dataset_context.txt` |
| Query Understanding Specialist | Corrects the question; identifies columns, metrics, aggregations, filters, calculation, clarification status | Raw user question | Structured query plan |
| Retrieval Count Extractor | Extracts the number of required columns | Query plan | Integer k |
| Python Data Analysis Code Generator | Writes executable Pandas code | User question, corrected question, retrieved chunks | Python code |

Agents are orchestrated with CrewAI crews using sequential task execution where appropriate.

### Components

| Module | Role |
|---|---|
| `app.py` | Streamlit interface |
| `main.py` | Command-line interface (if retained) |
| `data.py` | Dataset loading and metadata extraction |
| `agents.py` / `tasks.py` / `crews.py` | Agent, task, and crew definitions |
| `pipeline.py` | End-to-end analysis pipeline |
| `RAG.py` | Chunking, embeddings, ChromaDB storage and retrieval |
| `tools.py` | Custom CrewAI tools |
| `dataset_context.txt` | Structured dataset documentation |

### External Dependencies & Failure Modes

| Dependency | Purpose | Failure mode | Current behavior |
|---|---|---|---|
| Gemini API | Powers all agents | Quota, outage, model change | Run fails; no fallback |
| ChromaDB (in-memory) | Vector retrieval | Data lost on restart | Re-indexed when the RAG module initializes |
| Generated code | Computes the answer | Syntax/logic/runtime error | Error is captured and displayed |

---

## 08. Design Decisions

| ID | Decision | Alternatives | Selected | Rationale |
|---|---|---|---|---|
| ADR-01 | One chunk per column | Fixed-size chunks; whole document in prompt | One chunk per column | Matches how questions reference data (by column) and keeps context small |
| ADR-02 | Separate retrieval-count agent | Fixed top-k | Agent-determined k | Retrieval size adapts to how many columns the question needs |
| ADR-03 | Separate query-understanding step | Send the raw question to the code generator | Dedicated agent | Fixes flawed or ambiguous input before code generation |
| ADR-04 | Code generator receives both original and corrected question | Corrected only | Both | Preserves user intent if the correction drifts |
| ADR-05 | `all-MiniLM-L6-v2` embeddings | Larger embedding models; API embeddings | MiniLM | Lightweight, runs locally, and needs no extra API |
| ADR-06 | In-memory ChromaDB | Persistent store | In-memory | Simplest option for a single-dataset prototype; persistence is a future improvement |
| ADR-07 | Execute on a copy of the dataset | Execute on the original | Copy | Generated code cannot mutate the source data |

---

## 09. Technology Stack

| Layer | Technology | Purpose |
|---|---|---|
| Language | Python `[version]` | Core logic |
| Data | Pandas, openpyxl | Loading and analysis of Excel data |
| Agents | CrewAI | Multi-agent orchestration |
| LLM | Gemini | Language model for all agents |
| Embeddings | Sentence Transformers (`all-MiniLM-L6-v2`) | Semantic embeddings |
| Vector DB | ChromaDB | Similarity search |
| Visualization | Matplotlib | Charts |
| UI | Streamlit | Web interface |

> Pin exact versions in `requirements.txt`.

---

## 10. Data & Documentation Pipeline

- **Source:** a sales dataset in Excel format (e.g. columns such as `CustCountry`, `Total Cost`, product category, customer type, order date).
- **Documentation generation:** the Business Context Architect records column names, data types, unique values, observed categories, and potential business meanings.
- **Caveat:** the documented meaning of a column such as `Total Cost` is an interpretation and should be verified against actual business rules, not assumed.

### Example

Question: *What is the total cost for each country?*

1. Group by `CustCountry`.
2. Sum `Total Cost`.
3. Sort and display.

```python
result = (
    df.groupby("CustCountry")["Total Cost"]
      .sum()
      .sort_values(ascending=False)
)
print(result)
```

This is illustrative only. The application generates code dynamically for each question.

### Why RAG?

Retrieval gives the code generator the exact column names, their documented meanings, and only the context relevant to the question. This reduces unsupported assumptions about business logic and keeps prompts focused.

---

## 11. Testing & Evaluation

**Current state (stated honestly):** no automated unit, integration, or accuracy tests exist yet. The system has been exercised manually through the Streamlit UI using example questions. No quantitative correctness metric has been measured, so this README makes no accuracy claims.

**Planned**
- Unit tests for data loading, chunking, and retrieval.
- An evaluation set of questions with reference answers to measure code correctness and answer accuracy.
- Retrieval quality checks (is the right column retrieved for each question?).

---

## 12. Security Considerations

The application **executes LLM-generated Python code**. This is unsafe for untrusted input or public deployment without isolation. Run it only locally with trusted users. Keep API keys in environment variables and never commit them.

Planned mitigations: pre-execution code validation, sandboxed execution with resource limits, and controlled code regeneration on failure.

---

## 13. Setup & Reproducibility

```bash
# 1. Clone
git clone https://github.com/abdelrahmanheiba48/Data-Analyst-Copilot.git
cd Data-Analyst-Copilot

# 2. Environment
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 3. Dependencies
pip install -r requirements.txt

# 4. Configure the Gemini API key (do not commit it)
export GEMINI_API_KEY="your-key"  # or use a .env file

# 5. Run the app
streamlit run app.py
```

**Reproducibility note:** LLM outputs are non-deterministic and Gemini model versions may change, so generated code can vary between runs. The pipeline and its inputs are reproducible; exact outputs are not guaranteed.

---

## 14. Limitations & Failure Analysis

| Limitation | Impact | Planned fix |
|---|---|---|
| Built around one sales dataset | Needs adjustment for other datasets | Direct CSV/Excel upload and dataset-specific indexing |
| Generated code may be wrong | Incorrect answers for some questions | Code validation, tests, regeneration on failure |
| Business formulas unverified | Misleading metrics | Verify against documented business rules |
| Retrieval depends on documentation and embedding quality | Wrong columns retrieved | Metadata filters, better retrieval strategies |
| In-memory vector store | Re-indexing on every start | Persistent storage |
| Unsandboxed code execution | Unsafe for public use | Sandbox with resource limits |
| Dependence on external API | Failures when quota or model changes | Error handling and fallbacks |

**Non-guarantees:** the system does not guarantee correct answers, correct business interpretation, or safe handling of untrusted input.

---

## 15. Future Improvements

- Upload CSV/Excel files through the interface.
- Dataset profiling and automated data-quality checks.
- Validate generated code before execution.
- Sandboxed execution with resource limits.
- SQL execution backend as an alternative to Pandas.
- Better retrieval (metadata filters, advanced strategies).
- Unit tests and evaluation datasets.
- Persistent vector storage.
- Controlled code regeneration after execution failures.

---

## 16. Engineering Reflection

- **Key design insight:** separating question cleanup, retrieval sizing, and code generation into distinct agents makes each step inspectable.
- **Hardest challenge:** `[describe the toughest technical hurdle and how you solved it]`
- **A wrong assumption:** `[describe an assumption that failed during development]`
- **v2.0 priorities:** sandboxing, an evaluation suite, persistent retrieval.
- **Lesson:** an LLM pipeline is only as trustworthy as its context and its evaluation; documentation quality and testing matter as much as the prompts.

---



## 17. Acknowledgements, Attribution & License

### 🙏 Shout-out to Phronesis

A huge thank you to **Phronesis** — *"Build Engineers, Not Course Consumers."* This project was completed as part of the Phronesis learning curriculum. Its engineering-first approach pushed me to go beyond following tutorials: to define requirements, justify design decisions, document trade-offs honestly, separate assumptions from verified facts, and take ownership of every line I ship. The structure of this README follows the Phronesis Final Project documentation standard, and this project is better because of it. Thank you to the Phronesis team and to everyone in the cohort. 💙

> Phronesis is the educational program and platform; copyright and ownership of this student-created work remain with the author unless governed by a separate explicit agreement.



---

## 👨‍💻 Author

**Abdelrahman** — Data Analyst interested in Python, SQL, business intelligence, and practical applications of Generative AI in analytics.


LinkedIn: www.linkedin.com/in/abdelrahman-sayed-40321640b

*Built as a practical project exploring how multi-agent systems and retrieval-augmented generation can simplify data analysis through natural language.*
