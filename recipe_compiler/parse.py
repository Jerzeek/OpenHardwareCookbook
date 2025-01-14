from marko.block import Document, Heading, List, Quote, ListItem, Paragraph
from recipe_compiler.recipe import Recipe, IngredientSection
from recipe_compiler.recipe_category import RecipeCategory
from typing import List as TypingList
import marko
import frontmatter
from marko.inline import RawText

def extract_text_from_paragraph(paragraph: Paragraph) -> str:
    """Extract text from a paragraph node"""
    text = ""
    for child in paragraph.children:
        if isinstance(child, RawText):
            text += child.children
        else:
            text += str(child)
    return text.strip()

def get_ingredients_structured(document: Document) -> TypingList[IngredientSection]:
    """Returns the structured list of ingredients from the recipe document"""
    print("\nDEBUG: Starting ingredient parsing...")
    sections = []
    current_section = None
    is_within_ingredients = False
    
    for node in document.children:
        if isinstance(node, Heading):
            text = extract_text_from_paragraph(node)
            print(f"DEBUG: Found heading (level {node.level}): '{text}'")
            
            if node.level == 2 and text.lower() == "ingredients":
                print("DEBUG: Found main ingredients section")
                is_within_ingredients = True
                current_section = IngredientSection(title=None, items=[])
                sections.append(current_section)
            elif node.level == 2:
                print("DEBUG: Found level 2 heading, exiting ingredients section")
                is_within_ingredients = False
            elif node.level == 3 and is_within_ingredients:
                print(f"DEBUG: Found ingredient subsection: {text}")
                current_section = IngredientSection(title=text, items=[])
                sections.append(current_section)
        
        elif isinstance(node, List) and is_within_ingredients and current_section is not None:
            print("DEBUG: Processing ingredient list")
            for item in node.children:
                if isinstance(item, ListItem):
                    # The first child of a ListItem is typically a Paragraph
                    if item.children and isinstance(item.children[0], Paragraph):
                        item_text = extract_text_from_paragraph(item.children[0])
                        print(f"DEBUG: Found ingredient: '{item_text}'")
                        current_section.items.append(item_text)
    
    print(f"\nDEBUG: Found {len(sections)} sections")
    for section in sections:
        print(f"Section title: {section.title}")
        print(f"Items: {section.items}")
    
    return sections

def get_list_within_section(document: Document, header: str) -> TypingList[str]:
    """Returns a list nested within a section defined by the header string"""
    is_within_section = False
    all_items = []

    for node in document.children:
        if isinstance(node, Heading):
            text = extract_text_from_paragraph(node)
            if text.lower() == header.lower():
                is_within_section = True
            elif node.level <= 2 and is_within_section:
                is_within_section = False
        
        elif isinstance(node, List) and is_within_section:
            for item in node.children:
                if isinstance(item, ListItem) and item.children:
                    para = item.children[0]
                    if isinstance(para, Paragraph):
                        item_text = extract_text_from_paragraph(para)
                        all_items.append(item_text)

    return all_items

def get_recipe_name(document: Document) -> str:
    """Returns the content of the first h1 (#) tag in a markdown document"""
    for node in document.children:
        if isinstance(node, Heading) and node.level == 1:
            return extract_text_from_paragraph(node)

def get_quote(document: Document) -> str:
    """Returns the content of the first quote (>) tag in a markdown document"""
    for node in document.children:
        if isinstance(node, Quote):
            # Handle both single and multi-line quotes
            text = ""
            for child in node.children:
                if isinstance(child, Paragraph):
                    text += extract_text_from_paragraph(child) + "\n"
            return text.strip()

def get_instructions(document: Document) -> TypingList[str]:
    """Returns the list of instructions from the recipe document"""
    print("\nDEBUG: Looking for instructions")
    instructions = get_list_within_section(document, "Directions")
    if not instructions:
        instructions = get_list_within_section(document, "Instructions")
    
    print(f"DEBUG: Found {len(instructions)} instructions")
    for instr in instructions:
        print(f"DEBUG: Instruction: {instr}")
    
    return instructions

def parse_to_recipe(content: str) -> Recipe:
    """Parse a Markdown formatted string to a Recipe object"""
    print("\nParsing recipe...")
    
    recipe_metadata = frontmatter.loads(content)
    document = marko.parse(content)
    
    recipe_name = get_recipe_name(document)
    quote = get_quote(document)
    ingredient_sections = get_ingredients_structured(document)
    instructions = get_instructions(document)

    print(f"\nRecipe name: {recipe_name}")
    print("\nIngredient sections:")
    for section in ingredient_sections:
        print(f"\nSection title: {section.title}")
        print("Items:", section.items)
    print("\nInstructions:", instructions)
    
    return Recipe(
        name=recipe_metadata["name"],
        residence=recipe_metadata["residence"],
        category=RecipeCategory(recipe_metadata["category"].lower()),
        recipe_name=recipe_name,
        quote=quote,
        ingredient_sections=ingredient_sections,
        instructions=instructions,
    )