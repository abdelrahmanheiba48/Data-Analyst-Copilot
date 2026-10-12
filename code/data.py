from pathlib import Path
import pandas as pd

DATA_PATH = "C:/Users/Abdu/Downloads/Sales.xlsx"
CONTEXT_FILE = "dataset_context.txt"

df = pd.read_excel(DATA_PATH)

columns = df.columns.to_list()

columns_data = {col: [df[col].nunique(), str(df[col].dtype)] for col in columns}


def load_documentation():
    """Read the context file and split it into one chunk per column."""
    text = Path(CONTEXT_FILE).read_text(encoding="utf-8")
    chunks = [part.strip() for part in text.split("__COLUMN__") if part.strip()]
    return text, chunks