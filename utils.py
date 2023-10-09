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


def get_data_from_sheets(sheet_name:str, api=API_KEY, sheet_id=SHEET_ID) -> pd.DataFrame:
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

#%%

def get_data_from_csv_or_txt(data_name:str, filetype:str) -> pd.DataFrame:
    """
    DESCRIPTION
    ----------
    Give data from a sheets file or csv file, return the data as a pandas dataframe

    This is supposed to handle test cases and such

    CONTRACT
    --------
    """
    if (filetype == "csv") :
        return pd.read_csv(f"{data_name}.csv")
    else :
        data =  pd.read_csv(f"{data_name}.txt", sep = " ", header= None)
        data.columns = ["year/month/day_hour/min/sec"]
        return data

# %%
