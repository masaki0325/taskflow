# Database Migration Command

データベースマイグレーションファイルを作成してください。

## 実行方法

Task tool を使用して、マイグレーション作成専用の general-purpose エージェントを起動してください。

エージェントへの指示内容:

```
TaskFlowプロジェクトのデータベースマイグレーションファイルを作成してください。

## マイグレーション作成手順

1. ユーザーがどのモデルを作成/変更したいか確認
2. 既存のモデルファイルを確認（`backend/app/models/`）
3. 新しいモデルまたは変更内容を実装
4. Alembicマイグレーションファイルを生成

## モデル定義のベストプラクティス

### 必須カラム
すべてのテーブルに以下を含める:

```python
from sqlalchemy import Column, Integer, DateTime
from sqlalchemy.sql import func

class YourModel(Base):
    __tablename__ = "your_table"

    # 主キー（必須）
    id = Column(Integer, primary_key=True, index=True)

    # タイムスタンプ（推奨）
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
```

### リレーションシップの定義

**1対多（One-to-Many）**:
```python
# models/user.py
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    tasks = relationship("Task", back_populates="owner")

# models/task.py
class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="tasks")
```

**多対多（Many-to-Many）**:
```python
# 中間テーブル
task_tags = Table(
    'task_tags',
    Base.metadata,
    Column('task_id', Integer, ForeignKey('tasks.id')),
    Column('tag_id', Integer, ForeignKey('tags.id'))
)

# models/task.py
class Task(Base):
    tags = relationship("Tag", secondary=task_tags, back_populates="tasks")

# models/tag.py
class Tag(Base):
    tasks = relationship("Task", secondary=task_tags, back_populates="tags")
```

### インデックスの設定

検索に使うカラムにはインデックスを:

```python
email = Column(String, unique=True, index=True)  # ユニーク + インデックス
status = Column(String, index=True)              # 検索用インデックス
```

## マイグレーション生成コマンド

```bash
# 自動生成（推奨）
docker-compose exec backend alembic revision --autogenerate -m "Add tasks table"

# または手動作成
docker-compose exec backend alembic revision -m "Add tasks table"
```

## マイグレーションファイルのレビューポイント

Alembicの自動生成は完璧ではないため、以下を確認:

- [ ] NOT NULL制約が適切か
- [ ] デフォルト値が設定されているか
- [ ] インデックスが作成されているか
- [ ] 外部キー制約が正しいか
- [ ] downgrade()関数が実装されているか（ロールバック用）

## マイグレーション適用

```bash
# マイグレーション適用
docker-compose exec backend alembic upgrade head

# 1つ戻す
docker-compose exec backend alembic downgrade -1

# マイグレーション履歴確認
docker-compose exec backend alembic history
```

## 出力内容

以下を提供してください:

1. **モデルファイル**: `backend/app/models/your_model.py`
2. **マイグレーション実行コマンド**
3. **確認すべきポイント**
4. **ロールバック方法**

## 例: Taskモデルのマイグレーション

**ステップ1: モデル作成** (`backend/app/models/task.py`)
```python
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.core.database import Base

class TaskStatus(str, enum.Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"

class TaskPriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    status = Column(Enum(TaskStatus), default=TaskStatus.TODO)
    priority = Column(Enum(TaskPriority), default=TaskPriority.MEDIUM)
    due_date = Column(DateTime(timezone=True), nullable=True)

    # 外部キー
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # タイムスタンプ
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # リレーションシップ
    owner = relationship("User", back_populates="tasks")
```

**ステップ2: マイグレーション生成**
```bash
docker-compose exec backend alembic revision --autogenerate -m "Add tasks table"
```

**ステップ3: マイグレーション適用**
```bash
docker-compose exec backend alembic upgrade head
```
```

上記の指示でTask toolを起動し、マイグレーションファイルを作成してユーザーに報告してください。
