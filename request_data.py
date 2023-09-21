# %%
import requests 
from dotenv import load_dotenv
import os


# %%

API_KEY = os.getenv("API_KEY")
sheet_id = "1b-rhvBm4nw_aYTS5x4bFrMfTgtbECF-S_Lkr5eXF3-M"


BaseURL = f'https://sheets.googleapis.com/v4/spreadsheets/{sheet_id}/values/'

sheets_data_url = f"frame count?key={API_KEY}"
log_no = f"log_no?key={API_KEY}"
log_pos = f"log_pos?key={API_KEY}"

# make a GET reqeust to the URL 

response = requests.get(url)
# %%

# convert the response into a pandas dataframe
import pandas as pd
import json
data = response.json()
print(data["values"])



# %%
sheets_data = pd.DataFrame(data["values"])
# %%

display(sheets_data)
# %%
