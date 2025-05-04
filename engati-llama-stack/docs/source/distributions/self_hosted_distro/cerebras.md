# Cerebras Distribution

The `llamastack/distribution-cerebras` distribution consists of the following provider configurations.

| API | Provider(s) |
|-----|-------------|
| agents | `inline::meta-reference` |
| datasetio | `remote::huggingface`, `inline::localfs` |
| eval | `inline::meta-reference` |
| inference | `remote::cerebras` |
| safety | `inline::llama-guard` |
| scoring | `inline::basic`, `inline::llm-as-judge`, `inline::braintrust` |
| telemetry | `inline::meta-reference` |
| tool_runtime | `remote::brave-search`, `remote::tavily-search`, `inline::code-interpreter`, `inline::rag-runtime` |
| vector_io | `inline::faiss`, `remote::chromadb`, `remote::pgvector` |


### Environment Variables

The following environment variables can be configured:

- `LLAMA_STACK_PORT`: Port for the Llama Stack distribution server (default: `5001`)
- `CEREBRAS_API_KEY`: Cerebras API Key (default: ``)

### Models

The following models are available by default:

- `meta-llama/Llama-3.1-8B-Instruct (llama3.1-8b)`
- `meta-llama/Llama-3.3-70B-Instruct (llama-3.3-70b)`


### Prerequisite: API Keys

Make sure you have access to a Cerebras API Key. You can get one by visiting [cloud.cerebras.ai](https://cloud.cerebras.ai/).


## Running Llama Stack with Cerebras

You can do this via Conda (build code) or Docker which has a pre-built image.

### Via Docker

This method allows you to get started quickly without having to build the distribution code.

```bash
LLAMA_STACK_PORT=5001
docker run \
  -it \
  -p $LLAMA_STACK_PORT:$LLAMA_STACK_PORT \
  -v ./run.yaml:/root/my-run.yaml \
  llamastack/distribution-cerebras \
  --yaml-config /root/my-run.yaml \
  --port $LLAMA_STACK_PORT \
  --env CEREBRAS_API_KEY=$CEREBRAS_API_KEY
```

### Via Conda

```bash
llama stack build --template cerebras --image-type conda
llama stack run ./run.yaml \
  --port 5001 \
  --env CEREBRAS_API_KEY=$CEREBRAS_API_KEY
```
