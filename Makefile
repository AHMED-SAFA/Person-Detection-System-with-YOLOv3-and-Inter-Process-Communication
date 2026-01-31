CXX = g++
CXXFLAGS = -std=c++11 -Wall
OPENCV_FLAGS = `pkg-config --cflags --libs opencv4`

all: detector

detector: detector.cpp
	$(CXX) $(CXXFLAGS) detector.cpp -o detector $(OPENCV_FLAGS) -lpthread

clean:
	rm -f detector
	ipcs -m | grep $(USER) | awk '{print $$2}' | xargs -I {} ipcrm -m {} 2>/dev/null || true

.PHONY: all clean
