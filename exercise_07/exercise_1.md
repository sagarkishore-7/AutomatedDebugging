# Main Script:
```sh
import random
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


def heartbeat(length: int, payload: str) -> str:
    assert length == len(payload)
    store_data(payload)
    assert data.startswith(payload)
    r = get_data(length)
    assert r == payload
    return r
```
# 1. Heartbeat Payload Grammar:
```sh
HEARTBEAT_GRAMMAR: Grammar = {
    "<start>": ["<strings>"],
    "<strings>": ["<string>", "<string><strings>"],
    "<string>": ["<letters>", "<digits>", "<special_chars>"],
    "<letters>": ["<letter>", "<letter><letters>"],
    "<letter>": [string.ascii_letters],
    "<digits>": ["<digit><digits>", "<digit>"],
    "<digit>": [string.digits],
    "<special_chars>": ["<special_char>", "<special_char><special_chars>"],
    "<special_char>": ["!", """, "#",  ",", "-", ".", "/", ":", ";", "=", "?", "@", "[","$", "%", "&", """, "(", ")",
                       "*", "+", "\\", "]", "^", "_", "`", "{", "|", "}", "~"]
}
```
# 2.  Grammar Fuzzer Code:
```sh
fuzzer = GrammarFuzzer(HEARTBEAT_GRAMMAR)
random.random()
while True:
    fuzzed_input = fuzzer.fuzz()
    try:
        heartbeat(5, fuzzed_input)
    except AssertionError:
        break

failing_input = fuzzed_input
```
# 3. Delta Debugger Code:
```sh
with DeltaDebugger() as dd:
    heartbeat(5, failing_input)
print(dd)
```

# Output:
```sh
heartbeat(length=5, payload='')
```
Although the white space does in fact cause the program to fail, the payload - length mismatch, which is not reflected in the output, is the real cause of the program's failure. The output does not adequately explain the minimal failure input.# 4. DDSet Debugger
```sh
with DDSetDebugger(HEARTBEAT_GRAMMAR) as ddset:
    heartbeat(5, failing_input)
print(ddset)
```
# Output:
```sh
heartbeat(length=5, payload='<start>')
```

# 4.1
The output pattern is erroneous; asserting that the pattern is <start> just indicates that any input will lead to failure while omitting the obvious problem (the input length).
# 4.2 Fuzz_args and success rate code:
```sh
fail = 0

for i in range(10000):
    fuzz_args = ddset.fuzz_args()
    payload = fuzz_args.get("payload")
    try:
        heartbeat(5, payload)
    except AssertionError:
        fail += 1
print(fail)
print((1 - (fail / 10000)) * 100)
```
# Output:
```sh
9910
0.9000000000000008
```
The sucess rate is 90% which is high due to the randomness of the input length of 5 which is 9910/10000

# 4.3 
A potential enhancement is to incorporate the length parameter into the grammar and to link a larger test sample size to the failure factors for both the length and payload parameters.




