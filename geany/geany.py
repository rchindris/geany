import logging
from hyperconf import (
    ConfigDefs,
    HyperConfig,
    HyperMap
)
from geany.errors import GeanyError


class Geany:
    """The data sample generator."""

    def __init__(self, recipe_path: str):
        """Initialize for a data generator recipe.

        Args:
        recipe_path (str): path to a data generation recipe.
        """
        ConfigDefs.add_package("geany")

        self.recipe = HyperConfig.load_yaml(recipe_path)

        generator_class = HyperMap.get_class(self.recipe.llm)
        if generator_class is None:
            logging.error(
                "Could not find a generator class for tag"
                f"{self.recipe.llm.__def__.name}"
            )
        self.llm = generator_class(self.recipe.llm)

        prompt_builder_class = HyperMap.get_class(self.recipe.prompt)
        if prompt_builder_class is None:
            logging.error(
                "Could not find a class for prompt "
                f"{self.recipe.prompt.__def__.name}"
            )
        self.prompt = prompt_builder_class()

    def generate(self):
        for prompt in self.prompt.get_prompts(self.recipe.prompt):
            print(prompt.get_context())
            print(prompt.get_instruction(10))
