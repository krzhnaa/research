# backend/app/config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    SERPER_API_KEY: str = os.getenv("SERPER_API_KEY", "")
    OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "")
    OPENROUTER_DEFAULT_MODEL: str = os.getenv(
        "OPENROUTER_DEFAULT_MODEL", "meta-llama/llama-3.3-70b-instruct:free"
    )
    DISCORD_BOT_TOKEN: str = os.getenv("DISCORD_BOT_TOKEN", "")
    DISCORD_CHANNEL_ID: str = os.getenv("DISCORD_CHANNEL_ID", "")
    FRONTEND_ORIGIN: str = os.getenv("FRONTEND_ORIGIN", "http://127.0.0.1:4173")

    @property
    def frontend_origins(self) -> list[str]:
        configured = [origin.strip() for origin in self.FRONTEND_ORIGIN.split(",") if origin.strip()]
        defaults = [
            "http://127.0.0.1:4173",
            "http://localhost:4173",
            "http://127.0.0.1:5173",
            "http://localhost:5173",
        ]
        return list(dict.fromkeys(configured + defaults))

    def validate(self):
        missing = []
        if not self.SERPER_API_KEY:
            missing.append("SERPER_API_KEY")
        if not self.OPENROUTER_API_KEY:
            missing.append("OPENROUTER_API_KEY")
        if missing:
            print(f"⚠️  WARNING: Missing environment variables: {', '.join(missing)}")


settings = Settings()
settings.validate()
