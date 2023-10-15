import os
import re
import jaconv
import math
from tqdm import tqdm

from utils.connect_cookpad_db import *

 
config = get_config("../config.ini")
OUTPUT_ROOT = config.get("Output","output_path")

print("前処理（Cookpad）============================")

print("インデックス作成")
sql = """
CREATE INDEX recipe_id_index ON ingredients(recipe_id);
"""
execute_sql(config, sql)
print("DBアクセス")
sql = """
SELECT 
    recipes.id AS recipe_id,
    recipes.title AS recipe_title,
    recipes.description AS recipe_description,
    ingredients.name AS ingredient_name,
    ingredients.quantity AS ingredient_quantity
FROM 
    recipes
INNER JOIN 
    ingredients ON recipes.id = ingredients.recipe_id;

"""
marge_cookpad_data = execute_sql2df(config, sql)
print("カタカナ→ひらがな処理")
marge_cookpad_data.dropna(subset=['ingredient_name'], inplace=True)
marge_cookpad_data["ingredient_name"] = [jaconv.kata2hira(name) for name in marge_cookpad_data["ingredient_name"]] 
marge_cookpad_data.dropna(subset=['recipe_title'], inplace=True)
marge_cookpad_data["recipe_title"] = [jaconv.kata2hira(name) for name in marge_cookpad_data["recipe_title"]] 
marge_cookpad_data["data_source"] = "cookpad"
marge_cookpad_data["edge_type"] = "recipe-ingredient"
cookpad_edge = marge_cookpad_data[["recipe_id","recipe_title", "ingredient_name","edge_type","data_source"]].copy()
save_path = os.path.join(OUTPUT_ROOT,"output_csv","cookpad_edges.csv") 
print(f"Cookpadデータ保存: {save_path}")
cookpad_edge.to_csv(save_path,index=False)

print("前処理（Rakuten）============================")
rakuten_root_path = config['Data']['rakuten_data_path']

print("データ読み込み")
data_all = pd.read_csv(os.path.join(rakuten_root_path,"recipe01_all_20170118.txt"), sep="\t", encoding="utf-8", header=None)
column_names = [
    "recipe_id",
    "user_id",
    "major_category",
    "medium_category",
    "minor_category",
    "recipe_title",
    "recipe_origin",
    "recipe_introduction",
    "food_image_file",
    "dish_name",
    "tag1",
    "tag2",
    "tag3",
    "tag4",
    "one_point_info",
    "cooking_time_id",
    "occasion_id",
    "cost_id",
    "servings",
    "recipe_publish_date"
]
data_all.columns = column_names

data_ingredient = pd.read_csv(os.path.join(rakuten_root_path,"recipe02_material_20160112.txt"), sep="\t", encoding="utf-8", header=None)
column_names = [
    "recipe_id",
    "name",
    "quantity"
]
data_ingredient.columns = column_names
data_ingredient = data_ingredient.rename(columns={"name":"ingredient_name"})

merge_rakuten_data = pd.merge(data_all, data_ingredient, on='recipe_id')

print("カタカナ→ひらがな処理")

merge_rakuten_data.dropna(subset=['ingredient_name'], inplace=True)
merge_rakuten_data["ingredient_name"] = [jaconv.kata2hira(name) for name in merge_rakuten_data["ingredient_name"]] 
merge_rakuten_data.dropna(subset=['recipe_title'], inplace=True)
merge_rakuten_data["recipe_title"] = [jaconv.kata2hira(name) for name in merge_rakuten_data["recipe_title"]] 

merge_rakuten_data["data_source"] = "rakuten"
merge_rakuten_data["edge_type"] = "recipe-ingredient"
rakuten_edge = merge_rakuten_data[["recipe_id","recipe_title", "ingredient_name","edge_type","data_source"]].copy()

save_path = os.path.join(OUTPUT_ROOT,"output_csv","rakuten_edges.csv")
print(f"Rakutenデータ保存: {save_path}") 
rakuten_edge.to_csv(save_path,index=False)


print("前処理（日本食品標準成分表）============================")
nutrition_data_path = config.get("Data","nutrition_data_path")

def load_nutrition_data_from_folder(base_path, subfolder, column_mapping, header_row=4, sheet_name="表全体"):
    # フォルダパスを構築
    folder_path = os.path.join(base_path, subfolder)
    
    # このフォルダ内の全てのxlsxファイルを取得
    files = [f for f in os.listdir(folder_path) if f.endswith('.xlsx')]
    
    # 全データを格納する空のデータフレームを初期化
    all_nutrition_data = pd.DataFrame()
    
    for file in files:
        # ファイルからデータを読み込む
        file_path = os.path.join(folder_path, file)
        data = pd.read_excel(file_path, header=[header_row], sheet_name=sheet_name)
        
        # 列の名前を変更
        data = data.rename(columns=column_mapping)
        
        # 'food_code'がNAの行を削除
        data.dropna(subset=['food_code'], inplace=True)
        
        # 全データフレームにこのデータを追加
        all_nutrition_data = pd.concat([all_nutrition_data, data], ignore_index=True)
    
    return all_nutrition_data

### 成分表
column_mapping = {
    "Unnamed: 0":"food_group",
    "Unnamed: 1":"food_code",
    "Unnamed: 2":"reference_number",
    "成分識別子":"food_name",
    "Unnamed: 61":"note_all"
}
nutrition_data = load_nutrition_data_from_folder(nutrition_data_path,"mtx_01",column_mapping,header_row=11)

