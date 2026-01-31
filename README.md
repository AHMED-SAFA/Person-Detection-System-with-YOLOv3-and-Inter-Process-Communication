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
./run.sh your_video.mp4
```

Replace `your_video.mp4` with your actual video file path.

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

### Option 1: Using Makefile (Recommended)

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

### Option 2: Using CMake

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

### Option 3: Direct Compilation

```bash
# Compile C++ detector
g++ -std=c++11 detector.cpp -o detector \
    `pkg-config --cflags --libs opencv4` -lpthread

# Run detector
./detector video.mp4

# Run visualizer (in another terminal)
python3 visualizer.py video.mp4
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

## 🐛 Troubleshooting

### Issue: "Cannot open video file"
**Solution:** Verify video file path and format. Supported: mp4, avi, mov

### Issue: "Failed to create shared memory"
**Solution:** Clean up existing shared memory:
```bash
ipcs -m | grep $(whoami) | awk '{print $2}' | xargs -I {} ipcrm -m {}
```

### Issue: "Cannot connect to shared memory" (Python)
**Solution:** Ensure C++ detector is running first and created shared memory

### Issue: YOLO weights not found
**Solution:** Re-run setup script:
```bash
./setup.sh
```

### Issue: Low detection accuracy
**Solution:** Adjust `confThreshold` in detector.cpp (try 0.3-0.7)

### Issue: Too many false positives
**Solution:** Increase `confThreshold` or adjust `nmsThreshold`

## 📊 Performance Notes

- **Processing Speed:** ~1-5 FPS on CPU (depends on video resolution)
- **Memory Usage:** ~500MB for YOLO model + video processing
- **GPU Acceleration:** Not enabled (can be added by changing DNN backend)

## 🔍 Understanding the Output

The visualizer displays:
- **Green boxes:** Detected persons
- **Labels:** "Person: X.XX" where X.XX is confidence score
- **Frame info:** Current frame number and detection count
- **Output file:** `output_detected.mp4` with all visualizations

## 📈 Improvements and Extensions

Possible enhancements:
1. Add GPU support (CUDA) for faster processing
2. Track persons across frames (add tracking ID)
3. Count persons entering/exiting frame
4. Add signal handling for proper cleanup
5. Support multiple video formats
6. Real-time processing with camera input
7. Multi-threaded processing

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

## 📝 Code Explanation

### Key C++ Components

1. **YOLO Model Loading:**
```cpp
Net net = readNetFromDarknet("yolov3.cfg", "yolov3.weights");
```

2. **Shared Memory Creation:**
```cpp
key_t key = ftok("detector.cpp", 65);
int shmid = shmget(key, sizeof(DetectionData), 0666 | IPC_CREAT);
DetectionData* sharedData = (DetectionData*)shmat(shmid, NULL, 0);
```

3. **Detection Loop:**
```cpp
blobFromImage(frame, blob, 1/255.0, Size(416, 416), ...);
net.forward(outs, outNames);
// Process outputs and apply NMS
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
- OpenCV 4.x (with DNN module)
- System V IPC (built-in)

### Python Libraries
- opencv-python
- numpy
- sysv-ipc

## ⚖️ License

This is an educational project for assignment purposes.

## 🤝 Assignment Requirements Met

✅ Person detection using YOLO  
✅ C++ implementation for detection  
✅ Shared memory for IPC  
✅ Python visualization  
✅ Bounding box storage and retrieval  
✅ Signal-based communication (completion flag)  
✅ WSL compatibility  

## 📞 Support

If you encounter issues:
1. Check video file format and path
2. Verify all dependencies are installed
3. Clean shared memory before running
4. Check YOLO model files are downloaded
5. Review error messages in terminal

---

**Happy Detecting! 🎥👤**
