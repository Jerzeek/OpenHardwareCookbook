from marko.block import Document, Heading, List, Quote
from recipe_compiler.recipe import Recipe
from recipe_compiler.recipe_category import RecipeCategory

import marko
import frontmatter
from marko.inline import RawText


def get_recipe_name(document: Document) -> str:
    """Returns the content of the first h1 (#) tag in a markdown document

    Args:
        document (Document): A Marko Markdown Document object

    Returns:
        str: The content of the first h1 tag in the document
    """

    for node in document.children:
        if type(node) is Heading and node.level == 1:
            return node.children[0].children


def get_quote(document: Document) -> str:
    """Returns the content of the first quote (>) tag in a markdown document

    Args:
        document (Document): A Marko Markdown Document object

    Returns:
        str: The content of the first quote tag in the document
    """

    for node in document.children:
        if type(node) is Quote:
            return "\n".join(
                text.children
                for text in node.children[0].children
                if type(text) is RawText
            )


def get_list_within_section(document: Document, header: str) -> list[str]:
    """Returns a list nested within a section defined by the header string

    Args:
        document (Document): A Marko Markdown Document object
        section (str): The string of a header defining a given section

    Returns:
        list[str]: A list of items within the given section
    """
    is_within_section = False
    all_items = []

    for node in document.children:
        if type(node) is Heading:
            # Check if this is our target section or a subsection of it
            heading_text = node.children[0].children
            if heading_text.lower() == header.lower():
                is_within_section = True
            elif node.level <= 2 and is_within_section:  # End section at next h1 or h2
                is_within_section = False
        
        if type(node) is List and is_within_section:
            items = [item.children[0].children[0].children for item in node.children]
            all_items.extend(items)

    return all_items if all_items else None


def get_ingredients(document: Document) -> list[str]:
    """Returns the list of ingredients from the recipe document

    Args:
        document (Document): A Marko Markdown Document object

    Returns:
        list[str]: A list of ingredients from the document
    """
    # Try to get all ingredients, including those in subsections
    ingredients = get_list_within_section(document, "Ingredients")
    if not ingredients:
        # If no ingredients found, check for common variations
        for variant in ["Ingredient", "ingredients", "INGREDIENTS"]:
            ingredients = get_list_within_section(document, variant)
            if ingredients:
                break
    return ingredients

def get_instructions(document: Document) -> list[str]:
    """Returns the list of instructions from the recipe document

    Args:
        document (Document): A Marko Markdown Document object

    Returns:
        list[str]: A list of instructions from the document
    """

    return get_list_within_section(document, "Directions")


def parse_to_recipe(content: str) -> Recipe:
    """Parse a Markdown formatted string to a Recipe object

    Args:
        content (str): A Markdown formatted string

    Returns:
        Recipe: A Recipe object representing the given content
    """

    recipe_metadata = frontmatter.loads(content)

    document = marko.parse(content)
    recipe_name = get_recipe_name(document)
    quote = get_quote(document)
    ingredients = get_ingredients(document)
    instructions = get_instructions(document)

    return Recipe(
        name=recipe_metadata["name"],
        residence=recipe_metadata["residence"],
        category=RecipeCategory(recipe_metadata["category"].lower()),
        recipe_name=recipe_name,
        quote=quote,
        ingredients=ingredients,
        instructions=instructions,
    )
