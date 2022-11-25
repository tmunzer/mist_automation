import requests
from requests import HTTPError
import json
from libs.logger import Console
console = Console("teams")

def _generage_facts(data):
    if data:
        data_facts =  []
        for entry in data:
            data_facts.append({
            "name": entry,
            "value": data[entry]
        })
    else:
        data_facts = None
    return data_facts


def send_manual_message(incoming_webhook, title, data, color=None):
    '''
    Send message to MsTeams Channel

    Params:
        config  obj         Teams URL Configuration {default_url: str, url: {channels: str}}
        topic   str         Mist webhook topic
        title   str         Message Title
        text    str         Message Text
        info    [str]       Array of info
        actions [obj]       Array of actions {text: btn text, action: btn url, tag: btn id}
        channel str         Slack Channel
    '''
    body = {
        "@type": "MessageCard",
        "@context": "http://schema.org/extensions",
        "summary": title,
        "sections": [
            {
                "activityTitle": title,
                "facts": _generage_facts(data),
                "markdown": True
            }
        ]

    }

    if color:
        body["themeColor"] = color

    data = json.dumps(body)
    console.info("Sending message to TEAMS")
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
