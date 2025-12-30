# TaskFlow - タスク管理SaaS

チーム・個人向けのタスク管理アプリケーション

## 技術スタック

### Frontend
- **Web**: Next.js 15 + TypeScript + TailwindCSS + shadcn/ui
- **Mobile**: Flutter 3.x + Riverpod

### Backend
- **API**: FastAPI (Python 3.12+)
- **Database**: PostgreSQL 15
- **Cache**: Redis 7
- **ORM**: SQLAlchemy 2.0

### Infrastructure
- **Cloud**: AWS
- **IaC**: AWS CDK (TypeScript)
- **Container**: Docker
- **CI/CD**: GitHub Actions

## プロジェクト構成

```
taskflow/
├── backend/          # FastAPI
├── frontend/         # Next.js
├── mobile/           # Flutter
├── infrastructure/   # AWS CDK
├── docs/            # ドキュメント
└── docker-compose.yml
```

## 主要機能

- ✅ 認証・ユーザー管理（JWT + Google OAuth）
- ✅ タスク管理（CRUD、フィルター、検索）
- ✅ プロジェクト管理
- ✅ タグ機能
- ✅ ファイル添付（S3）
- ✅ コメント機能
- ✅ 通知機能
- ✅ ダッシュボード（統計）

## セキュリティ

- JWT認証によるセキュアなAPI
- パスワードハッシュ化（bcrypt）
- CORS設定

## セットアップ

### 前提条件

- Docker & Docker Compose
- Python 3.12+
- Node.js 18+
- Flutter 3.x

### 開発環境の起動

1. リポジトリをクローン
```bash
git clone <repository-url>
cd taskflow
```

2. 環境変数を設定
```bash
cp .env.example .env
# .envファイルを編集して適切な値を設定
```

3. Dockerコンテナを起動
```bash
docker-compose up -d
```

4. バックエンドAPIの確認
```bash
# APIドキュメント
open http://localhost:8000/docs
```

5. データベースマイグレーション
```bash
docker-compose exec backend alembic upgrade head
```

### コンテナの停止

```bash
docker-compose down
```

### ログの確認

```bash
# すべてのサービスのログ
docker-compose logs -f

# 特定のサービスのログ
docker-compose logs -f backend
docker-compose logs -f postgres
docker-compose logs -f redis
```

## 開発状況

- [x] Week 1-2: 環境構築 & Docker setup
- [ ] Week 3-4: 認証API実装
- [ ] Week 5-6: タスク管理API実装
- [ ] Week 7-8: フロントエンド - 認証画面
- [ ] Week 9-10: フロントエンド - タスク管理画面
- [ ] Week 11-12: ファイルアップロード & コメント
- [ ] Week 13-14: モバイルアプリ（Flutter）
- [ ] Week 15-16: AWS CDKでインフラ構築
- [ ] Week 17-18: CI/CD & テスト & ドキュメント

## ライセンス

MIT

---

🤖 Generated with [Claude Code](https://claude.com/claude-code)
