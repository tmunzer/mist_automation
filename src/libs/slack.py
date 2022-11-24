import requests
from requests import HTTPError
import json
from libs.logger import Console
from libs import json2mrkdwn
console = Console("slack")


def send_manual_message(incoming_webhook, title, data):
    '''
    Send message to Slack Channel

    Params:
        config  obj         Slack URL Configuration {default_url: str, url: {channels: str}}
        topic   str         Mist webhook topic
        title   str         Message Title
        text    str         Message Text
        info    [str]       Array of info
        actions [obj]       Array of actions {text: btn text, action: btn url, tag: btn id}
        channel str         Slack Channel
    '''
    print(data)
    print(type(data))
    mrkdown = json2mrkdwn.convert(data)

    body = {
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": title
                }
            }, {
                "type": "section",
                "text": {
                        "type": "mrkdwn",
                        "text": mrkdown
                }
            }
        ]
    }

    data = json.dumps(body)
    print(data)
    console.info("Sending message to SLACK")
    try:
        resp = requests.post(incoming_webhook, headers={
                             "Content-type": "application/json"}, data=data)
        resp.raise_for_status()
    except HTTPError as http_err:
        console.error(f'HTTP error occurred: {http_err}')  # Python 3.6
        console.error(f'HTTP error description: {resp.content}')
    except Exception as err:
        console.error(f'Other error occurred: {err}')  # Python 3.6
    else:
        console.info(resp.status_code)
