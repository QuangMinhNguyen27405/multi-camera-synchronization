import numpy as np
import cv2

def detect_frame_difference(camera_data):
    video = camera_data["video"]
    timestamps_df = camera_data["timestamps"]
    roi = camera_data["roi"]
    
    width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
    mask = create_roi_mask((height, width), roi)

    change_metrics = []
    prev_frame = None

    for i in range(len(timestamps_df)):
        frame_index = int(timestamps_df.at[i, "Image_number"])
        video.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
        ret, frame = video.read()

        if not ret:
            change_metrics.append(None)
            continue

        if prev_frame is None:
            prev_frame = frame
            change_metrics.append(0.0)
            continue

        diff_score = compute_frame_difference(prev_frame, frame, mask)
        change_metrics.append(diff_score)

        prev_frame = frame

    return change_metrics


def create_roi_mask(frame_shape, roi_points):
    """
    Create binary mask for polygonal ROI.

    Parameters:
        frame_shape (tuple): Shape of the frame (height, width).
        roi_points (List[Tuple[int, int]]): Points of the polygon.

    Returns:
        np.ndarray: Binary mask with ROI filled.
    """
    mask = np.zeros(frame_shape[:2], dtype=np.uint8)
    roi_pts = np.array(roi_points, dtype=np.int32)
    cv2.fillPoly(mask, [roi_pts], 255)
    return mask


def compute_frame_difference(prev_frame, curr_frame, mask=None):
    """
    Compute absolute pixel-wise difference between two frames.

    Parameters:
        prev_frame (np.ndarray): Previous frame.
        curr_frame (np.ndarray): Current frame.
        mask (np.ndarray): Optional binary mask to restrict difference to ROI.

    Returns:
        float: Normalized difference score (0 to 1).
    """
    prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
    curr_gray = cv2.cvtColor(curr_frame, cv2.COLOR_BGR2GRAY)
    diff = cv2.absdiff(prev_gray, curr_gray)

    if mask is not None:
        diff = cv2.bitwise_and(diff, diff, mask=mask)

    _, thresh = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)
    non_zero_count = np.count_nonzero(thresh)
    total_pixels = np.count_nonzero(mask) if mask is not None else thresh.size
    return non_zero_count / total_pixels if total_pixels > 0 else 0.0