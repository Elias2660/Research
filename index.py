# %%
import requests 
from dotenv import load_dotenv
import os
import re
import pandas as pd
from utils import getData
import numpy as np


# %%

load_dotenv()
API_KEY = os.getenv("API_KEY")
SHEET_ID = os.getenv("SHEET_ID")

# %%
frame_count, log_no, log_pos = getData()
print(f""" Frame Count Dataframe Shape: {frame_count.shape}""")
print(frame_count.head())
print(f"""\n Log No Dataframe Shape: {log_no.shape}""")
print(log_no.head())
print(f"""\n Log Pos Dataframe Shape: {log_pos.shape}""")
print(log_pos.head())


# %%
"""
We have different timestamps and have to combine them to a single timeline, with the correct frame counts

If that's so I guess I'm going to have to add everything together and the sort by timestamp

The standardized timestamp would be by second...

NOTICE: this only works as long as the day doesen't change
"""

#first, I'm probably going to have to create a new dataframe with standardized timestamps
#by second

#let's start with the frame count dataframe
def get_necessary_time(row):
    """
    Returns the time in seconds from the frame count dataframe, as long as it's all on the same month
    """
    matters = row.split("/")[1][:-6]
    date, time = matters.split(" ")
    years, months, days = date.split("-")
    hours, minutes, seconds = time.split(":")
    return round(float(str(years) + str(months) + str(days) + str(hours) + str(minutes) + str(seconds)),1)
frame_count_times = frame_count.Filename


frame_count_time_processed = frame_count_times.apply(get_necessary_time)

print(frame_count_time_processed.head())



# %%
"""
now, let's do the same for the log_no and the lot_pos dataframes

since they're the same structure-wise, I'm going to do it in a single function
"""
def process_log(row):
    date, time = row.split("_")
    return round(float(date + time),1)

    
log_no_times = log_no["year/month/day_hour/min/sec"]
log_pos_times = log_pos["year/month/day_hour/min/sec"]



log_no_times_processed = log_no_times.apply(process_log)
log_pos_times_processed = log_pos_times.apply(process_log)
# %%
"""
now, let's add the computed dataframes to the originals
"""
frame_count["time"] = frame_count_time_processed
log_no["time"] = log_no_times_processed
log_pos["time"] = log_pos_times_processed
# %%
fc_index, log_no_index, log_pos_index, event_number = 0, 0, 0, 0 #current indicies

current_class =  False if log_no.iloc[0]["time"] < log_pos.iloc[0]["time"] else True

if (min(log_no.iloc[0]["time"], log_pos.iloc[0]["time"]) != frame_count.iloc[0]["time"]):
    current_class = not current_class

#%%
"""
ALGORITHM

""" 

#%%
final = pd.DataFrame(columns = ["file", "class", "begin frame", "end_frame"])


def merge_dataframes(frame_count, log_no, log_pos):
    """
    merge the dataframes into one and sort
    """
    frame_count["class"] = frame_count["Filename"]
    log_no["class"] = False;
    log_pos["class"] = True;
    merged = pd.DataFrame(columns = ["time", "class"])
    merged = pd.concat([merged, frame_count[["time", "class"]]], ignore_index = True)
    merged = pd.concat([merged, log_no[["time", "class"]]], ignore_index = True)
    merged = pd.concat([merged, log_pos[["time", "class"]]], ignore_index = True)

    merged = merged.sort_values(by=["time"]).reset_index(drop=True)

    return merged

merged_dataframe = merge_dataframes(frame_count, log_no, log_pos)
    

# %%
merged_dataframe


#%%
def get_second_difference(time1, time2):
    """
    Given time, which is given as a float with the values 
    of YYYYMMDDHHMMSS.S, returns the difference in seconds
    """
    year_diff = int(time1 // 10000000000) - int(time2 // 10000000000)
    month_diff = int(time1 // 100000000)%100 - int(time2 // 100000000)%100
    day_diff = int(time1 // 1000000)%100 - int(time2 // 1000000)%100
    hour_diff = int(time1 // 10000)%100 - int(time2 // 10000)%100
    minute_diff = int(time1 // 100)%100 - int(time2 // 100)%100
    second_diff = int(time1 )% 100 - int(time2 ) %100
    return abs(year_diff * 31536000 + month_diff * 2592000 + day_diff * 86400 + hour_diff * 3600 + minute_diff * 60 + second_diff)


#%%

def get_last_class(merged_dataframe, index):
    """
    Given the merged dataframe and the current index, returns the last class with a true or false value
    """
    if (type(merged_dataframe.iloc[index]["class"])  == bool):
        return merged_dataframe.iloc[index]["class"]
    if index==0:
        return False if log_no["time"][0] < log_pos["time"][0] else True
    return get_last_class(merged_dataframe, index - 1)
        
        

# %%
for i in range(merged_dataframe.shape[0]):
    element = merged_dataframe.iloc[i]
    if (type(element["class"]) == bool):
        #the begin frame is the difference between the current time and the previous time (from vid change)
        begin_frame = get_second_difference(element["time"], merged_dataframe.iloc[i-1]["time"]) * 24
        #the end frame is the difference between the current time and the next time (from vid change)
        end_frame = (get_second_difference(merged_dataframe.iloc[i+1]["time"] , element["time"]) * 24 + begin_frame) if i <= merged_dataframe.shape[0]-2 else 20*60*24
        filename = merged_dataframe.iloc[i-1]["class"]
        class_type = "logPos" if element["class"] else "logNo"
        row = np.array([filename, class_type, begin_frame, end_frame])
        final = pd.concat([final, pd.DataFrame(row.reshape(1,-1), columns=list(final))], ignore_index=True)
    else:  # if the class is a string file name, 
        filename = element["class"]
        begin_frame = 0
        end_frame = get_second_difference(merged_dataframe.iloc[i+1]["time"], element["time"]) * 24  if i <= merged_dataframe.shape[0]-2 else 20*60*24
        class_type = "logPos" if get_last_class(merged_dataframe, i) else "logNo"
        row = np.array([filename, class_type, begin_frame, end_frame])
        final = pd.concat([final, pd.DataFrame(row.reshape(1,-1), columns=list(final))], ignore_index=True)

print(final[0:20])
# %%
final.to_csv("final.csv")
# %%
