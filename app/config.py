
from pydantic_settings import BaseSettings
from pydantic import Field
from pathlib import Path
class Settings(BaseSettings):
    gemini_api_key: str = Field(default="", description="Free key")
    gemini_model: str = "gemini-2.5-flash-lite"
    gemini_temperature: float = 0.1
    gemini_max_output_tokens: int = 4096
    docling_confidence_threshold: float = 0.3
    max_file_size_mb: int = 50
    output_dir: Path = Path("./outputs")
    db_path: Path = Path("./outputs/extractions.db")
    cors_origins: str = "http://localhost:3000,http://localhost:5173,http://localhost:8000"
    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "case_sensitive": False}
    @property
    def gemini_configured(self) -> bool:
        return bool(self.gemini_api_key) and self.gemini_api_key != "YOUR_KEY"
    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]
settings = Settings()
