# (Experimental) LLama Stack UI

## Docker Setup

:warning: This is a work in progress.

## Developer Setup

1. Start up Llama Stack API server. More details [here](https://llama-stack.readthedocs.io/en/latest/getting_started/index.html).

```
llama stack build --template together --image-type conda

llama stack run together
```

2. (Optional) Register datasets and eval tasks as resources. If you want to run pre-configured evaluation flows (e.g. Evaluations (Generation + Scoring) Page).

```bash
$ llama-stack-client datasets register \
--dataset-id "mmlu" \
--provider-id "huggingface" \
--url "https://huggingface.co/datasets/llamastack/evals" \
--metadata '{"path": "llamastack/evals", "name": "evals__mmlu__details", "split": "train"}' \
--schema '{"input_query": {"type": "string"}, "expected_answer": {"type": "string", "chat_completion_input": {"type": "string"}}}'
```

```bash
$ llama-stack-client eval_tasks register \
--eval-task-id meta-reference-mmlu \
--provider-id meta-reference \
--dataset-id mmlu \
--scoring-functions basic::regex_parser_multiple_choice_answer
```

3. Start Streamlit UI

```bash
cd llama_stack/distribution/ui
pip install -r requirements.txt
streamlit run app.py
```
