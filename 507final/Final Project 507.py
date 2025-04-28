import json
import itertools
import networkx as nx
import fnmatch
from collections import defaultdict

with open("/Users/mini_uia/Desktop/507Final/train.json", "r") as f:
    recipes = json.load(f)

def clean_ingredient(ingredient):
    return ingredient.strip().lower()

cooccurrence = defaultdict(lambda: defaultdict(int))
for recipe in recipes:
    ingredients = [clean_ingredient(i) for i in recipe["ingredients"]]
    for ing1, ing2 in itertools.combinations(ingredients, 2):
        cooccurrence[ing1][ing2] += 1
        cooccurrence[ing2][ing1] += 1

G = nx.Graph()
for recipe in recipes:
    for ingredient in recipe["ingredients"]:
        G.add_node(clean_ingredient(ingredient))

for ing1, neighbors in cooccurrence.items():
    for ing2, count in neighbors.items():
        G.add_edge(ing1, ing2, weight=count)

def search_ingredients(pattern):
    """
    Search for ingredients using a wildcard pattern.
    Use '%' in the pattern as a wildcard (replacing it internally with '*').
    For example: 'garlic', 'g%', '%a%', etc.
    """
    pattern = pattern.lower().replace('%', '*')
    matches = [ing for ing in sorted(G.nodes()) if fnmatch.fnmatch(ing, pattern)]
    if matches:
        print(f"\nIngredients matching pattern '{pattern}':")
        for ing in matches:
            print(ing)
        print(f"\nTotal matching ingredients: {len(matches)}")
    else:
        print(f"\nNo ingredients found matching pattern '{pattern}'.")

def most_similar_ingredients(ingredient, top_n=5):
    ingredient = ingredient.lower()
    if ingredient not in G:
        print(f"Ingredient '{ingredient}' not found.")
        return
    neighbors = G[ingredient]
    sorted_neighbors = sorted(neighbors.items(), key=lambda x: x[1]["weight"], reverse=True)
    print(f"\nIngredients that most frequently co-occur with '{ingredient}':")
    for neighbor, data in sorted_neighbors[:top_n]:
        print(f"  {neighbor} (co-occurrence count: {data['weight']})")

def find_shortest_path(ing1, ing2):
    ing1 = ing1.lower()
    ing2 = ing2.lower()
    if ing1 not in G or ing2 not in G:
        print("One or both ingredients not found in the network.")
        return
    try:
        path = nx.shortest_path(G, source=ing1, target=ing2)
        print(f"\nShortest path between '{ing1}' and '{ing2}':")
        print(" -> ".join(path))
    except nx.NetworkXNoPath:
        print(f"No path exists between '{ing1}' and '{ing2}'.")

def most_connected_among_inputs(top_n=5):
    print("\nEnter ingredients one at a time. Type 'done' when finished:")
    input_ingredients = []
    while True:
        ing = input("Ingredient (or 'done'): ").strip().lower()
        if ing == "done":
            break
        input_ingredients.append(ing)
    
    valid_inputs = [ing for ing in input_ingredients if ing in G]
    if not valid_inputs:
        print("None of the entered ingredients are in the network.")
        return
    
    candidate_scores = defaultdict(int)
    for ing in valid_inputs:
        for neighbor, data in G[ing].items():
            if neighbor in valid_inputs:
                continue
            candidate_scores[neighbor] += data['weight']
    
    if not candidate_scores:
        print("No candidate ingredients found that are connected to the provided inputs.")
        return

    sorted_candidates = sorted(candidate_scores.items(), key=lambda x: x[1], reverse=True)
    print("\nIngredients most connected to your input ingredients:")
    for candidate, score in sorted_candidates[:top_n]:
        print(f"  {candidate} (cumulative co-occurrence weight: {score})")

def stats_for_ingredient(ingredient):
    ingredient = ingredient.lower()
    if ingredient not in G:
        print(f"Ingredient '{ingredient}' not found.")
        return
    count_recipes = sum(1 for recipe in recipes if ingredient in [clean_ingredient(i) for i in recipe["ingredients"]])
    neighbors = G[ingredient]
    num_neighbors = len(neighbors)
    if num_neighbors > 0:
        avg_cooccur = sum(data['weight'] for data in neighbors.values()) / num_neighbors
    else:
        avg_cooccur = 0
    print(f"\nStats for '{ingredient}':")
    print(f"  Appears in {count_recipes} recipes.")
    print(f"  Has {num_neighbors} connected ingredients.")
    print(f"  Average co-occurrence count with its neighbors: {avg_cooccur:.2f}")

def interactive_prompt():
    while True:
        print("\nChoose a query option:")
        print("1. Search ingredients (use '%' as a wildcard)")
        print("2. Find shortest path between two ingredients")
        print("3. Find ingredients most connected to your input ingredients")
        print("4. Get statistics for an ingredient")
        print("5. Find most closely related ingredients")
        print("6. Exit")
        option = input("Enter option number: ").strip()
        if option == "1":
            pattern = input("Enter ingredient search pattern (e.g., garlic, g%, %a%): ")
            search_ingredients(pattern)
        elif option == "2":
            ing1 = input("Enter the first ingredient: ")
            ing2 = input("Enter the second ingredient: ")
            find_shortest_path(ing1, ing2)
        elif option == "3":
            most_connected_among_inputs()
        elif option == "4":
            ing = input("Enter an ingredient: ")
            stats_for_ingredient(ing)
        elif option == "5":
            ing = input("Enter an ingredient: ")
            most_similar_ingredients(ing)
        elif option == "6":
            print("Exiting...")
            break
        else:
            print("Invalid option. Please try again.")

if __name__ == "__main__":
    interactive_prompt()
