# main.py
import rdflib
from rdflib import Graph, Literal, BNode, Namespace, RDF, URIRef
from rdflib.namespace import DC, FOAF
from tqdm import tqdm
import jaconv

from utils.connect_cookpad_db import get_config, execute_sql

# データベース接続の設定
config = get_config("config.ini")  # config.iniへの相対パスを適切に設定

# RDFグラフの作成
g = Graph()

# ネームスペースの定義
n = Namespace("cookpad.com/")

# レシピノードの作成
recipes = execute_sql(config, "SELECT id, title FROM recipes")
for (id, title) in tqdm(recipes, desc="Creating recipe nodes(cookpad)"):
    recipe_node = URIRef(n + str(id))
    g.add((recipe_node, DC.identifier, Literal(id)))
    g.add((recipe_node, FOAF.title, Literal(title)))
    g.add((recipe_node, n.data_source, Literal('cookpad')))

# 食材ノードの作成
ingredients = execute_sql(config, "SELECT DISTINCT name FROM ingredients")
for (name,) in tqdm(ingredients, desc="Creating ingredient nodes"):
    if name is not None:
        ingredient_name = jaconv.kata2hira(name)  # convert katakana to hiragana
        ingredient_node = URIRef(n + ingredient_name)
        g.add((ingredient_node, FOAF.name, Literal(ingredient_name)))
    

# エッジの作成
relations = execute_sql(config, "SELECT recipe_id, name FROM ingredients")
for (recipe_id, name) in tqdm(relations, desc="Creating edges"):
    recipe_node = URIRef(n + str(recipe_id))
    ingredient_name = jaconv.kata2hira(name)  # convert katakana to hiragana
    ingredient_node = URIRef(n + ingredient_name)
    g.add((recipe_node, n.uses, ingredient_node))


# グラフをRDF形式で保存
g.serialize(destination="/mnt/d/cookpad-graph.rdf", format="rdfxml")