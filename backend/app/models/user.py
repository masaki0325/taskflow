from sqlalchemy import Boolean, Column, Integer, String, DateTime
from sqlalchemy.sql import func

from app.core.database import Base


class User(Base):
    """
    ユーザーモデル（SQLAlchemy ORM）

    このクラスがPostgreSQLの "users" テーブルに対応する
    Base.metadata.create_all() でテーブルが自動作成される

    認証とユーザー管理に使用
    """
    # テーブル名を指定（PostgreSQLに作成されるテーブル名）
    __tablename__ = "users"

    # ===============================================
    # カラム定義
    # ===============================================

    # 主キー（自動インクリメント）
    id = Column(
        Integer,
        primary_key=True,  # 主キー
        index=True         # インデックスを作成（検索を高速化）
    )

    # メールアドレス（ログインID）
    email = Column(
        String,
        unique=True,       # 重複不可（同じメールアドレスは登録できない）
        index=True,        # インデックスを作成（ログイン時の検索を高速化）
        nullable=False     # NULL不可（必須項目）
    )

    # パスワードハッシュ
    # セキュリティ要件: 平文パスワードは保存しない（bcryptでハッシュ化）
    hashed_password = Column(
        String,
        nullable=False     # NULL不可（必須項目）
    )

    # アカウント有効フラグ
    is_active = Column(
        Boolean,
        default=True,      # デフォルト値: True（新規ユーザーは有効）
        nullable=False
    )

    # 管理者権限フラグ
    is_superuser = Column(
        Boolean,
        default=False,     # デフォルト値: False（一般ユーザー）
        nullable=False
    )

    # ===============================================
    # タイムスタンプ
    # ===============================================

    # 作成日時
    created_at = Column(
        DateTime(timezone=True),  # タイムゾーン付き日時
        server_default=func.now(),  # DB側で現在時刻を自動設定
        nullable=False
    )

    # 更新日時
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),  # 作成時に現在時刻を設定
        onupdate=func.now(),        # 更新時に現在時刻を自動更新
        nullable=False
    )

    # ===============================================
    # デバッグ用の文字列表現
    # ===============================================
    def __repr__(self):
        """
        print(user) した時の表示
        例: <User(id=1, email=test@example.com)>
        """
        return f"<User(id={self.id}, email={self.email})>"
