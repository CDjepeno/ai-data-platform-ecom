from __future__ import annotations

import logging

from domain.errors import EmptyStreamError
from domain.ports import  StepCallbackPort
from domain.tools.sse import SseStep, SseToken
from domain.ports.ask_gateway_port import AskGatewayPort

logger = logging.getLogger(__name__)


class AskQuestionUseCase:

    def __init__(
        self,
        gateway: AskGatewayPort,
        callback: StepCallbackPort,
    ) -> None:
        self._gateway = gateway
        self._callback = callback

    async def execute(self, question: str, user_id: str) -> str:
        """
        Execute the use case.

        The gateway yields typed SseLine objects — SseStep, SseToken, SseEmpty.
        No parsing here — that belongs to the adapter layer.

        Args:
            question: Natural language business question.
            user_id:  Caller identifier for audit logging.

        Returns:
            Full assembled LLM answer as a plain string.

        Raises:
            StreamError:      if the pipeline signals [ERROR].
            EmptyStreamError: if the stream closes with no tokens.
        """
        logger.info(
            "AskQuestion.execute | user=%s | question=%r",
            user_id,
            question[:80],
        )

        tokens: list[str] = []
        step_count: int = 0

        # Gateway yields SseLine objects — already parsed by the adapter
        async for line in self._gateway.stream(question):

            if isinstance(line, SseStep):
                step_count += 1
                logger.debug("Step %d: %s", step_count, line.message)

                try:
                    await self._callback.on_step(line.message)
                except Exception:
                    logger.warning(
                        "StepCallback.on_step failed | user=%s | step=%r",
                        user_id,
                        line.message,
                        exc_info=True,
                    )

            elif isinstance(line, SseToken):
                tokens.append(line.token)

            # SseEmpty → skip silently

        if not tokens:
            logger.warning(
                "Empty stream | user=%s | steps_received=%d",
                user_id,
                step_count,
            )
            raise EmptyStreamError(step_count=step_count)

        answer = "".join(tokens).strip()

        logger.info(
            "AskQuestion complete | user=%s | length=%d chars | steps=%d",
            user_id,
            len(answer),
            step_count,
        )

        try:
            await self._callback.on_complete()
        except Exception:
            logger.warning(
                "StepCallback.on_complete failed | user=%s",
                user_id,
                exc_info=True,
            )

        return answer