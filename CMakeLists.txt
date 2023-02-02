cmake_minimum_required(VERSION 3.24)
project(Pyduino)

set(CMAKE_CXX_STANDARD 14)

include_directories(server/transpiler/SerialCommunication)

add_executable(Pyduino
        server/transpiler/SerialCommunication/Serial.cpp
        server/transpiler/SerialCommunication/SerialClass.h server/transpiler/SerialCommunication/Serial_PC.cpp server/transpiler/SerialCommunication/Serial_Arduino.ino)