## アミノ酸成分表
amino_column_mapping = {
    "Unnamed: 0":"food_group",
    "Unnamed: 1":"food_code",
    "Unnamed: 2":"reference_number",
    "成分識別子":"food_name",
    "Unnamed: 31":"note_amino"
}
amino_nutrition_data = load_nutrition_data_from_folder(nutrition_data_path,"mtx_02",amino_column_mapping,header_row=4)

## 脂肪酸成分表
fat_column_mapping = {
    "Unnamed: 0":"food_group",
    "Unnamed: 1":"food_code",
    "Unnamed: 2":"reference_number",
    "成分識別子":"food_name",
    "Unnamed: 31":"note_fat"
}
fat_nutrition_data = load_nutrition_data_from_folder(nutrition_data_path,"mtx_03",fat_column_mapping,header_row=4)

## 炭水化物成分表
carb_column_mapping = {
    "Unnamed: 0":"food_group",
    "Unnamed: 1":"food_code",
    "Unnamed: 2":"reference_number",
    "成分識別子":"food_name",
    "Unnamed: 17":"note_carb"
}
carb_nutrition_data = load_nutrition_data_from_folder(nutrition_data_path,"mtx_04",carb_column_mapping,header_row=4)

print("食品数（成分表）:",len(nutrition_data))
print("食品数（アミノ酸成分表）:",len(amino_nutrition_data))
print("食品数（脂肪酸成分表）:",len(fat_nutrition_data))
print("食品数（炭水化物成分表）:",len(carb_nutrition_data))

print("")


all_frames = [nutrition_data, amino_nutrition_data, fat_nutrition_data, carb_nutrition_data]

all_nutrition_data = pd.concat(all_frames, axis=0, ignore_index=True)

def clean_and_classify(row):
    original = row  # オリジナルの文字列を保持
    if not isinstance(row, str) or row == '':
        return {
            'food_name_cleaned': '',
            'sub_category': '',
            'type_category': '',
            'mid_category': '',
            'small_category': ''
        }
    # 同じ処理を続けます...
    sub_category = re.search(r'＜(.*?)＞', row)
    row = re.sub(r'＜(.*?)＞', '', row)

    type_category = re.search(r'（(.*?)）', row)
    row = re.sub(r'（(.*?)）', '', row)

    mid_category = re.search(r'［(.*?)］', row)
    row = re.sub(r'［(.*?)］', '', row)

    small_category = row.strip()

    return {
        'food_name_cleaned': original,
        'sub_category': sub_category.group(1) if sub_category else '',
        'type_category': type_category.group(1) if type_category else '',
        'mid_category': mid_category.group(1) if mid_category else '',
        'small_category': small_category
    }

# 新しい列を追加
all_nutrition_data = all_nutrition_data.join(all_nutrition_data['food_name'].apply(lambda row: pd.Series(clean_and_classify(row))))

def katakana_to_hiragana(name):
    if isinstance(name, str):  # nameが文字列かどうかを確認
        return jaconv.kata2hira(name)
    else:
        return name
    
all_nutrition_data.dropna(subset=['food_name_cleaned'], inplace=True)
all_nutrition_data["food_name_cleaned"] = all_nutrition_data["food_name_cleaned"].apply(katakana_to_hiragana)
all_nutrition_data.dropna(subset=['food_code'], inplace=True)

# floatからintに変換（NaNがなくなったので問題なく変換できる）
all_nutrition_data['food_code'] = all_nutrition_data['food_code'].astype(int)

# intからstrに変換
all_nutrition_data['food_code'] = all_nutrition_data['food_code'].astype(str)


drop_col_ls = [
    'food_group',
    'food_code',
    'reference_number',
    'food_name_cleaned',
    'Unnamed: 14',
    'Unnamed: 17',
    'Unnamed: 32',
    'note_all',
    'note_amino',
    'Unnamed: 29',
    'Unnamed: 27',
    'Unnamed: 62',
    'Unnamed: 58',
    'Unnamed: 59',
    'note_carb',
    'Unnamed: 3',
    'Unnamed: 4',
    'プロスキー変法',
    'Unnamed: 6',
    'Unnamed: 7',
    'AOAC.2011.25法',
    'Unnamed: 9',
    'Unnamed: 10',
    'Unnamed: 11',
    'Unnamed: 12',
    'Unnamed: 13',
    'Unnamed: 28',
    'sub_category',
    'type_category',
    'mid_category',
    'small_category',
    ]
trg_col_ls = list(set(all_nutrition_data.columns) - set(drop_col_ls))

nutrition_edge_mtx = []
for index,row in tqdm(all_nutrition_data.iterrows(),total = len(all_nutrition_data)):
    food_name = row["food_name_cleaned"]
    food_code = row["food_code"]
    for nut_col in trg_col_ls:
        trg_value = row[nut_col]
        if isinstance(trg_value, (int, float)) and not math.isnan(trg_value):
            add_nutrition_edge_ls = [food_code,food_name,nut_col,trg_value,"ingredient-nutrition","seibunhyo"]
            nutrition_edge_mtx.append(add_nutrition_edge_ls)
nutrition_edge_df = pd.DataFrame(nutrition_edge_mtx,columns=["food_code","food_name","nutrition_name","value","edge_type","data_source"])

save_path = os.path.join(OUTPUT_ROOT,"output_csv","seibunhyo_edges.csv") 
print(f"成分表データ保存: {save_path}") 
nutrition_edge_df.to_csv(save_path,index=False)

print("すべての工程完了")