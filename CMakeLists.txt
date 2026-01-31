cmake_minimum_required(VERSION 3.10)
project(PersonDetector)

set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Find OpenCV
find_package(OpenCV REQUIRED)

include_directories(${OpenCV_INCLUDE_DIRS})

# Add executable
add_executable(detector detector.cpp)

# Link libraries
target_link_libraries(detector ${OpenCV_LIBS} pthread)
