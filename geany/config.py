"""Geany configuration (recipe) utilities."""
from pathlib import Path
from hyperconfig import ConfigDefs, HyperConfig

def load_recipe(file_path: str) -> HyperConfig:
    """Validate and load a sample generation recipe.

    Args:
    file_path: the path to the recipe file.

    Return:
    a HyperConfig configuration object.
    """
