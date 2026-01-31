#!/bin/bash

echo "======================================"
echo "Person Detection Setup Script"
echo "======================================"
echo ""

# Update package list
echo "[1/6] Updating package list..."
sudo apt-get update -qq

# Install OpenCV and build tools
echo "[2/6] Installing OpenCV and build tools..."
sudo apt-get install -y \
    build-essential \
    cmake \
    pkg-config \
    libopencv-dev \
    python3-opencv \
    python3-pip \
    wget

# Install Python dependencies
echo "[3/6] Installing Python dependencies..."
pip3 install --break-system-packages sysv-ipc opencv-python numpy

# Download YOLOv3 configuration and weights
echo "[4/6] Downloading YOLOv3 model files..."

if [ ! -f "yolov3.cfg" ]; then
    echo "Downloading yolov3.cfg..."
    wget -q https://raw.githubusercontent.com/pjreddie/darknet/master/cfg/yolov3.cfg
    echo "✓ yolov3.cfg downloaded"
else
    echo "✓ yolov3.cfg already exists"
fi

if [ ! -f "yolov3.weights" ]; then
    echo "Downloading yolov3.weights (237 MB - this may take a while)..."
    wget -q --show-progress https://pjreddie.com/media/files/yolov3.weights
    echo "✓ yolov3.weights downloaded"
else
    echo "✓ yolov3.weights already exists"
fi

# Download COCO names
if [ ! -f "coco.names" ]; then
    echo "Downloading coco.names..."
    wget -q https://raw.githubusercontent.com/pjreddie/darknet/master/data/coco.names
    echo "✓ coco.names downloaded"
else
    echo "✓ coco.names already exists"
fi

# Build the C++ detector
echo "[5/6] Building C++ detector..."
make clean
make

if [ -f "detector" ]; then
    echo "✓ Detector compiled successfully"
else
    echo "✗ Compilation failed!"
    exit 1
fi

# Clean up any existing shared memory segments
echo "[6/6] Cleaning up shared memory..."
ipcs -m | grep $(whoami) | awk '{print $2}' | xargs -I {} ipcrm -m {} 2>/dev/null || true

echo ""
echo "======================================"
echo "Setup Complete!"
echo "======================================"
echo ""
echo "Files created:"
echo "  ✓ detector (C++ executable)"
echo "  ✓ visualizer.py (Python script)"
echo "  ✓ yolov3.cfg (YOLO config)"
echo "  ✓ yolov3.weights (YOLO weights)"
echo ""
echo "Next steps:"
echo "1. Place your video file in this directory"
echo "2. Run: ./run.sh your_video.mp4"
echo ""
