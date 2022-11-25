from libs.logger import Console
import sys
import os
import hmac
import hashlib
from automation import process_automation

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(SCRIPT_DIR)

"""System modules"""
console = Console("webhook")

#######################################
#  FUNCTIONS


def _process_event(topic: str, event: dict, automation_config: dict):
    topic_automations = automation_config.get(topic)
    if topic_automations:
        event_type = event.get("type")
        if event_type:
            automations = topic_automations.get(event_type, [])
        else:
            automations = topic_automations
        for automation_name in automations:
            process_automation = True
            conditions = automations[automation_name].get("conditions", [])
            actions = automations[automation_name].get("actions", [])
            if conditions:
                for key in conditions:
                    value = conditions[key]
                    if not event.get(key):
                        console.warning(f"Event does not have the field {key}")
                        process_automation = False
                    elif (type(value) == str and event.get(key) != value) \
                            or (type(value) == list and not event.get(key) in value):
                        console.warning(
                            f"Event not matching condition {key} with value {value}")
                        process_automation = False
            if process_automation:
                process_automation(topic, event, automation_name, actions)


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
