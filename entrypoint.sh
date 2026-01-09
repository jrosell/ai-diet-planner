#!/bin/bash

# Start Ollama in the background
ollama serve &

# Wait for Ollama to start (it usually takes a few seconds)
sleep 5

# Pull the model you need (e.g., llama3) 
# Note: This increases startup time. Better to bake it into the image if possible.
ollama pull llama3

# Start the Streamlit app
uv run streamlit run app.py --server.port=8080 --server.address=0.0.0.0