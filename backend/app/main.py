from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from sqladmin import Admin, ModelView

from app.core.config import settings
from app.core.database import engine, Base
from app.models.user import User


# アプリケーション起動時・終了時の処理
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    アプリケーションのライフサイクル管理
    
    起動時: データベーステーブルを作成
    終了時: クリーンアップ処理（必要に応じて）
    """
    # 起動時: 全てのテーブルを作成
    # Base.metadata.create_all() は、Baseを継承した全てのモデルのテーブルを作成
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created")
    
    yield  # アプリケーション実行中
    
    # 終了時の処理（必要に応じて追加）
    print("🛑 Application shutdown")


# FastAPIアプリケーションインスタンス
app = FastAPI(
    title="TaskFlow API",
    description="タスク管理SaaSのバックエンドAPI",
    version="1.0.0",
    lifespan=lifespan,
)


# CORSミドルウェアの設定
# セキュリティ要件: ホワイトリスト形式でオリジンを制限
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,  # .envで設定したオリジンのみ許可
    allow_credentials=True,  # Cookie送信を許可（JWT用）
    allow_methods=["*"],  # 全てのHTTPメソッド許可
    allow_headers=["*"],  # 全てのヘッダー許可
)


# ヘルスチェックエンドポイント
@app.get("/health", tags=["Health"])
def health_check():
    """
    サーバーの稼働状況を確認するエンドポイント
    
    AWS ECSのヘルスチェックや監視ツールで使用
    """
    return {
        "status": "ok",
        "environment": settings.ENVIRONMENT,
    }


# ルート エンドポイント
@app.get("/", tags=["Root"])
def root():
    """
    APIのルートエンドポイント
    """
    return {
        "message": "Welcome to TaskFlow API",
        "docs": "/docs",
        "health": "/health",
    }


# 認証APIルーターを登録
from app.api.v1 import auth

app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])

# TODO: タスクAPIルーターを追加
# app.include_router(tasks.router, prefix="/api/v1/tasks", tags=["Tasks"])


# ===============================================
# 管理画面（SQLAdmin）
# ===============================================
# TODO: 本番環境デプロイ前に認証を追加する必要がある
#       - AuthenticationBackend を実装してログイン機能を追加
#       - または環境変数で開発環境のみ有効化（settings.ENVIRONMENT == "development"）
#       現在は開発用途のため認証なし

# SQLAdmin の初期化
admin = Admin(app, engine, title="TaskFlow 管理画面")


# ユーザー管理画面
class UserAdmin(ModelView, model=User):
    # 一覧に表示するカラム
    column_list = [User.id, User.email, User.is_active, User.is_superuser, User.created_at]

    # パスワードハッシュだけ非表示（セキュリティ対策）
    form_excluded_columns = [User.hashed_password]


# 管理画面に登録
admin.add_view(UserAdmin)
