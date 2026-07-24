
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
    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "case_sensitive": False}
    @property
    def gemini_configured(self) -> bool:
        return bool(self.gemini_api_key) and self.gemini_api_key != "YOUR_KEY"
settings = Settings()
