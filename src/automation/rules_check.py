import pytz
import datetime
from libs.logger import Console
"""System modules"""
console = Console("rules_check")


def process_webhook_rules(rule:dict):
    automation_name = rule.get("name")
    automation_topic = rule.get("topic")
    automation_actions = rule.get("actions")
    automation_conditions = rule.get("conditions")

    # check the rule configuration
    if not automation_name: 
        console.error("rule Name missing in the automation configuration")
        return False
    if not automation_topic: 
        console.error(f"\"topic\" field is missing in the automation configuration in rule {automation_name}")
        return False 
    if not automation_actions: 
        console.error(f"\"actions\" field is missing in the automation configuration in rule {automation_name}")
        return False 

    return rule
    
    

def process_time_rules(rule: dict):
    automation_name = rule.get("name")
    automation_at = rule.get("at")
    automation_actions = rule.get("actions")
    automation_timezone = rule.get("timezone", "UTC")

    if not automation_name: 
        console.error("rule Name missing in the automation configuration")
        return False
    if not automation_at: 
        console.error(f"\"at\" field is missing in the automation configuration in rule {automation_name}")
        return False
    if not automation_actions: 
        console.error(f"\"actions\" field is missing in the automation configuration in rule {automation_name}")
        return False

    try:
        hours = int(automation_at.split(":")[0])
        minutes = int(automation_at.split(":")[1])
        if automation_timezone is not "UTC":
            tz = pytz.timezone(automation_timezone)
            utc = pytz.timezone("UTC")
            time = datetime.datetime.now().replace(hour=hours, minute=minutes, second=0, microsecond=0, tzinfo=tz)
            time = time.astimezone(utc)
            rule["set"]=f"{time.hour}:{time.minute}"
    except:
        console.error(f"\"at\" value is not valid in the automation configuration in rule {automation_name}")
        return False

    return rule


