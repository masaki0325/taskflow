# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

## プロジェクト概要

**TaskFlow** - フルスタックタスク管理SaaS（ポートフォリオプロジェクト）

### 技術スタック構成

```
Frontend: Next.js 15 + TypeScript + TailwindCSS + shadcn/ui
Backend:  FastAPI + Python 3.12 + SQLAlchemy 2.0 + Alembic
Database: PostgreSQL 15 + Redis 7
Infra:    AWS CDK + Docker
```

### アーキテクチャの原則

- **セキュリティファースト**: SQL injection, XSS, CSRF対策を必須とする
- **型安全性**: TypeScript/Python共に型ヒントを必ず使用
- **品質優先**: 保守可能なコードを書く（動けば良いではない）
- **本番運用レベル**: ポートフォリオだが本番品質を目指す

---

## 開発コマンド

### 環境起動・停止

```bash
# 全サービス起動（PostgreSQL + Redis + Backend + Frontend）
docker compose up -d

# ログ確認
docker compose logs -f backend
docker compose logs -f

# 停止
docker compose down
```

### バックエンド開発

```bash
# コンテナ内でコマンド実行
docker compose exec backend <command>

# データベースマイグレーション
docker compose exec backend alembic revision --autogenerate -m "Add tasks table"
docker compose exec backend alembic upgrade head
docker compose exec backend alembic downgrade -1

# テスト実行
docker compose exec backend pytest
docker compose exec backend pytest app/tests/test_auth.py -v
docker compose exec backend pytest -k "test_login"

# Python環境（ローカル開発時）
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### アクセスURL

- **Backend API**: http://localhost:8000
- **API Docs (Swagger)**: http://localhost:8000/docs
- **Admin Panel**: http://localhost:8000/admin
- **Frontend**: http://localhost:3000
- **Health Check**: http://localhost:8000/health

---

## コード規約の重要ポイント

### 必須: PDCA開発フロー（ブランチ運用）

**すべての開発タスクは以下のPDCAサイクルに従うこと:**

#### 0. 事前準備: ブランチ作成（必須）
```bash
# 必ず新しいブランチを作成してから作業開始
git checkout -b feature/機能名
# 例: git checkout -b feature/task-crud
```

**重要:**
- mainブランチで直接作業しない
- 1機能 = 1ブランチ
- ブランチ名は `feature/`, `fix/`, `chore/` などのプレフィックスを使用

#### 1. Plan（計画）
```
- TodoWriteツールでタスクを細分化・計画
- 実装方針を明確にする
- 必要に応じてユーザーに確認
```

#### 2. Do（実行）
```
- Taskツールでサブエージェント（subagent_type: "general-purpose"）を起動
- サブエージェントに実装を委譲
- サブエージェントが自律的にコードを実装
```

**サブエージェントの使い方:**
```python
# 例: タスクCRUD機能の実装
Task tool with:
  subagent_type: "general-purpose"
  description: "Implement task CRUD"
  prompt: """
  タスクCRUD機能を実装してください:
  1. app/models/task.py でTaskモデルを作成
  2. app/schemas/task.py でPydanticスキーマを作成
  3. app/crud/task.py でCRUD操作を実装
  4. app/api/v1/tasks.py でAPIエンドポイントを作成
  5. main.pyにルーターを登録

  セキュリティ要件:
  - 所有者チェック必須（current_user.id == task.owner_id）
  - SQLAlchemy ORMを使用（生SQL禁止）

  backend.mdの規約に従ってください。
  """
```

#### 3. Check（評価）
```
- サブエージェント完了後、必ず `/local-review` スキルを実行
- コードレビュー結果を確認
- Critical/High の問題がないか確認
```

#### 4. Act（改善・コミット・PR作成）
```
1. レビュー結果をユーザーに報告
2. Critical の問題がある場合: 即座に修正
3. 問題なし/軽微な問題のみ: コミット実施
   - 変更内容ごとに分けてコミット（1コミット = 1つの論理的な変更）
4. プルリクエスト作成（gh pr create）
5. PR URLをユーザーに報告
```

**コミット・PR作成例:**
```bash
# 複数の変更がある場合は分けてコミット
git add backend/app/models/task.py backend/app/schemas/task.py
git commit -m "feat: Add Task model and schemas"

git add backend/app/api/v1/tasks.py backend/app/crud/task.py
git commit -m "feat: Add Task CRUD API endpoints"

# プルリクエスト作成
gh pr create --title "タスクCRUD機能の実装" --body "..."
```

**完全なフロー例:**
```
1. ユーザー「タスクCRUD機能を実装して」
   ↓
2. ブランチ作成: git checkout -b feature/task-crud
   ↓
3. TodoWriteで計画を立てる
   ↓
4. Taskツールでサブエージェントを起動（実装を委譲）
   ↓
5. サブエージェント完了後、`/local-review` を実行
   ↓
6. レビュー結果を確認・報告
   ↓
7. 問題があれば修正、なければコミット
   ↓
8. プルリクエスト作成 → PR URLを報告
   ↓
