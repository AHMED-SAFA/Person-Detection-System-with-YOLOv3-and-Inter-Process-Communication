#!/bin/bash

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

if [ $# -ne 1 ]; then
    echo -e "${RED}Usage: ./run.sh <video_path>${NC}"
    echo "Example: ./run.sh person_walking.mp4"
    exit 1
fi

VIDEO_PATH=$1

if [ ! -f "$VIDEO_PATH" ]; then
    echo -e "${RED}Error: Video file '$VIDEO_PATH' not found!${NC}"
    exit 1
fi

if [ ! -f "detector" ]; then
    echo -e "${RED}Error: Detector not compiled. Run './setup.sh' first!${NC}"
    exit 1
fi

echo -e "${GREEN}======================================"
echo "Person Detection System"
echo "======================================${NC}"
echo ""
echo -e "Video: ${YELLOW}$VIDEO_PATH${NC}"
echo ""

# Clean up any existing shared memory
echo "Cleaning up previous shared memory..."
ipcs -m | grep $(whoami) | awk '{print $2}' | xargs -I {} ipcrm -m {} 2>/dev/null || true

# Run detector in background
echo -e "${GREEN}[1/2] Starting C++ detector...${NC}"
./detector "$VIDEO_PATH" &
DETECTOR_PID=$!

# Give detector time to initialize
sleep 5

# Check if detector is running
if ! ps -p $DETECTOR_PID > /dev/null; then
    echo -e "${RED}Error: Detector failed to start!${NC}"
    exit 1
fi

# Run visualizer
echo -e "${GREEN}[2/2] Starting Python visualizer...${NC}"
python3 visualizer.py "$VIDEO_PATH"

# Wait for detector to finish
wait $DETECTOR_PID

echo ""
echo -e "${GREEN}======================================"
echo "Processing Complete!"
echo "======================================${NC}"
echo ""
echo "Output saved to: output_detected.mp4"
echo ""

# Cleanup shared memory
echo "Cleaning up shared memory..."
ipcs -m | grep $(whoami) | awk '{print $2}' | xargs -I {} ipcrm -m {} 2>/dev/null || true

echo -e "${GREEN}Done!${NC}"