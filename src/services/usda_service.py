"""
USDA FoodData Central API Service
Fetches real nutrition data (calories, protein, carbs, fats, fiber, sugar, sodium)
for ingredients used in diet plans.

Speed optimisations vs the original sequential version:
  1. Parallel HTTP requests via ThreadPoolExecutor — all unique meal names
     are looked up at the same time instead of one-by-one.
  2. /foods/search?nutrientIds= returns nutrients in the search response,
     so we skip the second /food/{id} fetch entirely (1 request per meal
     instead of 2).
  3. In-memory session cache — repeated lookups (same meal name across days)
     cost 0 HTTP requests.
  4. time.sleep() removed — not needed at these request rates.

API docs: https://fdc.nal.usda.gov/api-guide/
Put your API key in .env as: USDA_API_KEY=your_key_here
"""

import os
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv

load_dotenv()

# Nutrient IDs in USDA FoodData Central
NUTRIENT_IDS = {
    "calories":  1008,  # Energy (kcal)
    "protein":   1003,  # Protein
    "carbs":     1005,  # Carbohydrate, by difference
    "fats":      1004,  # Total lipid (fat)
    "fiber":     1079,  # Fiber, total dietary
    "sugar":     2000,  # Total Sugars
    "sodium":    1093,  # Sodium, Na
}

# Session-level cache: normalised name → per-100g nutrition dict
_nutrition_cache: dict = {}

# Max parallel workers — stays well under USDA's 1000 req/hr limit
_MAX_WORKERS = 8


