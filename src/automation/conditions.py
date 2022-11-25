import datetime
import pytz
from libs.logger import Console
console = Console("conditions")

def _find_field_value(condition_field: list, event:dict):
    condition_fields= condition_field.split(".")
    field_value=None
    if condition_fields[0] == "event":
        field_value = event
        condition_fields.pop(0)
    for field in condition_fields:
        field_value = field_value.get(field, {})
    return field_value


def _numeric_condition(rule_name: str, event: dict, condition: dict):
    condition_above = condition.get("above")
    condition_below = condition.get("below")
    condition_field= condition.get("field")
    field_value = None
    # Validate condition configuration
    if not condition_field:
        console.error(f"Rule \"{rule_name}\": missing \"field\" field in numeric condition")
        return False
    if not condition_above and not condition_below:
        console.error(f"Rule \"{rule_name}\": missing \"above\" and/or \"below\" fields in numeric condition" )
        return False
    if condition_above and type(condition_above) not in [int,float]:
        console.error(f"Rule \"{rule_name}\": fields \"above\" is not a number in numeric condition" )
        return False
    if condition_below and type(condition_below) not in [int,float]:
        console.error(f"Rule \"{rule_name}\": fields \"below\" is not a number in numeric condition" )
        return False
    # Try to find the value and its value
    field_value=_find_field_value(condition_field, event)
    # Check the field value
    if type(field_value) not in [int,float]:
        console.warning(f"Rule \"{rule_name}\": field \"{condition_field}\" not find in the event or not a number")
        return False
    elif condition_below and not condition_field <= condition_below:
        console.warning(f"Rule \"{rule_name}\": field \"{condition_field}\" is {field_value}, not below {condition_below}")
        return False
    elif condition_above and not condition_field >= condition_above:
        console.warning(f"Rule \"{rule_name}\": field \"{condition_field}\" is {field_value}, not above {condition_above}")
        return False
    # If everything passed
    console.info(f"Rule \"{rule_name}\": field \"{condition_field}\" validated")
    return True


def _partial_match_condition(rule_name: str, event: dict, condition: dict):    
    condition_value = condition.get("value")
    condition_field= condition.get("field")
    field_value = None
    # Validate condition configuration
    if not condition_field:
        console.error(f"Rule \"{rule_name}\": missing \"field\" field in partial_match condition")
        return False
    if not condition_value:
        console.error(f"Rule \"{rule_name}\": missing \"value\" field in partial_match condition" )
        return False
    # Try to find the value and its value
    field_value=_find_field_value(condition_field, event)
    # Check the field value
    if type(field_value) is not str:
        console.warning(f"Rule \"{rule_name}\": field \"{condition_field}\" not find in the event or not a string")
        return False
    elif condition_value not in field_value:
        console.warning(f"Rule \"{rule_name}\": field \"{condition_field}\" is \"{field_value}\", not matching \"{condition_value}\"")
        return False
    # If everything passed
    console.info(f"Rule \"{rule_name}\": field \"{condition_field}\" validated")
    return True


def _exact_match_condition(rule_name: str, event: dict, condition: dict):    
    condition_value = condition.get("value")
    condition_field= condition.get("field")
    field_value = None
    # Validate condition configuration
    if not condition_field:
        console.error(f"Rule \"{rule_name}\": missing \"field\" field in exact_match condition")
        return False
    if not condition_value:
        console.error(f"Rule \"{rule_name}\": missing \"value\" field in exact_match condition" )
        return False
    # Try to find the value and its value
    field_value=_find_field_value(condition_field, event)
    # Check the field value
    if type(field_value) is not str:
        console.warning(f"Rule \"{rule_name}\": field \"{condition_field}\" not find in the event or not a string")
        return False
    elif condition_value != field_value:
        console.warning(f"Rule \"{rule_name}\": field \"{condition_field}\" is \"{field_value}\", not equal to \"{condition_value}\"")
        return False
    # If everything passed
    console.info(f"Rule \"{rule_name}\": field \"{condition_field}\" validated")
    return True


