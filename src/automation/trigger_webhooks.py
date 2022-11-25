import hmac
import hashlib
from automation import conditions as Conditions
from automation import automation as Automation
from automation.rules_memory import Memory
from libs.logger import Console

"""System modules"""
console = Console("webhook")

#######################################
#  FUNCTIONS


def _process_event(mist_topic: str, mist_event: dict, automation_rules: Memory):
    event_type = mist_event.get("type")
    rules = automation_rules.get_webhook_rules(mist_topic, event_type)
    for rule in rules:

        process_automation = True
        rule_name = rule.get("name", "No Name")
        rule_conditions = rule.get("conditions", [])
        rule_actions = rule.get("actions", [])

        if rule_conditions:
            process_automation = False
            process_automation = Conditions.process(
                rule_name, mist_event, rule_conditions)
        if process_automation:
            Automation.process(mist_topic, mist_event, rule_name, rule_actions)


def new_event(req, webhook_secret, automation_rules: Memory):
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
            automation_rules
        )
    return '', 200
