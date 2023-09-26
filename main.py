
# %%
import pandas as pd
from utils import getData
frame_count, log_no, log_pos = getData()

# set Frame count column to be int
frame_count['Frame count'] = frame_count['Frame count'].astype(int)
frame_count['time'] = frame_count['Filename'].str.split('/').str[1].str.replace('.h264\'', '')
frame_count['time'] = pd.to_datetime(frame_count['time'], format='%Y-%m-%d %H:%M:%S.%f')
frame_count['start_frame'] = 0
frame_count['end_frame'] = frame_count['Frame count']

log_no['state'] = False
log_pos['state'] = True
state_changes_df = pd.concat([log_no, log_pos], axis=0)
state_changes_df.columns=['time', 'state']

# parse the time column into a datetime object
state_changes_df['time'] = pd.to_datetime(state_changes_df['time'], format='%Y%m%d_%H%M%S')
# sort the dataframe by time
state_changes_df = state_changes_df.sort_values(by='time')

# %%
# set the state of the frame_count
merge_df = pd.merge_asof(frame_count, state_changes_df, on='time', direction='backward')
merge_df = merge_df.sort_values(by='time')
# set merge_df index to time column
merge_df = merge_df.set_index('time')
# merge merge_df and state_changes_df horizontally 
merge_df2 = pd.concat([merge_df, state_changes_df.set_index('time')], axis=0)
# resort the merge_df2 by its index
merge_df2 = merge_df2.sort_index().reset_index()

merge_df2

# %%

# loop through merge_df row by row with row_number
for row_number in range(merge_df2.shape[0]):
    # if the Filename is null
    current_row = merge_df2.iloc[row_number]
    if pd.isnull(current_row['Filename']): # if the row is merged from state changes
        previous_row = merge_df2.iloc[row_number-1]
        total_frame = previous_row['Frame count']
        # get the number of frames for the time for the previous row
        previous_row_frames = (merge_df2.iloc[row_number].time - merge_df2.iloc[row_number-1].time).seconds * 24 
        merge_df2.at[row_number-1, 'Frame count'] = previous_row_frames
        previous_end_frame = merge_df2.at[row_number-1, 'start_frame'] + previous_row_frames
        merge_df2.at[row_number, 'end_frame'] = merge_df2.at[row_number-1, 'end_frame'] 
        merge_df2.at[row_number-1, 'end_frame'] = previous_end_frame
        merge_df2.at[row_number, 'Frame count'] = total_frame - previous_row_frames 
        merge_df2.at[row_number, 'start_frame'] = previous_row_frames 
        merge_df2.at[row_number, 'Filename'] = merge_df2.at[row_number-1, 'Filename'] 
        merge_df2.at[row_number, 'FPS: 24'] = merge_df2.at[row_number-1, 'FPS: 24'] 


# set the frame count, start_frame, and end_frame to be int
merge_df2['Frame count'] = merge_df2['Frame count'].astype(int)
merge_df2['start_frame'] = merge_df2['start_frame'].astype(int)
merge_df2['end_frame'] = merge_df2['end_frame'].astype(int)

# remove rows where end_frame is the same as start_frame
merge_df2 = merge_df2[merge_df2['end_frame'] != merge_df2['start_frame']]

merge_df2.to_csv('merge_df2.csv')
# %%
