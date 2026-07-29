# AI-Plant-Monitoring-System



A local AI plant-care system that combines an Arduino, environmental sensors, retrieval-augmented generation, a local language model, and machine-learning-based plant health prediction.

The plant can describe how it feels, answer questions using plant-specific care documentation, evaluate live sensor readings, request permission to water itself, and activate a water pump only after passing Python-side safety checks.

Features
*Reads temperature, humidity, soil moisture, and light levels from an Arduino
*Communicates with a locally hosted LLM through LM Studio
*Retrieves plant-care information from PDF documents using ChromaDB
*Generates embeddings with Sentence Transformers
*Speaks in first person as the monitored plant
*Displays different emotional states on the Arduino
*Requests permission before automatically suggested watering
*Accepts direct user watering commands
*Uses Python guardrails before activating the pump
*Runs a machine-learning model to predict plant health
*Provides a simple Tkinter conversation window
*Performs periodic automatic sensor evaluations


System Overview
Plant-care PDF
      |
      v
PDF extraction and chunking
      |
      v
Sentence Transformer embeddings
      |
      v
ChromaDB vector database
      |
      +------------------------------+
                                     |
User message                        |
      |                              |
      v                              v
Python application ----------> Relevant PDF context
      |                              |
      +--------------+---------------+
                     |
                     v
              Local LLM server
                LM Studio
                     |
                     v
             Structured JSON response
                     |
                     v
          Python validation and guardrails
                     |
          +----------+-----------+
          |                      |
          v                      v
 Arduino display/message     Water pump command
                             only when authorized