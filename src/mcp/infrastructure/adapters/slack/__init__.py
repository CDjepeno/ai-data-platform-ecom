from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from infrastructure.adapters.slack.silent_step_callback import (
        SilentStepCallbackAdapter,
    )
    from infrastructure.adapters.slack.slack_step_callback import SlackStepCallback

__all__ = [
    "SlackStepCallback",
    "SilentStepCallbackAdapter",
]


def __getattr__(name: str) -> object:
    if name == "SilentStepCallbackAdapter":
        from infrastructure.adapters.slack.silent_step_callback import (
            SilentStepCallbackAdapter,
        )

        return SilentStepCallbackAdapter

    if name == "SlackStepCallback":
        from infrastructure.adapters.slack.slack_step_callback import SlackStepCallback

        return SlackStepCallback

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
