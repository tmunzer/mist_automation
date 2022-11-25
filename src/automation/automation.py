from libs.logger import Console
from libs import msteams as Teams
from libs import slack as Slack
import sys
import os
import re
import json
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
                    action_entry = action_entry.replace(
                        variable, json.dumps(event))
                else:
                    variable_name = variable.replace("{", "").replace("}", "")
                    variable_value = event.get(variable_name)
                    action_entry = action_entry.replace(
                        variable, variable_value)
            action[entry] = action_entry
    return action


def process_automation(topic: str, event: dict, automation_name: str, actions: list):
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
            http_request.send_request(action.get("method"), action.get(
                "url"), action.get("headers", {}), action.get("body"))

        elif action_type == "slack":
            console.debug(event)
            action = _replace_var(action, event, ["title", "body"])
            incoming_webhook_url = action.get("incoming_webhook_url")
            title = action.get(
                "title", f"Incoming Webhook: {topic} - {event_type}")
            data = json.loads(action["body"])
            Slack.send_manual_message(incoming_webhook_url, title, data)

        elif action_type == "teams":
            console.debug(event)
            action = _replace_var(action, event, ["title", "body"])
            incoming_webhook_url = action.get("incoming_webhook_url")
            title = action.get(
                "title", f"Incoming Webhook: {topic} - {event_type}")
            data = json.loads(action["body"])
            color = action.get("color")
            Teams.send_manual_message(incoming_webhook_url, title, data, color)