class USDAService:
    BASE_URL = "https://api.nal.usda.gov/fdc/v1"

    def __init__(self):
        self.api_key = os.getenv("USDA_API_KEY", "")
        if not self.api_key:
            print("[USDA] Warning: USDA_API_KEY not set in .env — nutrition lookup disabled")

    def is_available(self) -> bool:
        return bool(self.api_key)

    # ------------------------------------------------------------------ #
    #  Public API                                                          #
    # ------------------------------------------------------------------ #

    def get_nutrition(self, ingredient_name: str, grams: float = 100.0) -> dict | None:
        """
        Returns nutrition data per `grams` for the given ingredient.
        All values scaled from per-100g USDA data.
        """
        if not self.is_available():
            return None

        cache_key = ingredient_name.lower().strip()
        if cache_key not in _nutrition_cache:
            base = self._search_and_fetch(ingredient_name)
            if base is None:
                return None
            _nutrition_cache[cache_key] = base

        factor = grams / 100.0
        return {k: round(v * factor, 1) for k, v in _nutrition_cache[cache_key].items()}

    def enrich_meal_plan(self, plan: dict) -> dict:
        """
        Enriches every meal in the 7-day plan with real USDA nutrition data.
        All unique meal names are fetched IN PARALLEL — typical speedup 6-8×
        compared to sequential requests.

        Falls back to AI estimates for any meal that can't be found.
        Adds top-level 'daily_avg' and 'weekly_totals' dicts.
        """
        if not self.is_available():
            print("[USDA] API key not set — skipping nutrition enrichment")
            return plan

        DAYS = {"monday","tuesday","wednesday","thursday","friday","saturday","sunday"}

        # ── Step 1: collect all unique meal names not already cached ──────
        unique_names = set()
        for day_key, day_data in plan.items():
            if day_key not in DAYS or not isinstance(day_data, dict):
                continue
            for meal in day_data.values():
                if isinstance(meal, dict):
                    name = meal.get("name", "").strip()
                    if name and name.lower() not in _nutrition_cache:
                        unique_names.add(name)

        # ── Step 2: fetch all uncached names in parallel ──────────────────
        if unique_names:
            print(f"[USDA] Fetching {len(unique_names)} unique meals in parallel...")
            with ThreadPoolExecutor(max_workers=_MAX_WORKERS) as pool:
                futures = {pool.submit(self._search_and_fetch, name): name
                           for name in unique_names}
                for future in as_completed(futures):
                    name = futures[future]
                    try:
                        result = future.result()
                        if result:
                            _nutrition_cache[name.lower()] = result
                    except Exception as e:
                        print(f"[USDA] Error fetching {name!r}: {e}")

        # ── Step 3: apply cached data to every meal ───────────────────────
        weekly = {k: 0.0 for k in NUTRIENT_IDS}

        for day_key in ["monday","tuesday","wednesday","thursday","friday","saturday","sunday"]:
            day_data = plan.get(day_key, {})
            day_totals = {k: 0.0 for k in NUTRIENT_IDS}

            for meal in day_data.values():
                if not isinstance(meal, dict):
                    continue
                name = meal.get("name", "").strip()
                cached = _nutrition_cache.get(name.lower())

                if cached:
                    # Scale to ~300g serving
                    factor = 300.0 / 100.0
                    for k in NUTRIENT_IDS:
                        meal[k] = round(cached[k] * factor, 1)
                    meal["usda_verified"] = True
                else:
                    meal.setdefault("fiber",  0)
                    meal.setdefault("sugar",  0)
                    meal.setdefault("sodium", 0)
                    meal["usda_verified"] = False

                for k in NUTRIENT_IDS:
                    day_totals[k] += meal.get(k, 0)

            plan[day_key]["_day_totals"] = {k: round(v, 1) for k, v in day_totals.items()}
            for k in NUTRIENT_IDS:
                weekly[k] += day_totals[k]

        plan["weekly_totals"] = {k: round(v, 1) for k, v in weekly.items()}
        plan["daily_avg"]     = {k: round(v / 7, 1) for k, v in weekly.items()}
        plan["usda_enriched"] = True
        return plan

    def get_ingredient_nutrition_list(self, ingredient_names: list[str]) -> dict:
        """
        Batch-lookup for a list of ingredient names (used by grocery link).
        Fetches all in parallel, returns {name: {calories, protein, ...}} per 100g.
        """
        if not self.is_available():
            return {}

        # Fetch uncached names in parallel
        uncached = [n for n in ingredient_names if n.lower() not in _nutrition_cache]
        if uncached:
            with ThreadPoolExecutor(max_workers=_MAX_WORKERS) as pool:
                futures = {pool.submit(self._search_and_fetch, name): name
                           for name in uncached}
                for future in as_completed(futures):
                    name = futures[future]
                    try:
                        result = future.result()
                        if result:
                            _nutrition_cache[name.lower()] = result
                    except Exception as e:
                        print(f"[USDA] Error fetching ingredient {name!r}: {e}")

        return {
            name: _nutrition_cache[name.lower()]
            for name in ingredient_names
            if name.lower() in _nutrition_cache
        }

    # ------------------------------------------------------------------ #
    #  Internal helpers                                                    #
    # ------------------------------------------------------------------ #

    def _search_and_fetch(self, query: str) -> dict | None:
        """
        Single USDA request using /foods/search with nutrientIds parameter.
        This returns nutrients directly in the search response — no second
        /food/{id} call needed, cutting request count in half.
        """
        url = f"{self.BASE_URL}/foods/search"
        # Request only the 7 nutrient IDs we care about
        nutrient_ids_str = ",".join(str(v) for v in NUTRIENT_IDS.values())
        params = {
            "api_key":    self.api_key,
            "query":      query,
            "dataType":   "Foundation,SR Legacy",
            "pageSize":   3,
            "nutrientIds": nutrient_ids_str,
        }
        try:
            resp = requests.get(url, params=params, timeout=10)
            resp.raise_for_status()
            foods = resp.json().get("foods", [])

            if not foods:
                # Fallback to Branded
                params["dataType"] = "Branded"
                resp = requests.get(url, params=params, timeout=10)
                resp.raise_for_status()
                foods = resp.json().get("foods", [])

            if not foods:
                print(f"[USDA] No result for: {query!r}")
                return None

            food = foods[0]
            result = {k: 0.0 for k in NUTRIENT_IDS}

            # foodNutrients in search response uses nutrientId (not nested)
            for n in food.get("foodNutrients", []):
                nid = n.get("nutrientId") or n.get("nutrient", {}).get("id")
                val = n.get("value") or n.get("amount") or 0.0
                for key, target_id in NUTRIENT_IDS.items():
                    if nid == target_id:
                        result[key] = round(float(val), 2)

            return result

        except Exception as e:
            print(f"[USDA] Search error for {query!r}: {e}")
            return None