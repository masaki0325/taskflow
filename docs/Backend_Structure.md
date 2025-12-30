# Backend 構造説明ドキュメント

TaskFlowプロジェクトのバックエンド（FastAPI）の構造と各ファイルの役割を説明します。

## 目次

1. [ディレクトリ構造](#ディレクトリ構造)
2. [各ファイルの詳細説明](#各ファイルの詳細説明)
3. [Docker関連ファイル](#docker関連ファイル)
4. [開発の流れ](#開発の流れ)
5. [よくある質問](#よくある質問)

---

## ディレクトリ構造

```
backend/
├── .dockerignore          # Dockerビルド時に除外するファイルリスト
├── Dockerfile             # Dockerイメージの設計図
├── requirements.txt       # Pythonパッケージの依存関係リスト
├── app/                   # アプリケーションコード
│   ├── __init__.py       # Pythonパッケージマーカー
│   └── main.py           # FastAPIアプリケーションのエントリーポイント
└── (今後追加予定)
    ├── models/           # データベースモデル
    ├── schemas/          # Pydanticスキーマ（バリデーション）
    ├── routers/          # エンドポイント定義
    ├── services/         # ビジネスロジック
    ├── database.py       # データベース接続設定
    └── tests/            # テストコード
```

---

## 各ファイルの詳細説明

### 1. Dockerfile

**役割:** Pythonアプリケーションを動かすDockerイメージの設計図

**内容:**
```dockerfile
# ベースイメージ: Python 3.12 slim版（軽量）
FROM python:3.12-slim

# 作業ディレクトリ
WORKDIR /app

# システムパッケージのインストール
RUN apt-get update && apt-get install -y \
    gcc \                    # Cコンパイラ（一部のPythonパッケージに必要）
    postgresql-client \      # PostgreSQLクライアント
    && rm -rf /var/lib/apt/lists/*

# 依存関係のインストール（キャッシュ最適化のため先にコピー）
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションコードのコピー
COPY . .

# ポート公開
EXPOSE 8000

# 起動コマンド
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**ポイント:**
- **レイヤーキャッシュ:** `requirements.txt` を先にコピーすることで、コード変更時に `pip install` をスキップ
- **軽量化:** slim版を使用してイメージサイズを削減（約150MB）
- **マルチステージビルド対応:** 将来的に本番用の最適化が可能

**ビルドコマンド:**
```bash
# 手動ビルド（通常は不要、docker-composeが自動実行）
docker build -t taskflow-backend ./backend
```

---

### 2. .dockerignore

**役割:** Dockerイメージに含めたくないファイルを指定（.gitignoreと同じ仕組み）

**除外するファイル:**

```
# Pythonキャッシュ
__pycache__/
*.pyc
*.pyo
*.pyd

# 仮想環境
.venv/
venv/
env/

# 環境変数ファイル（機密情報）
.env

# Git履歴（不要 & 巨大）
.git/

# テスト関連
.pytest_cache/
.coverage
htmlcov/

# ドキュメント
README.md
```

**重要性:**
1. **イメージサイズ削減:** .git ディレクトリだけで数百MBになることも
2. **ビルド時間短縮:** コピーするファイルが少ないほど高速
3. **セキュリティ:** .env ファイルがイメージに含まれると機密情報が漏洩
4. **一貫性:** ローカル環境の設定が混入しない

---

### 3. requirements.txt

**役割:** プロジェクトで使用するPythonパッケージのリスト（Node.jsの package.json に相当）

**主要パッケージ:**

#### Webフレームワーク
```
fastapi==0.109.0           # FastAPI本体
uvicorn[standard]==0.27.0  # ASGIサーバー
python-multipart==0.0.6    # ファイルアップロード対応
```

#### データベース
```
sqlalchemy==2.0.25         # ORM（Sequelize/Prismaに相当）
alembic==1.13.1            # マイグレーションツール
asyncpg==0.29.0            # PostgreSQL非同期ドライバ
psycopg2-binary==2.9.9     # PostgreSQL同期ドライバ
```

#### キャッシュ・セッション
```
redis==5.0.1               # Redisクライアント
```

#### 認証・セキュリティ
```
python-jose[cryptography]==3.3.0  # JWT トークン
passlib[bcrypt]==1.7.4            # パスワードハッシュ化
python-dotenv==1.0.0              # 環境変数読み込み
```

#### バリデーション
```
pydantic==2.5.3            # データバリデーション
pydantic-settings==2.1.0   # 環境変数管理
email-validator==2.1.0     # メールアドレス検証
```

#### テスト
```
pytest==7.4.4              # テストフレームワーク
pytest-asyncio==0.23.3     # 非同期テスト対応
httpx==0.26.0              # HTTPクライアント（APIテスト用）
```

#### 将来の機能
```
boto3==1.34.26             # AWS S3（ファイル保存）
google-auth==2.26.2        # Googleログイン
```

**インストール方法:**
```bash
# ローカル環境で
pip install -r requirements.txt

# Docker内では自動実行（Dockerfileで指定済み）
```

**バージョン固定の理由:**
- **再現性:** どの環境でも同じバージョン
- **安定性:** 新バージョンで互換性が壊れても影響を受けない
- **セキュリティ:** 意図しないバージョンアップを防ぐ

---

### 4. app/__init__.py

**役割:** `app/` ディレクトリをPythonパッケージとして認識させる

**重要性:**

```python
# __init__.py がない場合
from app.main import app  # ❌ エラー: app is not a package

# __init__.py がある場合
from app.main import app  # ✅ OK
```

**現在:** 空ファイル

**将来的な使い方:**
```python
# app/__init__.py

# バージョン情報
__version__ = "1.0.0"

# 初期化関数
from .database import init_db
from .redis import init_redis

# エクスポート
__all__ = ["init_db", "init_redis"]
```

---

### 5. app/main.py

**役割:** FastAPIアプリケーションのエントリーポイント（メインファイル）

**構造:**

```python
# ============================================================
# 1. インポート
# ============================================================
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# ============================================================
# 2. FastAPIアプリケーションの初期化
# ============================================================
app = FastAPI(
    title="TaskFlow API",
    description="Task Management SaaS API",
    version="1.0.0",
    docs_url="/docs",       # Swagger UI
    redoc_url="/redoc",     # ReDoc
)

# ============================================================
# 3. CORS設定
# ============================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================
# 4. エンドポイント定義
# ============================================================
@app.get("/")
async def root():
    """ルートエンドポイント"""
    return {
        "message": "Welcome to TaskFlow API",
        "version": "1.0.0",
        "docs": "/docs",
    }

@app.get("/health")
async def health_check():
    """ヘルスチェックエンドポイント"""
    return {
        "status": "healthy",
        "service": "TaskFlow API",
    }
```

**アクセス方法:**
```bash
# サーバー起動
docker-compose up -d

# エンドポイントにアクセス
curl http://localhost:8000/
curl http://localhost:8000/health

# APIドキュメント（ブラウザで開く）
open http://localhost:8000/docs
```

**FastAPIの特徴:**
1. **自動ドキュメント生成:** `/docs` でSwagger UIが自動生成
2. **型ヒント:** Python の型ヒントで自動バリデーション
3. **非同期対応:** `async def` で高速処理
4. **JSONレスポンス:** 辞書を返すと自動的にJSON化

---

## Docker関連ファイル

### docker-compose.yml との連携

プロジェクトルートの `docker-compose.yml` でバックエンドサービスを定義:

```yaml
backend:
  build:
    context: ./backend      # このディレクトリをビルド
    dockerfile: Dockerfile  # Dockerfileを使用
  ports:
    - "8000:8000"           # ポート公開
  volumes:
    - ./backend:/app        # ホットリロード（コード変更が即反映）
  depends_on:
    - postgres              # PostgreSQL起動後に起動
    - redis                 # Redis起動後に起動
  command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 開発フロー

```
1. コードを編集 (backend/app/main.py)
   ↓
2. ボリュームマウントで即座にコンテナ内に反映
   ↓
3. --reload オプションでuvicornが自動再起動
   ↓
4. ブラウザでリロード → 変更が反映される
```

---

## 開発の流れ

### 1. 環境構築

```bash
# リポジトリをクローン
git clone <repository-url>
cd taskflow

# 環境変数を設定
cp .env.example .env

# Dockerコンテナを起動
docker-compose up -d

# ログを確認
docker-compose logs -f backend
```

### 2. 開発サイクル

```bash
# 1. コードを編集
vim backend/app/main.py

# 2. 自動的に反映される（--reloadのおかげ）

# 3. ブラウザで確認
open http://localhost:8000/docs

# 4. テスト
docker-compose exec backend pytest

# 5. コミット
git add .
git commit -m "feat: Add new endpoint"
```

### 3. 新しいエンドポイントの追加

```python
# backend/app/main.py

@app.get("/tasks")
async def get_tasks():
    """タスク一覧を取得"""
    return [
        {"id": 1, "title": "タスク1", "completed": False},
        {"id": 2, "title": "タスク2", "completed": True},
    ]

# 保存すると自動で反映される！
# http://localhost:8000/docs で新しいエンドポイントが確認できる
```

### 4. データベース接続（今後）

```python
# backend/app/database.py を作成予定

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
```

---

## よくある質問

### Q1: コードを変更したのに反映されない

**A:** 以下を確認してください:

```bash
# 1. コンテナが起動しているか
docker-compose ps

# 2. ログでエラーが出ていないか
docker-compose logs -f backend

# 3. --reload オプションが有効か
# docker-compose.yml の command を確認

# 4. キャッシュをクリアして再起動
docker-compose down
docker-compose up -d --build
```

### Q2: pip でパッケージを追加したい

**A:**

```bash
# 1. requirements.txt に追加
echo "新しいパッケージ==バージョン" >> backend/requirements.txt

# 2. コンテナを再ビルド
docker-compose up -d --build backend

# または、コンテナ内で直接インストール（一時的）
docker-compose exec backend pip install 新しいパッケージ
```

### Q3: データベースに接続できない

**A:**

```bash
# 1. PostgreSQLが起動しているか確認
docker-compose ps postgres

# 2. ヘルスチェックの状態を確認
docker-compose ps
# STATUS が (healthy) になっているか

# 3. 接続URLが正しいか確認
docker-compose exec backend env | grep DATABASE_URL

# 4. PostgreSQLに直接接続してテスト
docker-compose exec postgres psql -U taskflow -d taskflow
```

### Q4: ポート8000が使えない

**A:**

```bash
# 1. 既に使用中のプロセスを確認
lsof -i :8000

# 2. プロセスを終了
kill -9 <PID>

# 3. 別のポートを使う
# .env ファイルで変更
BACKEND_PORT=8001

# docker-compose.yml も対応済み
```

### Q5: Dockerイメージが大きすぎる

**A:**

```bash
# 1. 現在のイメージサイズを確認
docker images taskflow-backend

# 2. .dockerignore が正しく設定されているか確認
cat backend/.dockerignore

# 3. 不要なレイヤーを削減
# Dockerfile で RUN コマンドを結合

# 4. マルチステージビルドを検討（将来）
```

---

## 次のステップ

### 実装予定の機能

1. **認証システム**
   - JWT トークン発行
   - ユーザー登録・ログイン
   - パスワードリセット

2. **データベースモデル**
   - User, Task, Project, Comment モデル
   - SQLAlchemy で定義
   - Alembic でマイグレーション

3. **エンドポイント拡充**
   - CRUD操作（Create, Read, Update, Delete）
   - フィルタリング・検索
   - ページネーション

4. **テスト**
   - 単体テスト（pytest）
   - 統合テスト
   - APIテスト（httpx）

5. **セキュリティ**
   - レート制限（Redis）
   - CSRF対策
   - SQL インジェクション対策

---

## 参考リンク

- [FastAPI 公式ドキュメント](https://fastapi.tiangolo.com/)
- [Docker 公式ドキュメント](https://docs.docker.com/)
- [SQLAlchemy ドキュメント](https://docs.sqlalchemy.org/)
- [Pydantic ドキュメント](https://docs.pydantic.dev/)

---

**作成日:** 2025-12-30
**プロジェクト:** TaskFlow
**バージョン:** 1.0
