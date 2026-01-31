#include <opencv2/opencv.hpp>
#include <opencv2/dnn.hpp>
#include <sys/ipc.h>
#include <sys/shm.h>
#include <sys/types.h>
#include <signal.h>
#include <unistd.h>
#include <iostream>
#include <vector>
#include <cstring>

using namespace cv;
using namespace cv::dnn;
using namespace std;

// Shared memory structure for detection data
struct DetectionData {
    int frame_number;
    int num_detections;
    struct BBox {
        float x;
        float y;
        float width;
        float height;
        float confidence;
    } boxes[50]; // Max 50 detections per frame
    bool processing_complete;
};

int main(int argc, char** argv) {
    if (argc != 2) {
        cout << "Usage: ./detector <video_path>" << endl;
        return -1;
    }

    string videoPath = argv[1];
    
    // Load YOLO model
    cout << "Loading YOLO model..." << endl;
    Net net = readNetFromDarknet("yolov3.cfg", "yolov3.weights");
    net.setPreferableBackend(DNN_BACKEND_OPENCV);
    net.setPreferableTarget(DNN_TARGET_CPU);
    
    // Get output layer names
    vector<string> outNames = net.getUnconnectedOutLayersNames();
    
    // Open video
    VideoCapture cap(videoPath);
    if (!cap.isOpened()) {
        cout << "Error: Cannot open video file!" << endl;
        return -1;
    }
    
    int frame_width = cap.get(CAP_PROP_FRAME_WIDTH);
    int frame_height = cap.get(CAP_PROP_FRAME_HEIGHT);
    
    // Create shared memory
    key_t key = ftok("detector.cpp", 65);
    int shmid = shmget(key, sizeof(DetectionData), 0666 | IPC_CREAT);
    if (shmid == -1) {
        cout << "Error: Failed to create shared memory!" << endl;
        return -1;
    }
    
    DetectionData* sharedData = (DetectionData*)shmat(shmid, NULL, 0);
    if (sharedData == (void*)-1) {
        cout << "Error: Failed to attach shared memory!" << endl;
        return -1;
    }
    
    // Initialize shared memory
    memset(sharedData, 0, sizeof(DetectionData));
    sharedData->processing_complete = false;
    
    cout << "Processing video..." << endl;
    Mat frame, blob;
    int frameCount = 0;
    
    // YOLO parameters
    float confThreshold = 0.5;
    float nmsThreshold = 0.4;
    int inpWidth = 416;
    int inpHeight = 416;
    
    while (true) {
        cap >> frame;
        if (frame.empty()) break;
        
        frameCount++;
        
        // Create blob from frame
        blobFromImage(frame, blob, 1/255.0, Size(inpWidth, inpHeight), Scalar(0,0,0), true, false);
        net.setInput(blob);
        
        // Forward pass
        vector<Mat> outs;
        net.forward(outs, outNames);
        
        // Process detections
        vector<int> classIds;
        vector<float> confidences;
        vector<Rect> boxes;
        
        for (size_t i = 0; i < outs.size(); ++i) {
            float* data = (float*)outs[i].data;
            for (int j = 0; j < outs[i].rows; ++j, data += outs[i].cols) {
                Mat scores = outs[i].row(j).colRange(5, outs[i].cols);
                Point classIdPoint;
                double confidence;
                minMaxLoc(scores, 0, &confidence, 0, &classIdPoint);
                
                // Class 0 is 'person' in COCO dataset
                if (classIdPoint.x == 0 && confidence > confThreshold) {
                    int centerX = (int)(data[0] * frame.cols);
                    int centerY = (int)(data[1] * frame.rows);
                    int width = (int)(data[2] * frame.cols);
                    int height = (int)(data[3] * frame.rows);
                    int left = centerX - width / 2;
                    int top = centerY - height / 2;
                    
                    classIds.push_back(classIdPoint.x);
                    confidences.push_back((float)confidence);
                    boxes.push_back(Rect(left, top, width, height));
                }
            }
        }
        
        // Apply Non-Maximum Suppression
        vector<int> indices;
        NMSBoxes(boxes, confidences, confThreshold, nmsThreshold, indices);
        
        // Update shared memory with detections
        sharedData->frame_number = frameCount;
        sharedData->num_detections = min((int)indices.size(), 50);
        
        for (size_t i = 0; i < sharedData->num_detections; ++i) {
            int idx = indices[i];
            Rect box = boxes[idx];
            sharedData->boxes[i].x = box.x;
            sharedData->boxes[i].y = box.y;
            sharedData->boxes[i].width = box.width;
            sharedData->boxes[i].height = box.height;
            sharedData->boxes[i].confidence = confidences[idx];
        }
        
        cout << "Frame " << frameCount << ": Detected " << sharedData->num_detections << " persons" << endl;
        
        // Small delay to allow Python to process
        usleep(30000); // 30ms delay
    }
    
    // Mark processing as complete
    sharedData->processing_complete = true;
    cout << "Detection complete. Total frames: " << frameCount << endl;
    
    // Send signal to Python process (using process group)
    // The Python script will need to register its PID
    cout << "Sending completion signal..." << endl;
    
    // Detach shared memory (don't delete it - Python needs it)
    shmdt(sharedData);
    
    cout << "Shared memory ID: " << shmid << endl;
    cout << "Detection process finished." << endl;
    
    return 0;
}
