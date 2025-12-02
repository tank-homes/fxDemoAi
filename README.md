# FX Auto Trading Simulator (FastAPI + WebSocket)

このプロジェクトは FastAPI と WebSocket、そして簡易的な機械学習（RandomForest）を使って  
「3分間の自動売買をリアルタイムで可視化する FX シミュレーター」です。

HTML UI から：
- 通貨ペアの選択  
- レバレッジ  
- 初期残高  
- 売買閾値（買い／売り）  
を設定し、WebSocket により 5 秒おきにリアルタイムで価格・予測・総資産が更新されます。



## 🔧 使用技術
- FastAPI
- WebSocket
- yfinance（リアル相場データ取得）
- scikit-learn（RandomForest）
- Chart.js（価格グラフ）
- HTML & JavaScript


## 📁 ディレクトリ構成

fastApiStudy/
├─ main.py
├─ requirements.txt
└─ templates/
└─ index.html



## 🚀 セットアップ

### 1. リポジトリのクローン

git clone https://github.com/tank-homes/fxDemoAi


### 2. 仮想環境の作成（任意）

python -m venv venv
.\venv\Scripts\activate


### 3. 依存パッケージのインストール

pip install -r requirements.txt



## ▶️ 実行

python -m uvicorn main:app --reload


ブラウザで：

http://127.0.0.1:8000

を開いてください。


## 機能

### ✔ 3分間の自動売買（リアルタイム更新）

- 5 秒周期で yfinance から最新価格を取得
- RandomForest による「次の価格予測」
- 閾値を超えたら自動で買い/売り
- 総資産を WebSocket で UI に送信して表示

### ✔ UI 機能
- 通貨ペア選択（USDJPY, EURUSD, GBPJPY など）
- レバレッジ設定
- 初期残高設定
- 売買閾値設定
- 価格チャート（Chart.js）
- 売買履歴テーブル

---
