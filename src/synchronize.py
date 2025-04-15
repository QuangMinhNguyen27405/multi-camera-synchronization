import os
import pandas as pd
import ast
import cv2
import numpy as np

def load_cameras(folder):
    """
    Loads video, timestamp CSV, and ROI for two cameras
    
    Parameters:
        folder (str): Path to the folder containing video and data files
        
    Returns:
        dict, dict: Two dictionaries containing camera data
    """
    
    camera1 = load_camera(folder, "VisualCamera1")
    camera2 = load_camera(folder, "VisualCamera2")    
    return camera1, camera2

def load_camera(folder, camera_name):
    """
    Loads video, timestamp CSV, and ROI for a given camera
    
    Parameters:
        folder (str): Path to the folder containing video and data files
        
    Returns:
        dict: A dictionary containing camera data
    """
    video_path = os.path.join(folder, f"{camera_name}.mp4")
    timestamp_path = os.path.join(folder, f"{camera_name}_Timestamps.csv")
    roi_path = os.path.join(folder, f"{camera_name}_ROI.txt")

    video = cv2.VideoCapture(video_path)
    if not video.isOpened():
        raise FileNotFoundError(f"Could not open video: {video_path}")

    if not os.path.exists(timestamp_path):
        raise FileNotFoundError(f"Timestamps CSV not found: {timestamp_path}")
    timestamps_df = pd.read_csv(timestamp_path)
    timestamps_df["Timestamp"] = pd.to_datetime(timestamps_df["Timestamp"], format="%Y-%m-%d-%H-%M-%S_%f")
    timestamps_df["Timestamp"] = timestamps_df["Timestamp"].astype(np.int64) // 10**6  # convert to ms

    if not os.path.exists(roi_path):
        raise FileNotFoundError(f"ROI file not found: {roi_path}")
    with open(roi_path, "r") as f:
        roi_str = f.read().strip()
        roi = ast.literal_eval(roi_str)
    
    camera_data = {
        "name": camera_name,
        "video": video,
        "timestamps": timestamps_df,
        "roi": roi
    }
    
    return camera_data

def synchronize_timestamps(camera1, camera2, tolerance_ms=50):
    """
    Synchronize streams using two pointers approach so that each timestamp from one
    stream is matched with a close timestamp from the other. This create a master timestamp 
    that combines both timestamps of two cameras
    
    Parameters:
        ts1_df (pd.DataFrame): Camera 1 timestamps
        ts2_df (pd.DataFrame): Camera 2 timestamps
        tolerance_ms (int): Max allowed offset to match
    
    Returns:
        dict, dict: synchronized frames for both cameras
    """
    ts1_df = camera1["timestamps"]
    ts2_df = camera2["timestamps"]
    
    i, j = 0, 0
    new_ts1 = []
    new_ts2 = []

    while i < len(ts1_df) and j < len(ts2_df):
        t1 = ts1_df.at[i, "Timestamp"]
        t2 = ts2_df.at[j, "Timestamp"]
        offset = abs(t1 - t2)

        if offset <= tolerance_ms:
            master_timestamp = min(t1, t2)
            new_ts1.append({
                "master_timestamp": master_timestamp,
                "camera_1_frame": int(ts1_df.at[i, "Image_number"]),
                "camera_1_original_timestamp": int(t1),
                "camera_1_offset": int(t1 - master_timestamp),
            })
            new_ts2.append({
                "master_timestamp": master_timestamp,
                "camera_2_frame": int(ts2_df.at[j, "Image_number"]),
                "camera_2_original_timestamp": int(t2),
                "camera_2_offset": int(t2 - master_timestamp),
            })
            i += 1
            j += 1
        elif t1 < t2:
            i += 1
        else:
            j += 1

    return new_ts1, new_ts2