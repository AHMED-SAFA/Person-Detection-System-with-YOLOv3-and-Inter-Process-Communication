import cv2
import numpy as np
import sysv_ipc
import struct
import time
import sys
import os
import signal

# Shared memory structure for detection data
# struct DetectionData {
#     int frame_number;          // 4 bytes
#     int num_detections;        // 4 bytes
#     struct BBox {
#         float x;               // 4 bytes
#         float y;               // 4 bytes
#         float width;           // 4 bytes
#         float height;          // 4 bytes
#         float confidence;      // 4 bytes
#     } boxes[50];               // 20 bytes * 50 = 1000 bytes
#     bool processing_complete;  // 1 byte
# } Total: 4 + 4 + 1000 + 1 = 1009 bytes (with padding: 1012 bytes)

BBOX_SIZE = 20  # 5 floats * 4 bytes
MAX_DETECTIONS = 50
HEADER_SIZE = 8  # frame_number + num_detections
DATA_SIZE = HEADER_SIZE + (BBOX_SIZE * MAX_DETECTIONS) + 4  # +4 for bool and padding

def read_shared_memory(shm):
    """Read detection data from shared memory"""
    data = shm.read()
    
    # Unpack header
    frame_number, num_detections = struct.unpack('ii', data[:8])
    
    # Unpack bounding boxes
    boxes = []
    offset = 8
    for i in range(num_detections):
        box_data = struct.unpack('fffff', data[offset:offset+20])
        boxes.append({
            'x': int(box_data[0]),
            'y': int(box_data[1]),
            'width': int(box_data[2]),
            'height': int(box_data[3]),
            'confidence': box_data[4]
        })
        offset += 20
    
    # Check if processing is complete
    processing_complete = struct.unpack('?', data[HEADER_SIZE + (BBOX_SIZE * MAX_DETECTIONS):HEADER_SIZE + (BBOX_SIZE * MAX_DETECTIONS) + 1])[0]
    
    return frame_number, boxes, processing_complete

def visualize_video(video_path, shmid):
    """Visualize detections from shared memory"""
    
    # Connect to shared memory
    try:
        key = sysv_ipc.ftok("detector.cpp", 65)
        shm = sysv_ipc.SharedMemory(key)
        print(f"Connected to shared memory (ID: {shm.id})")
    except:
        print(f"Error: Cannot connect to shared memory!")
        print(f"Make sure the C++ detector is running first.")
        return
    
    # Open video
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("Error: Cannot open video file!")
        return
    
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    
    # Create output video writer
    output_path = 'output_detected.mp4'
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (frame_width, frame_height))
    
    print("Waiting for detection data...")
    print("Press 'q' to quit visualization")
    
    current_frame = 0
    last_frame_number = -1
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        current_frame += 1
        
        # Read detection data from shared memory
        try:
            frame_number, boxes, processing_complete = read_shared_memory(shm)
            
            # Wait for C++ to process this frame
            while frame_number < current_frame and not processing_complete:
                time.sleep(0.01)  # 10ms wait
                frame_number, boxes, processing_complete = read_shared_memory(shm)
            
            # Draw bounding boxes if we have new data
            if frame_number == current_frame:
                for box in boxes:
                    x = box['x']
                    y = box['y']
                    w = box['width']
                    h = box['height']
                    conf = box['confidence']
                    
                    # Draw rectangle
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    
                    # Draw label
                    label = f'Person: {conf:.2f}'
                    label_size, _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)
                    cv2.rectangle(frame, (x, y - label_size[1] - 10), 
                                (x + label_size[0], y), (0, 255, 0), -1)
                    cv2.putText(frame, label, (x, y - 5), 
                              cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
                
                # Display frame info
                info_text = f'Frame: {current_frame} | Detections: {len(boxes)}'
                cv2.putText(frame, info_text, (10, 30), 
                          cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
        except Exception as e:
            print(f"Error reading shared memory: {e}")
        
        # Write frame to output video
        out.write(frame)
        
        # Display frame
        cv2.imshow('Person Detection', frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        
        # Check if processing is complete
        try:
            _, _, processing_complete = read_shared_memory(shm)
            if processing_complete and current_frame >= frame_number:
                print("Detection processing complete!")
                break
        except:
            pass
    
    # Cleanup
    cap.release()
    out.release()
    cv2.destroyAllWindows()
    
    print(f"\nVisualization complete!")
    print(f"Output saved to: {output_path}")
    print(f"Total frames processed: {current_frame}")

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 visualizer.py <video_path>")
        sys.exit(1)
    
    video_path = sys.argv[1]
    
    if not os.path.exists(video_path):
        print(f"Error: Video file '{video_path}' not found!")
        sys.exit(1)
    
    print("Starting Python visualizer...")
    print(f"Video: {video_path}")
    
    # Get shared memory ID (will be created by C++ detector)
    shmid = None
    
    visualize_video(video_path, shmid)

if __name__ == "__main__":
    main()
