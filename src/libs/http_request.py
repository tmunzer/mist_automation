import requests
from requests.exceptions import HTTPError
from libs.logger import Console

console = Console("http req")

def send_request(method: str, url: str, headers: dict, body:str):
    console.info("Sending HTTP request")
    try:
        resp = requests.request(method=method, url=url, headers=headers, data=body)
        resp.raise_for_status()
    except HTTPError as http_err:
        console.error(f'HTTP error occurred: {http_err}')  # Python 3.6
        console.error(f'HTTP error description: {resp.content}')
    except Exception as err:
        console.error(f'Other error occurred: {err}')  # Python 3.6
    else:           
        console.info(resp.status_code)  