"""System modules"""
import os
import sys
import yaml
import json
from datetime import datetime

from flask import Flask
from flask import request
from config import webhook_conf
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
    import automation
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

def process_automation_config(automation_config: list):
    AUTOMATION = {}
    for automation in automation_config:
        name = automation.get("name")
        topic = automation.get("topic")
        event = automation.get("event")
        actions = automation.get("actions")
        filters = automation.get("filters")

        if not topic in AUTOMATION:
            AUTOMATION[topic] = {}

        if event:
            if not event in AUTOMATION:
                AUTOMATION[topic][event] = {}
            AUTOMATION[topic][event][name] = {
                "actions": actions,
                "filters": filters
            }
        else:
            AUTOMATION[topic][name] = {
                "actions": actions,
                "filters": filters
            }

    return AUTOMATION


def load_automation():
    print("Loading automation file ".ljust(79, "."), end="", flush=True)
    try:
        with open("automation.yml", "r") as f:
            automation_config = yaml.load(f, Loader=yaml.FullLoader)
            AUTOMATION = process_automation_config(automation_config)
        print("\033[92m\u2714\033[0m")
    except:
        print('\033[31m\u2716\033[0m')
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
    res = automation.new_event(
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
