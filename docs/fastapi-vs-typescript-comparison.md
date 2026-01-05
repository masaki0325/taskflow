# FastAPI（Python）vs TypeScript - バックエンド開発比較ガイド

このドキュメントは、TaskFlowプロジェクトで実装した認証APIを例に、FastAPI（Python）とTypeScriptでバックエンドを構築する場合の違いを比較します。

## 📋 目次

1. [比較サマリー](#比較サマリー)
2. [スキーマ定義](#1-スキーマ定義)
3. [JWT生成](#2-jwt生成)
4. [パスワードハッシュ化](#3-パスワードハッシュ化)
5. [データベース操作](#4-データベース操作)
6. [APIエンドポイント](#5-apiエンドポイント)
7. [認証ミドルウェア](#6-認証ミドルウェア)
8. [主な違いまとめ](#主な違いまとめ)

---

## 比較サマリー

| 項目 | FastAPI（Python） | TypeScript（Next.js/Express） |
|------|-------------------|------------------------------|
| **コードスタイル** | 宣言的（Declarative） | 命令的（Imperative） |
| **ボイラープレート** | 少ない | 多い |
| **型安全性** | Pydantic（実行時検証） | Zod/TypeScript（コンパイル時 + 実行時） |
| **ドキュメント生成** | 自動（OpenAPI/Swagger） | 手動設定必要 |
| **依存性注入** | 組み込み（`Depends()`） | 手動実装 |
| **ORM** | SQLAlchemy 2.0 | Prisma/TypeORM |
| **エラーハンドリング** | 自動 | 手動try/catch |
| **開発速度** | 速い | やや遅い |
| **エコシステム** | データサイエンス寄り | Web開発全般 |

---

## 1. スキーマ定義

### FastAPI（Pydantic）

```python
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import datetime

class UserCreate(BaseModel):
    """ユーザー作成リクエスト"""
    email: EmailStr
    password: str = Field(..., min_length=8)

class UserResponse(BaseModel):
    """ユーザーレスポンス（パスワードを除外）"""
    id: int
    email: str
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)  # SQLAlchemyモデルから自動変換
```

**特徴:**
- `EmailStr`: メールアドレス形式を自動検証
- `Field()`: バリデーションルール定義
- `model_config = ConfigDict(from_attributes=True)`: ORMモデル → Pydanticモデルの自動変換（Pydantic V2形式）

---

### TypeScript（Zod）

```typescript
import { z } from 'zod';

// リクエストスキーマ
const userCreateSchema = z.object({
  email: z.string().email(),
  password: z.string().min(8),
});

// レスポンス型
interface UserResponse {
  id: number;
  email: string;
  is_active: boolean;
  is_superuser: boolean;
  created_at: Date;
  updated_at: Date;
}

// リクエストボディをパース
const parseUserCreate = (body: unknown) => {
  return userCreateSchema.parse(body);
};
```

**特徴:**
- Zodで実行時バリデーション（TypeScriptはコンパイル時のみ）
- `interface`: 型定義（コンパイル時にのみ存在）
- パース処理を手動で実装

---

## 2. JWT生成

### FastAPI（python-jose）

```python
from datetime import datetime, timedelta, UTC
from jose import jwt
from app.core.config import settings

def create_access_token(data: dict) -> str:
    """Access Token（15分有効）を生成"""
    to_encode = data.copy()
    expire = datetime.now(UTC) + timedelta(minutes=15)
    to_encode.update({"exp": expire, "type": "access"})

    return jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm="HS256"
    )
```

**特徴:**
- シンプルな関数定義
- 設定は`settings`から自動読み込み（Pydantic Settings）
- 型ヒントで引数・戻り値を明示

---

### TypeScript（jsonwebtoken）

```typescript
import jwt from 'jsonwebtoken';

function createAccessToken(data: { sub: string }): string {
  const SECRET_KEY = process.env.SECRET_KEY!;
  const expire = Math.floor(Date.now() / 1000) + 15 * 60; // 15分

  return jwt.sign(
    {
      ...data,
      exp: expire,
      type: 'access',
    },
    SECRET_KEY,
    { algorithm: 'HS256' }
  );
}
```

**特徴:**
- 環境変数を手動取得（`process.env.SECRET_KEY!`）
- Unix timestampへの変換が必要
- 設定を関数内で直接記述

---

## 3. パスワードハッシュ化

### FastAPI（passlib + bcrypt）

```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """パスワードをbcryptでハッシュ化"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """パスワードを検証"""
    return pwd_context.verify(plain_password, hashed_password)
```

**特徴:**
- `CryptContext`: 複数のハッシュアルゴリズムをサポート
- `deprecated="auto"`: 古いアルゴリズムを自動検出
- ソルト自動生成

---

### TypeScript（bcryptjs）

```typescript
import bcrypt from 'bcryptjs';

async function hashPassword(password: string): Promise<string> {
  const saltRounds = 10;
  return await bcrypt.hash(password, saltRounds);
}

async function verifyPassword(
  plainPassword: string,
  hashedPassword: string
): Promise<boolean> {
  return await bcrypt.compare(plainPassword, hashedPassword);
}
```

**特徴:**
- 非同期関数（`async/await`）
- `saltRounds`を明示的に指定
- 基本的な機能はFastAPIと同じ

---

## 4. データベース操作

### FastAPI（SQLAlchemy 2.0）

```python
from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate
from app.core.security import hash_password

def create_user(db: Session, user_create: UserCreate) -> User:
    """新規ユーザーを作成"""
    hashed_password = hash_password(user_create.password)

    db_user = User(
        email=user_create.email,
        hashed_password=hashed_password,
        is_active=True,
        is_superuser=False,
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user
```

**特徴:**
- ORMモデル（`User`）で型安全にデータ操作
- トランザクション管理（`commit()`）
- `refresh()`: DBから最新データを取得

---

### TypeScript（Prisma）

```typescript
import { PrismaClient } from '@prisma/client';
import { hashPassword } from './security';

const prisma = new PrismaClient();

async function createUser(email: string, password: string) {
  const hashedPassword = await hashPassword(password);

  const user = await prisma.user.create({
    data: {
      email,
      hashed_password: hashedPassword,
      is_active: true,
      is_superuser: false,
    },
  });

  return user;
}
```

**特徴:**
- Prismaで型安全なクエリ（自動生成された型）
- 非同期処理（`async/await`）
- トランザクションは自動管理

---

## 5. APIエンドポイント

### FastAPI

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.user import UserCreate, UserResponse
from app.crud.user import create_user, get_user_by_email

router = APIRouter()

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_create: UserCreate, db: Session = Depends(get_db)):
    """ユーザー登録"""
    # メールアドレスの重複チェック
    existing_user = get_user_by_email(db, user_create.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # ユーザー作成
    user = create_user(db, user_create)
    return user
```

**特徴:**
- **自動バリデーション**: `UserCreate`でリクエストボディを検証
- **依存性注入**: `Depends(get_db)`でDBセッションを自動注入
- **自動ドキュメント**: OpenAPI/Swaggerが自動生成される
- **型安全なレスポンス**: `response_model=UserResponse`でパスワードを自動除外

**自動生成されるドキュメント:**
```
http://localhost:8000/docs
```
- リクエスト/レスポンススキーマ表示
- インタラクティブなAPI試行
- curl/HTTPクライアントのコード生成

---

### TypeScript（Next.js App Router）

```typescript
import { NextRequest, NextResponse } from 'next/server';
import { z } from 'zod';
import { prisma } from '@/lib/prisma';
import { hashPassword } from '@/lib/security';

const userCreateSchema = z.object({
  email: z.string().email(),
  password: z.string().min(8),
});

export async function POST(request: NextRequest) {
  try {
    // ①リクエストボディをパース
    const body = await request.json();

    // ②Zodでバリデーション（手動）
    const { email, password } = userCreateSchema.parse(body);

    // ③メールアドレスの重複チェック（手動）
    const existingUser = await prisma.user.findUnique({
      where: { email },
    });

    if (existingUser) {
      return NextResponse.json(
        { error: 'Email already registered' },
        { status: 400 }
      );
    }

    // ④ユーザー作成
    const hashedPassword = await hashPassword(password);
    const user = await prisma.user.create({
      data: {
        email,
        hashed_password: hashedPassword,
        is_active: true,
        is_superuser: false,
      },
      select: {
        id: true,
        email: true,
        is_active: true,
        is_superuser: true,
        created_at: true,
        updated_at: true,
        // hashed_passwordは除外
      },
    });

    return NextResponse.json(user, { status: 201 });

  } catch (error) {
    if (error instanceof z.ZodError) {
      return NextResponse.json(
        { error: 'Validation error', details: error.errors },
        { status: 400 }
      );
    }

    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}
```

**特徴:**
- **手動バリデーション**: Zodで明示的にパース
- **手動エラーハンドリング**: try/catchで全てのエラーを処理
- **手動レスポンス制御**: `select`でフィールドを明示的に除外
- **ドキュメント**: 自動生成なし（Swagger設定が必要）

---

## 6. 認証ミドルウェア

### FastAPI（依存性注入）

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from jose import JWTError
from app.core.security import decode_token
from app.core.database import get_db
from app.crud.user import get_user_by_email
from app.models.user import User

security = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    """現在のユーザーを取得（依存性注入用）"""
    token = credentials.credentials

    try:
        payload = decode_token(token)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        ) from None

    # トークンタイプの確認
    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
        )

    user_email = payload.get("sub")
    if not user_email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    user = get_user_by_email(db, user_email)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return user

# 使用例
@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """現在のユーザー情報を取得"""
    return current_user
```

**特徴:**
- **依存性注入**: `Depends(get_current_user)`で認証を宣言的に追加
- **自動実行**: FastAPIが関数を自動的に呼び出す
- **型安全**: `current_user: User`で型が保証される
- **コード量**: エンドポイント実装は1行

---

### TypeScript（手動実装）

```typescript
import { NextRequest, NextResponse } from 'next/server';
import jwt from 'jsonwebtoken';
import { prisma } from '@/lib/prisma';

// 認証ミドルウェア（関数として再利用可能）
async function getCurrentUser(request: NextRequest) {
  const authHeader = request.headers.get('authorization');

  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    throw new Error('No token provided');
  }

  const token = authHeader.substring(7);

  try {
    const payload = jwt.verify(token, process.env.SECRET_KEY!) as {
      sub: string;
      type: string;
    };

    // トークンタイプの確認
    if (payload.type !== 'access') {
      throw new Error('Invalid token type');
    }

    const user = await prisma.user.findUnique({
      where: { email: payload.sub },
    });

    if (!user || !user.is_active) {
      throw new Error('User not found');
    }

    return user;

  } catch (error) {
    throw new Error('Invalid token');
  }
}

// 使用例
export async function GET(request: NextRequest) {
  try {
    // ①認証処理を手動で呼び出し
    const currentUser = await getCurrentUser(request);

    // ②ユーザー情報を返す
    return NextResponse.json({
      id: currentUser.id,
      email: currentUser.email,
      is_active: currentUser.is_active,
      is_superuser: currentUser.is_superuser,
      created_at: currentUser.created_at,
      updated_at: currentUser.updated_at,
    });

  } catch (error) {
    const message = error instanceof Error ? error.message : 'Authentication failed';
    return NextResponse.json(
      { error: message },
      { status: 401 }
    );
  }
}
```

**特徴:**
- **手動呼び出し**: 各エンドポイントで`getCurrentUser()`を明示的に呼ぶ
- **try/catch**: エラーハンドリングを毎回記述
- **関数再利用**: `getCurrentUser()`を共通関数として定義可能
- **コード量**: エンドポイント実装は5-10行

---

## 主な違いまとめ

### 1. コード量の違い

**FastAPIエンドポイント（保護されたAPI）:**
```python
@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user
```
**コード行数: 3行**

---

**TypeScriptエンドポイント（保護されたAPI）:**
```typescript
export async function GET(request: NextRequest) {
  try {
    const currentUser = await getCurrentUser(request);
    return NextResponse.json({
      id: currentUser.id,
      email: currentUser.email,
      is_active: currentUser.is_active,
      is_superuser: currentUser.is_superuser,
      created_at: currentUser.created_at,
      updated_at: currentUser.updated_at,
    });
  } catch (error) {
    const message = error instanceof Error ? error.message : 'Authentication failed';
    return NextResponse.json(
      { error: message },
      { status: 401 }
    );
  }
}
```
**コード行数: 18行**

---

### 2. ドキュメント生成

| FastAPI | TypeScript |
|---------|------------|
| ✅ **自動生成** | ❌ 手動設定必要 |
| `http://localhost:8000/docs` にアクセスするだけ | Swagger/OpenAPI設定を別途実装 |
| リクエスト/レスポンススキーマ自動表示 | スキーマを手動で記述 |
| インタラクティブなAPI試行機能 | 別途ツール導入が必要 |

---

### 3. 依存性注入（Dependency Injection）

**FastAPI:**
```python
# 宣言的（Declarative）
def get_me(current_user: User = Depends(get_current_user)):
    return current_user
```
- 認証処理は`Depends()`で宣言するだけ
- FastAPIが自動的に実行
- try/catchは不要

**TypeScript:**
```typescript
// 命令的（Imperative）
export async function GET(request: NextRequest) {
  try {
    const currentUser = await getCurrentUser(request);
    // ... 処理 ...
  } catch (error) {
    // ... エラーハンドリング ...
  }
}
```
- 認証処理を明示的に呼び出す
- 毎回try/catchが必要
- より細かい制御が可能

---

### 4. 型安全性

**FastAPI（Pydantic）:**
- **実行時検証**: リクエストボディを自動パース・検証
- エラー時は自動で422 Unprocessable Entityを返す
- 型ヒントで静的解析も可能

**TypeScript（Zod）:**
- **コンパイル時 + 実行時検証**: TypeScript型 + Zod検証
- エラーハンドリングを手動実装
- より厳密な型チェック

---

### 5. FastAPIを選ぶべき理由

1. **開発速度が速い**
   - 自動ドキュメント生成
   - 組み込み依存性注入
   - ボイラープレートが少ない

2. **データサイエンス連携**
   - NumPy, Pandas, scikit-learnと親和性が高い
   - 機械学習モデルのAPI化が簡単

3. **Pythonエコシステム**
   - 豊富なライブラリ（画像処理、自然言語処理など）
   - Celery（非同期タスク処理）との連携

4. **高性能**
   - Starletteベース（非同期I/O）
   - Node.jsと同等のパフォーマンス

---

### 6. TypeScriptを選ぶべき理由

1. **フロントエンドとの統一**
   - 同じ言語（TypeScript）で全てを記述
   - 型定義を共有可能

2. **Next.js統合**
   - フロントエンド + バックエンドを1つのリポジトリで管理
   - Server ActionsでAPI不要に

3. **エンタープライズ向け**
   - 大規模チームで使われる実績
   - Vercel/AWSへのデプロイが容易

4. **細かい制御**
   - より低レベルな処理が可能
   - カスタマイズ性が高い

---

## まとめ

### TaskFlowプロジェクトでFastAPIを選んだ理由

1. **ポートフォリオとして複数技術を学習**
   - フロントエンド（Next.js/TypeScript） + バックエンド（FastAPI/Python）
   - マルチプラットフォーム開発力の証明

2. **API開発に特化**
   - 自動ドキュメント生成で開発効率アップ
   - RESTful API設計のベストプラクティス

3. **将来の拡張性**
   - 機械学習モデルの統合（タスク優先度予測など）
   - データ分析機能の追加

### 結論

| 用途 | おすすめ |
|------|---------|
| **純粋なAPI開発** | FastAPI |
| **フロントエンド統合** | TypeScript（Next.js） |
| **機械学習統合** | FastAPI |
| **小規模プロトタイプ** | どちらでも可 |
| **エンタープライズ** | TypeScript |

**FastAPIの最大の利点**: コード量が少なく、ドキュメントが自動生成され、開発速度が速いこと

**TypeScriptの最大の利点**: フロントエンドと同じ言語で記述でき、エコシステムが広いこと

---

**作成日**: 2026-01-04
**プロジェクト**: TaskFlow
**作成者**: Claude Sonnet 4.5
