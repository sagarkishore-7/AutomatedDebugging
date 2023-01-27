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

fuzzer = GrammarFuzzer(HEARTBEAT_GRAMMAR)
random.random()
while True:
    fuzzed_input = fuzzer.fuzz()
    try:
        heartbeat(5, fuzzed_input)
    except AssertionError:
        break

failing_input = fuzzed_input

with DeltaDebugger() as dd:
    heartbeat(5, failing_input)
print(dd)

with DDSetDebugger(HEARTBEAT_GRAMMAR) as ddset:
    heartbeat(5, failing_input)
print(ddset)

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
