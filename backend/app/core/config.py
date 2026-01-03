from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    アプリケーション設定

    .envファイルから環境変数を読み込む
    Pydantic Settingsを使用して、型安全に環境変数を管理
    """

    # Database
    DATABASE_URL: str  # 必須項目（デフォルト値なし）- PostgreSQL接続URL

    # Security
    SECRET_KEY: str  # 必須項目 - JWT署名用の秘密鍵
    ALGORITHM: str = "HS256"  # JWT署名アルゴリズム（デフォルト: HS256）
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15  # Access Tokenの有効期限（分）
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7  # Refresh Tokenの有効期限（日）

    # CORS
    ALLOWED_ORIGINS: str = "http://localhost:3000"  # CORS許可オリジン（カンマ区切り）

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"  # Redis接続URL

    # Environment
    ENVIRONMENT: str = "development"  # 実行環境（development/staging/production）

    model_config = SettingsConfigDict(
        env_file=".env",  # 読み込む環境変数ファイル
        case_sensitive=True  # 大文字小文字を区別する（DATABASE_URL ≠ database_url）
    )

    @property
    def cors_origins(self) -> list[str]:
        """
        CORS許可オリジンをリストで返す

        ALLOWED_ORIGINS="http://localhost:3000,http://localhost:8000"
        → ["http://localhost:3000", "http://localhost:8000"]
        """
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]


# シングルトンインスタンス
# アプリケーション全体で共有する設定オブジェクト
# 使用例: from app.core.config import settings
#         print(settings.DATABASE_URL)
settings = Settings()
