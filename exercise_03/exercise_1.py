data = 'password:hjasdiebk456jhaccount:smytzek'


def store_data(payload: str):
    global data
    data = payload + data


def get_data(length: int) -> str:
    return data[:min(length, len(data) + 1)]


def heartbeat(length: int, payload: str) -> str:
    """Pre-Conditions"""
    assert length > 0 or isinstance(length, int) or isinstance(payload, str) or payload != "" or len(payload) == length
    store_data(payload)
    """Post-Conditions"""
    assert len(get_data(length)) <= length and payload in get_data(length), "Mismatch in Req -> Reply data"
    return get_data(length)
