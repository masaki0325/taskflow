# 全部入りタスク管理SaaS - 詳細仕様書

## 📋 プロジェクト概要

### プロジェクト名
**TaskFlow** - チーム・個人向けタスク管理SaaS

### 目的
このポートフォリオプロジェクトで証明すること：
- ✅ フルスタック開発力（Web + Mobile + Backend + Infra）
- ✅ モダンな技術スタック（Next.js + FastAPI + Flutter + AWS CDK）
- ✅ 本番運用レベルのコード品質
- ✅ セキュアなアーキテクチャ設計
- ✅ スケーラブルなインフラ構築

### ターゲットユーザー
- 個人ユーザー（個人のタスク管理）
- 小規模チーム（5-10人程度）

---

## 🎯 機能要件

### MVP（Minimum Viable Product）機能一覧

#### 1. **認証・ユーザー管理**
- [ ] メールアドレス + パスワードでのユーザー登録
- [ ] ログイン（JWT認証）
- [ ] ログアウト
- [ ] パスワードリセット（メール送信）
- [ ] Google OAuth ログイン（ソーシャルログイン）
- [ ] ユーザープロフィール編集（名前、アバター画像）
- [ ] アクセストークン + リフレッシュトークンの実装

#### 2. **タスク管理（CRUD）**
- [ ] タスク作成
  - タイトル（必須）
  - 説明（任意、Markdown対応）
  - 期限日（任意）
  - 優先度（低・中・高）
  - ステータス（未着手・進行中・完了）
- [ ] タスク一覧表示
  - フィルター（ステータス、優先度、期限）
  - ソート（作成日、期限日、優先度）
  - 検索（タイトル・説明文）
- [ ] タスク詳細表示
- [ ] タスク編集
- [ ] タスク削除
- [ ] タスク完了/未完了の切り替え

#### 3. **プロジェクト・カテゴリ管理**
- [ ] プロジェクト作成（例: "仕事"、"個人"、"趣味"）
- [ ] プロジェクトごとのタスク表示
- [ ] プロジェクトの色分け
- [ ] プロジェクトの編集・削除

#### 4. **タグ機能**
- [ ] タグの作成（例: "緊急"、"バグ修正"、"新機能"）
- [ ] タスクへのタグ付け（複数可）
- [ ] タグによるフィルタリング

#### 5. **ファイル添付**
- [ ] タスクへのファイル添付（画像、PDF等）
- [ ] S3へのアップロード
- [ ] ファイルのプレビュー
- [ ] ファイルの削除

#### 6. **コメント機能**
- [ ] タスクへのコメント追加
- [ ] コメントの編集・削除
- [ ] コメントのタイムスタンプ表示

#### 7. **通知機能**
- [ ] 期限が近いタスクの通知（期限1日前）
- [ ] コメントが追加された時の通知
- [ ] 通知一覧表示
- [ ] 通知の既読/未読管理

#### 8. **ダッシュボード**
- [ ] 今日のタスク一覧
- [ ] 期限が近いタスク
- [ ] 完了したタスクの統計（今日、今週、今月）
- [ ] プロジェクト別のタスク数グラフ
- [ ] 優先度別のタスク数

### 追加機能（余裕があれば）
- [ ] チーム機能（複数ユーザーでプロジェクト共有）
- [ ] タスクの割り当て（担当者設定）
- [ ] サブタスク（タスクの階層化）
- [ ] カンバンボード表示
- [ ] ガントチャート表示
- [ ] リアルタイム更新（WebSocket）
- [ ] ダークモード対応

---

## 🎨 画面設計

### Web（Next.js）画面一覧

#### 1. **認証関連**
- `/login` - ログイン画面
- `/register` - ユーザー登録画面
- `/forgot-password` - パスワードリセット画面
- `/reset-password/:token` - パスワード再設定画面

#### 2. **メイン画面**
- `/dashboard` - ダッシュボード（ホーム画面）
- `/tasks` - タスク一覧
- `/tasks/:id` - タスク詳細
- `/projects` - プロジェクト一覧
- `/projects/:id` - プロジェクト詳細
- `/settings` - 設定画面（プロフィール編集）

#### 3. **レイアウト構成**
```
┌─────────────────────────────────────┐
│ Header (ロゴ、ユーザー名、通知)      │
├──────┬──────────────────────────────┤
│      │                              │
│ Side │  Main Content                │
│ bar  │                              │
│      │  - Dashboard                 │
│ - Home                              │
│ - Tasks                             │
│ - Projects                          │
│ - Settings                          │
│      │                              │
└──────┴──────────────────────────────┘
```

