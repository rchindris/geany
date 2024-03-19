import click

from geany import Geany

@click.command("Geany")
@click.argument("recipe")
def generate(recipe):
    # preload config definitions.
    g = Geany(recipe)
    g.generate()


if __name__ == "__main__":
    generate()
        
