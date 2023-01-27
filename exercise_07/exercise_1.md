## Main Function:
```sh
import string

from debuggingbook.DDSetDebugger import DDSetDebugger
from debuggingbook.DeltaDebugger import DeltaDebugger
from fuzzingbook.GrammarFuzzer import GrammarFuzzer
from fuzzingbook.Grammars import Grammar

data = 'password:hjasdiebk456jhaccount:smytzek'

def store_data(payload: str):
    global data
    data = payload + data

def get_data(length: int) -> str:
    return data[:length]
    
def heartbeat(length: int , payload: str) -> str:
    assert length == len(payload)
    store_data(payload)
    assert data.startswith(payload)
    r = get_data(length)
    assert r == payload
    return r
```
## 1. Heartbeat Payload Grammer:
```sh
HEARTBEAT_GRAMMAR: Grammar = {
    "<start>":
        ["<plain-text>"],

    "<plain-text>":
        ["", "<plain-char><plain-text>"],
    "<plain-char>":
        ["<letter>", "<digit>", "<other>", "<whitespace>"],

    "<letter>": list(string.ascii_letters),
    "<digit>": list(string.digits),
    "<other>": list(string.punctuation.replace('<', '').replace('>', '')),
    "<whitespace>": list(string.whitespace)
}
```
## 2.  Grammer Fuzzer Code:
```sh
heartbeat_fuzzer = GrammarFuzzer(HEARTBEAT_GRAMMAR)

for i in range(100):
    fuzz_heartbeat = heartbeat_fuzzer.fuzz()
    heartbeat(5, fuzz_heartbeat)
```
## 3. Delta Debugger Code:
```sh
with DeltaDebugger(log=False) as dd:
    heartbeat(5, fuzz_heartbeat)
print(dd)
```

## Output:
```sh
heartbeat(length=5, payload='')
```
The output does not explain the minimum failure input very well, the white space does in fact cause the program to fail however, the reason the program is failing is the payload - length mismatch which is not shown in the output.
## 4. DDSet Debugger
```sh
fuzz_heartbeat = heartbeat_fuzzer.fuzz()
with DDSetDebugger(HEARTBEAT_GRAMMAR, log=False) as dd:
    heartbeat(5, fuzz_heartbeat)
print(dd)
```
## Output:
```sh
heartbeat(length=5, payload='<start>')
```

## 4.1
The output pattern is incorrect, saying that the pattern is <start> just implies that any input results in a faliure while ignoring the elephant in the room (the input lenght).

## 4.2 Fuzz_args and succes rate code:
```sh
fail=0

for i in range(10000):
    fuzz_args = dd.fuzz_args()
    payload = fuzz_args.get("payload")
    try:
        heartbeat(5, payload)
    except AssertionError:
        fail += 1
print(fail)
print((1 - fail/10000) * 100)
```
## Output:
```sh
9846
1.539999999999997
```
The sucess rate is 1.54% which is very low due to the randomness of the input only 1.54% out of 10000 attempts results in an input of lenght 5.

## 4.3 
A potential improvement is to take into account the length parameter in the grammar and correlate the failure causes of both Length and Payload parameters with broader test sample size.





