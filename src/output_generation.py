import csv
import time

def generate_output(matches, cam1_changes, cam2_changes, output_path):
    """
    Generates a CSV file with synchronized frame info, ROI change, and processing time.

    Parameters:
        matches (List[Dict]): List of synchronized frame pairs
        cam1_changes (List[float]): ROI change metrics for camera 1
        cam2_changes (List[float]): ROI change metrics for camera 2
        output_path (str): Path to the output CSV file
    """
    fieldnames = [
        "master_timestamp",
        "camera_1_frame",
        "camera_1_original_timestamp",
        "camera_1_offset_ms",
        "camera_1_roi_change",
        "camera_2_frame",
        "camera_2_original_timestamp",
        "camera_2_offset_ms",
        "camera_2_roi_change",
        "processing_time_ms"
    ]

    with open(output_path, mode="w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for match in matches:
            start_time = time.time()

            cam1_index = match["camera_1_frame"]
            cam2_index = match["camera_2_frame"]

            row = {
                "master_timestamp": match["master_timestamp"],
                "camera_1_frame": match["camera_1_frame"],
                "camera_1_original_timestamp": match["camera_1_original_timestamp"],
                "camera_1_offset_ms": match["camera_1_offset_ms"],
                "camera_1_roi_change": cam1_changes[cam1_index] if cam1_index < len(cam1_changes) else None,
                "camera_2_frame": match["camera_2_frame"],
                "camera_2_original_timestamp": match["camera_2_original_timestamp"],
                "camera_2_offset_ms": match["camera_2_offset_ms"],
                "camera_2_roi_change": cam2_changes[cam2_index] if cam2_index < len(cam2_changes) else None,
                "processing_time_ms": round((time.time() - start_time) * 1000, 3)
            }

            writer.writerow(row)