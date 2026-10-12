from crewai.tools import tool
from pandas.api.types import ( is_object_dtype, is_categorical_dtype, is_string_dtype )
from data import columns , df




@tool ("define_categorical_data")

def define_categorical_data():
    """Return the categories of the categorical data"""
    categorical_col = {}
    for column in columns:
        if is_object_dtype(df[column]) or is_categorical_dtype(df[column]) or is_string_dtype(df[column]):
            categorical_col[column] = df[column].dropna().unique().tolist()
    return categorical_col