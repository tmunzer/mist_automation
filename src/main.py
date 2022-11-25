"""System modules"""
import os
import sys
import yaml
from datetime import datetime
import traceback
from config import webhook_conf
from flask import Flask
from flask import request
from thread_time import TimeWorker
from thread_http import HttpWorker

from automation import rules_memory
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
    if WEBHOOK_SECRET:
        print(
            f"Webhook Secret  : {WEBHOOK_SECRET[:6]}........{WEBHOOK_SECRET[len(WEBHOOK_SECRET)-6:]}")
    print(f"WEBHOOK URI     : {WEBHOOK_URI}")
    print(f"Debug Mode      : {DEBUG}")


###########################
# LAOD AUTOMATION


def load_automation():
    print("Loading automation file ".ljust(79, "."), end="", flush=True)
    try:
        with open("automation.yml", "r") as f:
            rules_config = yaml.load(f, Loader=yaml.FullLoader)
            AUTOMATION = rules_memory.Memory(rules_config)
        print("\033[92m\u2714\033[0m")
    except Exception:
        print('\033[31m\u2716\033[0m')
        traceback.print_exc()
        sys.exit(255)
    return AUTOMATION


###########################
# ENTRY POINT
print(" Configuration ".center(80, "_"))
WEBHOOK_SECRET = load_conf("webhook_secret")
WEBHOOK_URI = load_conf("webhook_uri")
print(" Automation ".center(80, "_"))
AUTOMATION = load_automation()
print("Configuraiton loaded".center(80, "_"))
display_conf()
AUTOMATION.print_rules()


if __name__ == '__main__':
    worker_http = HttpWorker(SERVER_PORT, WEBHOOK_URI,WEBHOOK_SECRET, AUTOMATION)
    worker_http.daemon = False
    worker_http.start()
    worker_time = TimeWorker()
    worker_time.daemon = True
    worker_time.start()
