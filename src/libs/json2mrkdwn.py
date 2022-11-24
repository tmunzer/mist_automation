
def convert(data:dict):
    data = _dict(None, data)
    return data

def _string(key, data):
    return  f"{key}: {data}\r\n"

def _bool(key, data):
    return  f"{key}: {data}\r\n"

def _list(key, data):
    tmp_string = "{key}: \r\n"
    for value in data:
        tmp_string += f" - {value}\r\n"
    return value

def _dict(key, data, index=0):
    tmp_string = ""
    if key:
        for i in range(0, index):
            tmp_string += "#"
        tmp_string += f" {key} \r\n"
    for entry in data:
        if type(data[entry])== bool:
            tmp_string += _bool(entry, data[entry])
        if type(data[entry])== str:
            tmp_string += _string(entry, data[entry])
        if type(data[entry])== list:
            tmp_string += _list(entry, data[entry])
        if type(data[entry])== dict:
            tmp_string += _dict(entry, data[entry], index+1)
    return tmp_string