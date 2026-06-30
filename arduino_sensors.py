import time
from llm_agent import automatic_sensor_evaluation

def get_sensor_data(arduino):
    """
    Retrieves sensor data from arduino. 
    - DHT11: temperature and humidity. (TEMP, HUM)
    - Capacitive Soil Moisture: soil moisture reading. (SOIL)
    - Photoresistor: Light intensity (LUM)

    Output:
    All sensor readings in one line.
    """
    arduino.reset_input_buffer()
    arduino.write(("GET_SENSOR_DATA\n").encode("utf-8"))
    time.sleep(0.5)

    line = arduino.readline().decode("utf-8").strip()
    return line


# def get_sensor_data_dict(sensor_data):
#     """
#     Retrieves sensor data from arduino. 
#     - DHT11: temperature and humidity. (TEMP, HUM)
#     - Capacitive Soil Moisture: soil moisture reading. (SOIL)
#     - Photoresistor: Light intensity (LUM)

#     output: dictionary of sensor readings.
#     """
#     readings = {}

#     try:
#         parts = sensor_data.split(",")

#         for part in parts:
#             key, value = part.split(":")
#             readings[key.strip()] = float(value.strip())

#     except Exception:
#         return None

#     return readings


def activate_pump(arduino):
    """
    Sends "WATER" to arduino, commanding the program to activate the water pump.
    """
    arduino.write(("WATER\n").encode("utf-8"))
    print("\nPump command sent to Arduino.")





def automatic_sensor_loop(
    conversation_history,
    embedding_model,
    collection,
    arduino,
    lm_studio_url,
    model_name,
    interval,
    pending_action
):
    """
    At every loop, sensor information is sent to the LLM for evaluation.

    Important:
    The automatic loop can ask for permission, but it cannot activate the pump.
    """

    while True:
        time.sleep(interval)

        automatic_sensor_evaluation(
            conversation_history=conversation_history,
            embedding_model=embedding_model,
            collection=collection,
            arduino=arduino,
            lm_studio_url=lm_studio_url,
            model_name=model_name,
            pending_action=pending_action
        )