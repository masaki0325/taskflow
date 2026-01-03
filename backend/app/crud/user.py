from sqlalchemy.orm import Session
from typing import Optional

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import hash_password, verify_password


# ===============================================
# ユーザーCRUD操作
# ===============================================
# CRUD: Create（作成）, Read（読み取り）, Update（更新）, Delete（削除）
#
# 役割: データベース操作のロジックを抽象化
# - APIエンドポイント（auth.py）から呼び出される
# - SQLAlchemy ORMを使用してSQL injectionを防ぐ


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """
    メールアドレスでユーザーを取得（Read操作）

    Args:
        db: データベースセッション
        email: メールアドレス

    Returns:
        ユーザーオブジェクト、存在しない場合はNone

    使用例:
        user = get_user_by_email(db, "test@example.com")
        if user:
            print(f"見つかりました: {user.email}")
        else:
            print("ユーザーが存在しません")

    SQL例:
        SELECT * FROM users WHERE email = 'test@example.com' LIMIT 1;
    """
    # SQLAlchemy ORMでSQL injectionを防ぐ
    # db.query(User): SELECT * FROM users
    # .filter(User.email == email): WHERE email = ?
    # .first(): LIMIT 1（最初の1件を取得）
    return db.query(User).filter(User.email == email).first()


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """
    IDでユーザーを取得
    
    Args:
        db: データベースセッション
        user_id: ユーザーID
    
    Returns:
        ユーザーオブジェクト、存在しない場合はNone
    """
    return db.query(User).filter(User.id == user_id).first()


def create_user(db: Session, user_create: UserCreate) -> User:
    """
    新規ユーザーを作成（Create操作）

    Args:
        db: データベースセッション
        user_create: ユーザー作成データ（email, password）

    Returns:
        作成されたユーザーオブジェクト

    セキュリティ:
        - パスワードをbcryptでハッシュ化してから保存
        - 平文パスワードは保存しない

    処理フロー:
        1. パスワードをハッシュ化
           "Password123" → "$2b$12$EixZa..."

        2. Userモデルを作成（まだDBには保存されない）

        3. db.add() でセッションに追加

        4. db.commit() でDBに保存（トランザクションをコミット）

        5. db.refresh() でDBから最新の状態を取得
           → id, created_at などが自動生成される

    SQL例:
        INSERT INTO users (email, hashed_password, is_active, is_superuser)
        VALUES ('test@example.com', '$2b$12$...', TRUE, FALSE)
        RETURNING id, created_at, updated_at;
    """
    # ①パスワードをハッシュ化
    hashed_password = hash_password(user_create.password)

    # ②ユーザーモデルを作成（メモリ上）
    db_user = User(
        email=user_create.email,
        hashed_password=hashed_password,
        is_active=True,         # デフォルト: 有効
        is_superuser=False,     # デフォルト: 一般ユーザー
    )

    # ③データベースに保存
    db.add(db_user)           # セッションに追加（まだコミットされない）
    db.commit()               # トランザクションをコミット（DBに反映）
    db.refresh(db_user)       # DBから最新の状態を取得（id, created_atなど）

    return db_user


def update_user(db: Session, user_id: int, user_update: UserUpdate) -> Optional[User]:
    """
    ユーザー情報を更新（Update操作）

    Args:
        db: データベースセッション
        user_id: 更新対象のユーザーID
        user_update: 更新データ（email, password, is_activeなど）

    Returns:
        更新されたユーザーオブジェクト、存在しない場合はNone

    処理フロー:
        1. ユーザーを検索
        2. 存在しなければ None を返す
        3. 提供されたフィールドのみを更新
        4. パスワードが含まれていればハッシュ化
        5. DBに保存

    使用例:
        # メールアドレスだけ更新
        update_data = UserUpdate(email="new@example.com")
        updated_user = update_user(db, user_id=1, user_update=update_data)

    SQL例:
        UPDATE users
        SET email = 'new@example.com', updated_at = NOW()
        WHERE id = 1;
    """
    # ①ユーザーを検索
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        return None  # 見つからなければNoneを返す

    # ②提供されたフィールドのみ抽出
    # exclude_unset=True: 値が指定されたフィールドのみ取得
    # 例: UserUpdate(email="new@...") → {"email": "new@..."}
    #     password は含まれない
    update_data = user_update.model_dump(exclude_unset=True)

    # ③パスワードが含まれている場合、ハッシュ化
    if "password" in update_data:
        hashed_password = hash_password(update_data["password"])
        del update_data["password"]  # passwordを削除
        update_data["hashed_password"] = hashed_password  # hashed_passwordを追加

    # ④ユーザー情報を更新
    # setattr(obj, key, value): obj.key = value と同じ
    # 例: setattr(db_user, "email", "new@...") → db_user.email = "new@..."
    for key, value in update_data.items():
        setattr(db_user, key, value)

    # ⑤DBに保存
    db.commit()        # トランザクションをコミット
    db.refresh(db_user)  # DBから最新の状態を取得（updated_atが自動更新される）

    return db_user


def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """
    ユーザー認証（ログイン）

    Args:
        db: データベースセッション
        email: メールアドレス
        password: 平文パスワード

    Returns:
        認証成功時はユーザーオブジェクト、失敗時はNone

    処理フロー:
        1. メールアドレスでユーザーを検索
           ↓ 存在しない → None（認証失敗）

        2. パスワードを検証
           ↓ 間違っている → None（認証失敗）

        3. アカウントが有効かチェック
           ↓ 無効 → None（認証失敗）

        4. 全てOK → ユーザーオブジェクト（認証成功）

    セキュリティ:
        - 「ユーザーが存在しない」と「パスワードが間違っている」を区別しない
          → どちらも None を返す
        - 理由: ユーザーの存在を推測されるのを防ぐ

    使用例:
        user = authenticate_user(db, "test@example.com", "Password123")
        if user:
            print("ログイン成功")
            access_token = create_access_token({"sub": user.email})
        else:
            print("ログイン失敗")
    """
    # ①メールアドレスでユーザーを検索
    user = get_user_by_email(db, email)
    if not user:
        return None  # ユーザーが存在しない

    # ②パスワードを検証
    # verify_password(): bcryptでハッシュ化されたパスワードを検証
    if not verify_password(password, user.hashed_password):
        return None  # パスワードが間違っている

    # ③アカウントが有効かチェック
    if not user.is_active:
        return None  # アカウントが無効（削除済みなど）

    # ④全てOK
    return user
