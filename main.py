import threading

from sentence_transformers import SentenceTransformer

from arduino_interaction import connect_arduino
from vectorization import connect_chromaDB
from arduino_sensors import automatic_sensor_loop
from llm_agent import interact_with_LLM, create_chat_window

def main():

    # Vector databse
    chromadb_fldr = "chroma_db"
    # pdf as source of information for LLM.
    collection_name = "pdf_documents"
    # Arduino USB port
    arduino_port = "COM9"
    # To connect to LM Studio's local LLM server.
    lm_studio_url = "http://127.0.0.1:1234/v1/chat/completions"
    LLM_model_name = "google/gemma-4-e4b"
    
    # List of dictionaries, holding the conversation history between user and LLM.
    conversation_history = []
    # For chat window showing conversation between user and LLM.
    root, text_box = create_chat_window()
    
    vectorization_model = SentenceTransformer("all-MiniLM-L6-v2")

    # Connect to vector databse.
    chromaDB_PDF_chunks = connect_chromaDB(chroma_folder=chromadb_fldr,
                                  collection_name=collection_name)
    # Connect to arduino microcontroller.
    arduino = connect_arduino(port=arduino_port,baud_rate=9600)

    pending_action = {"action": None}

    # Automatic sensor loop
    sensor_thread = threading.Thread(
        target=automatic_sensor_loop,
        args=(conversation_history,vectorization_model,
              chromaDB_PDF_chunks,arduino,lm_studio_url,
              LLM_model_name,1200,pending_action),
        daemon=True
    )
 
    sensor_thread.start()

    # User chat loop
    chat_thread = threading.Thread(
        target=interact_with_LLM,
        args=(conversation_history,vectorization_model,
              chromaDB_PDF_chunks,arduino,lm_studio_url,LLM_model_name,
              text_box,pending_action),
        daemon=True
    )

    chat_thread.start()

    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("Exiting...")

if __name__ == "__main__":
    main()