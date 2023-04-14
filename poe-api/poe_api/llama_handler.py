"""

Demo bot: catbot.

"""
from __future__ import annotations

import os
from typing import AsyncIterable, List, Optional, Sequence, Type

from sse_starlette.sse import ServerSentEvent

from llama_index import IndexStructType
from llama_index.indices.base import BaseGPTIndex
from llama_index.indices.response.builder import ResponseMode
from llama_index.indices.registry import INDEX_STRUCT_TYPE_TO_INDEX_CLASS
from llama_index import Document as LlamaDocument

from poe_api.base_handler import PoeHandler
from poe_api.types import (
    ContentType,
    Document,
    QueryRequest,
    ReportFeedbackRequest,
    SettingsRequest,
    SettingsResponse,
    AddDocumentsRequest,
)

INDEX_STRUCT_TYPE_STR = os.environ.get('LLAMA_INDEX_TYPE', IndexStructType.SIMPLE_DICT.value)
INDEX_JSON_PATH = os.environ.get('LLAMA_INDEX_JSON_PATH', None)
QUERY_KWARGS_JSON_PATH = os.environ.get('LLAMA_QUERY_KWARGS_JSON_PATH', None)
RESPONSE_MODE = os.environ.get('LLAMA_RESPONSE_MODE', ResponseMode.NO_TEXT.value)


EXTERNAL_VECTOR_STORE_INDEX_STRUCT_TYPES = [
    IndexStructType.DICT,
    IndexStructType.WEAVIATE,
    IndexStructType.PINECONE,
    IndexStructType.QDRANT,
    IndexStructType.CHROMA,
    IndexStructType.VECTOR_STORE,
]

SETTINGS = SettingsResponse(
    context_clear_window_secs=60 * 60, allow_user_context_clear=True
)

SAVE_PATH = './index.json'


def _to_llama_documents(docs: Sequence[Document]) -> List[LlamaDocument]:
    return [LlamaDocument(text=doc.text, doc_id=doc.doc_id) for doc in docs]


def _create_or_load_index(
    index_type_str: Optional[str] = None,
    index_json_path: Optional[str] = None,
    index_type_to_index_cls: Optional[dict[str, Type[BaseGPTIndex]]] = None,
) -> BaseGPTIndex:
    """Create or load index from json path."""
    index_json_path = index_json_path or INDEX_JSON_PATH
    index_type_to_index_cls = index_type_to_index_cls or INDEX_STRUCT_TYPE_TO_INDEX_CLASS
    index_type_str = index_type_str or INDEX_STRUCT_TYPE_STR
    index_type = IndexStructType(index_type_str)

    if index_type not in index_type_to_index_cls:
        raise ValueError(f'Unknown index type: {index_type}')

    # TODO: support this
    if index_type in EXTERNAL_VECTOR_STORE_INDEX_STRUCT_TYPES:
        raise ValueError('Please use vector store directly.')

    index_cls = index_type_to_index_cls[index_type]
    if index_json_path is None:
        return index_cls(nodes=[])  # Create empty index
    else:
        return index_cls.load_from_disk(index_json_path) # Load index from disk


class LlamaBotHandler(PoeHandler):
    def __init__(self) -> None:
        """Setup LlamaIndex."""
        self._index = _create_or_load_index()

    async def get_response(self, query: QueryRequest) -> AsyncIterable[ServerSentEvent]:
        """Return an async iterator of events to send to the user."""

        last_message = query.query[-1]
        message_content = last_message.content
        response = self._index.query(message_content)
        yield self.text_event(response.response)


    async def on_feedback(self, feedback: ReportFeedbackRequest) -> None:
        """Called when we receive user feedback such as likes."""
        print(
            f"User {feedback.user_id} gave feedback on {feedback.conversation_id}"
            f"message {feedback.message_id}: {feedback.feedback_type}"
        )

    async def get_settings(self, settings: SettingsRequest) -> SettingsResponse:
        """Return the settings for this bot."""
        return SETTINGS

    async def add_documents(self, request: AddDocumentsRequest) -> SettingsResponse:
        """Add documents."""
        llama_docs = _to_llama_documents(request.documents)
        nodes = self._index.service_context.node_parser.get_nodes_from_documents(llama_docs)
        self._index.insert_nodes(nodes)
    
    def shutdown(self) -> None:
        self._index.save_to_dict(SAVE_PATH)


    