def _multiple_matches_condition(rule_name: str, event: dict, condition: dict):    
    condition_value = condition.get("value")
    condition_field= condition.get("field")
    field_value = None
    # Validate condition configuration
    if not condition_field:
        console.error(f"Rule \"{rule_name}\": missing \"field\" field in multiple_matches condition")
        return False
    if not condition_value:
        console.error(f"Rule \"{rule_name}\": missing \"value\" field in multiple_matches condition" )
        return False
    # Try to find the value and its value
    field_value=_find_field_value(condition_field, event)
    # Check the field value
    if type(field_value) is not str:
        console.warning(f"Rule \"{rule_name}\": field \"{condition_field}\" not find in the event or not a string")
        return False
    elif field_value not in condition_value:
        console.warning(f"Rule \"{rule_name}\": field \"{condition_field}\" is \"{field_value}\", not in \"{condition_value}\"")
        return False
    # If everything passed
    console.info(f"Rule \"{rule_name}\": field \"{condition_field}\" validated")
    return True


def _time_condition(rule_name: str, condition: dict):  
    condition_after= condition.get("after")
    condition_before = condition.get("before")
    condition_timezone = condition.get("timezone", "UTC")
    condition_weekday= condition.get("weekday")
    days = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
    # Validate condition configuration
    if not condition_after and not condition_before:
        console.error(f"Rule {rule_name}: missing \"before\" and/or \"after\" fields in time condition" )
        return False
    else:
        if condition_after:
            try:
                after_hour = int(condition_after.split(":")[0])
                after_minute = int(condition_after.split(":")[1])
                after = datetime.datetime.now().replace(hour=after_hour, minute=after_minute, second=0, microsecond=0)
            except:
                console.error(f"Rule {rule_name}: \"after\" field is invalid in time condition" )
                return False
        if condition_before:
            try:
                before_hour = int(condition_after.split(":")[0])
                before_minute = int(condition_after.split(":")[1])
                before = datetime.datetime.now().replace(hour=before_hour, minute=before_minute, second=0, microsecond=0)
            except:
                console.error(f"Rule {rule_name}: \"before\" field is invalid in time condition" )
                return False
    if condition_timezone and condition_timezone not in pytz.common_timezones:
        console.error(f"Rule {rule_name}: \"timezone\" value not valid in time condition" )
        return False
    if condition_weekday:
        for day in condition_weekday:
            if day not in days:
                console.error(f"Rule {rule_name}: \"weekday\" value {day} not valid in time condition" )
                return False

    tz=pytz.timezone(condition_timezone)
    current_time = datetime.datetime.now(tz)
    current_day_num = datetime.date.isoweekday(current_day_num)
    cuurent_day_str = days[current_day_num]

    if cuurent_day_str not in condition_weekday:
        console.warning(f"Rule {rule_name}: field today in not part of the weedkay list")
        return False
    elif condition_after and not current_time < after:
        console.warning(f"Rule {rule_name}: current time if before {condition_after}")
        return False
    elif condition_before and not current_time > before:
        console.warning(f"Rule {rule_name}: current time if after {condition_before}")
        return False

    return True


def process(rule_name: str, event: dict, conditions: list): 
    for condition in conditions:
        condition_type = condition.get("type")
        if condition_type == "numeric" and not _numeric_condition(rule_name, event, condition):
            return False
        if condition_type == "partial_match" and not _partial_match_condition(rule_name, event, condition):
            return False
        if condition_type == "exact_match" and not _exact_match_condition(rule_name, event, condition):
            return False
        if condition_type == "multiple_matches" and not _multiple_matches_condition(rule_name, event, condition):
            return False
        if condition_type == "time" and not _time_condition(rule_name, condition):
            return False
    return True
