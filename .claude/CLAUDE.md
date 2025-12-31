# TaskFlow プロジェクト - Claude 開発ガイド

このファイルは、TaskFlow プロジェクトでの開発時にClaude Codeが従うべき全体的なルールと指針を定義します。

## 📋 プロジェクト概要

### プロジェクト名
**TaskFlow** - チーム・個人向けタスク管理SaaS

### 目的
フルスタック開発力を証明するポートフォリオプロジェクト
- Web（Next.js）+ Mobile（Flutter）+ Backend（FastAPI）+ Infrastructure（AWS CDK）
- 本番運用レベルのコード品質
- セキュアなアーキテクチャ設計
- スケーラブルなインフラ構築

### 技術スタック全体図

```
┌─────────────────────────────────────────────────────┐
│                   クライアント                       │
├──────────────────────┬──────────────────────────────┤
│  Web (Next.js 15)    │  Mobile (Flutter 3.x)        │
│  - TypeScript        │  - Dart                      │
│  - TailwindCSS       │  - Riverpod                  │
│  - shadcn/ui         │  - Material Design           │
└──────────┬───────────┴─────────────┬────────────────┘
           │                         │
           └─────────┬───────────────┘
                     │ REST API
                     ▼
┌─────────────────────────────────────────────────────┐
│           Backend (FastAPI + Python 3.12)           │
│  - FastAPI (API Framework)                          │
│  - SQLAlchemy 2.0 (ORM)                             │
│  - Alembic (マイグレーション)                        │
│  - Pydantic (バリデーション)                         │
└──────────┬──────────────────────────┬───────────────┘
           │                          │
           ▼                          ▼
┌─────────────────────┐    ┌─────────────────────────┐
│ PostgreSQL 15       │    │ Redis 7                 │
│ (メインDB)          │    │ (キャッシュ/セッション)  │
└─────────────────────┘    └─────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────────┐
│              AWS Infrastructure (CDK)               │
│  - ECS Fargate (コンテナ実行)                        │
│  - RDS (PostgreSQL)                                 │
│  - ElastiCache (Redis)                              │
│  - S3 (ファイル保存)                                 │
│  - CloudFront (CDN)                                 │
└─────────────────────────────────────────────────────┘
```

---

## 🎯 全般的なコーディング方針

### 開発原則
- **品質優先**: 動くコードではなく、保守可能なコードを書く
- **セキュリティファースト**: 脆弱性を作らない（SQL injection, XSS, CSRF等）
- **型安全**: TypeScript, Python共に型ヒントを必ず使用
- **ドキュメント**: 複雑なロジックにはコメントを残す
- **テスト**: 重要な機能には必ずテストを書く

### 詳細なコーディング規約

各技術スタックの詳細なコーディング規約は以下を参照：

- **バックエンド（FastAPI）**: [backend.md](./backend.md)
- **フロントエンド（Next.js）**: [frontend.md](./frontend.md)

---

## 🔒 セキュリティ要件

### 必須のセキュリティ対策

```
┌─────────────────────────────────────────────┐
│  脅威               対策                     │
├─────────────────────────────────────────────┤
│  SQL Injection    → SQLAlchemy ORM使用      │
│                     生SQLは使わない          │
├─────────────────────────────────────────────┤
│  XSS              → React自動エスケープ     │
│                     dangerouslySetInnerHTML禁止│
├─────────────────────────────────────────────┤
│  CSRF             → SameSite Cookie設定     │
│                     CORSホワイトリスト       │
├─────────────────────────────────────────────┤
│  認証             → JWT + Refresh Token     │
│                     bcryptでパスワードハッシュ│
├─────────────────────────────────────────────┤
│  機密情報         → .envで管理              │
│                     GitHubにpushしない       │
└─────────────────────────────────────────────┘
```

### パスワード要件
- 最小8文字
- 英大文字・小文字・数字を含む
- bcryptでハッシュ化（ソルト自動生成）
- 平文保存は絶対禁止

### JWT トークン管理
```
Access Token:  有効期限15分（短命）
Refresh Token: 有効期限7日（長命）
               Redis/DBで管理、ログアウト時に無効化
```

---

## 🌿 Git ワークフロー

### ブランチ戦略

```
main
  │
  ├── feature/auth-api          ← 認証API実装
  ├── feature/task-crud          ← タスクCRUD実装
  ├── feature/file-upload        ← ファイルアップロード
  └── feature/notifications      ← 通知機能
```

### ブランチ命名規則
- `feature/認証機能` → `feature/auth-api`
- `fix/バグ修正` → `fix/task-deletion-bug`
- `chore/設定変更` → `chore/update-docker-config`

### コミットメッセージ規則

```
<type>: <subject>

<body>

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
```

**Type:**
- `feat`: 新機能
- `fix`: バグ修正
- `docs`: ドキュメント更新
- `chore`: 設定変更、依存関係更新
- `refactor`: リファクタリング
- `test`: テスト追加

**例:**
```
feat: Implement user authentication with JWT

- Add login/register endpoints
- Implement JWT token generation and validation
- Add password hashing with bcrypt
- Create user model and migration

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
```

---

## 📝 開発時の注意事項

### 環境変数の管理

```bash
# ❌ 絶対にやってはいけないこと
git add .env  # 機密情報を含む.envをコミット

# ✅ 正しい方法
# .env.example をコミット（サンプル値のみ）
# .env は .gitignore に追加済み
```

### API設計

```
RESTful API設計原則:

GET    /api/v1/tasks          タスク一覧取得
GET    /api/v1/tasks/{id}     タスク詳細取得
POST   /api/v1/tasks          タスク作成
PUT    /api/v1/tasks/{id}     タスク更新
DELETE /api/v1/tasks/{id}     タスク削除

ステータスコード:
200 OK              成功（GET, PUT）
201 Created         作成成功（POST）
204 No Content      削除成功（DELETE）
400 Bad Request     バリデーションエラー
401 Unauthorized    認証エラー
403 Forbidden       権限エラー
404 Not Found       リソースが見つからない
500 Internal Error  サーバーエラー
```

---

## 🚀 開発フロー

### 新機能開発の流れ

```
1. ブランチ作成
   git checkout -b feature/new-feature

2. 実装
   ├─ バックエンド: backend.md を参照
   └─ フロントエンド: frontend.md を参照

3. 動作確認
   docker-compose up
   http://localhost:3000
   http://localhost:8000/docs

4. CodeRabbitのローカルレビューを確認
   Cursorのextensionで自動レビュー

5. コミット & プッシュ
   git add .
   git commit -m "feat: Add new feature"
   git push -u origin feature/new-feature

6. プルリクエスト作成
   CodeRabbitが自動レビュー（日本語設定済み）
```

---

## 📚 参考資料

- [FastAPI公式ドキュメント](https://fastapi.tiangolo.com/)
- [Next.js公式ドキュメント](https://nextjs.org/docs)
- [SQLAlchemy公式ドキュメント](https://docs.sqlalchemy.org/)
- [Pydantic公式ドキュメント](https://docs.pydantic.dev/)
- [shadcn/ui公式ドキュメント](https://ui.shadcn.com/)

---

**このガイドに従って、高品質なコードを書きましょう！** 🚀