### Mobile（Flutter）画面一覧

#### 1. **認証関連**
- Login Screen
- Register Screen
- Forgot Password Screen

#### 2. **メイン画面**
- Home Screen（ダッシュボード）
- Task List Screen
- Task Detail Screen
- Add/Edit Task Screen
- Project List Screen
- Settings Screen

#### 3. **ナビゲーション**
- Bottom Navigation Bar:
  - Home
  - Tasks
  - Add Task (中央、強調)
  - Projects
  - Profile

---

## 🗄️ データベース設計（PostgreSQL）

### ER図（エンティティ関係図）

```
users (ユーザー)
  ├─ has many ─→ tasks (タスク)
  ├─ has many ─→ projects (プロジェクト)
  ├─ has many ─→ comments (コメント)
  └─ has many ─→ notifications (通知)

projects (プロジェクト)
  └─ has many ─→ tasks (タスク)

tasks (タスク)
  ├─ belongs to ─→ user
  ├─ belongs to ─→ project
  ├─ has many ─→ comments
  ├─ has many ─→ task_tags (多対多)
  └─ has many ─→ attachments (添付ファイル)

tags (タグ)
  └─ has many ─→ task_tags (多対多)

comments (コメント)
  ├─ belongs to ─→ user
  └─ belongs to ─→ task
```

### テーブル定義

#### **users（ユーザー）**
| カラム名 | 型 | 制約 | 説明 |
|---------|-----|------|------|
| id | UUID | PRIMARY KEY | ユーザーID |
| email | VARCHAR(255) | UNIQUE, NOT NULL | メールアドレス |
| password_hash | VARCHAR(255) | NOT NULL | ハッシュ化されたパスワード |
| name | VARCHAR(100) | NOT NULL | ユーザー名 |
| avatar_url | TEXT | NULL | アバター画像URL（S3） |
| google_id | VARCHAR(255) | UNIQUE, NULL | Google OAuth ID |
| is_active | BOOLEAN | DEFAULT TRUE | アカウント有効フラグ |
| created_at | TIMESTAMP | NOT NULL | 作成日時 |
| updated_at | TIMESTAMP | NOT NULL | 更新日時 |

#### **projects（プロジェクト）**
| カラム名 | 型 | 制約 | 説明 |
|---------|-----|------|------|
| id | UUID | PRIMARY KEY | プロジェクトID |
| user_id | UUID | FOREIGN KEY, NOT NULL | オーナーユーザーID |
| name | VARCHAR(100) | NOT NULL | プロジェクト名 |
| description | TEXT | NULL | 説明 |
| color | VARCHAR(7) | DEFAULT '#3B82F6' | カラーコード（hex） |
| created_at | TIMESTAMP | NOT NULL | 作成日時 |
| updated_at | TIMESTAMP | NOT NULL | 更新日時 |

#### **tasks（タスク）**
| カラム名 | 型 | 制約 | 説明 |
|---------|-----|------|------|
| id | UUID | PRIMARY KEY | タスクID |
| user_id | UUID | FOREIGN KEY, NOT NULL | 作成ユーザーID |
| project_id | UUID | FOREIGN KEY, NULL | プロジェクトID |
| title | VARCHAR(200) | NOT NULL | タスクタイトル |
| description | TEXT | NULL | 説明（Markdown） |
| status | ENUM | NOT NULL | ステータス（todo, in_progress, done） |
| priority | ENUM | NOT NULL | 優先度（low, medium, high） |
| due_date | DATE | NULL | 期限日 |
| completed_at | TIMESTAMP | NULL | 完了日時 |
| created_at | TIMESTAMP | NOT NULL | 作成日時 |
| updated_at | TIMESTAMP | NOT NULL | 更新日時 |

**ENUM定義**:
```sql
CREATE TYPE task_status AS ENUM ('todo', 'in_progress', 'done');
CREATE TYPE task_priority AS ENUM ('low', 'medium', 'high');
```

#### **tags（タグ）**
| カラム名 | 型 | 制約 | 説明 |
|---------|-----|------|------|
| id | UUID | PRIMARY KEY | タグID |
| user_id | UUID | FOREIGN KEY, NOT NULL | 作成ユーザーID |
| name | VARCHAR(50) | NOT NULL | タグ名 |
| color | VARCHAR(7) | DEFAULT '#6B7280' | カラーコード |
| created_at | TIMESTAMP | NOT NULL | 作成日時 |

