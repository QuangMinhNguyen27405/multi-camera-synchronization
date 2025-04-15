import argparse
from synchronize import load_cameras, synchronize_timestamps
from detect_frame_difference import detect_frame_difference
  
def main():
    parser = argparse.ArgumentParser(description="Camera Capture")
    parser.add_argument("--input", required=True, help="Video and data folder")
    parser.add_argument("--output", required=True, help="CSV ouptut folder")
    args = parser.parse_args()

    # Requirement 1: Synchronization Engine
    camera1, camera2 = load_cameras(input=args.input)
    camera1["timestamps"], camera2["timestamps"] = synchronize_timestamps(camera1, camera2, tolerance_ms=50)
    
    # Requirement 2: ROI and frame detection
    frames_diff1 = detect_frame_difference(camera1)
    frames_diff2 = detect_frame_difference(camera2)
    
    # Requirement 3: Output Generation
    

if __name__ == "__main__":
    main()