
from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator

from domain.tools.sse import SseLine


class AskGatewayPort(ABC):


    @abstractmethod
    def stream(self, question: str) -> AsyncIterator[SseLine]:
        """
        Stream a question to the AI pipeline and yield typed SSE lines.

        The application layer iterates over SseLine value objects —
        it never sees raw bytes, HTTP responses, or SSE text.

        Args:
            question: Natural language business question.

        Yields:
            SseLine subclasses — SseEmpty, SseStep, or SseToken.
            The caller decides what to do with each type.

        Raises:
            StreamErrorSignal: when the pipeline signals [ERROR].
            EmptyStreamError:  raised by the use case if no tokens arrive.

        Example:
            async for line in gateway.stream("What were sales last month?"):
                if isinstance(line, SseToken):
                    tokens.append(line.token)
                elif isinstance(line, SseStep):
                    await on_step(line.message)
        """
        ...