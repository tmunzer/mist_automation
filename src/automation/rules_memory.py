from automation import rules_check
import datetime
import pytz
import json
from libs.logger import Console
"""System modules"""
console = Console("rules_memory")


class Memory:
    def __init__(self, rules_config:list):
        self.webhook_rules = []
        self.time_rules = []
        self._process_automation_config(rules_config)

    def _process_automation_config(self, rules_config: list):
        for rule in rules_config:
            automation_trigger = rule.get("trigger")

            if automation_trigger == "webhook" and rules_check.process_webhook_rules(rule):
                self.webhook_rules.append(rule)
            if automation_trigger == "time" and rules_check.process_time_rules(rule):
                self.time_rules.append(rule)

    def get_webhook_rules(self, topic: str, event: str):
        return list(filter(lambda rule: rule.get('topic') == topic and (rule.get("event") == event or rule.get("event") == None), self.webhook_rules))

    def get_time_rules(self):
        tz = pytz.timezone("UTC")
        now = datetime.datetime.now(tz)
        now_string = f"{now.hour}:{now.minute}"
        return list(filter(lambda rule: rule.get('at') == now_string, self.time_rules))

    def print_rules(self):
        print(" Webhook based rules ".center(80,"."))
        print(json.dumps(self.webhook_rules, indent=2))
        print(" Time based rules ".center(80,"."))
        print(json.dumps(self.time_rules, indent=2))

