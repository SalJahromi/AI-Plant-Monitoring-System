import time
import serial
import json
import re

def connect_arduino(port, baud_rate=9600):
    """
    Connects to arduino via usb port.
    input:
    port: The usb port COM.
    baud_rate: communication speed.

    output:
    arduino
    """
    arduino = serial.Serial(port, baud_rate, timeout=1)
    time.sleep(2)  # gives Arduino time to reset
    return arduino


def clean_for_arduino(text):
    """
    Arduino reads one line at a time. Remove line breaks and keep message simple.
    Input:
    text: Output from llm. 
    Output:
    text: Cleaned text.
    """

    text = text.replace("\n", " ")
    text = text.replace("\r", " ")
    return text.strip()


def extract_json_from_text(text):
    """
    Tries to extract JSON from the LLM response.

    Sometimes local models return extra text before/after JSON.
    This function helps recover the JSON part.
    """

    try:
        return json.loads(text)
    except Exception:
        pass

    match = re.search(r"\{.*\}", str(text), re.DOTALL)

    if match:
        try:
            return json.loads(match.group())
        except Exception:
            pass

    return None


def make_agent_output(emotion="neutral",action="NONE",message="I had trouble understanding that.",permission_status="not_needed",action_source="none"):
    """
    Creates a valid JSON string for the plant agent.
    """

    return json.dumps({
        "emotion": emotion,
        "action": action,
        "message": message,
        "permission_status": permission_status,
        "action_source": action_source
    })


def parse_agent_output(llm_output):
    """
    Parses the LLM JSON output.

    Expected format:
    {
        "emotion": "neutral | happy | sad | angry",
        "action": "NONE | ASK_WATER | WATER",
        "message": "plant response",
        "permission_status": "not_needed | needs_permission | approved | rejected",
        "action_source": "none | sensor_condition | direct_user_command | user_approved_pending_action | user_rejected_pending_action"
    }
    """

    valid_emotions = {"neutral", "happy", "sad", "angry"}
    valid_actions = {"NONE", "ASK_WATER", "WATER", "DIAGNOSE_HEALTH"}
    valid_permission_statuses = {
        "not_needed",
        "needs_permission",
        "approved",
        "rejected"
    }
    valid_action_sources = {
        "none",
        "sensor_condition",
        "direct_user_command",
        "user_approved_pending_action",
        "user_rejected_pending_action"
    }

    data = extract_json_from_text(llm_output)

    if data is None:
        return {
            "emotion": "neutral",
            "action": "NONE",
            "message": clean_for_arduino(llm_output),
            "permission_status": "not_needed",
            "action_source": "none"
        }

    emotion = data.get("emotion", "neutral")
    action = data.get("action", "NONE")
    message = data.get("message", "I am here.")
    permission_status = data.get("permission_status", "not_needed")
    action_source = data.get("action_source", "none")

    if emotion not in valid_emotions:
        emotion = "neutral"

    if action not in valid_actions:
        action = "NONE"

    if permission_status not in valid_permission_statuses:
        permission_status = "not_needed"

    if action_source not in valid_action_sources:
        action_source = "none"

    message = clean_for_arduino(message)

    if not message:
        message = "I am here."

    return {
        "emotion": emotion,
        "action": action,
        "message": message,
        "permission_status": permission_status,
        "action_source": action_source
    }




def send_to_arduino(arduino, llm_output, allow_actions=False):
    """
    Sends the plant's face/message to Arduino.

    Important safety rule:
    The pump only activates if:
    1. action == WATER
    2. permission_status == approved
    3. allow_actions == True

    This means the LLM can request water, but Python decides if the pump actually runs.
    """

    decision = parse_agent_output(llm_output)

    emotion = decision["emotion"]
    action = decision["action"]
    message = decision["message"]
    permission_status = decision["permission_status"]

    if action == "WATER":
        if allow_actions and permission_status == "approved":
            arduino.write(b"WATER\n")
            time.sleep(0.1)
            print("\nPump command approved and sent to Arduino.")
        else:
            print("\nBlocked WATER action because permission was not approved by Python.")

    arduino_message = f"{emotion}|{message}"

    arduino.write((arduino_message + "\n").encode("utf-8"))

    print("\nSent to Arduino:")
    print(arduino_message)

    return decision