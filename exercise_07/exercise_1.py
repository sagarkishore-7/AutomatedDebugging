from fuzzingbook.Grammars import Grammar
from fuzzingbook.GrammarFuzzer import GrammarFuzzer
from debuggingbook.DeltaDebugger import DeltaDebugger
from debuggingbook.DDSetDebugger import DDSetDebugger
import string

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

fuzzer = GrammarFuzzer(HEARTBEAT_GRAMMAR)
fuzz_heartbeat = fuzzer.fuzz()

for i in range(100):
    heartbeat(5, fuzz_heartbeat)

with DeltaDebugger(log=False) as dd:
    heartbeat(5, fuzz_heartbeat)
print(dd)

with DDSetDebugger(HEARTBEAT_GRAMMAR, log=False) as dd:
    heartbeat(5, fuzz_heartbeat)

fail = 0

for i in range(10000):
    fuzz_args = dd.fuzz_args()
    payload = fuzz_args.get("payload")
    try:
        heartbeat(5, payload)
    except AssertionError:
        fail += 1
print(fail)
print((1 - fail / 10000) * 100)