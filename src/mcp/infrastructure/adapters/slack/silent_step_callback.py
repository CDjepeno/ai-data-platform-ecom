
from utils import get_logger
from domain.ports.step_callback_port import StepCallbackPort

logger = get_logger(__name__)

class SilentStepCallbackAdapter(StepCallbackPort):
    


    async def on_step(self, message: str) -> None:
        logger.debug("Step (silent): %s", message)

    async def on_complete(self) -> None:
        logger.debug("Complete (silent)")