from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from typing import Generator

from app.core.config import settings


# SQLAlchemyエンジンの作成
# データベース接続を管理するオブジェクト
# pool_pre_ping=True: コネクションプールから接続を取得する前に、接続が有効かチェック
#                     → DBサーバーが再起動した場合でも自動的に再接続できる
engine = create_engine(
    settings.DATABASE_URL,  # config.pyから読み込んだDB接続URL
    pool_pre_ping=True,
)

# セッションファクトリーの作成
# セッション: DBへのクエリ実行やトランザクション管理を行うオブジェクト
# autocommit=False: 明示的にcommit()を呼ぶまでコミットしない（トランザクション管理）
# autoflush=False: 明示的にflush()を呼ぶまでDBに反映しない
# bind=engine: このエンジンを使用してDB接続する
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

# 全てのモデルのベースクラス
# これを継承してUserモデル、Taskモデルなどを作成する
# Base.metadata.create_all(bind=engine) でテーブルを自動作成できる
Base = declarative_base()


# FastAPIの依存性注入で使用するDB接続
# yieldを使うことで、リクエスト処理後に自動的にdb.close()が呼ばれる
def get_db() -> Generator:
    """
    データベースセッションを提供する依存性注入関数

    使用例:
        @app.get("/users")
        def get_users(db: Session = Depends(get_db)):
            users = db.query(User).all()
            return users

    処理フロー:
        1. リクエスト開始 → SessionLocal()でセッション作成
        2. yield db → セッションを関数に渡す
        3. リクエスト終了 → finally ブロックで db.close() 実行
    """
    db = SessionLocal()
    try:
        yield db  # ここで一時停止し、関数にdbを渡す
    finally:
        db.close()  # リクエスト終了後、必ずDB接続をクローズ
