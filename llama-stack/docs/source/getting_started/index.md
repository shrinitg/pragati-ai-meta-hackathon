# Quick Start

In this guide, we'll walk through how you can use the Llama Stack (server and client SDK ) to test a simple RAG agent.

A Llama Stack agent is a simple integrated system that can perform tasks by combining a Llama model for reasoning with tools (e.g., RAG, web search, code execution, etc.) for taking actions.

In Llama Stack, we provide a server exposing multiple APIs. These APIs are backed by implementations from different providers. For this guide, we will use [Ollama](https://ollama.com/) as the inference provider.


### 1. Start Ollama

```bash
ollama run llama3.2:3b-instruct-fp16 --keepalive 60m
```

By default, Ollama keeps the model loaded in memory for 5 minutes which can be too short. We set the `--keepalive` flag to 60 minutes to ensure the model remains loaded for sometime.

NOTE: If you do not have ollama, you can install it from [here](https://ollama.ai/docs/installation).



### 2. Pick a client environment

Llama Stack has a service-oriented architecture, so every interaction with the Stack happens through an REST interface. You can interact with the Stack in two ways:

* Install the `llama-stack-client` PyPI package and point `LlamaStackClient` to a local or remote Llama Stack server.
* Or, install the `llama-stack` PyPI package and use the Stack as a library using `LlamaStackAsLibraryClient`.

```{admonition} Note
:class: tip

The API is **exactly identical** for both clients.
```

:::{dropdown} Starting up the Llama Stack server
The Llama Stack server can be configured flexibly so you can mix-and-match various providers for its individual API components -- beyond Inference, these include Vector IO, Agents, Telemetry, Evals, Post Training, etc.

To get started quickly, we provide various Docker images for the server component that work with different inference providers out of the box. For this guide, we will use `llamastack/distribution-ollama` as the Docker image.

Lets setup some environment variables that we will use in the rest of the guide.
```bash
INFERENCE_MODEL="meta-llama/Llama-3.2-3B-Instruct"
LLAMA_STACK_PORT=8321
```

You can start the server using the following command:
```bash
docker run -it \
  -p $LLAMA_STACK_PORT:$LLAMA_STACK_PORT \
  -v ~/.llama:/root/.llama \
  llamastack/distribution-ollama \
  --port $LLAMA_STACK_PORT \
  --env INFERENCE_MODEL=$INFERENCE_MODEL \
  --env OLLAMA_URL=http://host.docker.internal:11434
```
Configuration for this is available at `distributions/ollama/run.yaml`.

:::


:::{dropdown} Installing the Llama Stack client CLI and SDK

You can interact with the Llama Stack server using various client SDKs. We will use the Python SDK which you can install using the following command. Note that you must be using Python 3.10 or newer:
```bash
yes | conda create -n stack-client python=3.10
conda activate stack-client

pip install llama-stack-client
```

Let's use the `llama-stack-client` CLI to check the connectivity to the server.

```bash
llama-stack-client configure --endpoint http://localhost:$LLAMA_STACK_PORT
llama-stack-client models list
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━┓
┃ identifier                       ┃ provider_id ┃ provider_resource_id      ┃ metadata ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━┩
│ meta-llama/Llama-3.2-3B-Instruct │ ollama      │ llama3.2:3b-instruct-fp16 │          │
└──────────────────────────────────┴─────────────┴───────────────────────────┴──────────┘
```

You can test basic Llama inference completion using the CLI too.
```bash
llama-stack-client \
  inference chat-completion \
  --message "hello, what model are you?"
```
:::

&nbsp;

### 3. Run inference with Python SDK

Here is a simple example to perform chat completions using the SDK.
```python
import os

def create_http_client():
    from llama_stack_client import LlamaStackClient
    return LlamaStackClient(base_url=f"http://localhost:{os.environ['LLAMA_STACK_PORT']}")

def create_library_client(template="ollama"):
    from llama_stack import LlamaStackAsLibraryClient
    client = LlamaStackAsLibraryClient(template)
    client.initialize()
    return client


client = create_library_client()  # or create_http_client() depending on the environment you picked

# List available models
models = client.models.list()
print("--- Available models: ---")
for m in models:
    print(f"- {m.identifier}")
print()

response = client.inference.chat_completion(
    model_id=os.environ["INFERENCE_MODEL"],
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Write a haiku about coding"}
    ]
)
print(response.completion_message.content)
```

### 4. Your first RAG agent

Here is an example of a simple RAG (Retrieval Augmented Generation) chatbot agent which can answer questions about TorchTune documentation.

```python
import os
from termcolor import cprint

from llama_stack_client.lib.agents.agent import Agent
from llama_stack_client.lib.agents.event_logger import EventLogger
from llama_stack_client.types.agent_create_params import AgentConfig
from llama_stack_client.types import Document

client = create_library_client()  # or create_http_client() depending on the environment you picked

# Documents to be used for RAG
urls = ["chat.rst", "llama3.rst", "datasets.rst", "lora_finetune.rst"]
documents = [
    Document(
        document_id=f"num-{i}",
        content=f"https://raw.githubusercontent.com/pytorch/torchtune/main/docs/source/tutorials/{url}",
        mime_type="text/plain",
        metadata={},
    )
    for i, url in enumerate(urls)
]

# Register a vector database
vector_db_id = "test-vector-db"
client.vector_dbs.register(
    vector_db_id=vector_db_id,
    embedding_model="all-MiniLM-L6-v2",
    embedding_dimension=384,
)

# Insert the documents into the vector database
client.tool_runtime.rag_tool.insert(
    documents=documents,
    vector_db_id=vector_db_id,
    chunk_size_in_tokens=512,
)

agent_config = AgentConfig(
    model=os.environ["INFERENCE_MODEL"],
    # Define instructions for the agent ( aka system prompt)
    instructions="You are a helpful assistant",
    enable_session_persistence=False,
    # Define tools available to the agent
    toolgroups = [
        {
          "name": "builtin::rag",
          "args" : {
            "vector_db_ids": [vector_db_id],
          }
        }
    ],
)

rag_agent = Agent(client, agent_config)
session_id = rag_agent.create_session("test-session")

user_prompts = [
    "What are the top 5 topics that were explained? Only list succinct bullet points.",
]

# Run the agent loop by calling the `create_turn` method
for prompt in user_prompts:
    cprint(f'User> {prompt}', 'green')
    response = rag_agent.create_turn(
        messages=[{"role": "user", "content": prompt}],
        session_id=session_id,
    )
    for log in EventLogger().log(response):
        log.print()
```

## Next Steps

- Learn more about Llama Stack [Concepts](../concepts/index.md)
- Learn how to [Build Llama Stacks](../distributions/index.md)
- See [References](../references/index.md) for more details about the llama CLI and Python SDK
- For example applications and more detailed tutorials, visit our [llama-stack-apps](https://github.com/meta-llama/llama-stack-apps/tree/main/examples) repository.
