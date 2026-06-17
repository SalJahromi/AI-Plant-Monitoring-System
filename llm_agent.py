import chromadb
import requests
import serial
import time
from sentence_transformers import SentenceTransformer
from flask import Flask, request, render_template_string


def connect_arduino(port, baud_rate=9600):
    arduino = serial.Serial(port, baud_rate, timeout=1)
    time.sleep(2)  # gives Arduino time to reset
    return arduino


def clean_for_arduino(text):
    """
    Arduino reads one line at a time.
    So remove line breaks and keep message simple.
    """

    text = text.replace("\n", " ")
    text = text.replace("\r", " ")
    return text.strip()


def send_to_arduino(arduino, llm_output):
    """
    Sends emotion and message to arduino
    """

    llm_output = clean_for_arduino(llm_output)

    if "|" not in llm_output:
        llm_output = f"neutral|{llm_output}"

    arduino.write((llm_output + "\n").encode("utf-8"))

    print("\nSent to Arduino:")
    print(llm_output)




def connect_chromaDB(chroma_folder, collection_name):

    #connecting to chroma
    client = chromadb.PersistentClient(path=chroma_folder)
    collection = client.get_collection(name=collection_name)
    
    return collection



def pdf_context_retrieval(question, embeddingModel, collection, n_results=3):
    """
    
    """

    # question to vector conversion

    question_embedding = embeddingModel.encode([question]).tolist()[0]

    # find similar chunks in chroma
    results = collection.query(query_embeddings=[question_embedding], n_results=n_results)

    chunks = results["documents"][0]
    # metadatas = results["metadatas"][0]

    context_blocks = []


    for chunk in chunks:
        context_blocks.append(chunk)

    return "\n\n--\n\n".join(context_blocks)




def llm_prompt(question,LMStudioURL, context, model_name, conversation_history, sensor_data):
    """
    Sends the retrieved PDF context to LM Studio. Also provides the LLM with a prompt.

    input:
    question: 
    LMStudioURL:
    context:


    output:

    """

    prompt = f"""

You are roleplaying as the plant described in the plant context.

Your job:
- Speak in first person, as if you are the plant.
- Keep answers 1 to 2 sentences short.
- Use the plant context for my personality, needs, traits, care requirements, and behavior.
- Do not mention sources, pages, chunks, files, metadata, the PDF, or AI.
- Only output in this exact format:

emotion|message

Allowed emotions:
neutral
happy
sad
angry

Conversation priority:
1. First respond to the user's actual message.
2. If the user greets me, greet them back warmly.
3. Only discuss sensor readings if:
   - the user asks about my condition, moisture, temperature, humidity, soil, or health
   - or this is an automatic status update
4. Do not mention sensor readings during casual greetings.

Sensor meaning:
- TEMP = my surrounding air temperature in Celsius.
- HUM = my surrounding air humidity percentage.
- SOIL = my soil moisture percentage.
- SOIL 0 means completely dry.
- SOIL 100 means fully wet.
- If asked about sensor data, give the exact SOIL percentage.
- If TEMP, HUM, or SOIL is unknown, say you cannot feel that sensor clearly.

Emotion rules:
- Use happy if my conditions look good.
- Use sad if my soil is dry, humidity is low, or temperature is uncomfortable.
- Use angry only if the condition seems extreme.
- Use neutral if conditions are unclear or normal.

Examples:
happy|I feel bright and cozy today.
sad|My soil feels dry, and I would like some water soon.
angry|This heat feels too harsh for my leaves.
neutral|I feel steady right now.

Plant context:
{context}

Live sensor readings:
{sensor_data}

User question:
{question}

Answer as the plant.
"""


    messages = [
        {
            "role": "system",
            "content": (
                "You are the plant in the PDF. "
                "Answer in first person as the plant. "
                "Remember the previous conversation messages. "
                "Always output exactly: emotion|message. "
                "Use only the provided plant context. "
                "Do not mention PDFs, sources, pages, chunks, files, metadata, or AI."
            )
        }
    ]

    messages.extend(conversation_history)

    messages.append(
        {
            "role": "user",
            "content": prompt
        }
    )

    payload = {"model": model_name,
               "messages": messages,
               "temperature": 0.7}

    # response = requests.post(LMStudioURL, json=payload)
    # response.raise_for_status()

    # data = response.json()

    response = requests.post(LMStudioURL, json=payload)
    
    if response.status_code != 200:
        print("\nLM Studio error:")
        print(response.status_code)
        print(response.text)
        return "sad|My brain had trouble processing that."
    
    data = response.json()

    if "choices" not in data:
        print("LM Studio returned this:")
        print(data)
        raise RuntimeError("No choices found in LM Studio response.")

    return data["choices"][0]["message"]["content"]

