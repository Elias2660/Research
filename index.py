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
    return round(float(str(years) + str(months) + str(days) + str(hours) + str(minutes) + str(seconds)),0)
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
"""
ALGORITHM

So we're going to have a sort of "set state" function.
We're going to have a current event, and then forcast
to future events, causing the next entry to the dataframe

Events are either 
""" 
final = pd.DataFrame(columns = ["file", "class", "begin frame", "end_frame"])




def find_last_frame(frame_count, event_number, fc_index, final):
    """
    find the begin_frame
    """
    #if it's the beginning of this event, start with 0, else start with the end of the last frame
    if (final.shape[0] == 0 or final.iloc[event_number-1]["file"] != frame_count.iloc[fc_index]["Filename"]):
        #if this the first event or the last event was in a different file, start with 0
        return 0
    else:
        #else, start with the last frame
        return final.iloc[event_number-1]["end_frame"] + 1


def find_end_frame(frame_count, log_no, log_pos, fc_index, log_no_index, log_pos_index) :
    """
    given the current event, time and indicies of the current log_no and log_pos,
    determine the next event
    """
    #if the next event is going to be change_video event, just return the frame count
    #else, make it the frame count of the next event minus one
    if (frame_count.iloc[fc_index+1]["time"] < min(log_no.iloc[log_no_index+1]["time"], log_pos.iloc[log_pos_index+1]["time"])):
        return frame_count.iloc[fc_index]["Frame count"]
    else:
        return (min(log_no.iloc[log_no_index+1]["time"], log_pos.iloc[log_pos_index+1]["time"]) - frame_count.iloc[fc_index]["time"])*24


def update_event(frame_count, log_no, log_pos, fc_index, log_no_index, log_pos_index):
    """
    determine the type of event, and update the index values based in that
    """
    if (frame_count.iloc[fc_index]["time"] < min(log_no.iloc[log_no_index]["time"], log_pos.iloc[log_pos_index]["time"])):
        #frame count event
        fc_index+=1
        print("change_video")
    if (log_no.iloc[log_no_index]["time"] < log_pos.iloc[log_pos_index]["time"]):
        #log_no event
        log_no_index+=1
        print("logNo")
    if (log_no.iloc[log_no_index]["time"] < log_pos.iloc[log_pos_index]["time"]):
        #log_pos event
        log_pos_index+=1
        print("logPos")
    return fc_index, log_no_index, log_pos_index
         
def return_state(frame_count, log_no, log_pos, fc_index, log_no_index, log_pos_index):
    """
    given the indicies, determine the state
    """
    current_file_state = frame_count.iloc[fc_index]["Filename"]
    class_state = "logPos" if current_class else "logNo"
    begin_frame = find_last_frame(frame_count, event_number, fc_index, final)
    end_frame = find_end_frame(frame_count, log_no, log_pos, fc_index, log_no_index, log_pos_index)
    return np.array([current_file_state, class_state, begin_frame, end_frame])


while (fc_index < frame_count.shape[0]):
    #while not all the frame counts have been processed, keep going
    current_state = return_state(frame_count, log_no, log_pos, fc_index, log_no_index, log_pos_index)
    # add curent_state to final as a new row
    final.loc[event_number] = current_state
    event_number+=1
    print(current_state)
    fc_index, log_no_index, log_pos_index = update_event(frame_count, log_no, log_pos, fc_index, log_no_index, log_pos_index)
        








# %%
