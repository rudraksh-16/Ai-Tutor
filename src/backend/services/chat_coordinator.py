import json
import logging
from typing import AsyncGenerator, Callable, Dict, Any, Optional, Awaitable
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from src.backend.db.database import SessionLocal

logger = logging.getLogger(__name__)


class ChatCoordinator:
    """Orchestrates the lifecycle of an agent stream: setup, streaming, and persistence."""

    @staticmethod
    async def create_streaming_response(
        conversation_id: Any,
        agent_stream: AsyncGenerator[Dict[str, Any], None],
        save_func: Callable[[AsyncSession, Any, Dict[str, Any]], Awaitable[None]],
        final_payload_callback: Optional[Callable[[Dict[str, Any]], AsyncGenerator[str, None]]] = None
    ) -> StreamingResponse:
        """Creates a FastAPI StreamingResponse for an agent SSE stream."""
        collected_final = {}

        async def streaming_wrapper():
            # 1. Main SSE Event Loop
            async for chunk in ChatCoordinator._stream_agent_events(agent_stream, collected_final):
                yield chunk

            # 2. Results Persistence
            if collected_final:
                await ChatCoordinator._finalize_and_persist(conversation_id, collected_final, save_func)

                # 3. Post-completion logic (e.g., triggering background tasks)
                if final_payload_callback:
                    async for extra_event in ChatCoordinator._run_post_processing(final_payload_callback, collected_final):
                        yield extra_event

        return StreamingResponse(streaming_wrapper(), media_type="text/event-stream")

    @staticmethod
    async def _stream_agent_events(stream: AsyncGenerator, final_data: dict) -> AsyncGenerator[str, None]:
        """Iterates through agent events, formatting for SSE and capturing final data."""
        try:
            async for event in stream:
                if event.get("type") == "final":
                    final_data.update(event.get("data", {}))
                yield f"data: {json.dumps(event)}\n\n"
        except Exception as e:
            logger.exception("Error during agent streaming")
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    @staticmethod
    async def _finalize_and_persist(conv_id: Any, data: dict, save_fn: Callable) -> None:
        """Saves the final agent output to the database."""
        try:
            async with SessionLocal() as db:
                await save_fn(db, conv_id, data)
        except Exception as e:
            logger.error("Failed to save final stream results for %s: %s", conv_id, e)

    @staticmethod
    async def _run_post_processing(callback: Callable, data: dict) -> AsyncGenerator[str, None]:
        """Executes optional post-completion logic and yields any resulting SSE events."""
        try:
            async for extra_event in callback(data):
                yield extra_event
        except Exception as e:
            logger.error("Error in final payload callback: %s", e)
