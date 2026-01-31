# Person Detection with YOLO - C++ and Python Inter-Process Communication

This project demonstrates person detection using YOLOv3 in C++ with shared memory communication to a Python visualization system.

## 📋 Project Overview

### Architecture
1. **C++ Detector** (`detector.cpp`)
   - Reads video file
   - Runs YOLOv3 model for person detection
   - Stores bounding box information in shared memory
   - Processes frame-by-frame

2. **Shared Memory** (IPC)
   - Stores detection data (frame number, bounding boxes, confidence scores)
   - Allows communication between C++ and Python processes
   - Uses System V shared memory

3. **Python Visualizer** (`visualizer.py`)
   - Reads detection data from shared memory
   - Draws bounding boxes on video frames
   - Saves output video with detections

### Data Flow
```
Video → C++ Detector → Shared Memory → Python Visualizer → Output Video
         (YOLOv3)      (IPC)           (Drawing)          (with boxes)
```

## 🚀 Quick Start

### Prerequisites
- WSL (Windows Subsystem for Linux) with Ubuntu
- At least 2GB free disk space (for YOLO weights)
- Video file with person(s) walking

### Installation

1. **Make scripts executable:**
```bash
chmod +x setup.sh run.sh
```

2. **Run setup (installs dependencies and downloads YOLO model):**
```bash
./setup.sh
```

This will:
- Install OpenCV, build tools, and Python dependencies
- Download YOLOv3 config and weights (~237 MB)
- Compile the C++ detector

### Usage

**Run the complete system:**
```bash
./run.sh person_walk.mp4
```

Replace `person_walk.mp4` with your actual video file path.

## 📁 Project Structure

```
.
├── detector.cpp          # C++ YOLOv3 detector (main detection logic)
├── visualizer.py         # Python visualizer (draws boxes on video)
├── Makefile             # Build configuration
├── CMakeLists.txt       # Alternative CMake build config
├── setup.sh             # Setup and installation script
├── run.sh               # Main execution script
├── yolov3.cfg           # YOLO model configuration (downloaded)
├── yolov3.weights       # YOLO model weights (downloaded)
└── coco.names           # Class names (downloaded)
```

## 🔧 Manual Compilation and Execution

### Using Makefile (Recommended)

```bash
# Compile
make

# Run detector
./detector video.mp4

# In another terminal, run visualizer
python3 visualizer.py video.mp4

# Clean up
make clean
```

### Using CMake

```bash
# Create build directory
mkdir build && cd build

# Configure
cmake ..

# Compile
make

# Run
./detector ../video.mp4
```

## 📊 How It Works

### Shared Memory Structure

```c
struct DetectionData {
    int frame_number;              // Current frame being processed
    int num_detections;            // Number of persons detected
    struct BBox {
        float x, y;                // Top-left corner
        float width, height;       // Bounding box dimensions
        float confidence;          // Detection confidence (0-1)
    } boxes[50];                   // Up to 50 detections per frame
    bool processing_complete;      // Signal for completion
};
```

### Detection Process

1. **C++ Detector:**
   - Opens video file
   - Creates shared memory segment
   - For each frame:
     - Runs YOLO inference
     - Filters detections (person class only)
     - Applies Non-Maximum Suppression (NMS)
     - Writes bounding boxes to shared memory
   - Marks processing as complete

2. **Python Visualizer:**
   - Connects to shared memory
   - Opens same video file
   - For each frame:
     - Reads detection data from shared memory
     - Draws bounding boxes and labels
     - Writes to output video
   - Saves final video file

## 🎯 Configuration

### YOLO Parameters (in detector.cpp)

```cpp
float confThreshold = 0.5;    // Confidence threshold (0.0 - 1.0)
float nmsThreshold = 0.4;     // NMS threshold
int inpWidth = 416;           // Input width for YOLO
int inpHeight = 416;          // Input height for YOLO
```

### Shared Memory Key

Generated using:
```cpp
key_t key = ftok("detector.cpp", 65);
```
Both C++ and Python must use the same key to communicate.



## Results 

## Input Video

https://github.com/person_walk.mp4

## Output Video

https://github.com/output_detected.mp4


<img width="1920" height="1023" alt="Screenshot (145)" src="https://github.com/user-attachments/assets/373ca8fa-0ddf-49c5-b0e7-f75636e3d89d" /> 

<img width="1920" height="1023" alt="Screenshot (144)" src="https://github.com/user-attachments/assets/57ef60cf-1163-4fd4-8c7f-35c42c3fd96f" />

<img width="1920" height="1028" alt="Screenshot (141)" src="https://github.com/user-attachments/assets/c603105b-2b29-4dac-a7ea-abb61eb3172d" />



## 📊 Performance Notes

- **Processing Speed:** ~1-5 FPS on CPU (depends on video resolution)
- **Memory Usage:** ~500MB for YOLO model + video processing

## 🔍 Understanding the Output

The visualizer displays:
- **Green boxes:** Detected persons
- **Labels:** "Person: X.XX" where X.XX is confidence score
- **Frame info:** Current frame number and detection count
- **Output file:** `output_detected.mp4` with all visualizations


## 🔐 Shared Memory Management

**View active shared memory segments:**
```bash
ipcs -m
```

**Remove specific segment:**
```bash
ipcrm -m <shmid>
```

**Remove all your segments:**
```bash
ipcs -m | grep $(whoami) | awk '{print $2}' | xargs -I {} ipcrm -m {}
```


### Key Python Components

1. **Shared Memory Connection:**
```python
key = sysv_ipc.ftok("detector.cpp", 65)
shm = sysv_ipc.SharedMemory(key)
```

2. **Reading Detection Data:**
```python
frame_number, num_detections = struct.unpack('ii', data[:8])
```

3. **Drawing Boxes:**
```python
cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
```

## 📚 Dependencies

### C++ Libraries
- OpenCV
- System V IPC 

### Python Libraries
- opencv-python
- numpy
- sysv-ipc

## 🤝 Assignment Requirements Met

✅ Person detection using YOLO  
✅ C++ implementation for detection  
✅ Shared memory for IPC  
✅ Python visualization  
✅ Bounding box storage and retrieval  
✅ Signal-based communication (completion flag)  
✅ WSL compatibility  

