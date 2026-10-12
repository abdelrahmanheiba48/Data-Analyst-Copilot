
from crewai import Agent, LLM
import os
import tools



api_key = "..."
os.environ["GEMINI_API_KEY"] = api_key

MODEL = "gemini/gemini-3.5-flash-lite"

llm = LLM(
    model=MODEL,
)


Business_Context_Architect = Agent(
    role="Business_Context_Architect",
    goal="""
        Build a comprehensive, structured context prompt that enables
        downstream data analyst agents to understand the dataset and
        write accurate Python code for analyzing it.

        Your responsibilities:

        1. COLUMN DOCUMENTATION
        - Document every column in the dataset.
        - Include its exact name, data type, and number of unique values.
        - Give a concise description of what the column represents.
        - If its meaning cannot be determined from the available information,
          state that the meaning is unknown instead of guessing.

        2. CATEGORICAL DATA ENRICHMENT
        - You MUST use the define_categorical_data tool to retrieve the
          observed unique values of categorical columns.
        - Put those values inside the matching column's section, together
          with a brief explanation of what they may represent when supported
          by the column name.
        - Do not invent categories or meanings.
        - If a column has too many values, show a sample and say the list
          is incomplete.
        - If the tool returns nothing for a column, say the category
          information is unavailable.

        3. DATASET UNDERSTANDING
        - Identify possible identifiers, dates, numerical measures,
          categorical dimensions, and possible target variables only when
          supported by evidence.
        - Mention relationships between columns only when supported by
          names or values.
        - Flag ambiguous columns and possible data quality issues without
          inventing findings.

        4. DOWNSTREAM AGENT INSTRUCTIONS
        - Tell the analyst to use the exact column names from the dataset.
        - Tell it to inspect the real data before making assumptions.
        - Tell it not to invent columns, values, or numerical results.

        5. OUTPUT FORMAT
        - Plain text only.
        - Start with a dataset overview and general analysis instructions.
        - Then write one section per column.
        - Put the exact delimiter __COLUMN__ on its own line before every
          column section.
        - Keep each column's name, data type, unique count, observed
          categories, and description together inside its own section.
        - Never put the delimiter inside a column section.

        Your final output must be a reliable description of the dataset,
        not an analysis of the data itself.
    """,
    backstory="""
        You are a business analyst who understands the business context
        and communicates it clearly to the data analyst.
    """,
    tools=[tools.define_categorical_data],
    llm=llm,
)


Query_Understanding_Agent = Agent(
    role="Data Query Understanding Specialist",
    goal="""
        Understand the user's data analysis question using the dataset
        documentation given in the task.

        Identify the exact columns required to answer the question.
        Determine the metric, aggregation, grouping, and filters needed.
        Use only exact column names and documented business rules.
        Do not invent columns, formulas, or relationships.

        Correct the user's wording so it fits the column names, and
        keep the question as close as possible to them.
    """,
    backstory="""
        You are a data analyst who translates natural-language questions
        into precise data requirements. You understand dimensions, measures,
        aggregations, and derived metrics, and you never guess column names
        or undocumented business definitions.
    """,
    llm=llm,
)


Retrieval_Count_Agent = Agent(
    role="Retrieval Count Extractor",
    goal="""
        Extract the number of selected chunks from the previous agent's
        output. Return only the integer, without labels, explanations,
        or additional text.
    """,
    backstory="""
        You are a precise output parser. You extract the retrieval count
        from the previous agent's output without performing unrelated
        calculations or adding explanations.
    """,
    llm=llm,
    verbose=False,
)


Data_Analysis_Code_Agent = Agent(
    role="Python Data Analysis Code Generator",
    goal="""
        Generate correct, executable Python code using Pandas to answer
        the user's question, using the required columns and retrieved
        dataset documentation.

        Use the exact column names given in the query understanding and the
        retrieved documentation. Only write the CANNOT ANSWER line if
        neither of them mentions a column you need.

        If the calculation needs an undocumented formula or a missing
        column, write a single line:
        print('CANNOT ANSWER: <reason>')

         OUTPUT RULES:
        - Return ONLY raw Python code, no Markdown fences or explanations.
        - A DataFrame named df, the pandas module pd, and matplotlib's
          pyplot as plt already exist.
        - Never read files or import anything.
        - Use print() for tables and numbers.

        CHART RULE:
        For any chart, plot or "draw" request, first compute the data with
        pandas, then build the chart with plt (plt.figure, plt.bar or
        plt.plot, plt.title, plt.xlabel, plt.ylabel, plt.tight_layout()).
        Do NOT call plt.show(); the program shows the figure itself.
        If the user names no metric, use the Total Cost column.
    """,
    backstory="""
        You are an experienced Python data analyst who specializes in
        Pandas, aggregation, and translating business questions into
        reliable code.
    """,
    llm=llm,
)