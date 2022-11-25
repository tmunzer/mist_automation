"""System modules"""
import os
import sys
import yaml
import json
from datetime import datetime
import traceback

from flask import Flask
from flask import request
from config import webhook_conf

from automation import webhooks
###########################
# APP SETTINGS
DEBUG = False
LOG_LEVEL = "INFO"
SERVER_PORT = 51361

try:
    import config
    if hasattr(config, 'debug'):
        DEBUG = config.debug
    if hasattr(config, 'log_level'):
        print(config.log_level)
        LOG_LEVEL = config.log_level
    if hasattr(config, 'port'):
        SERVER_PORT = config.port
except:
    pass
finally:
    os.environ["LOG_LEVEL"] = LOG_LEVEL
    if not DEBUG:
        os.environ['FLASK_ENV'] = 'PRODUCTION'
    from libs.logger import Console
    console = Console("main")

###########################
# LOAD CONF FUNCTIONS


def load_conf(value):
    """Process config"""
    print(f"Loading {value} ".ljust(79, "."), end="", flush=True)
    if value in webhook_conf:
        print("\033[92m\u2714\033[0m")
        return webhook_conf[value]
    else:
        print('\033[31m\u2716\033[0m')
        sys.exit(255)


def display_conf():
    """Display config"""
    print(
        f"Webhook Secret  : {WEBHOOK_SECRET[:6]}........{WEBHOOK_SECRET[len(WEBHOOK_SECRET)-6:]}")
    print(f"WEBHOOK URI        : {WEBHOOK_URI}")
    print(f"Debug Mode      : {DEBUG}")


###########################
# LAOD AUTOMATION

def _process_automation_webhook(automation_rules: dict, rule_config:dict):
        automation_name = rule_config.get("name")
        automation_topic = rule_config.get("topic")
        automation_event = rule_config.get("event")
        automation_actions = rule_config.get("actions")
        automation_conditions = rule_config.get("conditions")

        if not automation_name: 
            console.error("rule Name missing in the automation configuration")
            return automation_rules
        if not automation_topic: 
            console.error(f"\"topic\" field is missing in the automation configuration in rule {automation_name}")
            return automation_rules
        if not automation_actions: 
            console.error(f"\"actions\" field is missing in the automation configuration in rule {automation_name}")
            return automation_rules

        if automation_topic and not automation_topic in automation_rules["webhook"]:
            automation_rules["webhook"][automation_topic] = {}

        if automation_event:
            if not automation_event in automation_rules["webhook"]:
                automation_rules["webhook"][automation_topic][automation_event] = {}
            automation_rules["webhook"][automation_topic][automation_event][automation_name] = {
                "actions": automation_actions,
                "conditions": automation_conditions
            }
        else:
            automation_rules["webhook"][automation_topic][automation_name] = {
                "actions": automation_actions,
                "conditions": automation_conditions
            }
        return automation_rules

def _process_automation_datetime(automation_rules: dict, rule_config: dict):
        automation_name = rule_config.get("name")
        automation_at = rule_config.get("at")
        automation_when = rule_config.get("when")
        automation_actions = rule_config.get("actions")

        if not automation_name: 
            console.error("rule Name missing in the automation configuration")
            return automation_rules
        if not automation_at and not automation_when: 
            console.error(f"\"at\" or \"when\" fields are missing in the automation configuration in rule {automation_name}")
            return automation_rules
        if not automation_actions: 
            console.error(f"\"actions\" field is missing in the automation configuration in rule {automation_name}")
            return automation_rules

        automation_rules["datetime"][automation_name] = {
            "actions": automation_actions
        }
        if automation_when: 


def _process_automation_config(automation_config: list):
    automation_rules = {}
    for rule in automation_config:
        automation_type = rule.get("type")

        if not automation_type in automation_rules:
            automation_rules[automation_type] = {}
        
        if automation_type == "webhook":
            _process_automation_webhook(automation_rules, rule)


    return automation_rules


def load_automation():
    print("Loading automation file ".ljust(79, "."), end="", flush=True)
    try:
        with open("automation.yml", "r") as f:
            automation_config = yaml.load(f, Loader=yaml.FullLoader)
            AUTOMATION = _process_automation_config(automation_config)
        print("\033[92m\u2714\033[0m")
    except Exception:        
        print('\033[31m\u2716\033[0m')    
        traceback.print_exc()
        sys.exit(255)
    return AUTOMATION


def display_automation():
    print("Automation rules:")
    print(json.dumps(AUTOMATION, indent=4))


###########################
# ENTRY POINT
print(" Configuration ".center(80, "_"))
WEBHOOK_SECRET = load_conf("webhook_secret")
WEBHOOK_URI = load_conf("webhook_uri")
print(" Automation ".center(80, "_"))
AUTOMATION = load_automation()
print("Configuraiton loaded".center(80, "_"))
display_conf()
display_automation()

app = Flask(__name__)


@app.route(WEBHOOK_URI, methods=["POST"])
def postJsonHandler():
    console.info(" New message reveived ".center(60, "-"))
    start = datetime.now()
    res = webhooks.new_event(
        request,
        WEBHOOK_SECRET,
        AUTOMATION
    )
    delta = datetime.now() - start
    console.info(f"Processing time {delta.seconds}.{delta.microseconds}s")
    return res


if __name__ == '__main__':
    print(f"Starting Server: 0.0.0.0:{SERVER_PORT}".center(80, "_"))
    app.run(debug=False, host='0.0.0.0', port=SERVER_PORT)