#### **task_tags（タスク-タグ 中間テーブル）**
| カラム名 | 型 | 制約 | 説明 |
|---------|-----|------|------|
| task_id | UUID | FOREIGN KEY, NOT NULL | タスクID |
| tag_id | UUID | FOREIGN KEY, NOT NULL | タグID |
| created_at | TIMESTAMP | NOT NULL | 作成日時 |

PRIMARY KEY: (task_id, tag_id)

#### **comments（コメント）**
| カラム名 | 型 | 制約 | 説明 |
|---------|-----|------|------|
| id | UUID | PRIMARY KEY | コメントID |
| task_id | UUID | FOREIGN KEY, NOT NULL | タスクID |
| user_id | UUID | FOREIGN KEY, NOT NULL | コメント投稿者ID |
| content | TEXT | NOT NULL | コメント内容 |
| created_at | TIMESTAMP | NOT NULL | 作成日時 |
| updated_at | TIMESTAMP | NOT NULL | 更新日時 |

#### **attachments（添付ファイル）**
| カラム名 | 型 | 制約 | 説明 |
|---------|-----|------|------|
| id | UUID | PRIMARY KEY | 添付ファイルID |
| task_id | UUID | FOREIGN KEY, NOT NULL | タスクID |
| user_id | UUID | FOREIGN KEY, NOT NULL | アップロードユーザーID |
| file_name | VARCHAR(255) | NOT NULL | ファイル名 |
| file_url | TEXT | NOT NULL | ファイルURL（S3） |
| file_size | INTEGER | NOT NULL | ファイルサイズ（bytes） |
| mime_type | VARCHAR(100) | NOT NULL | MIMEタイプ |
| created_at | TIMESTAMP | NOT NULL | 作成日時 |

#### **notifications（通知）**
| カラム名 | 型 | 制約 | 説明 |
|---------|-----|------|------|
| id | UUID | PRIMARY KEY | 通知ID |
| user_id | UUID | FOREIGN KEY, NOT NULL | 通知先ユーザーID |
| type | ENUM | NOT NULL | 通知タイプ（task_due, comment_added） |
| title | VARCHAR(200) | NOT NULL | 通知タイトル |
| message | TEXT | NOT NULL | 通知メッセージ |
| link | TEXT | NULL | リンク先URL |
| is_read | BOOLEAN | DEFAULT FALSE | 既読フラグ |
| created_at | TIMESTAMP | NOT NULL | 作成日時 |

---

## 🔌 API設計（FastAPI）

### ベースURL
```
開発環境: http://localhost:8000/api/v1
本番環境: https://api.taskflow.example.com/api/v1
```

### 認証方式
- **JWT（JSON Web Token）** ベースの認証
- Headerに `Authorization: Bearer <token>` を付与

### API エンドポイント一覧

#### **認証 (Authentication)**

