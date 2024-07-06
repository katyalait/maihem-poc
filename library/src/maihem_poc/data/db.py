import os
from typing import List

import pandas as pd


def get_vector_db(filename: str) -> pd.DataFrame:
    try:
        return load_file(filename, scope='vectordb')
    except FileNotFoundError:
        return None


def save_file(df: pd. DataFrame, filename: str, scope: str, optional_suffix: str = None):
    if not os.path.exists('database/{}'.format(scope)):
        os.makedirs('database/{}'.format(scope))

    file_name_no_path = filename.rsplit('/',  maxsplit=1)[1]
    if optional_suffix != None:
        file_name_no_path = file_name_no_path + optional_suffix
    df.to_csv('database/{}/{}.csv'.format(scope, file_name_no_path), index=False)
    print("Saved file: {}".format(file_name_no_path))


def load_file(filename: str, scope: str, direct: bool = False) -> pd.DataFrame:
    if not direct:
        file_name_no_path = filename.rsplit('/', maxsplit=1)[1]
        file_to_read = 'database/{}/{}.csv'.format(scope, file_name_no_path)
    else:
        file_to_read = 'database/{}/{}'.format(scope, filename)
    return pd.read_csv(file_to_read)


def load_scope(scope: str, filename_filter: str) -> list[str]:
    file_name_no_path = filename_filter.rsplit('/', maxsplit=1)[1]
    relevant_files = []
    for file in os.listdir('database/{}'.format(scope)):
        if file_name_no_path in file:
            relevant_files.append(file)
    return relevant_files