9. ユーザーがレビュー・マージ
```

**重要な注意点:**
- **必ずブランチを切ってから作業開始**（mainで直接作業しない）
- サブエージェントには明確な指示を与える（セキュリティ要件、規約への準拠を明記）
- 複数の機能を実装する場合は、機能ごとにサブエージェントを分けて起動
- レビューはスキップせず必ず実行すること
- **コミット後は必ずプルリクエストを作成**
- 1機能の実装完了 = 1プルリクエスト

### バックエンド（FastAPI）

詳細は [backend.md](./backend.md) 参照。

**ディレクトリ構成:**
```
backend/app/
├── main.py           # FastAPIエントリーポイント
├── core/             # config, database, security
├── models/           # SQLAlchemyモデル（テーブル定義）
├── schemas/          # Pydanticスキーマ（バリデーション）
├── api/v1/           # APIルート
├── crud/             # CRUD操作
└── tests/            # pytest テスト
```

**セキュリティ必須事項:**
- SQLAlchemy ORMを使用（生SQLは禁止 → SQL injection防止）
- パスワードは必ずbcryptでハッシュ化（平文保存は絶対禁止）
- JWTトークンは`Depends(get_current_user)`で必ず検証
- 所有者チェックを実装（他人のデータにアクセス不可）

**Pydantic V2を使用:**
```python
# ✅ 正しい
from pydantic import BaseModel, ConfigDict

class UserResponse(BaseModel):
    id: int
    email: str
    model_config = ConfigDict(from_attributes=True)

# ❌ 間違い（V1の古い形式）
class Config:
    from_attributes = True
```

**型ヒント必須:**
```python
# ✅
def get_user(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()

# ❌
def get_user(db, user_id):
    return db.query(User).filter(User.id == user_id).first()
```

### フロントエンド（Next.js）

詳細は [frontend.md](./frontend.md) 参照。

**重要な型規約:**
- ID型は`number`で統一（バックエンドのintと一致）
- `any`型は使用禁止
- TypeScript型定義を必ず使用

**セキュリティ:**
- `dangerouslySetInnerHTML`は使用禁止（XSS防止）
- 環境変数は`NEXT_PUBLIC_`プレフィックス必須（クライアント側に露出する場合）

**Server Component vs Client Component:**
```typescript
// Server Component（デフォルト） - データフェッチに最適
export default async function TasksPage() {
  const tasks = await getTasks();
  return <TaskList tasks={tasks} />;
}

// Client Component - インタラクティブな操作
"use client";
export default function TaskForm() {
  const [title, setTitle] = useState("");
  return <input value={title} onChange={(e) => setTitle(e.target.value)} />;
}
```

---

## API設計規則

RESTful API規則:
```
GET    /api/v1/tasks          タスク一覧取得
GET    /api/v1/tasks/{id}     タスク詳細取得
POST   /api/v1/tasks          タスク作成
PUT    /api/v1/tasks/{id}     タスク更新
DELETE /api/v1/tasks/{id}     タスク削除
```

**ステータスコード:**
- `200 OK`: 成功（GET, PUT）
- `201 Created`: 作成成功（POST）
- `204 No Content`: 削除成功（DELETE）
- `400 Bad Request`: バリデーションエラー
- `401 Unauthorized`: 認証エラー
- `403 Forbidden`: 権限エラー
- `404 Not Found`: リソースが見つからない
- `500 Internal Error`: サーバーエラー

---

## データベース関連

### マイグレーション作成フロー

1. `app/models/` でSQLAlchemyモデルを定義
2. `app/models/__init__.py` にインポート追加（重要！）
3. Alembicマイグレーション生成:
   ```bash
   docker compose exec backend alembic revision --autogenerate -m "Add tasks table"
   ```
4. 生成されたマイグレーションファイルを確認（`backend/alembic/versions/`）
5. マイグレーション適用:
   ```bash
   docker compose exec backend alembic upgrade head
   ```

### 認証トークン設計

```
Access Token:  有効期限15分（短命）
Refresh Token: 有効期限7日（長命、Redis/DBで管理）
```

---

## Git ワークフロー

### ブランチ戦略

```
main
  ├── feature/auth-api
  ├── feature/task-crud
  ├── feature/file-upload
  └── feature/notifications
```

**ブランチ命名規則:**
- `feature/auth-api` - 新機能
- `fix/task-deletion-bug` - バグ修正
- `chore/update-docker-config` - 設定変更

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

## 環境変数管理

```bash
# ❌ 絶対にやってはいけない
git add .env

# ✅ 正しい方法
# .env.example をコミット（サンプル値のみ）
# .env は .gitignore に追加済み
```

**本番環境のSECRET_KEY生成:**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

## プロジェクト固有の重要事項

### SQLAlchemy 2.0を使用

- 新しいクエリスタイルを使用（`select()`ベース推奨）
- `Base.metadata.create_all()`はdevelopment環境のみ（本番はAlembic使用）

### FastAPI依存性注入パターン

```python
@router.get("/tasks/{task_id}")
def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 所有者チェック必須
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.owner_id == current_user.id
    ).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task
```

### 管理画面（SQLAdmin）

- 開発環境では認証なしで使用可能
- **本番デプロイ前に認証を追加する必要がある**（TODO: `app/main.py`参照）

---

## 参考リンク

- [FastAPI公式](https://fastapi.tiangolo.com/)
- [Next.js公式](https://nextjs.org/docs)
- [SQLAlchemy公式](https://docs.sqlalchemy.org/)
- [Pydantic公式](https://docs.pydantic.dev/)
- [shadcn/ui公式](https://ui.shadcn.com/)
