from libs.logger import Console
import sys
import os
from crontab import CronTab

from automation import process_auatomation

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(SCRIPT_DIR)

"""System modules"""
console = Console("datetime")

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
                process_auatomation(topic, event, automation_name, actions)


def start(automation_config):


