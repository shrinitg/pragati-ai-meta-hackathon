# NVIDIA Distribution

The `llamastack/distribution-nvidia` distribution consists of the following provider configurations.

| API | Provider(s) |
|-----|-------------|
| agents | `inline::meta-reference` |
| datasetio | `remote::huggingface`, `inline::localfs` |
| eval | `inline::meta-reference` |
| inference | `remote::nvidia` |
| safety | `inline::llama-guard` |
| scoring | `inline::basic`, `inline::llm-as-judge`, `inline::braintrust` |
| telemetry | `inline::meta-reference` |
| tool_runtime | `remote::brave-search`, `remote::tavily-search`, `inline::code-interpreter`, `inline::rag-runtime`, `remote::model-context-protocol` |
| vector_io | `inline::faiss` |


### Environment Variables

The following environment variables can be configured:

- `LLAMASTACK_PORT`: Port for the Llama Stack distribution server (default: `5001`)
- `NVIDIA_API_KEY`: NVIDIA API Key (default: ``)

### Models

The following models are available by default:

- `meta-llama/Llama-3-8B-Instruct (meta/llama3-8b-instruct)`
- `meta-llama/Llama-3-70B-Instruct (meta/llama3-70b-instruct)`
- `meta-llama/Llama-3.1-8B-Instruct (meta/llama-3.1-8b-instruct)`
- `meta-llama/Llama-3.1-70B-Instruct (meta/llama-3.1-70b-instruct)`
- `meta-llama/Llama-3.1-405B-Instruct-FP8 (meta/llama-3.1-405b-instruct)`
- `meta-llama/Llama-3.2-1B-Instruct (meta/llama-3.2-1b-instruct)`
- `meta-llama/Llama-3.2-3B-Instruct (meta/llama-3.2-3b-instruct)`
- `meta-llama/Llama-3.2-11B-Vision-Instruct (meta/llama-3.2-11b-vision-instruct)`
- `meta-llama/Llama-3.2-90B-Vision-Instruct (meta/llama-3.2-90b-vision-instruct)`


### Prerequisite: API Keys

Make sure you have access to a NVIDIA API Key. You can get one by visiting [https://build.nvidia.com/](https://build.nvidia.com/).


## Running Llama Stack with NVIDIA

You can do this via Conda (build code) or Docker which has a pre-built image.

### Via Docker

This method allows you to get started quickly without having to build the distribution code.

```bash
LLAMA_STACK_PORT=5001
docker run \
  -it \
  -p $LLAMA_STACK_PORT:$LLAMA_STACK_PORT \
  -v ./run.yaml:/root/my-run.yaml \
  llamastack/distribution-nvidia \
  --yaml-config /root/my-run.yaml \
  --port $LLAMA_STACK_PORT \
  --env NVIDIA_API_KEY=$NVIDIA_API_KEY
```

### Via Conda

```bash
llama stack build --template nvidia --image-type conda
llama stack run ./run.yaml \
  --port 5001 \
  --env NVIDIA_API_KEY=$NVIDIA_API_KEY
  --env INFERENCE_MODEL=$INFERENCE_MODEL
```
