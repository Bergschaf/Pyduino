# Pyduino

Pyduino is a new programming language that allows you to write code for the Arduino Microcontroller in a Python-like syntax.
It is designed to be easy to learn and use, and is a great way to get started with programming. The core features of Pyduino are:
- Easy to leran, Python-like syntax
- The same syntax runs on both the Arduino and the PC
- PC and Arduino can be connected via the serial port
- The PC can acces Arduino's pins and sensors
- The Arduino print to the PC's console and call functions on the PC
- They can run independently or together
- In the future, Pyduino will have a IntelliJ based IDE for easy development 

The language works by transpiling the Pyduino code to C++ and the compiling it to run on the Arduino and on the PC.
To exchange data or call functions between the PC and the Arduino, the serial port is used. The PC uses a separate listener
thread to listen for data from the Arduino. The Arduino doesn't support multithreading, so it checks after every command
if there is data to be read from the serial port. If there is, it reads it and executes the command.

## Syntax

### Variables
Variables are declared with the datatype and name, and can be assigned a value.
There is no semicolon at the end of a line.
```c 
int x = 5
float y = 3.14
```
Arrays are declared with the datatype, name and an intializer list.
```c
int[] x = [1, 2, 3]
```

### Functions

operatoren: ,+ ,-, *, / ,% ,// für floor division,

python and or not etc.
geht aber auch mit !, ||, &&

print(value1,valie2,...,break=default True,round=default 0 für nicht runden)


python loops \
break und continue\
python classes \
static types for variables and lists:\
int,float,double,string, char,int8...., bool\
typecasting mit: \
int(float, string etc) \
round funktion zu float, ggf mit stellen\
roundToInt Funktion zu int\

liste: list<type> name = [element1,element2,...] .add .remove \
array: array<type> name = []\
tupel: tuple<type1,type2> = ()\
dict : dict<keyType,valueType> = {key:value,key:value} oder lehr: {}\
element: array/list/tupel[index]

Arduino: \
write(port,value)
value: True,1,0, False für ein und aus,von 1 bis 0 für analog
tone Befehl wie arduino \
read(port) returns value: 1,0 bool
delay(millis)

analogRead(analogPort): value von 1 bis 0

math modul für sin cost tan wurzel etc

Jeder (globalen) Variable auf dem Arduino und auf dem Pc wird ein index zugewiesen.\
GetVariable(name) gibt den Wert zurück

Promise?
Asynchorer Datenaustausch mit dem Arduino

Await Syntax:
Alle Funktion um Daten vom Arduino zu bekommen sind asynchron,|\
wenn await for dem Funktionsaufruf steht, wird erst weitergemacht, wenn die Daten da sind|\
sonst muss async davor stehen

