from libs.logger import Console
from libs import msteams as Teams
from libs import slack as Slack
import sys
import os
import re
import json
from datetime import datetime
import hmac
import hashlib
from libs import http_request

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(SCRIPT_DIR)

"""System modules"""
console = Console("automation")

#######################################
#  FUNCTIONS


def _find_var_names(src: str):
    regexp = r"\{[a-z_]+\}"
    return re.findall(regexp, src)
        

def _replace_var(action: dict, event: dict, entries: list):
    for entry in entries:
        action_entry = action.get(entry)
        if action_entry:
            if type(action_entry) is not str:
                action_entry = json.dumps(action.get(entry))
            variables = _find_var_names(action_entry)
            for variable in variables:
                if variable == "{event}":
                    action_entry= action_entry.replace(variable, json.dumps(event))
                else:
                    variable_name = variable.replace("{", "").replace("}", "")
                    variable_value = event.get(variable_name)
                    action_entry= action_entry.replace(variable, variable_value)
            action[entry] = action_entry
    return action

def _process_auatomation(topic:str, event:dict, automation_name: str, actions:list):
    """Process new event"""
    event_type = event.get("type", "New Event")
    for tmp_action in actions:
        action = tmp_action.copy()
        console.info(f"starting automation for rule {automation_name}")
        #action = actions[action_name][0].copy()
        action_type = action.get("type")

        if action_type == "http_request":
            console.debug(event)
            action = _replace_var(action, event, ["url", "body"])
            http_request.send_request(action.get("method"), action.get("url"), action.get("headers", {}), action.get("body"))

        elif action_type == "slack":
            console.debug(event)
            action = _replace_var(action, event, ["title", "body"])
            incoming_webhook_url=action.get("incoming_webhook_url")
            title=action.get("title", f"Incoming Webhook: {topic} - {event_type}")
            data = json.loads(action["body"])
            Slack.send_manual_message(incoming_webhook_url, title, data)

        elif action_type == "teams":
            console.debug(event)
            action = _replace_var(action, event, ["title", "body"])
            incoming_webhook_url=action.get("incoming_webhook_url")
            title=action.get("title", f"Incoming Webhook: {topic} - {event_type}")
            data = json.loads(action["body"])
            color = action.get("color")
            Teams.send_manual_message(incoming_webhook_url, title, data, color)

def _process_event(topic:str, event:dict, automation_config:dict):
    topic_automations = automation_config.get(topic)
    if topic_automations:
        event_type = event.get("type")
        if event_type:
            automations = topic_automations.get(event_type, [])
        else:
            automations = topic_automations
        for automation_name in automations:
            process_automation = True
            filters = automations[automation_name].get("filters", [])
            actions = automations[automation_name].get("actions", [])
            if filters:
                for filter in filters:
                    if not event.get(filter["field"]):
                        console.warning(f"Event does not have the field {filter['field']}")
                        process_automation = False
                    elif  event.get(filter["field"]) != filter["value"]:
                        console.warning(f"Event not matching filter {filter['field']} with value {filter['value']}")
                        process_automation = False
            if process_automation:
                _process_auatomation(topic, event, automation_name, actions)


def new_event(req, webhook_secret, automation_config):
    '''
    Start to process new webhook message
    request         flask request
    secret          str             webhook secret
    host            str             Mist Cloud host (api.mist.com, ...)
    approved_admins str             List of approved admins (used for audit logs)
    automation        obj           dict of automation configurations
    '''
    if webhook_secret:
        signature = req.headers['X-Mist-Signature-v2'] if "X-Mist-Signature-v2" in req.headers else None
        key = str.encode(webhook_secret)
        message = req.data
        digester = hmac.new(key, message, hashlib.sha256).hexdigest()
    if webhook_secret and signature != digester:
        console.error("Webhook signature doesn't match")
        console.debug(f"message: {req.data}")
        console.debug(f"secret: {webhook_secret}")
        console.debug(f"signature: {signature}")
        return '', 401
    elif webhook_secret:
        console.info("Webhook signature confirmed")
    console.info("Processing new webhook message")
    content = req.get_json()
    console.debug(content)
    topic = content["topic"]

    console.info(f"Message topic: {topic}")
    events = content["events"]
    for event in events:
        _process_event(
            topic,
            event,
            automation_config
        )
    return '', 200
