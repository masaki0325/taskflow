from pydantic import BaseModel, EmailStr, ConfigDict, Field
from datetime import datetime


# ===============================================
# ユーザースキーマ（Pydantic）
# ===============================================
# 役割: APIリクエスト/レスポンスのデータ検証とシリアライズ
#
# models/user.py との違い:
#   models/user.py  → データベースのテーブル構造（SQLAlchemy）
#   schemas/user.py → APIのデータ検証（Pydantic）


class UserBase(BaseModel):
    """
    ユーザーの共通フィールド

    他のスキーマで継承して使う
    """
    # EmailStr: Pydanticが自動的にメールアドレス形式を検証
    # "test@example.com" → OK
    # "invalid-email" → エラー
    email: EmailStr


class UserCreate(UserBase):
    """
    ユーザー作成時のスキーマ（POST /api/v1/auth/register）

    パスワードを含む（登録時のみ）

    使用例:
        リクエスト:
        {
          "email": "test@example.com",
          "password": "Password123"
        }
    """
    password: str = Field(
        ...,  # 必須フィールド（...は「必須」を意味する）
        min_length=8,  # 最小8文字（セキュリティ要件）
        description="パスワード（最小8文字、英大文字・小文字・数字を含む）",
    )


class UserUpdate(BaseModel):
    """
    ユーザー更新時のスキーマ（PUT /api/v1/users/{id}）

    全てのフィールドはオプション（一部だけ更新できる）

    使用例:
        リクエスト（メールアドレスだけ変更）:
        {
          "email": "new@example.com"
        }

        リクエスト（パスワードだけ変更）:
        {
          "password": "NewPassword123"
        }
    """
    # | None = None でオプショナルにする
    email: EmailStr | None = None
    password: str | None = Field(None, min_length=8)
    is_active: bool | None = None


class UserResponse(UserBase):
    """
    APIレスポンス用スキーマ（GET /api/v1/auth/me など）

    セキュリティ要件: パスワード（hashed_password）を含まない

    使用例:
        レスポンス:
        {
          "id": 1,
          "email": "test@example.com",
          "is_active": true,
          "is_superuser": false,
          "created_at": "2026-01-01T10:00:00Z",
          "updated_at": "2026-01-01T10:00:00Z"
        }
        ※ passwordやhashed_passwordは含まれない
    """
    id: int
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime

    # Pydantic V2構文: ORMモデル（SQLAlchemy）からの変換を許可
    # from_attributes=True: user.id, user.email などの属性から自動変換
    #
    # 使用例:
    #   db_user = db.query(User).first()  # SQLAlchemyモデル
    #   return UserResponse.model_validate(db_user)  # Pydanticスキーマに変換
    model_config = ConfigDict(from_attributes=True)


class UserInDB(UserResponse):
    """
    データベース内部用スキーマ

    hashed_passwordを含む（API応答には使わない）

    用途: CRUD操作やパスワード検証などの内部処理
    """
    hashed_password: str
