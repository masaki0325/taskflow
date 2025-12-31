# TaskFlow - Backend (FastAPI) コーディング規約

このファイルは、TaskFlowのバックエンド開発における詳細なルールとベストプラクティスを定義します。

## 技術スタック

```
FastAPI + Python 3.12
├── FastAPI         API Framework
├── SQLAlchemy 2.0  ORM (データベース操作)
├── Alembic         マイグレーション管理
├── Pydantic        バリデーション/スキーマ定義
├── pytest          テストフレームワーク
├── python-jose     JWT認証
├── passlib         パスワードハッシュ化
└── redis           キャッシュ/セッション管理
```

---

## ディレクトリ構成

```
backend/
├── app/
│   ├── main.py                  # FastAPIアプリのエントリーポイント
│   │
│   ├── core/                    # コア機能（設定、セキュリティ）
│   │   ├── __init__.py
│   │   ├── config.py           # 環境変数、設定
│   │   ├── security.py         # JWT、パスワードハッシュ
│   │   └── database.py         # DB接続、セッション管理
│   │
│   ├── models/                  # SQLAlchemyモデル（DBテーブル定義）
│   │   ├── __init__.py
│   │   ├── user.py             # Userテーブル
│   │   ├── task.py             # Taskテーブル
│   │   ├── project.py          # Projectテーブル
│   │   └── tag.py              # Tagテーブル
│   │
│   ├── schemas/                 # Pydanticスキーマ（バリデーション）
│   │   ├── __init__.py
│   │   ├── user.py             # UserCreate, UserUpdate, UserResponse
│   │   ├── task.py             # TaskCreate, TaskUpdate, TaskResponse
│   │   ├── project.py          # ProjectCreate, ProjectUpdate, ProjectResponse
│   │   └── token.py            # Token, TokenPayload
│   │
│   ├── api/                     # APIルート
│   │   ├── __init__.py
│   │   ├── deps.py             # 依存性注入（認証チェック、DB取得等）
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── auth.py         # 認証エンドポイント
│   │       ├── users.py        # ユーザー管理
│   │       ├── tasks.py        # タスク管理
│   │       ├── projects.py     # プロジェクト管理
│   │       └── tags.py         # タグ管理
│   │
│   ├── crud/                    # CRUD操作（DB操作ロジック）
│   │   ├── __init__.py
│   │   ├── base.py             # 基本CRUDクラス
│   │   ├── user.py             # ユーザーCRUD
│   │   ├── task.py             # タスクCRUD
│   │   └── project.py          # プロジェクトCRUD
│   │
│   └── tests/                   # テスト
│       ├── __init__.py
│       ├── conftest.py         # pytest設定、フィクスチャ
│       ├── test_auth.py        # 認証テスト
│       ├── test_tasks.py       # タスクテスト
│       └── test_users.py       # ユーザーテスト
│
├── alembic/                     # DBマイグレーション
│   ├── versions/               # マイグレーションファイル
│   └── env.py                  # Alembic設定
│
├── requirements.txt             # Python依存関係
├── Dockerfile                   # Dockerイメージ定義
└── pytest.ini                   # pytest設定
```

---

## コーディング規約

### 1. モデル定義（models/）

```python
# models/user.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class User(Base):
    """
    ユーザーモデル

    Attributes:
        id: ユーザーID（主キー）
        email: メールアドレス（ユニーク）
        username: ユーザー名
        hashed_password: ハッシュ化されたパスワード
        is_active: アクティブ状態
        is_superuser: 管理者フラグ
        created_at: 作成日時
        updated_at: 更新日時
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)

    # タイムスタンプ（自動設定）
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # リレーション
    tasks = relationship("Task", back_populates="owner")
    projects = relationship("Project", back_populates="owner")
```

### 2. スキーマ定義（schemas/）

```python
# schemas/user.py
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional

# リクエストスキーマ（入力）
class UserCreate(BaseModel):
    """ユーザー登録リクエスト"""
    email: EmailStr = Field(..., description="メールアドレス")
    username: str = Field(..., min_length=3, max_length=50, description="ユーザー名")
    password: str = Field(..., min_length=8, description="パスワード（最小8文字）")

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "username": "john_doe",
                "password": "SecurePass123!"
            }
        }

class UserUpdate(BaseModel):
    """ユーザー更新リクエスト"""
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None

# レスポンススキーマ（出力）
class UserResponse(BaseModel):
    """ユーザー情報レスポンス"""
    id: int
    email: str
    username: str
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True  # SQLAlchemyモデルから変換可能に
```

### 3. CRUD操作（crud/）

```python
# crud/user.py
from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash
from typing import Optional

class CRUDUser:
    """ユーザーCRUD操作"""

    def get(self, db: Session, id: int) -> Optional[User]:
        """IDでユーザーを取得"""
        return db.query(User).filter(User.id == id).first()

    def get_by_email(self, db: Session, email: str) -> Optional[User]:
        """メールアドレスでユーザーを取得"""
        return db.query(User).filter(User.email == email).first()

    def create(self, db: Session, obj_in: UserCreate) -> User:
        """新規ユーザーを作成"""
        db_obj = User(
            email=obj_in.email,
            username=obj_in.username,
            hashed_password=get_password_hash(obj_in.password),
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, db_obj: User, obj_in: UserUpdate) -> User:
        """ユーザー情報を更新"""
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

# シングルトンインスタンス
user = CRUDUser()
```

