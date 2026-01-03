from datetime import datetime, timedelta
from typing import Any, Dict
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings


# ===============================================
# パスワードハッシュ化の設定（bcrypt）
# ===============================================
# bcrypt: パスワードハッシュ化アルゴリズム
# - ソルトを自動生成（同じパスワードでも毎回異なるハッシュ）
# - 計算コストが高い（ブルートフォース攻撃に強い）
# - 一方向ハッシュ（元のパスワードは復元不可能）
#
# 例: "password123" を3回ハッシュ化すると...
#   1回目: $2b$12$EixZaYVK1fsbw1ZfbX3OXe...
#   2回目: $2b$12$KQZ9x8vN2mH7pL3qR1sT4u...  ← 異なる！
#   3回目: $2b$12$MnP5yA2bC8dE7fG9hJ0kL1...  ← 異なる！
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    パスワードをbcryptでハッシュ化
    
    Args:
        password: 平文パスワード
    
    Returns:
        ハッシュ化されたパスワード
        
    例:
        "password123" → "$2b$12$EixZaYVK1fsbw1ZfbX3OXe..."
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    パスワードを検証
    
    Args:
        plain_password: ユーザーが入力した平文パスワード
        hashed_password: データベースに保存されたハッシュ化パスワード
    
    Returns:
        パスワードが一致すればTrue、異なればFalse
    """
    return pwd_context.verify(plain_password, hashed_password)


# ===============================================
# JWTトークンの生成・検証
# ===============================================
def create_access_token(data: Dict[str, Any]) -> str:
    """
    Access Token（短命トークン）を生成

    Args:
        data: トークンに埋め込むデータ（例: {"sub": "user@example.com"}）

    Returns:
        JWT Access Token (例: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...")

    セキュリティ要件:
        - 有効期限: 15分（設定ファイルから読み込み）
        - 短命なので、漏洩時の被害を最小化

    JWT の構造:
        ヘッダー.ペイロード.署名

        ヘッダー: {"alg": "HS256", "typ": "JWT"}
        ペイロード: {"sub": "user@example.com", "exp": 1234567890, "type": "access"}
        署名: SECRET_KEY を使って計算（改ざん検知）
    """
    to_encode = data.copy()  # 元のdataを変更しないようにコピー

    # 有効期限を設定（現在時刻 + 15分）
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "type": "access"})

    # JWTを生成（SECRET_KEYで署名）
    encoded_jwt = jwt.encode(
        to_encode,               # ペイロード
        settings.SECRET_KEY,     # 署名用の秘密鍵
        algorithm=settings.ALGORITHM,  # 署名アルゴリズム（HS256）
    )
    return encoded_jwt


def create_refresh_token(data: Dict[str, Any]) -> str:
    """
    Refresh Token（長命トークン）を生成

    Args:
        data: トークンに埋め込むデータ（例: {"sub": "user@example.com"}）

    Returns:
        JWT Refresh Token

    セキュリティ要件:
        - 有効期限: 7日（設定ファイルから読み込み）
        - Access Tokenの再発行に使用
        - Redis/DBで管理し、ログアウト時に無効化する

    Access Token と Refresh Token の違い:
        Access Token (15分):
            - API呼び出し時に使用
            - 短命 → 漏洩しても被害が限定的

        Refresh Token (7日):
            - Access Tokenの再発行にのみ使用
            - 長命 → ユーザーは頻繁にログインしなくてOK
            - DBで管理 → ログアウト時に無効化できる
    """
    to_encode = data.copy()

    # 有効期限を設定（現在時刻 + 7日）
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})  # type で区別

    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )
    return encoded_jwt


def decode_token(token: str) -> Dict[str, Any]:
    """
    JWT トークンをデコードして検証

    Args:
        token: JWT トークン

    Returns:
        デコードされたペイロード（例: {"sub": "user@example.com", "exp": 1234567890}）

    Raises:
        JWTError: トークンが無効または期限切れの場合

    検証内容:
        1. 署名の検証: SECRET_KEY で署名を再計算し、一致するかチェック
           → 改ざんされていないことを保証

        2. 有効期限のチェック: exp（expiration）が現在時刻より後か
           → 期限切れトークンは拒否

        3. アルゴリズムの検証: 指定したアルゴリズム（HS256）で署名されているか
           → アルゴリズム攻撃を防ぐ
    """
    try:
        payload = jwt.decode(
            token,                      # デコードするトークン
            settings.SECRET_KEY,        # 署名検証用の秘密鍵
            algorithms=[settings.ALGORITHM],  # 許可するアルゴリズム
        )
        return payload
    except JWTError as e:
        # トークンが無効、期限切れ、署名が不正など
        raise JWTError(f"Invalid token: {str(e)}")
