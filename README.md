# 日本語レシピ知識グラフ (version 1.0)
## 概要
日本語データで作成したレシピー食材ー栄養素の知識グラフです．

## 処理方法
知識グラフの作成にはレシピデータとして**クックパッドデータ**，**楽天レシピデータ**を，栄養素データとして，
**日本語食品標準成分表データが**必要です．

## 結果
### グラフ統計量
 

---
---
# 実行方法
## 1.データ準備
このリポジトリでは，Cookpadデータセットと楽天レシピ,日本語食品成分表のデータが必要です．
### レシピデータ
ダウンロードには国立情報学研究所との契約が必要です．
それぞれのデータは以下のディレクトリになるように設置してください．
```python 
├─data_recipe_Cookpad # Cookpadデータ(5.56GB)
│      cookpad_data.sql
│
├─data_recipe_Rakuten #楽天データ (910 MB)
│      recipe01_all_20170118.txt
│      recipe02_material_20160112.txt
│      recipe03_process_20160112.txt
│      recipe04_tsukurepo_20160112.txt
```

### 日本食品標準成分表データ
文科省から出ている日本食品成分表をダウンロードしてください．
このリポジトリでは[日本食品標準成分表（八訂）増補2023年](https://www.mext.go.jp/a_menu/syokuhinseibun/mext_00001.html)を使用します．

すべてのデータを以下のようなディレクトリ構造で保存してください．
(7.69 MB)
```
├─mtx_01 #成分表
│      20230428-mxt_kagsei-mext_00001_012.xlsx
│
├─mtx_02 #アミノ酸成分表
│      20230428-mxt_kagsei-mext_00001_022.xlsx
│      20230428-mxt_kagsei-mext_00001_023.xlsx
│      20230428-mxt_kagsei-mext_00001_024.xlsx
│      20230428-mxt_kagsei-mext_00001_025.xlsx
│
├─mtx_03 #脂肪酸成分表
│      20230428-mxt_kagsei-mext_00001_032.xlsx
│      20230428-mxt_kagsei-mext_00001_033.xlsx
│      20230428-mxt_kagsei-mext_00001_034.xlsx
│
└─mtx_04 #炭水化物成分表
        20230428-mxt_kagsei-mext_00001_042.xlsx
        20230428-mxt_kagsei-mext_00001_043.xlsx
        20230428-mxt_kagsei-mext_00001_044.xlsx
```
---
## 2.環境
### python
このリポジトリは以下の環境で動きます．
- python:
- pip:

上記の環境のもと，以下のコマンドでモジュールをインストールしてください．
```
pip install -r requirment.txt
```

### 環境設定
cookpad_data.sqlを基にDockerなどでMysqlサーバを構築．
config.intファイルを各々の環境に合わせてポート・パスを改変してください.

```python
cookpad_db = 3306 #CookpadのDBサーバのポート番号
rakuten_data_path = /path/to/rakuten #楽天データのパス
nutrition_data_path = /path/to/nutrition_data #日本食品標準成分表データ
```

## 3.前処理

---
### バージョン履歴
- version1.0.0 リポジトリ公開