### 4. APIエンドポイント（api/v1/）

```python
# api/v1/users.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.api import deps
from app.crud import user as crud_user
from app.schemas.user import UserResponse, UserUpdate
from app.models.user import User

router = APIRouter()

@router.get("/me", response_model=UserResponse)
def read_current_user(
    current_user: User = Depends(deps.get_current_user)
) -> User:
    """
    現在ログイン中のユーザー情報を取得

    Returns:
        UserResponse: ユーザー情報
    """
    return current_user

@router.put("/me", response_model=UserResponse)
def update_current_user(
    user_in: UserUpdate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
) -> User:
    """
    現在ログイン中のユーザー情報を更新

    Args:
        user_in: 更新するユーザー情報
        db: データベースセッション
        current_user: 現在のユーザー

    Returns:
        UserResponse: 更新後のユーザー情報
    """
    user = crud_user.user.update(db, db_obj=current_user, obj_in=user_in)
    return user

@router.get("/{user_id}", response_model=UserResponse)
def read_user(
    user_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
) -> User:
    """
    指定されたIDのユーザー情報を取得

    Args:
        user_id: ユーザーID
        db: データベースセッション
        current_user: 現在のユーザー（認証チェック）

    Returns:
        UserResponse: ユーザー情報

    Raises:
        HTTPException: ユーザーが見つからない場合（404）
    """
    user = crud_user.user.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user
```

### 5. 依存性注入（api/deps.py）

```python
# api/deps.py
from typing import Generator
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.core.config import settings
from app.core.security import ALGORITHM
from app.crud import user as crud_user
from app.models.user import User
from app.schemas.token import TokenPayload

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

def get_db() -> Generator:
    """
    データベースセッションを取得

    Yields:
        Session: SQLAlchemyセッション
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> User:
    """
    JWTトークンから現在のユーザーを取得

    Args:
        db: データベースセッション
        token: JWTアクセストークン

    Returns:
        User: 現在のユーザー

    Raises:
        HTTPException: トークンが無効な場合（401）
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[ALGORITHM]
        )
        user_id: int = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        token_data = TokenPayload(sub=user_id)
    except JWTError:
        raise credentials_exception

    user = crud_user.user.get(db, id=token_data.sub)
    if user is None:
        raise credentials_exception

    return user

def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    アクティブなユーザーのみ取得

    Args:
        current_user: 現在のユーザー

    Returns:
        User: アクティブなユーザー

    Raises:
        HTTPException: ユーザーが非アクティブの場合（400）
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user
```

---

## テスト

### テストの書き方（tests/）

```python
# tests/test_users.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.config import settings
from app.schemas.user import UserCreate
from app.crud import user as crud_user

def test_create_user(client: TestClient, db: Session):
    """ユーザー作成が正常に動作することを確認"""
    response = client.post(
        f"{settings.API_V1_STR}/auth/register",
        json={
            "email": "test@example.com",
            "username": "testuser",
            "password": "SecurePass123!"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["username"] == "testuser"
    assert "password" not in data  # パスワードを返さない
    assert "id" in data

def test_read_current_user(
    client: TestClient,
    db: Session,
    normal_user_token_headers: dict
):
    """認証済みユーザーの情報取得を確認"""
    response = client.get(
        f"{settings.API_V1_STR}/users/me",
        headers=normal_user_token_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert "email" in data
    assert "username" in data

def test_read_user_unauthorized(client: TestClient):
    """未認証でのアクセスが拒否されることを確認"""
    response = client.get(f"{settings.API_V1_STR}/users/me")
    assert response.status_code == 401
```

---

## データベースマイグレーション

### Alembicの使い方

```bash
# 新しいマイグレーションを自動生成
alembic revision --autogenerate -m "Add users table"

# マイグレーションを適用
alembic upgrade head

# 1つ前のマイグレーションに戻す
alembic downgrade -1

# マイグレーション履歴を確認
alembic history
```

### マイグレーションファイルのレビュー

```python
# alembic/versions/xxx_add_users_table.py
def upgrade():
    """マイグレーション適用"""
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('username', sa.String(), nullable=False),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)

def downgrade():
    """マイグレーションを戻す"""
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
```

---

## 注意事項

### やってはいけないこと

```python
# ❌ 生のSQLを直接実行（SQL Injection の危険）
db.execute(f"SELECT * FROM users WHERE email = '{email}'")

# ✅ ORMを使う
db.query(User).filter(User.email == email).first()

# ❌ パスワードを平文で保存
user.password = "mypassword"

# ✅ ハッシュ化して保存
user.hashed_password = get_password_hash("mypassword")

# ❌ すべての例外をキャッチ
try:
    ...
except:  # 何の例外かわからない
    pass

# ✅ 具体的な例外をキャッチ
try:
    ...
except ValueError as e:
    logger.error(f"Invalid value: {e}")
    raise HTTPException(status_code=400, detail=str(e))
```

---

**バックエンド開発時はこのガイドに従ってください！**
