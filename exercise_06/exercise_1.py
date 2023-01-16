from debuggingbook.DynamicInvariants import precondition, postcondition

data = 'password:hjasdiebk456jhaccount:smytzek'

@postcondition(lambda return_value, payload: return_value==None)
def store_data(payload: str):
    global data
    data = payload + data

@postcondition(lambda return_value, length: data.startswith(return_value))
def get_data(length: int) -> str:
    return data[:min(length, len(data) + 1)]

@precondition(lambda length, payload: len(payload)==length)
@postcondition(lambda return_value, length, payload: return_value==payload )
def heartbeat(length: int, payload: str) -> str:
    store_data(payload)
    return get_data(length)
