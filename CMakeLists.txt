cmake_minimum_required(VERSION 3.21)
project(Pyduino)

set(CMAKE_CXX_STANDARD 14)

add_executable(Pyduino
        Arduino.c Arduino.hpp)
add_executable(PyduinoCompiled
        testPyduino.cpp)
