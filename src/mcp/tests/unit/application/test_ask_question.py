from __future__ import annotations

from collections.abc import AsyncIterator

import pytest

from domain.errors import EmptyStreamError, StreamErrorSignal
from domain.ports import AskGatewayPort, StepCallbackPort
from domain.tools.sse import SseEmpty, SseLine, SseStep, SseToken
from application.use_cases.ask_question_usecase import AskQuestionUseCase


# ── Fakes ──────────────────────────────────────────────────────────────────────

class FakeAskGateway(AskGatewayPort):
    """
    Fake gateway that yields a predefined sequence of SseLine objects.

    Simulates the FastAPI SSE stream without any HTTP calls.
    """

    def __init__(self, lines: list[SseLine]) -> None:
        self._lines = lines

    async def stream(self, question: str) -> AsyncIterator[SseLine]:  # type: ignore[override]
        for line in self._lines:
            yield line


class FakeStepCallback(StepCallbackPort):
    """
    Fake callback that records on_step and on_complete calls.

    Used to assert that the use case notifies progress correctly.
    """

    def __init__(self) -> None:
        self.steps: list[str] = []
        self.completed: bool = False

    async def on_step(self, message: str) -> None:
        self.steps.append(message)

    async def on_complete(self) -> None:
        self.completed = True


class FailingStepCallback(StepCallbackPort):
    """
    Fake callback that always raises — simulates Slack being down.
    Used to verify that callback failures don't interrupt the stream.
    """

    async def on_step(self, message: str) -> None:
        raise RuntimeError("Slack rate limited")

    async def on_complete(self) -> None:
        raise RuntimeError("Slack rate limited")


# ── Helper ─────────────────────────────────────────────────────────────────────

def _make_use_case(
    lines: list[SseLine],
    callback: StepCallbackPort | None = None,
) -> AskQuestionUseCase:
    gateway = FakeAskGateway(lines)
    cb = callback or FakeStepCallback()
    return AskQuestionUseCase(gateway=gateway, callback=cb)


# ── Happy path ─────────────────────────────────────────────────────────────────

class TestHappyPath:

    async def test_assembles_tokens_into_answer(self) -> None:
        use_case = _make_use_case([
            SseStep("🧠 Understanding..."),
            SseToken("Les ventes "),
            SseToken("de mars "),
            SseToken("sont 142k€"),
            SseStep("✅ Done"),
        ])

        answer = await use_case.execute("Quelles sont les ventes ?", "U123")

        assert answer == "Les ventes de mars sont 142k€"

    async def test_strips_whitespace_from_answer(self) -> None:
        use_case = _make_use_case([
            SseToken("  hello world  "),
        ])

        answer = await use_case.execute("test", "U1")
        assert answer == "hello world"

    async def test_ignores_sse_empty_lines(self) -> None:
        use_case = _make_use_case([
            SseEmpty(),
            SseToken("answer"),
            SseEmpty(),
        ])

        answer = await use_case.execute("test", "U1")
        assert answer == "answer"


# ── Step callback ──────────────────────────────────────────────────────────────

class TestStepCallback:

    async def test_on_step_called_for_each_step(self) -> None:
        callback = FakeStepCallback()
        use_case = _make_use_case(
            lines=[
                SseStep("🧠 Understanding..."),
                SseStep("📊 Querying..."),
                SseToken("answer"),
            ],
            callback=callback,
        )

        await use_case.execute("test", "U1")

        assert len(callback.steps) == 2
        assert "🧠 Understanding..." in callback.steps
        assert "📊 Querying..." in callback.steps

    async def test_on_complete_called_after_answer(self) -> None:
        callback = FakeStepCallback()
        use_case = _make_use_case(
            lines=[SseToken("answer")],
            callback=callback,
        )

        await use_case.execute("test", "U1")

        assert callback.completed is True

    async def test_callback_failure_does_not_interrupt_stream(self) -> None:
        """
        Most important test — Slack being down must never lose the answer.
        """
        callback = FailingStepCallback()
        use_case = _make_use_case(
            lines=[
                SseStep("🧠 Step"),
                SseToken("answer despite slack failure"),
            ],
            callback=callback,
        )

        # Must not raise — answer must be returned despite callback failures
        answer = await use_case.execute("test", "U1")
        assert answer == "answer despite slack failure"

    async def test_on_complete_failure_does_not_lose_answer(self) -> None:
        callback = FailingStepCallback()
        use_case = _make_use_case(
            lines=[SseToken("the answer")],
            callback=callback,
        )

        answer = await use_case.execute("test", "U1")
        assert answer == "the answer"


# ── Error cases ────────────────────────────────────────────────────────────────

class TestErrorCases:

    async def test_empty_stream_raises_empty_stream_error(self) -> None:
        use_case = _make_use_case([
            SseStep("🧠 Understanding..."),
            # No tokens
        ])

        with pytest.raises(EmptyStreamError) as exc_info:
            await use_case.execute("test", "U1")

        assert exc_info.value.step_count == 1

    async def test_stream_error_signal_propagates(self) -> None:
        """
        StreamErrorSignal from the gateway must propagate to the caller.
        The use case does not catch it — the adapter or bot handles it.
        """
        class ErrorGateway(AskGatewayPort):
            async def stream(self, question: str) -> AsyncIterator[SseLine]:  # type: ignore[override]
                raise StreamErrorSignal("LangGraph timeout")
                yield  # make it a generator

        use_case = AskQuestionUseCase(
            gateway=ErrorGateway(),
            callback=FakeStepCallback(),
        )

        with pytest.raises(StreamErrorSignal):
            await use_case.execute("test", "U1")

    async def test_empty_stream_step_count_is_accurate(self) -> None:
        use_case = _make_use_case([
            SseStep("step 1"),
            SseStep("step 2"),
            SseStep("step 3"),
            # No tokens
        ])

        with pytest.raises(EmptyStreamError) as exc_info:
            await use_case.execute("test", "U1")

        assert exc_info.value.step_count == 3