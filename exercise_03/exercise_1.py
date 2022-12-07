data = 'password:hjasdiebk456jhaccount:smytzek'

def store_data(payload: str):
    global data
    data = payload + data

def get_data(length: int) -> str:
    return data[:min(length, len(data) + 1)]
    
def heartbeat(length: int, payload: str) -> str:
    store_data(payload)
    return get_data(length)
