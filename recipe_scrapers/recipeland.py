from ._abstract import AbstractScraper
from ._grouping_utils import IngredientGroup
from ._utils import normalize_string


class RecipeLand(AbstractScraper):
    @classmethod
    def host(cls):
        return "recipeland.com"

    def _parse_ingredient_row(self, row):
        amount = row.select_one(".amount-measure .ir-us") and row.select_one(".amount-measure .ir-us").get_text()
        measure = row.select_one(".ingredient .ir-us") and row.select_one(".ingredient .ir-us").get_text()
        ingredient_elem = row.select_one("a")
        ingredient = ingredient_elem and ingredient_elem.get_text()

        full_ingredient = f"{amount} {measure} {ingredient}"
        return normalize_string(full_ingredient)

    def ingredients(self):
        ingredient_rows = self.soup.select("#ingredient_list .ingredient-row")
        ingredient_rows = [
            self._parse_ingredient_row(row)
            for row in ingredient_rows
            if not row.select_one("th.i-head")
        ]
        if ingredient_rows == []:
            ingredient_rows = self.schema.ingredients()
        return ingredient_rows

    def ingredient_groups(self):
        ingredient_rows = self.soup.select("#ingredient_list .ingredient-row")
        groups = []
        current_group = None
        grouped_ingredients = []

        for row in ingredient_rows:
            group_header = row.select_one(".preparation")
            if group_header:
                if current_group or grouped_ingredients:
                    groups.append(
                        IngredientGroup(
                            ingredients=grouped_ingredients, purpose=current_group
                        )
                    )
                current_group = group_header.get_text(strip=True)
                grouped_ingredients = []
            else:
                full_ingredient = self._parse_ingredient_row(row)
                if full_ingredient:
                    grouped_ingredients.append(full_ingredient)

        if current_group or grouped_ingredients:
            groups.append(
                IngredientGroup(ingredients=grouped_ingredients, purpose=current_group)
            )

        return groups
