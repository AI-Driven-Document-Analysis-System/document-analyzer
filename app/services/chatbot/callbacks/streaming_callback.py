from langchain.callbacks.base import BaseCallbackHandler
from langchain.schema import LLMResult
from typing import Any, Dict, List, Optional
import asyncio
import json


class StreamingCallbackHandler(BaseCallbackHandler):
    def __init__(self, websocket=None, client_id: str = None):
        self.websocket = websocket
        self.client_id = client_id
        self.tokens = []

    def on_llm_new_token(self, token: str, **kwargs: Any) -> None:
        self.tokens.append(token)
        if self.websocket and self.client_id:
            asyncio.create_task(self._send_token(token))

    async def _send_token(self, token: str):
        if self.websocket:
            await self.websocket.send_text(json.dumps({
                'type': 'token',
                'data': token,
                'client_id': self.client_id
            }))

    def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        full_response = "".join(self.tokens)
        if self.websocket and self.client_id:
            asyncio.create_task(self._send_complete(full_response))

    async def _send_complete(self, response: str):
        if self.websocket:
            await self.websocket.send_text(json.dumps({
                'type': 'complete',
                'data': response,
                'client_id': self.client_id
            }))


class AsyncStreamingCallbackHandler(BaseCallbackHandler):
    def __init__(self):
        self.tokens = []
        self.token_queue = asyncio.Queue()

    def on_llm_new_token(self, token: str, **kwargs: Any) -> None:
        self.tokens.append(token)
        asyncio.create_task(self.token_queue.put(token))

    def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        asyncio.create_task(self.token_queue.put(None))

    async def get_tokens(self):
        while True:
            token = await self.token_queue.get()
            if token is None:
                break
            yield token