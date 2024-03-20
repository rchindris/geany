import logging
from hyperconf import (
    ConfigDefs,
    HyperConfig,
    HyperMap
)
from geany.data import Dataset
from geany.errors import GeanyError


class Geany:
    """The data sample generator."""

    def __init__(self, recipe_path: str):
        """Initialize for a data generator recipe.

        Args:
        recipe_path (str): path to a data generation recipe.
        """
        ConfigDefs.add_package("geany")

        if recipe_path is None:
            raise ValueError("recipe_path is None")
        
        self.recipe = HyperConfig.load_yaml(recipe_path)

        generator_class = HyperMap.get_class(self.recipe.llm)
        if generator_class is None:
            logging.error(
                "Could not find a generator class for tag"
                f"{self.recipe.llm.__def__.name}"
            )
        self.generator = generator_class(self.recipe.llm)

        prompt_builder_class = HyperMap.get_class(self.recipe.prompt)
        if prompt_builder_class is None:
            logging.error(
                "Could not find a class for prompt "
                f"{self.recipe.prompt.__def__.name}"
            )
        self.prompt = prompt_builder_class()
        self.dataset = Dataset(self.recipe.dataset)
        

    def generate(self, max_retries=3):
        for prompt in self.prompt.get_prompts(self.recipe.prompt):
            self.generator.set_context(prompt.get_context())
            
            num_samples = self.recipe.dataset.num_samples_per_prompt
            num_retries = 0
            
            while num_samples > 0 and num_retries < max_retries:
                message = self.generator.generate_samples(
                    prompt.get_instruction(num_samples)
                )
                
                samples = prompt.parse_output(message)
                self.dataset.append(samples)
                
                num_samples -= len(samples)
                num_retries += 1

        self.dataset.save()
