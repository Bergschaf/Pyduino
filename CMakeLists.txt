cmake_minimum_required(VERSION 3.24)
project(Pyduino)

set(CMAKE_CXX_STANDARD 14)

include_directories(server/transpiler/SerialCommunication)

add_executable(Pyduino  temp/temp_pc.cpp )
