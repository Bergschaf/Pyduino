project(SerialCommunication)

add_executable(executable.cpp SerialCommunication/SerialPc.cpp SerialCommunication/Serial.cpp SerialCommunication/SerialClass.h)

add_executable(executable2.cpp main.cpp)