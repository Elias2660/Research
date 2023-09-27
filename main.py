
# %%
import pandas as pd
from utils import get_data
frame_count, log_no, log_pos = get_data()

def format_videos(vidoes_df: pd.DataFrame) -> pd.DataFrame: 
    # set Frame count column to be int
    frame_count['Frame count'] = frame_count['Frame count'].astype(int)
    # add a time column to frame_count by parsing the Filename column
    frame_count['time'] = frame_count['Filename'].str.split('/').str[1].str.replace('.h264\'', '')
    frame_count['time'] = pd.to_datetime(frame_count['time'], format='%Y-%m-%d %H:%M:%S.%f')
    # add start_frame and end_frame column
    frame_count['start_frame'] = 0
    frame_count['end_frame'] = frame_count['Frame count']
    return frame_count


def format_state_changes(log_no: pd.DataFrame, log_pos: pd.DataFrame) -> pd.DataFrame:
    # create a 
    log_no['state'] = False
    log_pos['state'] = True
    state_changes_df = pd.concat([log_no, log_pos], axis=0)
    state_changes_df.columns=['time', 'state']
    # parse the time column into a datetime object
    state_changes_df['time'] = pd.to_datetime(state_changes_df['time'], format='%Y%m%d_%H%M%S')
    # sort the dataframe by time
    state_changes_df = state_changes_df.sort_values(by='time')
    return state_changes_df


def merge_asof(frame_count: pd.DataFrame, state_changes: pd.DataFrame) -> pd.DataFrame:
    merge_df = pd.merge_asof(
        frame_count, 
        state_changes, 
        on='time', direction='backward')  # mix in state changes
    merge_df = merge_df.sort_values(by='time') 
    # set merge_df index to time column
    merge_df = merge_df.set_index('time')
    # merge merge_df and state_changes_df horizontally 
    merge_df2 = pd.concat([merge_df, state_changes.set_index('time')], axis=0)
    # resort the merge_df2 by its index
    merge_df2 = merge_df2.sort_index().reset_index()
    return merge_df2


def fill_state_change_rows(merge_df2: pd.DataFrame) -> pd.DataFrame:
    # loop through merge_df row by row with row_number
    # and process each newly added state columns 
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

    return merge_df2

# merge the videos with the state changes
merge_df2 = merge_asof(
    format_videos(frame_count), 
    format_state_changes(log_no, log_pos))

all_videos_w_state = fill_state_change_rows(merge_df2)

# remove rows where end_frame is the same as start_frame
all_videos_w_state = all_videos_w_state[all_videos_w_state['end_frame'] != all_videos_w_state['start_frame']]

all_videos_w_state.to_csv('all_videos_w_state.csv')
# %%
