import pandas as pd


def get_vector_db(filename: str) -> pd.DataFrame:
    try:
        df_name = f"{filename}_vectordb.csv"
        print("Trying to load vector database: {}".format(df_name))
        return pd.read_csv(df_name)
    except FileNotFoundError:
        return None
