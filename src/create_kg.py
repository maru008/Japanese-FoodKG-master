import os
import pandas as pd
import configparser
from tqdm import tqdm
import uuid
from rdflib import Graph, Namespace, URIRef, BNode, Literal, RDF, RDFS
from rdflib.namespace import XSD
from urllib.parse import quote

config = configparser.ConfigParser()
config.read("../config.ini")
OUTPUT_ROOT = config.get("Output","output_path")

print("データ読み込み")
cookpad_edges_path = os.path.join(OUTPUT_ROOT,"output_csv/cookpad_edges.csv") 
rakuten_edges_path = os.path.join(OUTPUT_ROOT,"output_csv/rakuten_edges.csv") 
seibunhyo_edges_path = os.path.join(OUTPUT_ROOT,"output_csv/seibunhyo_edges.csv") 

print("Cookpad...")
cookpad_edges = pd.read_csv(cookpad_edges_path)
print("rakuten...")
rakuten_edges = pd.read_csv(rakuten_edges_path)
print("seibunhyo...")
seibunhyo_edges = pd.read_csv(seibunhyo_edges_path)

print("完了")

print("====================")
print("データ数")
print("クックパッド: ",len(cookpad_edges))
print("楽天レシピ: ",len(rakuten_edges))
print("成分表:",len(seibunhyo_edges))


print("知識グラフ作成")
g = Graph()
# 名前空間の定義
RECIPE = Namespace("http://JapaneseFoodKG.org/Recipe/")
INGREDIENT = Namespace("http://JapaneseFoodKG.org/Ingredient/")
NUTRITION = Namespace("http://JapaneseFoodKG.org/Nutrition/")
DATA_SOURCE = Namespace("http://JapaneseFoodKG.org/data_source/")
RELATION = Namespace("http://JapaneseFoodKG.org/relation/")

import re


ingredient_uris = {}
for index, row in tqdm(cookpad_edges.iterrows(),total=len(cookpad_edges),desc="Cookpad"):
    recipe_id = row['recipe_id']
    recipe_title = row['recipe_title']
    ingredient_name = row['ingredient_name']
    data_source = row['data_source']

    if pd.isna(recipe_id) or pd.isna(ingredient_name):
        continue
    
    recipe_id_encoded = quote(recipe_id, safe='')  # 全ての文字をエンコード
    ingredient_name_encoded = quote(ingredient_name, safe='')  # 全ての文字をエンコード
    
    # レシピに関する情報を追加
    recipe_uri = RECIPE[recipe_id_encoded]
    g.add((recipe_uri, RDF.type, RECIPE.Recipe))
    g.add((recipe_uri, RECIPE.title, Literal(recipe_title)))
    g.add((recipe_uri, DATA_SOURCE.source, Literal(data_source)))  # データソースをレシピに追加
    
    
    # 食材のURI（文字列が一致する場合は既存のURIを使用）
    if ingredient_name_encoded not in ingredient_uris:
        random_uuid = str(uuid.uuid4())
        ingredient_uris[ingredient_name_encoded] = INGREDIENT[random_uuid]
    ingredient_uri = ingredient_uris[ingredient_name_encoded]

    # 食材に関する情報を追加
    g.add((ingredient_uri, RDF.type, INGREDIENT.Ingredient))
    g.add((ingredient_uri, INGREDIENT.name, Literal(ingredient_name)))

    # レシピと食材の関係を追加
    g.add((recipe_uri, RECIPE.hasIngredient, ingredient_uri))


for index, row in tqdm(rakuten_edges.iterrows(),total=len(rakuten_edges),desc="Rakten"):
    recipe_id = row['recipe_id']
    recipe_title = row['recipe_title']
    ingredient_name = row['ingredient_name']
    data_source = row['data_source']
    
    # レシピに関する情報を追加
    recipe_uri = RECIPE[recipe_id]
    g.add((recipe_uri, RDF.type, RECIPE.Recipe))
    g.add((recipe_uri, RECIPE.title, Literal(recipe_title)))
    g.add((recipe_uri, DATA_SOURCE.source, Literal(data_source)))  # データソースをレシピに追加
    
    
    # 食材のURI（文字列が一致する場合は既存のURIを使用）
    if ingredient_name not in ingredient_uris:
        random_uuid = str(uuid.uuid4())
        ingredient_uris[ingredient_name] = INGREDIENT[random_uuid]
    ingredient_uri = ingredient_uris[ingredient_name]

    # 食材に関する情報を追加
    g.add((ingredient_uri, RDF.type, INGREDIENT.Ingredient))
    g.add((ingredient_uri, INGREDIENT.name, Literal(ingredient_name)))

    # レシピと食材の関係を追加
    g.add((recipe_uri, RECIPE.hasIngredient, ingredient_uri))
    
nutrition_uris = {}

for index, row in tqdm(seibunhyo_edges.iterrows(),total=len(seibunhyo_edges),desc="Seibunhyo"):
    food_name = row['food_name']
    nutrition_name = row['nutrition_name']
    value = row['value']
    data_source = row['data_source']  # データソースの値を取得

    # 栄養素のURI（文字列が一致する場合は既存のURIを使用）
    if nutrition_name not in nutrition_uris:
        # ランダムなUUIDを生成
        random_uuid = str(uuid.uuid4())
        nutrition_uris[nutrition_name] = NUTRITION[random_uuid]
    nutrition_uri = nutrition_uris[nutrition_name]
    
    # 栄養素に関する情報を追加
    g.add((nutrition_uri, RDF.type, NUTRITION.Nutrient))
    g.add((nutrition_uri, NUTRITION.name, Literal(nutrition_name)))
    
    food_name = food_name.replace('\u3000', ' ')  # 全角スペースを半角スペースに置換
    matching_ingredients = {name: uri for name, uri in ingredient_uris.items() if isinstance(name, str) and name in food_name}


    for ingredient_name, ingredient_uri in matching_ingredients.items():
        relation_uri = RELATION[str(uuid.uuid4())]  # エッジのURI
        g.add((ingredient_uri, relation_uri, nutrition_uri))
        g.add((relation_uri, RDF.type, RELATION.Contains))
        g.add((relation_uri, RELATION.value, Literal(value, datatype=XSD.float)))
        g.add((relation_uri, DATA_SOURCE.source, Literal(data_source))) 


japanesefoodkg_ttl_path = os.path.join(OUTPUT_ROOT, "JapaneseFoodKG.ttl") 
with open(japanesefoodkg_ttl_path, "wb") as f:
    print(f"saving to {japanesefoodkg_ttl_path}")
    f.write(g.serialize(format="turtle"))

# .rdfファイルとして保存
japanesefoodkg_rdf_path = os.path.join(OUTPUT_ROOT, "JapaneseFoodKG.rdf") 
with open(japanesefoodkg_rdf_path, "wb") as f:
    print(f"saving to {japanesefoodkg_rdf_path}")
    f.write(g.serialize(format="xml"))