from dataclasses import dataclass
from typing import List, Optional
from recipe_compiler.recipe_category import RecipeCategory

@dataclass
class IngredientSection:
    title: Optional[str]
    items: List[str]

@dataclass
class InstructionSection:
    title: Optional[str]
    steps: List[str]
    note: Optional[str] = None

@dataclass
class ContentSection:
    title: str
    content: str

@dataclass
class Recipe:
    name: str
    residence: str
    category: RecipeCategory
    recipe_name: str
    quote: str
    ingredient_sections: List[IngredientSection]
    instruction_sections: List[InstructionSection]
    content_sections: List[ContentSection]
    tags: List[str]
    image: Optional[str] = None

    @property
    def slug(self) -> str:
        """Returns the recipe name formatted as kebab-case

        Returns:
            str: The recipe_name in kebab-case format
        """
        return self.recipe_name.lower().replace(" ", "-").replace("'", "").replace('"', "")