from abc import abstractmethod
from hyperconf import HyperConfig


class LLMSampleGenerator:
    """Define base class for sample generators."""

    @abstractmethod
    def set_context(context: str) -> None:
        """Set the context for sample generation.

        Args:
        context (str): initial system message.
        """
        ...

    @abstractmethod
    def generate(instruction: str) -> str:
        """Execute instruction in the current context."""
        ...


class Prompt:
    """Provide context and instructions for LLMs."""
    
    @abstractmethod
    def get_context(self):
        """Get the initial, system, message."""
        ...

    @abstractmethod
    def get_instruction(self, num_samples: int):
        """Get an instruction to generate num_samples samples."""
        ...

    @abstractmethod
    def parse_output(self, text: str):
        """Parse the given text and extract samples."""
        ...


class PromptBuilder:
    """A prompt builder constructs prompt objects from config."""

    @abstractmethod
    def get_prompts(self, config: HyperConfig):
        """Create prompt objects from config."""
        ...
