"""OpenAI GPT models for sample generation."""
import openai

from hyperconf import HyperConfig, hypermap
from geany.abc import LLMSampleGenerator


@hypermap("gpt")
class Gpt(LLMSampleGenerator):
    """A sample generator that uses GPT through OpenAI API."""
    
    def __init__(self, config: HyperConfig):
        """Initialize an OpenAI API client.

        Args:
        config (HyperConfig): a configuration object containing
        the API key and other configuration options.
        prompt (str): the initial context/prompt.
        """
        if config is None:
            raise ValueError("config is None")

        self._client = openai.OpenAI(api_key=config.api_key)
        self._engine = config.engine

    def set_context(initial_context: str):
        """Set the initial system message.

        Args:
        initial_context (str): task description
        """
        self._messages.clear()
        self._messages.append({
            "role": "system",
            "content": initial_context
        })

    def generate_samples(self, command: str) -> str:
        """Set the context and execute instruction.

        Args:
        command (str): the instruction to start generation.

        Return:
        the model response containing the completion for the instruction.
        """
        self._messages.append({
            "role": "user",
            "content": command
        },
                              )
        response = self._client.chat.completions.create(
            model=self._engine,
            messages=self._messages
        )

        samples = response.choices[0].message.content
        self.messages.append({
            "role": "system",
            "content": samples
        })
        return samples


        
          
                             
            
