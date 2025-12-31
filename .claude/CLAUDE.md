# TaskFlow プロジェクト - Claude 開発ガイド

このファイルは、TaskFlow プロジェクトでの開発時にClaude Codeが従うべきルールと指針を定義します。

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

## 🎯 コーディング規約

### 全般的な方針
- **品質優先**: 動くコードではなく、保守可能なコードを書く
- **セキュリティファースト**: 脆弱性を作らない（SQL injection, XSS, CSRF等）
- **型安全**: TypeScript, Python共に型ヒントを必ず使用
- **ドキュメント**: 複雑なロジックにはコメントを残す
- **テスト**: 重要な機能には必ずテストを書く

### Python (FastAPI) コーディング規約

```python
# ✅ Good: 型ヒント、docstring、明確な命名
from pydantic import BaseModel, EmailStr
from typing import Optional

class UserCreate(BaseModel):
    """ユーザー登録リクエストのスキーマ"""
    email: EmailStr
    password: str
    username: str

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "SecurePass123!",
                "username": "john_doe"
            }
        }

async def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db)
) -> User:
    """
    新しいユーザーを作成する

    Args:
        user_data: ユーザー登録情報
        db: データベースセッション

    Returns:
        作成されたユーザーオブジェクト

    Raises:
        HTTPException: メールアドレスが既に登録済みの場合
    """
    # パスワードをハッシュ化（平文保存は絶対NG）
    hashed_password = get_password_hash(user_data.password)

    db_user = User(
        email=user_data.email,
        hashed_password=hashed_password,
        username=user_data.username
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user
```

### TypeScript (Next.js) コーディング規約

```typescript
// ✅ Good: 型定義、エラーハンドリング、明確な責務分離

// 型定義ファイル (types/task.ts)
export interface Task {
  id: string;
  title: string;
  description?: string;
  status: 'todo' | 'in_progress' | 'done';
  priority: 'low' | 'medium' | 'high';
  dueDate?: Date;
  createdAt: Date;
  updatedAt: Date;
}

export interface CreateTaskRequest {
  title: string;
  description?: string;
  priority: Task['priority'];
  dueDate?: string;
}

// APIクライアント (lib/api/tasks.ts)
export async function createTask(
  data: CreateTaskRequest
): Promise<Task> {
  try {
    const response = await fetch('/api/tasks', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      throw new Error(`Failed to create task: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error creating task:', error);
    throw error;
  }
}
```

### ディレクトリ構成

```
backend/
├── app/
│   ├── main.py                  # FastAPIアプリのエントリーポイント
│   ├── core/                    # コア機能（設定、セキュリティ）
│   │   ├── config.py           # 環境変数、設定
│   │   ├── security.py         # JWT、パスワードハッシュ
│   │   └── database.py         # DB接続
│   ├── models/                  # SQLAlchemyモデル（DBテーブル定義）
│   │   ├── user.py
│   │   ├── task.py
│   │   └── project.py
│   ├── schemas/                 # Pydanticスキーマ（バリデーション）
│   │   ├── user.py
│   │   ├── task.py
│   │   └── token.py
│   ├── api/                     # APIルート
│   │   ├── deps.py             # 依存性注入（認証チェック等）
│   │   └── v1/
│   │       ├── auth.py         # 認証エンドポイント
│   │       ├── users.py        # ユーザー管理
│   │       ├── tasks.py        # タスク管理
│   │       └── projects.py     # プロジェクト管理
│   ├── crud/                    # CRUD操作（DB操作ロジック）
│   │   ├── user.py
│   │   ├── task.py
│   │   └── project.py
│   └── tests/                   # テスト
│       ├── test_auth.py
│       ├── test_tasks.py
│       └── conftest.py
├── alembic/                     # DBマイグレーション
├── requirements.txt
└── Dockerfile

frontend/
├── app/                         # Next.js App Router
│   ├── layout.tsx              # ルートレイアウト
│   ├── page.tsx                # ホームページ
│   ├── (auth)/                 # 認証関連ページ
│   │   ├── login/
│   │   └── register/
│   └── (dashboard)/            # ダッシュボード（認証必須）
│       ├── tasks/
│       ├── projects/
│       └── settings/
├── components/                  # 再利用可能なコンポーネント
│   ├── ui/                     # shadcn/ui コンポーネント
│   ├── TaskCard.tsx
│   ├── TaskList.tsx
│   └── Header.tsx
├── lib/                         # ユーティリティ
│   ├── api/                    # APIクライアント
│   │   ├── client.ts          # 共通HTTPクライアント
│   │   ├── auth.ts
│   │   └── tasks.ts
│   ├── hooks/                  # カスタムフック
│   │   ├── useAuth.ts
│   │   └── useTasks.ts
│   └── utils.ts                # ヘルパー関数
├── types/                       # 型定義
│   ├── task.ts
│   ├── user.ts
│   └── api.ts
└── public/                      # 静的ファイル
```

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

## 🧪 テスト方針

### バックエンド（pytest）

```python
# tests/test_auth.py
def test_user_registration(client: TestClient):
    """ユーザー登録が正常に動作することを確認"""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "password": "SecurePass123!",
            "username": "testuser"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert "password" not in data  # パスワードを返さない
```

### フロントエンド（Jest + React Testing Library）

```typescript
// __tests__/components/TaskCard.test.tsx
import { render, screen } from '@testing-library/react';
import TaskCard from '@/components/TaskCard';

describe('TaskCard', () => {
  it('renders task title and description', () => {
    const task = {
      id: '1',
      title: 'Test Task',
      description: 'Test Description',
      status: 'todo' as const,
      priority: 'high' as const,
      createdAt: new Date(),
      updatedAt: new Date(),
    };

    render(<TaskCard task={task} />);

    expect(screen.getByText('Test Task')).toBeInTheDocument();
    expect(screen.getByText('Test Description')).toBeInTheDocument();
  });
});
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

### データベースマイグレーション

```bash
# 新しいモデルを追加したら必ずマイグレーション作成
alembic revision --autogenerate -m "Add tasks table"
alembic upgrade head

# マイグレーションファイルは必ずレビューする
# （autogenerateが完璧とは限らない）
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

2. バックエンド実装
   ├─ モデル作成（models/）
   ├─ スキーマ作成（schemas/）
   ├─ CRUD作成（crud/）
   ├─ API作成（api/v1/）
   └─ テスト作成（tests/）

3. フロントエンド実装
   ├─ 型定義（types/）
   ├─ APIクライアント（lib/api/）
   ├─ コンポーネント（components/）
   ├─ ページ（app/）
   └─ テスト（__tests__/）

4. 動作確認
   docker-compose up
   http://localhost:3000
   http://localhost:8000/docs

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