##### POST `/auth/register`
ユーザー登録

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!",
  "name": "山田太郎"
}
```

**Response (201 Created)**:
```json
{
  "user": {
    "id": "uuid-here",
    "email": "user@example.com",
    "name": "山田太郎",
    "avatar_url": null,
    "created_at": "2025-01-01T00:00:00Z"
  },
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

##### POST `/auth/login`
ログイン

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}
```

**Response (200 OK)**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

##### POST `/auth/refresh`
トークンのリフレッシュ

**Request Body**:
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response (200 OK)**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

##### POST `/auth/google`
Google OAuth ログイン

**Request Body**:
```json
{
  "id_token": "google-id-token-here"
}
```

---

#### **ユーザー (Users)**

##### GET `/users/me`
現在のユーザー情報取得

**Response (200 OK)**:
```json
{
  "id": "uuid-here",
  "email": "user@example.com",
  "name": "山田太郎",
  "avatar_url": "https://s3.amazonaws.com/bucket/avatar.jpg",
  "created_at": "2025-01-01T00:00:00Z"
}
```

##### PATCH `/users/me`
ユーザー情報更新

**Request Body**:
```json
{
  "name": "山田花子",
  "avatar_url": "https://s3.amazonaws.com/bucket/new-avatar.jpg"
}
```

---

#### **タスク (Tasks)**

##### GET `/tasks`
タスク一覧取得

**Query Parameters**:
- `status`: todo | in_progress | done（任意）
- `priority`: low | medium | high（任意）
- `project_id`: UUID（任意）
- `search`: 検索キーワード（任意）
- `sort_by`: created_at | due_date | priority（デフォルト: created_at）
- `order`: asc | desc（デフォルト: desc）
- `limit`: 件数（デフォルト: 50）
- `offset`: オフセット（デフォルト: 0）

**Response (200 OK)**:
```json
{
  "tasks": [
    {
      "id": "uuid-here",
      "title": "プロジェクト仕様書を作成",
      "description": "詳細な仕様書を作成する",
      "status": "in_progress",
      "priority": "high",
      "due_date": "2025-12-31",
      "project": {
        "id": "project-uuid",
        "name": "ポートフォリオ開発",
        "color": "#3B82F6"
      },
      "tags": [
        {
          "id": "tag-uuid",
          "name": "重要",
          "color": "#EF4444"
        }
      ],
      "created_at": "2025-01-01T00:00:00Z",
      "updated_at": "2025-01-01T00:00:00Z"
    }
  ],
  "total": 42,
  "limit": 50,
  "offset": 0
}
```

##### POST `/tasks`
タスク作成

**Request Body**:
```json
{
  "title": "新しいタスク",
  "description": "タスクの説明（Markdown対応）",
  "status": "todo",
  "priority": "medium",
  "due_date": "2025-12-31",
  "project_id": "project-uuid",
  "tag_ids": ["tag-uuid-1", "tag-uuid-2"]
}
```

**Response (201 Created)**:
```json
{
  "id": "task-uuid",
  "title": "新しいタスク",
  "description": "タスクの説明（Markdown対応）",
  "status": "todo",
  "priority": "medium",
  "due_date": "2025-12-31",
  "project": {
    "id": "project-uuid",
    "name": "プロジェクト名",
    "color": "#3B82F6"
  },
  "tags": [
    {
      "id": "tag-uuid-1",
      "name": "タグ1",
      "color": "#10B981"
    }
  ],
  "created_at": "2025-01-01T00:00:00Z",
  "updated_at": "2025-01-01T00:00:00Z"
}
```

##### GET `/tasks/{task_id}`
タスク詳細取得

**Response (200 OK)**:
```json
{
  "id": "task-uuid",
  "title": "タスクタイトル",
  "description": "詳細説明",
  "status": "in_progress",
  "priority": "high",
  "due_date": "2025-12-31",
  "project": {
    "id": "project-uuid",
    "name": "プロジェクト名",
    "color": "#3B82F6"
  },
  "tags": [],
  "attachments": [
    {
      "id": "attachment-uuid",
      "file_name": "screenshot.png",
      "file_url": "https://s3.amazonaws.com/bucket/file.png",
      "file_size": 102400,
      "mime_type": "image/png",
      "created_at": "2025-01-01T00:00:00Z"
    }
  ],
  "comments": [
    {
      "id": "comment-uuid",
      "user": {
        "id": "user-uuid",
        "name": "山田太郎",
        "avatar_url": "https://..."
      },
      "content": "コメント内容",
      "created_at": "2025-01-01T00:00:00Z"
    }
  ],
  "created_at": "2025-01-01T00:00:00Z",
  "updated_at": "2025-01-01T00:00:00Z"
}
```

##### PATCH `/tasks/{task_id}`
タスク更新

**Request Body**:
```json
{
  "title": "更新されたタイトル",
  "status": "done",
  "priority": "low"
}
```

##### DELETE `/tasks/{task_id}`
タスク削除

**Response (204 No Content)**

---

#### **プロジェクト (Projects)**

##### GET `/projects`
プロジェクト一覧取得

**Response (200 OK)**:
```json
{
  "projects": [
    {
      "id": "project-uuid",
      "name": "仕事",
      "description": "仕事関連のタスク",
      "color": "#3B82F6",
      "task_count": 15,
      "created_at": "2025-01-01T00:00:00Z"
    }
  ]
}
```

##### POST `/projects`
プロジェクト作成

##### GET `/projects/{project_id}`
プロジェクト詳細取得

##### PATCH `/projects/{project_id}`
プロジェクト更新

##### DELETE `/projects/{project_id}`
プロジェクト削除

---

#### **タグ (Tags)**

##### GET `/tags`
タグ一覧取得

##### POST `/tags`
タグ作成

##### DELETE `/tags/{tag_id}`
タグ削除

---

#### **コメント (Comments)**

##### POST `/tasks/{task_id}/comments`
コメント追加

**Request Body**:
```json
{
  "content": "コメント内容"
}
```

##### DELETE `/comments/{comment_id}`
コメント削除

---

#### **添付ファイル (Attachments)**

##### POST `/tasks/{task_id}/attachments`
ファイルアップロード

**Request**: multipart/form-data
- `file`: ファイルデータ

**Response (201 Created)**:
```json
{
  "id": "attachment-uuid",
  "file_name": "document.pdf",
  "file_url": "https://s3.amazonaws.com/bucket/uuid/document.pdf",
  "file_size": 204800,
  "mime_type": "application/pdf",
  "created_at": "2025-01-01T00:00:00Z"
}
```

##### DELETE `/attachments/{attachment_id}`
ファイル削除

---

#### **通知 (Notifications)**

##### GET `/notifications`
通知一覧取得

##### PATCH `/notifications/{notification_id}/read`
通知を既読にする

##### DELETE `/notifications/{notification_id}`
通知削除

---

#### **ダッシュボード (Dashboard)**

##### GET `/dashboard/stats`
統計情報取得

**Response (200 OK)**:
```json
{
  "today_tasks": 5,
  "upcoming_tasks": 12,
  "completed_today": 3,
  "completed_this_week": 15,
  "completed_this_month": 42,
  "tasks_by_priority": {
    "high": 8,
    "medium": 15,
    "low": 10
  },
  "tasks_by_project": [
    {
      "project_id": "uuid",
      "project_name": "仕事",
      "task_count": 20
    }
  ]
}
```

---

## 🏗️ インフラ構成（AWS）

### アーキテクチャ図

```
Internet
    │
    ├─→ CloudFront (CDN)
    │      └─→ S3 (Next.js 静的ファイル)
    │
    └─→ Route53 (DNS)
           └─→ ALB (Application Load Balancer)
                  └─→ ECS Fargate (FastAPI)
                         ├─→ RDS PostgreSQL (Private Subnet)
                         ├─→ ElastiCache Redis (Private Subnet)
                         └─→ S3 (ファイルアップロード用)
