from crewai import Task
import agents
import data

# Descriptions marked "set by pipeline.py" are filled in for every question.

understanding_task = Task(
    description=f"""
        Build a structured business context for the dataset using
        the following metadata:

        {data.columns_data}

        For each column, describe its name, data type, and number
        of unique values. Explain its possible business meaning
        only when supported by the available information.

        Clearly mark uncertain meanings instead of inventing them.

        Put the delimiter __COLUMN__ on its own line before each column section.
    """,
    expected_output="""
        A dataset overview followed by one section per column.
        Each section must start with the line __COLUMN__ and contain
        the column's metadata, observed categories, and a cautious
        explanation of its possible business meaning.
    """,
    agent=agents.Business_Context_Architect,
)


query_understanding_task = Task(
    description="set by pipeline.py",
    expected_output="""
        Use exactly this format:

        CORRECTED QUESTION: <question>

        REQUIRED COLUMNS:
        - <exact column name>
        - <exact column name>

        CALCULATION: <how to compute it>

        CLARIFICATION REQUIRED: Yes or No

        REASON: <short reason>

        RETRIEVAL COUNT: <integer>
    """,
    agent=agents.Query_Understanding_Agent,
)


Required_column_task = Task(
    description="""
        Read the output of the query understanding task.
        Count the number of items listed under REQUIRED COLUMNS.
        Return only the integer, without labels or explanations.
    """,
    expected_output="""
        A single integer representing the number of required columns.
        Do not include labels, punctuation, or explanations.
    """,
    context=[query_understanding_task],
    agent=agents.Retrieval_Count_Agent,
)


data_analysis_code_task = Task(
    description="set by pipeline.py",
    expected_output="""
        Only raw, executable Python code.
        Do not include Markdown fences or explanations.
    """,
    agent=agents.Data_Analysis_Code_Agent,
    context=[query_understanding_task],
)