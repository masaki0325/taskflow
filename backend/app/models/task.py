import enum
from sqlalchemy import Boolean, Column, Integer, String, Text, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


# ===============================================
# Enum定義（ステータス・優先度）
# ===============================================

class TaskStatus(str, enum.Enum):
    """
    タスクのステータス

    str を継承することで、JSONシリアライズ時に文字列として扱われる
    （Pydanticとの連携がスムーズになる）
    """
    TODO = "todo"              # 未着手
    IN_PROGRESS = "in_progress"  # 進行中
    DONE = "done"              # 完了


class TaskPriority(str, enum.Enum):
    """
    タスクの優先度

    str を継承することで、JSONシリアライズ時に文字列として扱われる
    """
    LOW = "low"       # 低
    MEDIUM = "medium"  # 中
    HIGH = "high"     # 高


# ===============================================
# Taskモデル
# ===============================================

class Task(Base):
    """
    タスクモデル（SQLAlchemy ORM）

    このクラスがPostgreSQLの "tasks" テーブルに対応する

    タスク管理のコア機能を提供
    """
    # テーブル名を指定（PostgreSQLに作成されるテーブル名）
    __tablename__ = "tasks"

    # ===============================================
    # カラム定義
    # ===============================================

    # 主キー（自動インクリメント）
    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    # タイトル（必須）
    title = Column(
        String(200),      # 最大200文字
        nullable=False    # NULL不可（必須項目）
    )

    # 説明（任意、長文可）
    description = Column(
        Text,             # 長文対応（Stringより大きい）
        nullable=True     # NULL可（任意項目）
    )

    # ステータス（Enum型）
    status = Column(
        Enum(TaskStatus),       # TaskStatus Enumを使用
        default=TaskStatus.TODO,  # デフォルト値: "todo"
        nullable=False
    )

    # 優先度（Enum型）
    priority = Column(
        Enum(TaskPriority),          # TaskPriority Enumを使用
        default=TaskPriority.MEDIUM,  # デフォルト値: "medium"
        nullable=False
    )

    # 期限日（任意）
    due_date = Column(
        DateTime(timezone=True),  # タイムゾーン付き日時
        nullable=True             # NULL可（期限なしタスクも可能）
    )

    # ===============================================
    # リレーション（外部キー）
    # ===============================================

    # 外部キー: ユーザーID
    # このタスクを作成したユーザーのID
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),  # ユーザー削除時にタスクも削除
        nullable=False  # タスクは必ず誰かのもの
    )

    # リレーション: Userモデルとの関連
    # SQLAlchemyが自動でJOINしてくれる
    # 使用例: task.user.email でユーザーのメールアドレスにアクセス可能
    user = relationship("User", back_populates="tasks")

    # ===============================================
    # タイムスタンプ
    # ===============================================

    # 作成日時
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),  # DB側で現在時刻を自動設定
        nullable=False
    )

    # 更新日時
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),  # 作成時に現在時刻を設定
        onupdate=func.now(),        # 更新時に現在時刻を自動更新
        nullable=False
    )

    # ===============================================
    # デバッグ用の文字列表現
    # ===============================================
    def __repr__(self):
        """
        print(task) した時の表示
        例: <Task(id=1, title='買い物に行く', status='todo')>
        """
        return f"<Task(id={self.id}, title='{self.title}', status='{self.status.value}')>"