```

### AWS リソース一覧

#### **ネットワーク**
- **VPC**: 1つ（CIDR: 10.0.0.0/16）
- **Public Subnet**: 2つ（Multi-AZ）
  - ALB配置用
- **Private Subnet**: 2つ（Multi-AZ）
  - ECS Fargate、RDS、ElastiCache配置用
- **Internet Gateway**: 1つ
- **NAT Gateway**: 1-2つ（コスト考慮で1つでも可）

#### **コンピューティング**
- **ECS Cluster**: 1つ
- **ECS Service** (Fargate):
  - FastAPI用
  - タスク数: 2（本番）、1（開発）
  - CPU: 256（0.25 vCPU）
  - メモリ: 512 MB
- **ALB**: 1つ
  - HTTPS対応（ACM証明書）
  - ヘルスチェック設定

#### **データベース**
- **RDS PostgreSQL**:
  - インスタンスタイプ: db.t3.micro（開発）、db.t3.small（本番）
  - バージョン: PostgreSQL 15
  - Multi-AZ: 本番環境のみ
  - 自動バックアップ: 7日間

#### **キャッシュ**
- **ElastiCache Redis**:
  - ノードタイプ: cache.t3.micro
  - セッション管理、APIキャッシュ用

#### **ストレージ**
- **S3 Bucket x2**:
  1. Next.js静的ファイル用（CloudFront経由）
  2. ファイルアップロード用（プライベート）

#### **CDN**
- **CloudFront**:
  - S3バケット（Next.js）への配信
  - HTTPS化、キャッシュ設定

#### **DNS**
- **Route53**:
  - ドメイン管理
  - ALB、CloudFrontへのルーティング

#### **セキュリティ**
- **ACM**: SSL/TLS証明書
- **Secrets Manager**: RDSパスワード、APIキー管理
- **IAM Role**: ECSタスク用のロール

#### **監視**
- **CloudWatch**:
  - ログ収集（ECS、RDS）
  - メトリクス監視
  - アラーム設定

---

## 🛠️ 技術スタック（確定版）

### フロントエンド（Web）
```yaml
Framework: Next.js 15 (App Router)
Language: TypeScript
Styling: TailwindCSS
Component Library: shadcn/ui
State Management: Zustand
API Client: React Query (TanStack Query)
Form Handling: React Hook Form + Zod
Markdown Editor: react-markdown
Testing: Vitest + Testing Library
```

### バックエンド
```yaml
Framework: FastAPI (Python 3.12+)
ORM: SQLAlchemy 2.0
Database: PostgreSQL 15
Cache: Redis
Authentication: JWT (python-jose)
Password Hashing: passlib (bcrypt)
Validation: Pydantic v2
Migration: Alembic
Testing: pytest + pytest-asyncio
```

### モバイル
```yaml
Framework: Flutter 3.x
Language: Dart 3.x
State Management: Riverpod 2.x
Immutable Models: Freezed
JSON Serialization: json_serializable
API Client: Dio
Local Storage: Hive / SharedPreferences
Testing: flutter_test + mockito
```

### インフラ
```yaml
Cloud: AWS
IaC: AWS CDK (TypeScript)
Container: Docker
CI/CD: GitHub Actions
Monitoring: CloudWatch, Sentry
```

---

## 📅 開発ステップ（12週間計画）

### Week 1-2: 環境構築 & バックエンド基礎

#### タスク
- [ ] プロジェクトリポジトリ作成（monorepo構成）
- [ ] Docker環境構築（PostgreSQL、Redis）
- [ ] FastAPI プロジェクト初期化
- [ ] SQLAlchemy モデル定義（users、tasks、projects）
- [ ] Alembic マイグレーション設定
- [ ] データベース初期化

**成果物**:
- `backend/` ディレクトリ
- `docker-compose.yml`
- データベースマイグレーションファイル

**AIに依頼できること**:
- FastAPIのプロジェクト構成の生成
- SQLAlchemyモデルのコード生成
- docker-compose.ymlの作成

---

### Week 3-4: 認証API実装

#### タスク
- [ ] JWT認証の実装
  - [ ] アクセストークン + リフレッシュトークン
  - [ ] トークン検証ミドルウェア
- [ ] ユーザー登録API (`/auth/register`)
- [ ] ログインAPI (`/auth/login`)
- [ ] トークンリフレッシュAPI (`/auth/refresh`)
- [ ] ユーザー情報取得API (`/users/me`)
- [ ] パスワードハッシュ化（bcrypt）
- [ ] pytestでテスト作成

**成果物**:
- 認証関連のAPIエンドポイント
- JWTトークン発行・検証機能
- テストコード

**AIに依頼できること**:
- JWT認証のコード実装
- パスワードハッシュ化の実装
- pytest テストケースの作成

---

### Week 5-6: タスク管理API実装

#### タスク
- [ ] タスクCRUD API実装
  - [ ] GET `/tasks` （一覧、フィルター、ソート）
  - [ ] POST `/tasks` （作成）
  - [ ] GET `/tasks/{id}` （詳細）
  - [ ] PATCH `/tasks/{id}` （更新）
  - [ ] DELETE `/tasks/{id}` （削除）
- [ ] プロジェクトCRUD API実装
- [ ] タグCRUD API実装
- [ ] Pydanticスキーマ定義
- [ ] テスト作成

**成果物**:
- タスク管理API
- プロジェクト管理API
- タグ管理API

**AIに依頼できること**:
- CRUD APIエンドポイントのコード生成
- Pydanticスキーマの作成
- フィルター・ソート機能の実装

---

### Week 7-8: フロントエンド基礎 & 認証実装

#### タスク
- [ ] Next.js プロジェクト初期化
- [ ] TailwindCSS、shadcn/ui セットアップ
- [ ] レイアウト作成（Header、Sidebar）
- [ ] ログイン画面実装
- [ ] ユーザー登録画面実装
- [ ] JWT認証フロー実装
  - [ ] トークン保存（localStorage or Cookie）
  - [ ] 認証状態管理（Zustand）
  - [ ] Protected Route（認証必須ページ）
- [ ] React Queryセットアップ
- [ ] APIクライアント作成（axios or fetch）

**成果物**:
- Next.jsアプリの基本構造
- ログイン・登録画面
- 認証機能

**AIに依頼できること**:
- Next.jsの初期セットアップ
- 認証フローの実装
- React Queryのセットアップ

---

### Week 9-10: フロントエンド - タスク管理画面実装

#### タスク
- [ ] ダッシュボード画面実装
  - [ ] 統計情報表示
  - [ ] 今日のタスク一覧
- [ ] タスク一覧画面実装
  - [ ] テーブル表示
  - [ ] フィルター機能（ステータス、優先度）
  - [ ] 検索機能
- [ ] タスク作成・編集フォーム実装
  - [ ] React Hook Form + Zod
  - [ ] プロジェクト選択
  - [ ] タグ選択
- [ ] タスク詳細画面実装
  - [ ] Markdown表示
  - [ ] コメント表示
- [ ] プロジェクト管理画面実装

**成果物**:
- タスク管理画面（一覧、作成、編集、詳細）
- ダッシュボード

**AIに依頼できること**:
- フォームのバリデーション実装
- React Queryでのデータフェッチ実装
- テーブルコンポーネントの作成

---

### Week 11-12: ファイルアップロード & コメント機能

#### タスク
- [ ] S3バケット作成
- [ ] FastAPI ファイルアップロードAPI実装
  - [ ] 署名付きURL生成
  - [ ] ファイルメタデータ保存
- [ ] フロントエンド ファイルアップロード実装
- [ ] コメント機能API実装
- [ ] コメント機能フロントエンド実装
- [ ] 画像プレビュー機能

**成果物**:
- ファイルアップロード機能
- コメント機能

**AIに依頼できること**:
- S3アップロードのコード実装
- ファイルアップロードフォームの作成

---

### Week 13-14: モバイルアプリ開発（Flutter）

#### タスク
- [ ] Flutterプロジェクト初期化
- [ ] Riverpod セットアップ
- [ ] 認証画面実装（Login、Register）
- [ ] トークン管理（FlutterSecureStorage）
- [ ] APIクライアント実装（Dio）
- [ ] タスク一覧画面実装
- [ ] タスク作成・編集画面実装
- [ ] Bottom Navigation実装

**成果物**:
- Flutterアプリ（iOS/Android対応）
- 基本的なタスク管理機能

**AIに依頼できること**:
- Flutterの画面レイアウトコード生成
- Riverpod状態管理の実装
- APIクライアントの実装

---

### Week 15-16: AWS CDKでインフラ構築

#### タスク
- [ ] AWS CDKプロジェクト初期化
- [ ] VPC、Subnet構築
- [ ] RDS PostgreSQL構築
- [ ] ElastiCache Redis構築
- [ ] ECS Cluster、Task Definition作成
- [ ] ALB構築
- [ ] Route53、ACM設定
- [ ] S3 + CloudFront構築
- [ ] Secrets Manager設定
- [ ] dev/prod環境の切り分け

**成果物**:
- AWS CDKコード
- 本番環境インフラ

**AIに依頼できること**:
- AWS CDKのリソース定義コード生成
- VPC、Subnet構成の実装
- セキュリティグループ設定

---

### Week 17-18: CI/CD & テスト & ドキュメント

#### タスク
- [ ] GitHub Actionsワークフロー作成
  - [ ] バックエンドテスト自動実行
  - [ ] フロントエンドテスト自動実行
  - [ ] Dockerイメージビルド
  - [ ] ECSへの自動デプロイ
- [ ] E2Eテスト実装（Playwright）
- [ ] README作成
  - [ ] プロジェクト概要
  - [ ] 技術スタック
  - [ ] セットアップ手順
  - [ ] デモGIF/動画
- [ ] API仕様書（Swagger）
- [ ] アーキテクチャ図作成

**成果物**:
- CI/CDパイプライン
- テストカバレッジ
- ドキュメント一式

**AIに依頼できること**:
- GitHub Actionsワークフローの作成
- README、ドキュメントの下書き
- アーキテクチャ図の作成（Mermaid等）

---

## 🧪 テスト戦略

### バックエンド（FastAPI）
```python
# pytestでのテスト例
def test_create_task(client, auth_headers):
    response = client.post(
        "/api/v1/tasks",
        json={
            "title": "Test Task",
            "status": "todo",
            "priority": "medium"
        },
        headers=auth_headers
    )
    assert response.status_code == 201
    assert response.json()["title"] == "Test Task"
