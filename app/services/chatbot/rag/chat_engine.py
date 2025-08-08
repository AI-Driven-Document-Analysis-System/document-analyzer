from langchain.schema import HumanMessage, AIMessage
from backend.chains.conversational_chain import CustomConversationalChain
from backend.callbacks.streaming_callback import AsyncStreamingCallbackHandler
from typing import Dict, Any, Optional, AsyncGenerator
import uuid
import json


class LangChainChatEngine:
    def __init__(self, conversational_chain: CustomConversationalChain):
        self.chain = conversational_chain
        self.conversations = {}

    async def process_query(self, query: str, conversation_id: Optional[str] = None,
                            user_id: Optional[str] = None) -> Dict[str, Any]:
        if not conversation_id:
            conversation_id = str(uuid.uuid4())

        try:
            result = await self.chain.arun(query)

            sources = []
            for doc in result["source_documents"]:
                sources.append({
                    'content': doc.page_content[:200] + "...",
                    'metadata': doc.metadata,
                    'score': doc.metadata.get('score', 0)
                })

            return {
                'conversation_id': conversation_id,
                'response': result["answer"],
                'sources': sources,
                'chat_history': [msg.dict() for msg in result["chat_history"]]
            }

        except Exception as e:
            raise Exception(f"Error processing query: {str(e)}")

    async def process_streaming_query(self, query: str,
                                      conversation_id: Optional[str] = None) -> AsyncGenerator[Dict, None]:
        if not conversation_id:
            conversation_id = str(uuid.uuid4())

        try:
            streaming_callback = AsyncStreamingCallbackHandler()

            task = asyncio.create_task(
                self.chain.arun(query, callbacks=[streaming_callback])
            )

            yield {
                'type': 'start',
                'conversation_id': conversation_id,
                'data': 'Starting response generation...'
            }

            async for token in streaming_callback.get_tokens():
                yield {
                    'type': 'token',
                    'conversation_id': conversation_id,
                    'data': token
                }

            result = await task

            sources = []
            for doc in result["source_documents"]:
                sources.append({
                    'content': doc.page_content[:200] + "...",
                    'metadata': doc.metadata,
                    'score': doc.metadata.get('score', 0)
                })

            yield {
                'type': 'sources',
                'conversation_id': conversation_id,
                'data': sources
            }

            yield {
                'type': 'complete',
                'conversation_id': conversation_id,
                'data': {
                    'response': result["answer"],
                    'sources': sources
                }
            }

        except Exception as e:
            yield {
                'type': 'error',
                'conversation_id': conversation_id,
                'data': str(e)
            }