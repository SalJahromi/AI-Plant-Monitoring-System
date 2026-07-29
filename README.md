# AI-Plant-Monitoring-System


# 🌱 AI Smart Plant Agent

This is a personal passion project.

An AI-powered smart plant monitoring system that combines **Arduino**, **local LLMs (LM Studio)**, **Retrieval-Augmented Generation (RAG)**, and **Machine Learning** to create an AI plant agent with access to sensor data, being able to monitor its environment, converse naturally, diagnose its health, and safely control its own irrigation.

In simple terms, the program receives a pdf holding information about a particular plant. Then, the AI agent pretends to be that plant, mimicing emotions, and "feeling" its own conditions by accessing real-time sensor readings.

The project demonstrates the integration of embedded systems with modern AI.

---

## Features

- 🌡️ Reads live sensor data from an Arduino
  - Temperature
  - Humidity
  - Soil moisture
  - Light intensity

- 🤖 Local AI assistant powered by LM Studio
  - Natural conversations
  - Plant roleplaying
  - Context-aware responses

- 📚 Retrieval-Augmented Generation (RAG)
  - Reads plant-care PDF documents
  - Stores embeddings in ChromaDB
  - Retrieves relevant context before every response

- 🧠 Machine Learning integration
  - Predicts plant health from live sensor readings
  - LLM explains ML predictions naturally

- 💧 Safe autonomous watering
  - Plant can request permission to water itself
  - Python validates every watering request
  - Automatic sensor updates **cannot** activate the pump without approval

- 😊 Emotional plant responses
  - Happy
  - Neutral
  - Sad
  - Angry

- 💬 Live chat interface
  - Tkinter conversation window
  - Conversation memory

---