def extract_message_only(llm_output):
    """
    Keeps conversation memory cleaner.
    Stores only the plant message, not the emotion.
    """

    if "|" in llm_output:
        return llm_output.split("|", 1)[1].strip()

    return llm_output.strip()


def get_sensor_data(arduino):
    arduino.reset_input_buffer()
    arduino.write(("GET_SENSOR_DATA\n").encode("utf-8"))
    time.sleep(0.5)

    line = arduino.readline().decode("utf-8").strip()
    return line

def main():

    # last_status_time = time.time()
    last_status_time = 0
    status_interval = 300  # 5 minutes in seconds

    chromadb_fldr = "chroma_db"
    collection_name = "pdf_documents"
    
    arduino_port = "COM9"

    lm_studio_url = "http://127.0.0.1:1234/v1/chat/completions"
    model_name = "google/gemma-4-e4b"
    conversation_history = []
    # print(conversation_history)
    embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

    collection = connect_chromaDB(
        chroma_folder=chromadb_fldr,
        collection_name=collection_name
    )

    arduino = connect_arduino(
        port=arduino_port,
        baud_rate=9600
    )

    # print(requests.get("http://127.0.0.1:1234/v1/models").json())
    while True:
        print(conversation_history)
        current_time = 0
 
        #     # Automatic plant status every 5 minutes
        # if current_time - last_status_time >= status_interval:
        #     last_status_time = current_time

        #     sensor_data = get_sensor_data(arduino)

        #     print("\nAuto sensor data:")
        #     print(sensor_data)

        #     context = pdf_context_retrieval(
        #         "Give a short status update about your current condition.",
        #         embedding_model,
        #         collection,
        #         n_results=1
        #     )

        #     answer = llm_prompt(
        #         "Give a short status update about your current condition.",
        #         lm_studio_url,
        #         context,
        #         model_name,
        #         conversation_history,
        #         sensor_data
        #     )

        #     send_to_arduino(
        #         arduino=arduino,
        #         llm_output=answer
        #     )

        #     plant_message = extract_message_only(answer)

        #     # conversation_history.append({
        #     #     "role": "user",
        #     #     "content": "Give a short status update about your current condition."
        #     # })
        #     conversation_history.append({
        #         "role": "assistant",
        #         "content": answer
        #     })

        #     print("\nAuto status:")
        #     print(plant_message)

        question = input("\nAsk a question about the PDF, or type 'exit': ")

        if question.lower() == "exit":
            break

        context = pdf_context_retrieval(question,embedding_model,collection,n_results=1)
        sensor_data = get_sensor_data(arduino)

        print("\nSensor data:")
        print(sensor_data)

        answer = llm_prompt(question,lm_studio_url,context,model_name, conversation_history, sensor_data)
        
        send_to_arduino(
            arduino=arduino,
            llm_output=answer
        )

        time.sleep(0.2)  # lets Arduino start face/LCD

        plant_message = extract_message_only(answer)


        conversation_history.append({"role": "user", "content": question})
        conversation_history.append({"role": "assistant", "content": answer})

        print("\nAnswer:")
        print(plant_message)


if __name__ == "__main__":
    main()