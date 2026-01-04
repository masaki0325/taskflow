from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Dict
from jose import JWTError

from app.core.database import get_db
from app.core.security import create_access_token, create_refresh_token, decode_token
from app.crud.user import create_user, get_user_by_email, authenticate_user
from app.schemas.user import UserCreate, UserResponse
from app.models.user import User


# ===============================================
# 認証APIエンドポイント
# ===============================================
# このファイルで定義するAPI:
#   POST /api/v1/auth/register  - ユーザー登録
#   POST /api/v1/auth/login     - ログイン
#   POST /api/v1/auth/refresh   - トークン更新
#   GET  /api/v1/auth/me        - 現在のユーザー情報取得

# APIRouterを作成（main.pyで登録する）
router = APIRouter()

# HTTPBearer: HTTP Authorization ヘッダーから Bearer トークンを取得
# クライアント: Authorization: Bearer <token>
security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    """
    依存性注入: 現在のユーザーを取得

    HTTPヘッダーから Access Token を取得し、ユーザーを返す

    処理フロー:
        1. HTTPヘッダーから Bearer トークンを取得
           Authorization: Bearer eyJhbGci...

        2. JWTをデコード・検証
           → 署名の検証、有効期限チェック

        3. トークンタイプの確認
           → type="access" であることを検証（Refresh Tokenは拒否）

        4. トークンから email を取得

        5. DBからユーザーを検索

        6. アカウントが有効かチェック

        7. ユーザーを返す

    使用例:
        @router.get("/protected")
        def protected_route(current_user: User = Depends(get_current_user)):
            # current_userが自動的に注入される
            return {"user": current_user.email}

        クライアント:
        GET /protected
        Headers: Authorization: Bearer <access_token>

    Raises:
        HTTPException 401: トークンが無効、期限切れ、タイプが不正、またはユーザーが存在しない場合
        HTTPException 403: アカウントが無効な場合

    セキュリティ:
        - Access Token（15分有効）のみを受け入れる
        - Refresh Token（7日有効）での認証は拒否される
        - これにより、トークンの短命設計が機能し、セキュリティが向上
    """
    # ①HTTPヘッダーから Bearer トークンを取得
    # credentials.credentials: "eyJhbGci..." (Bearerは除かれる)
    token = credentials.credentials

    # ②JWTをデコード・検証
    try:
        payload = decode_token(token)  # 署名検証 + 有効期限チェック
    except JWTError:
        # トークンが無効または期限切れ
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        ) from None

    # ③トークンタイプの確認（RefreshトークンではなくAccessトークンか）
    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
        )

    # ④トークンから email を取得
    # payload = {"sub": "user@example.com", "exp": 1234567890, "type": "access"}
    user_email = payload.get("sub")
    if not user_email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    # ⑤DBからユーザーを検索
    user = get_user_by_email(db, user_email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    # ⑥アカウントが有効かチェック
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user",
        )

    # ⑦ユーザーを返す
    return user


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_create: UserCreate, db: Session = Depends(get_db)):
    """
    ユーザー登録（POST /api/v1/auth/register）

    Args:
        user_create: ユーザー作成データ（email, password）
        db: データベースセッション（依存性注入）

    Returns:
        作成されたユーザー情報（パスワードを除く）

    Raises:
        HTTPException 400: メールアドレスが既に登録されている場合

    処理フロー:
        1. メールアドレスの重複チェック
        2. ユーザー作成（CRUD）
           → パスワードをbcryptでハッシュ化
           → DBに保存
        3. UserResponseに変換して返す

    使用例:
        POST /api/v1/auth/register
        {
          "email": "test@example.com",
          "password": "Password123"
        }

        Response (201 Created):
        {
          "id": 1,
          "email": "test@example.com",
          "is_active": true,
          "is_superuser": false,
          "created_at": "2026-01-01T10:00:00Z",
          "updated_at": "2026-01-01T10:00:00Z"
        }
    """
    # ①メールアドレスの重複チェック
    existing_user = get_user_by_email(db, user_create.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # ②ユーザー作成（パスワードはCRUD内でハッシュ化される）
    user = create_user(db, user_create)

    # ③UserResponseに変換して返す
    # response_model=UserResponse により、hashed_passwordは自動的に除外される
    return user


@router.post("/login")
def login(user_create: UserCreate, db: Session = Depends(get_db)) -> Dict[str, str]:
    """
    ログイン（POST /api/v1/auth/login）

    Args:
        user_create: ログイン情報（email, password）
        db: データベースセッション（依存性注入）

    Returns:
        Access Token + Refresh Token

    Raises:
        HTTPException 401: 認証失敗（メールアドレスまたはパスワードが間違っている）

    処理フロー:
        1. ユーザー認証（CRUD）
           → メールアドレスでユーザー検索
           → パスワード検証（bcrypt）
           → アカウント有効チェック

        2. トークン生成
           → Access Token（有効期限15分）
           → Refresh Token（有効期限7日）

        3. トークンを返す

    使用例:
        POST /api/v1/auth/login
        {
          "email": "test@example.com",
          "password": "Password123"
        }

        Response (200 OK):
        {
          "access_token": "eyJhbGci...",
          "refresh_token": "eyJhbGci...",
          "token_type": "bearer"
        }

        クライアント（Next.js）での使用:
        const { access_token, refresh_token } = await response.json();
        localStorage.setItem('access_token', access_token);
        localStorage.setItem('refresh_token', refresh_token);
    """
    # ①認証（メール+パスワード検証）
    user = authenticate_user(db, user_create.email, user_create.password)
    if not user:
        # セキュリティ: 「ユーザーが存在しない」と「パスワードが間違っている」を区別しない
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    # ②トークン生成
    # sub（subject）: トークンの対象となるユーザーのメールアドレス
    access_token = create_access_token({"sub": user.email})
    refresh_token = create_refresh_token({"sub": user.email})

    # ③トークンを返す
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",  # OAuth 2.0 の標準形式
    }


@router.post("/refresh")
def refresh(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> Dict[str, str]:
    """
    Refresh Tokenを使ってAccess Tokenを再発行
    
    Args:
        credentials: HTTPヘッダーのBearerトークン（Refresh Token）
        db: データベースセッション（依存性注入）
    
    Returns:
        新しいAccess Token
        
    Raises:
        HTTPException: Refresh Tokenが無効または期限切れの場合
    """
    token = credentials.credentials

    try:
        payload = decode_token(token)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        ) from None
    
    # トークンタイプの確認（AccessトークンではなくRefreshトークンか）
    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
        )
    
    user_email = payload.get("sub")
    if not user_email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )
    
    user = get_user_by_email(db, user_email)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )
    
    # 新しいAccess Tokenを発行
    new_access_token = create_access_token({"sub": user.email})
    
    return {
        "access_token": new_access_token,
        "token_type": "bearer",
    }


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """
    現在ログイン中のユーザー情報を取得
    
    Args:
        current_user: 現在のユーザー（依存性注入）
    
    Returns:
        ユーザー情報（パスワードを除く）
    """
    return current_user
