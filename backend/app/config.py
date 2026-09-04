from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Intelligent Incident Investigation System API"
    api_prefix: str = "/api/v1"
    database_url: str = "mysql+pymysql://iiis:iiis_password@localhost:3306/iiis"
    jwt_secret_key: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 120
    upload_dir: str = "uploads"
    model_path: str = "app/ml/artifacts/decision_tree_model.joblib"
    encoders_path: str = "app/ml/artifacts/encoders.joblib"
    feature_columns_path: str = "app/ml/artifacts/feature_columns.joblib"
    smtp_host: str | None = None
    smtp_port: int = 587
    smtp_username: str | None = None
    smtp_password: str | None = None
    smtp_from_email: str = "no-reply@iiis.local"
    smtp_use_tls: bool = True

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
