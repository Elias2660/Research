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

def get_sheet_data(sheet_name: str, api = API_KEY):
    ...
    
def getData(api = API_KEY, sheet_id = SHEET_ID):
    """
    Gets the data and returns three pandas dataframes with the frame count, logOn, and logPos
    dataframes
    """
    BaseURL = f'https://sheets.googleapis.com/v4/spreadsheets/{sheet_id}/values/'

    sheets_data = pd.DataFrame(requests.get(BaseURL + f"frame count?key={api}").json()["values"])
    log_no = pd.DataFrame(requests.get(BaseURL + f"logNo?key={api}").json()["values"])
    log_pos = pd.DataFrame(requests.get(BaseURL + f"logPos?key={api}").json()["values"])

    #setting the sheets_data column names to its first row
    sheets_data.columns = sheets_data.iloc[0]
    sheets_data = sheets_data[1:].reset_index(drop=True)


    #setting the log_no column names to its first row
    log_no.columns = log_no.iloc[0]
    log_no = log_no[1:].reset_index(drop=True)

    #setting the log_pos column names to its first row
    log_pos.columns = log_pos.iloc[0]
    log_pos = log_pos[1:].reset_index(drop=True)

    return sheets_data, log_no, log_pos



# %%
