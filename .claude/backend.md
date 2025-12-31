# TaskFlow - Backend (FastAPI) コーディング規約

このファイルは、TaskFlowのバックエンド開発における重要なルールを定義します。

## 技術スタック

```text
FastAPI + Python 3.12
├── FastAPI         API Framework
├── SQLAlchemy 2.0  ORM
├── Alembic         マイグレーション
├── Pydantic        バリデーション
├── pytest          テスト
├── python-jose     JWT認証
├── passlib         パスワードハッシュ
└── redis           キャッシュ
```

---

## ディレクトリ構成

```text
backend/
├── app/
│   ├── main.py              # FastAPIアプリのエントリーポイント
│   ├── core/                # 設定、セキュリティ、DB接続
│   ├── models/              # SQLAlchemyモデル（DBテーブル定義）
│   ├── schemas/             # Pydanticスキーマ（バリデーション）
│   ├── api/v1/              # APIルート
│   ├── crud/                # CRUD操作
│   └── tests/               # テスト
├── alembic/                 # DBマイグレーション
└── requirements.txt
```

---

## コーディング規約

### 型ヒントを必ず使用

```python
# ✅ 正しい
def get_user(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()

# ❌ 間違い
def get_user(db, user_id):
    return db.query(User).filter(User.id == user_id).first()
```

### Pydantic V2を使用

```python
# ✅ 正しい（Pydantic V2）
from pydantic import BaseModel, ConfigDict

class UserResponse(BaseModel):
    id: int
    email: str
    model_config = ConfigDict(from_attributes=True)

# ❌ 間違い（Pydantic V1の古い形式）
class UserResponse(BaseModel):
    id: int
    email: str
    class Config:
        from_attributes = True
```

### データベースマイグレーション

```bash
# マイグレーション生成
docker compose exec backend alembic revision --autogenerate -m "Add users table"

# マイグレーション適用
docker compose exec backend alembic upgrade head
```

---

## セキュリティ要件（重要）

### 絶対に守ること

```python
# ❌ 生のSQL（SQL Injection の危険）
db.execute(f"SELECT * FROM users WHERE email = '{email}'")

# ✅ ORMを使う
db.query(User).filter(User.email == email).first()

# ❌ パスワードを平文で保存
user.password = "mypassword"

# ✅ ハッシュ化して保存
from app.core.security import get_password_hash
user.hashed_password = get_password_hash("mypassword")

# ❌ すべての例外をキャッチ
try:
    ...
except:
    pass

# ✅ 具体的な例外をキャッチ
try:
    ...
except ValueError as e:
    logger.error(f"Invalid value: {e}")
    raise HTTPException(status_code=400, detail=str(e))
```

### 認証・認可

- JWTトークンは必ず`Depends(get_current_user)`で検証
- パスワードは必ずbcryptでハッシュ化
- ユーザーが他人のデータにアクセスできないよう所有者チェックを実装

```python
# ✅ 所有者チェックの例
@router.get("/tasks/{task_id}")
def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.owner_id == current_user.id  # 所有者チェック
    ).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task
```

---

## 参考資料

- [FastAPI公式ドキュメント](https://fastapi.tiangolo.com/)
- [SQLAlchemy公式ドキュメント](https://docs.sqlalchemy.org/)
- [Pydantic公式ドキュメント](https://docs.pydantic.dev/)

---

**バックエンド開発時はこのガイドに従ってください！**
