# ============================================================
# インポート: 必要なライブラリやモジュールを読み込む
# ============================================================

# FastAPI: Pythonの高速なWebフレームワーク (Node.jsのExpressに似ている)
from fastapi import FastAPI

# CORS (Cross-Origin Resource Sharing) ミドルウェア
# フロントエンド (Next.js) からAPIへのアクセスを許可するために必要
from fastapi.middleware.cors import CORSMiddleware

# 非同期コンテキストマネージャー (将来的にDB接続やRedis接続の管理に使用)
from contextlib import asynccontextmanager

# Redis の非同期クライアント (キャッシュ、セッション管理などに使用)
import redis.asyncio as redis


# ============================================================
# FastAPIアプリケーションの初期化
# ============================================================

# FastAPIのインスタンスを作成
# このappオブジェクトがAPIサーバーのメインオブジェクトになる
app = FastAPI(
    title="TaskFlow API",                      # APIのタイトル (ドキュメントに表示される)
    description="Task Management SaaS API",    # APIの説明
    version="1.0.0",                           # APIのバージョン
    docs_url="/docs",                          # Swagger UI のURL (自動生成されるAPIドキュメント)
    redoc_url="/redoc",                        # ReDoc のURL (別のドキュメント表示方法)
)


# ============================================================
# CORS (Cross-Origin Resource Sharing) の設定
# ============================================================
# フロントエンド (ブラウザ) から異なるドメインのAPIにアクセスする際に必要
# 例: フロントエンド (localhost:3000) → バックエンド (localhost:8000)

app.add_middleware(
    CORSMiddleware,                              # CORSミドルウェアを追加
    allow_origins=["http://localhost:3000"],     # アクセスを許可するオリジン (Next.js開発サーバー)
    allow_credentials=True,                      # Cookie、認証ヘッダーの送信を許可
    allow_methods=["*"],                         # すべてのHTTPメソッドを許可 (GET, POST, PUT, DELETE など)
    allow_headers=["*"],                         # すべてのHTTPヘッダーを許可
)


# ============================================================
# エンドポイント定義
# ============================================================

# ルートエンドポイント (トップページ)
# @app.get("/") はデコレータ: GETリクエストを"/"パスで受け付ける
# async def は非同期関数: 複数のリクエストを効率的に処理できる
@app.get("/")
async def root():
    """
    ルートエンドポイント

    http://localhost:8000/ にアクセスした際に呼び出される
    APIの基本情報を返す
    """
    # 辞書 (dict) を返すと、FastAPIが自動的にJSON形式に変換してレスポンスする
    return {
        "message": "Welcome to TaskFlow API",
        "version": "1.0.0",
        "docs": "/docs",
    }


# ヘルスチェックエンドポイント
# サーバーが正常に動作しているか確認するためのエンドポイント
# Docker、Kubernetes、監視ツールなどがこのエンドポイントを定期的にチェックする
@app.get("/health")
async def health_check():
    """
    ヘルスチェックエンドポイント

    http://localhost:8000/health にアクセスすると、
    サーバーが正常に動作しているか確認できる
    """
    return {
        "status": "healthy",           # サーバーの状態
        "service": "TaskFlow API",     # サービス名
    }


# APIバージョン付きヘルスチェック
# /api/v1/ 配下のエンドポイント
# 将来的にAPIのバージョンを変更する場合に備えて、バージョンをURLに含める
@app.get("/api/v1/health")
async def api_health_check():
    """
    APIバージョン付きヘルスチェック

    http://localhost:8000/api/v1/health にアクセス
    APIのバージョンを確認できる
    """
    return {
        "status": "healthy",
        "api_version": "v1",           # APIのバージョン
    }


# ============================================================
# FastAPIの基本的な使い方のまとめ
# ============================================================
#
# 1. エンドポイントの定義:
#    @app.get("/path")    → GETリクエスト
#    @app.post("/path")   → POSTリクエスト
#    @app.put("/path")    → PUTリクエスト
#    @app.delete("/path") → DELETEリクエスト
#
# 2. パスパラメータ:
#    @app.get("/users/{user_id}")
#    async def get_user(user_id: int):
#        return {"user_id": user_id}
#
# 3. クエリパラメータ:
#    @app.get("/items")
#    async def get_items(skip: int = 0, limit: int = 10):
#        return {"skip": skip, "limit": limit}
#
# 4. リクエストボディ:
#    from pydantic import BaseModel
#
#    class Item(BaseModel):
#        name: str
#        price: float
#
#    @app.post("/items")
#    async def create_item(item: Item):
#        return {"name": item.name, "price": item.price}
#
# 5. ドキュメント:
#    http://localhost:8000/docs で自動生成されたAPIドキュメントが見られる
#
# ============================================================
