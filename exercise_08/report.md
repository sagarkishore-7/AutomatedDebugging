# Report

# The functions that are terminating on all inputs:
## ex_1
```sh
 def ex_1(i: int):
 while i < 0:
    i = i + 1
```
The variable "i" increases by 1 until it finally reaches 0, breaking the condition "i < 0".

## ex_6
```sh
def ex_6(i: int):
    c = 0
    while i >= 0:
        j = 0
        while j <= i - 1:
            j = j + 1
            c = c + 1
        i = i - 1
```
The variable "i" decreases by 1 until it reaches 0 and violates the first loop's condition "i >= 0". Meanwhile, the variable "j" starts at 0 and increases by 1 until it reaches "i - 1", set by the prior loop, which must be non-negative. As a result, "j" will eventually break the second loop, and "i" will break the first.
# Functions that do not have a termination point:
## ex_2:
```sh
def ex_2(i: int):
    while i != 1 and i != 0:
        i = i - 2
```
For example, entering a negative value, such as "-2", into the function will cause an infinite loop of the variable "i" decreasing by 2 and never meeting the criteria of being equal to 1 or 0.
## The debugger's recorded frequency of each line.
```sh
The value of i =  -2
  60   0%     def ex_2(i: int):
  61  50%         while i != 1 and i != 0:
  62  49%             i = i - 2
 ```
 ## ex_3:
```sh
def ex_3(i: int, j: int):
    while i != j:
        i = i - 1
        j = j + 1
```
When the value of "i" (5) is smaller than "j" (10), the loop will continue indefinitely.
## The debugger's recorded frequency of each line.
```sh
The value of i = 5, The value of j =  10
  64   0%     def ex_3(i: int, j: int):
  65  33%         while i != j:
  66  33%             i = i - 1
  67  33%             j = j + 1
```
## ex_4:
```sh
def ex_4(i: int):
    while i >= -5 and i <= 5:
        if i > 0:
            i = i - 1
        if i < 0:
            i = i + 1
```
The variable "i" will either increase or decrease until it reaches zero, causing the loop to repeat indefinitely.
## The debugger's recorded frequency of each line.
```sh
The value of i = 0
  69   0%     def ex_4(i: int):
  70  33%         while i >= -5 and i <= 5:
  71  33%             if i > 0:
  72   0%                 i = i - 1
  73  33%             if i < 0:
  74   0%                 i = i + 1
```
## ex_5:
```sh
def ex_5(i: int):
    while i < 10:
        j = i
        while j > 0:
            j = j + 1
        i = i + 1
```
The variable "i" (-5) is incrementing by 1 until it becomes 1. Then, "j" is set to 1 and enters the second loop, incrementing by 1 repeatedly, causing the loop to run indefinitely.
## The debugger's recorded frequency of each line.
```sh
The value of i =  -5
  76   0%     def ex_5(i: int):
  77   0%         while i < 10:
  78   0%             j = i
  79  49%             while j > 0:
  80  49%                 j = j + 1
  81   0%             i = i + 1
```