```

**テスト対象**:
- [ ] 認証API（登録、ログイン、トークンリフレッシュ）
- [ ] タスクCRUD
- [ ] プロジェクトCRUD
- [ ] ファイルアップロード
- [ ] コメント機能
- [ ] バリデーションエラー処理

### フロントエンド（Next.js）
```typescript
// Vitestでのコンポーネントテスト例
import { render, screen } from '@testing-library/react';
import { TaskList } from './TaskList';

test('renders task list', () => {
  render(<TaskList tasks={mockTasks} />);
  expect(screen.getByText('Test Task')).toBeInTheDocument();
});
```

**テスト対象**:
- [ ] コンポーネントの表示
- [ ] フォームのバリデーション
- [ ] ユーザーインタラクション

### E2Eテスト（Playwright）
```typescript
// E2Eテスト例
test('user can create a task', async ({ page }) => {
  await page.goto('http://localhost:3000/login');
  await page.fill('input[name="email"]', 'user@example.com');
  await page.fill('input[name="password"]', 'password');
  await page.click('button[type="submit"]');

  await page.goto('http://localhost:3000/tasks');
  await page.click('text=New Task');
  await page.fill('input[name="title"]', 'E2E Test Task');
  await page.click('button:text("Create")');

  await expect(page.locator('text=E2E Test Task')).toBeVisible();
});
```

---

## 📖 ドキュメント構成

### リポジトリ構造
```
taskflow/
├── README.md                    # プロジェクト概要
├── docs/
│   ├── ARCHITECTURE.md          # アーキテクチャ設計
│   ├── API.md                   # API仕様書
│   ├── SETUP.md                 # セットアップ手順
│   └── DEPLOYMENT.md            # デプロイ手順
├── frontend/                    # Next.js
├── backend/                     # FastAPI
├── mobile/                      # Flutter
├── infrastructure/              # AWS CDK
└── docker-compose.yml
```

### README.md の構成
```markdown
# TaskFlow - タスク管理SaaS

