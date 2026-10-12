import io
from contextlib import redirect_stdout

import matplotlib.pyplot as plt
import pandas as pd

import crews, tasks, data, RAG


def run_code(code):
    """Run the generated code on a copy of the data and capture its printout."""
    buffer = io.StringIO()
    error = None
    plt.close("all")
    try:
        with redirect_stdout(buffer):
            exec(code, {"df": data.df.copy(), "pd": pd, "plt": plt})
    except Exception as e:
        error = f"{type(e).__name__}: {e}"
    return buffer.getvalue(), error


def answer(question):
    # STEP 1: translator agent + count agent
    tasks.query_understanding_task.description = f"""
        User question:
        {question}

        Full dataset documentation:
        {RAG.text}

        Work out what the user is asking, which metric is needed,
        how it should be grouped or filtered, and which exact columns
        are required.

        Use only exact column names from the documentation.
        Do not invent columns, formulas, or business rules.
    """
    count_result = crews.retrieval_count_crew.kickoff()
    plan = count_result.tasks_output[0].raw
    count = int(count_result.raw.strip())
    count = max(1, min(count + 1, len(RAG.chunks)))

    # STEP 2: RAG retrieval (the translator's output is the search text)
    retrieved_chunks = RAG.retrieve(plan, count)

    # STEP 3: code agent, then run its code
    tasks.data_analysis_code_task.description = f"""
        User question:
        {question}

        Relevant dataset documentation (retrieved chunks):
        {chr(10).join(retrieved_chunks)}

        Write Pandas code that answers the question using the DataFrame df.
    """
    code_result = crews.code_crew.kickoff()
    code = code_result.raw.replace("```python", "").replace("```", "").strip()

    output, error = run_code(code)

    return {
        "plan": plan,
        "chunk_count": count,
        "chunks": retrieved_chunks,
        "code": code,
        "output": output,
        "figures": [plt.figure(n) for n in plt.get_fignums()],
        "error": error,
    }