---
title: AI Diet Planner
emoji: 🥗
colorFrom: green
colorTo: blue
sdk: docker
app_file: app.py
pinned: false
---
## Build and Deploy an AI-Powered Diet Planner with Streamlit, Ollama and Duckdb.

In this repo you'll see how to build and deploy an AI-Powered Diet Planner. For UI using Streamlit, LLM model using Ollama, Duckdb for store data and docker container deployment.

Through the codelab, you will employ a step by step approach as follows:

* Prepare your project.
* Build genAI Diet Planner using streamlit, Ollama and Duckdb
* Deploy the application using a docker contaner

It's based on the codelab "Build and Deploy an AI-Powered Agent Diet Planner with Streamlit, Gemini Pro, Vertex AI and BigQuery" by Muhammad Saipul Rohman, Alvin Prayuda Juniarta Dwiyantoro.

### Installation

```
uv init
uv add streamlit pandas pyarrow  duckdb ollama python-dotenv
source .venv/bin/activate
streamlit run app.py
```

### Deploy

```
docker build -t streamlit-ollama .
docker run --rm --gpus all -p 8080:8080 -p 11434:11434 streamlit-ollama
```

### Troubleshooting

```
docker run -it --entrypoint bash my-streamlit-app
```

Then inside the container:

```
uv run streamlit run app.py
```