## 概要
（プロジェクトの説明、デモGIF）

## 技術スタック
- Frontend: Next.js 15 + TypeScript + TailwindCSS
- Backend: FastAPI + PostgreSQL + Redis
- Mobile: Flutter
- Infrastructure: AWS (ECS Fargate, RDS, S3, CloudFront)
- IaC: AWS CDK (TypeScript)

## 機能
- タスク管理（CRUD）
- プロジェクト管理
- タグ機能
- ファイル添付
- コメント機能
- 統計ダッシュボード

## アーキテクチャ
（システム構成図）

## セットアップ
（ローカル環境構築手順）

## デモ
（デモサイトURL、ログイン情報）

## スクリーンショット
（主要画面のスクショ）
```

---

## 🎯 AIへの依頼の仕方（例）

開発中にAIに依頼する際の具体例：

### 例1: FastAPI認証実装
```
「FastAPIでJWT認証を実装してください。
要件:
- アクセストークン（有効期限15分）とリフレッシュトークン（有効期限7日）を発行
- ユーザー登録API (/auth/register)
- ログインAPI (/auth/login)
- トークンリフレッシュAPI (/auth/refresh)
- パスワードはbcryptでハッシュ化
- SQLAlchemyのUserモデルを使用
使用ライブラリ: python-jose, passlib, fastapi
```

### 例2: Next.js タスク一覧画面
```
「Next.js (App Router) でタスク一覧画面を作成してください。
要件:
- shadcn/ui のTableコンポーネントを使用
- React Queryでタスク一覧を取得
- フィルター機能（ステータス、優先度）
- 検索機能（タイトルで検索）
- ページネーション
型定義:
type Task = {
  id: string;
  title: string;
  status: 'todo' | 'in_progress' | 'done';
  priority: 'low' | 'medium' | 'high';
  due_date: string | null;
}
```

### 例3: AWS CDK VPC構築
```
「AWS CDK (TypeScript) でVPCを構築してください。
要件:
- CIDR: 10.0.0.0/16
- Public Subnet x2 (Multi-AZ)
- Private Subnet x2 (Multi-AZ)
- Internet Gateway
- NAT Gateway x1
- Route Table設定
```

---

## 📝 開発時の注意点

### セキュリティ
- [ ] パスワードは必ずハッシュ化（bcrypt）
- [ ] SQLインジェクション対策（ORMの正しい使用）
- [ ] XSS対策（入力のサニタイズ）
- [ ] CSRF対策
- [ ] CORS設定（本番環境では厳格に）
- [ ] 環境変数で秘密情報を管理（.env.example用意）

### パフォーマンス
- [ ] データベースインデックス設定
- [ ] N+1問題の回避（SQLAlchemy eager loading）
- [ ] Redisキャッシング活用
- [ ] 画像の最適化（Next.js Image）
- [ ] APIレスポンスの圧縮（gzip）

### コード品質
- [ ] ESLint、Prettier設定
- [ ] 型定義の徹底（TypeScript strict mode）
- [ ] コメントの適切な記述
- [ ] ファイル・関数の適切な分割
- [ ] DRY原則（重複コードの排除）

---

## 🚀 完成後のアピールポイント

### ポートフォリオでアピールできること

1. **フルスタック開発力**
   - フロント（Next.js）、バック（FastAPI）、モバイル（Flutter）の全て実装

2. **モダンな技術スタック**
   - 2025年の市場で需要の高い技術を使用

3. **本番運用レベルの設計**
   - 認証・認可（JWT）
   - ファイルアップロード（S3）
   - キャッシング（Redis）
   - 監視（CloudWatch）

4. **スケーラブルなインフラ**
   - ECS Fargate（サーバーレス）
   - Multi-AZ構成
   - CDN活用

5. **コード品質**
   - テストカバレッジ
   - 型安全性（TypeScript）
   - ドキュメント整備

6. **Infrastructure as Code**
   - AWS CDKで全リソース管理
   - マルチ環境対応（dev/prod）

---

このポートフォリオを完成させれば、**「一人でWebアプリ・モバイルアプリ・インフラ全て作れます」**と自信を持って言えます！
