# Poe Knowledge Bot with LlamaIndex

A knowledge-augmented Poe bot powered by 
[LlamaIndex](https://gpt-index.readthedocs.io/en/latest/)
and FastAPI.

Easily ingest and chat with your own data as a knowledge base!

## Quick Start

Follow these steps to quickly setup and run the LlamaIndex bot for Poe:
### Setup Environment
1. Install poetry: `pip install poetry`
2. Install app dependencies: `poetry install`
3. Setup environment variables

| Name             | Required | Description                                                                                                                                                                                |
| ---------------- | -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `POE_API_KEY`   | Yes      | This is a secret token that you need to authenticate Poe requests to the API. You can generate this from https://poe.com/create_bot?api=1.                |
| `OPENAI_API_KEY` | Yes      | This is your OpenAI API key that LlamaIndex needs to call OpenAI services. You can get an API key by creating an account on [OpenAI](https://openai.com/). |

### Run API Server
* Run the API locally: `poetry run start`
* Make the API publicly available with [ngrok](https://ngrok.com/): in a different terminal, run `ngrok http 8080`

### Connect Poe to your Bot
* Create your bot at https://poe.com/create_bot?api=1
* Interact with your bot at https://poe.com/

## Customize Your LlamaIndex Poe Bot
By default, we ingest documents under `data/` and index them with a `GPTSimpleVectorIndex`.
> Read more about different index types [here](https://gpt-index.readthedocs.io/en/latest/guides/primer/index_guide.html)

You can configure the default behavior via environment variables:

| Name             | Required | Description                                                                                                                                                                                |
| ---------------- | -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `LLAMA_LOAD_DATA`   | Optional      | Whether to ingest documents in `DATA_DIR`.Defaults to `True`                |
| `LLAMA_DATA_DIR` | Optional      | Directory to ingest initial documents from. Defaults to `data/` |
| `LLAMA_INDEX_TYPE` | Optional      | Index type (see below for details). Defaults to `simple_dict`  |
| `INDEX_JSON_PATH` | Optional      |  Path to saved Index json file. `save/index.json`|

**Different Index Types**
By default, we use a `GPTSimpleVectorIndex` to store document chunks in memory, 
and retrieve top-k nodes by embedding similarity.
Different index types are optimized for different data and query use-cases.
See this guide on [How Each Index Works](https://gpt-index.readthedocs.io/en/latest/guides/primer/index_guide.html) to learn more.
You can configure the index type via the `LLAMA_INDEX_TYPE`, see [here](https://gpt-index.readthedocs.io/en/latest/reference/indices/composability_query.html#gpt_index.data_structs.struct_type.IndexStructType) for the full list of accepted index type identifiers.


Read more details on [readthedocs](https://gpt-index.readthedocs.io/en/latest/), 
and engage with the community on [discord](https://discord.com/invite/dGcwcsnxhU).

## Ingesting Data
LlamaIndex bot for Poe also exposes an API for ingesting additional data by `POST` to `/add_document` endpoint.
