#%%
import requests 
from dotenv import load_dotenv
import os
import pandas as pd
import json

load_dotenv()
API_KEY = os.getenv("API_KEY")
SHEET_ID = os.getenv("SHEET_ID")

# %%
# import ipdb; ipdb.set_trace()


def get_data(sheet_name:str, api=API_KEY, sheet_id=SHEET_ID) -> pd.DataFrame:
    """
    DESCRIPTION
    ----------
    Given the desired sheet name, return a dataframe with the sheet

    CONTRACT
    --------
    get_data(sheet_name, api, sheet_id) -> pd.DataFrame
    sheet_name: name of desired sheet, answers are: "frame count", "logNo", "logPos"
    api: api key used
    sheet_id: id of the sheet called from
    """
    base_url = f'https://sheets.googleapis.com/v4/spreadsheets/{sheet_id}/values/{sheet_name}?key={api}'
    data = pd.DataFrame(requests.get(base_url).json()["values"])

    data.columns = data.iloc[0]
    data = data[1:].reset_index(drop=True)
    return data

if __name__ == "__main__":
    frame_count = get_data("frame count")
    print(frame_count.head())



# %%
def get_file_data(filename:str, has_header=True) -> pd.DataFrame:
    """
    DESCRIPTION
    Get the data from a txt or csv file

    CONTRACT
    get_file_data(filename, has_header) -> pd.DataFrame
    filename: name of the file
    has_header: whether or not the file has a header
    """
    df =  pd.read_csv(f"{filename}") if has_header else pd.read_csv(f"{filename}", header=None)
    return df
# %%

if __name__ == "__main__":
    frame_count = get_data("frame count")
    print(frame_count.head())
    
    logNeg = get_file_data("logNeg.txt")
    print(logNeg.head())
# %%
