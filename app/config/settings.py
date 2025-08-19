# FIX-102
# app/config/settings.py

import json
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional, Union, Tuple

from pydantic import Field, SecretStr, field_validator, model_validator, ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict

# Loyiha asosiy papkasi
BASE_DIR = Path(__file__).resolve().parent.parent.parent

class Settings(BaseSettings):
    """'Tez Ovoz' botining asosiy sozlamalari modeli."""

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra='ignore',
        validate_default=True,
        populate_by_name=True
    )

    # --- Ishlash Rejimi (Deployment) Sozlamalari ---
    APP_ENV: Literal["development", "production"] = Field("development", description="Ilova ishlash muhiti.")
    
    # Botning asosiy sozlamalari
    BOT_TOKEN: SecretStr = Field(..., description="Telegram bot tokeni (BotFather'dan olingan).")
    ADMIN_IDS: List[int] = Field(default_factory=list, description="Adminlarning Telegram ID'lari ro'yxati (JSON formatda).")

    # Ma'lumotlar bazasi sozlamalari
    DATABASE_TYPE: Literal["postgresql", "mysql", "sqlite"] = Field("sqlite", description="Foydalaniladigan ma'lumotlar bazasi turi.")
    DB_URL: str = Field(..., description="Ma'lumotlar bazasiga ulanish URL'i.")
    DB_ECHO: bool = Field(False, description="Konsolga SQL so'rovlarini aks ettirish.")
    
    # Log sozlamalari
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field("DEBUG", description="Log darajasi.")
    LOG_FILE_PATH: Path = Field(BASE_DIR / "logs" / "bot.log", description="Log fayli yo'li.")

    # Til sozlamalari
    DEFAULT_LANGUAGE: str = Field("uz", description="Botning sukut bo'yicha tili.")
    SUPPORTED_LANGUAGES: List[str] = Field(["uz", "ru", "tg"], description="Qo'llab-quvvatlanadigan tillar ro'yxati.")
    LOCALES_DIR: Path = Field(BASE_DIR / "app" / "locales", description="Tarjima fayllari joylashgan papka.")
    I18N_DOMAIN: str = "main" # Tarjima fayllari uchun domen nomi
    
    LANGUAGE_CODES_MAPPING: Dict[str, Tuple[str, str]] = Field({
        "uz": ("O'zbek", "🇺🇿"),
        "ru": ("Русский", "🇷🇺"),
        "tg": ("Тоҷикӣ", "🇹🇯"),
    }, description="Til kodlarining tugma matni va emoji bilan bog'lanishi.")

    # Openbudget API Sozlamalari
    OPENBUDGET_API_URL: str = Field(..., description="Openbudget API asosiy manzili.")
    OPENBUDGET_PROJECT_ID: int = Field(..., description="Ovoz berish uchun loyiha identifikatori.")

    # --- Validatorlar ---
    @field_validator('ADMIN_IDS', 'SUPPORTED_LANGUAGES', mode='before')
    @classmethod
    def _parse_list_from_json_string(cls, v: Union[str, List[Any]]) -> List[Any]:
        """JSON satridan ro'yxatni ajratib oladi."""
        if isinstance(v, str):
            try:
                parsed_list = json.loads(v)
                if not isinstance(parsed_list, list):
                    raise ValueError("JSON satri ro'yxat bo'lishi kerak.")
                return parsed_list
            except json.JSONDecodeError as e:
                raise ValueError(f"JSON formati noto'g'ri: {e}")
        return v
    
    @model_validator(mode='after')
    def check_db_url_and_type(self) -> 'Settings':
        """DATABASE_TYPE va DB_URL bir-biriga mos kelishini tekshiradi."""
        if self.DATABASE_TYPE == "postgresql" and not self.DB_URL.startswith("postgresql"):
            raise ValueError("DATABASE_TYPE 'postgresql' bo'lganda, DB_URL 'postgresql' bilan boshlanishi kerak.")
        if self.DATABASE_TYPE == "mysql" and not self.DB_URL.startswith("mysql"):
            raise ValueError("DATABASE_TYPE 'mysql' bo'lganda, DB_URL 'mysql' bilan boshlanishi kerak.")
        if self.DATABASE_TYPE == "sqlite" and not self.DB_URL.startswith("sqlite"):
            raise ValueError("DATABASE_TYPE 'sqlite' bo'lganda, DB_URL 'sqlite' bilan boshlanishi kerak.")
        return self

    @model_validator(mode='after')
    def check_supported_languages_mapping(self) -> 'Settings':
        """SUPPORTED_LANGUAGES ro'yxatidagi til kodlari LANGUAGE_CODES_MAPPING lug'atida mavjudligini tekshiradi."""
        # 'SUPPORTED_LANGUAGES' nomini to'g'ri yozish kerak
        for lang_code in self.SUPPORTED_LANGUAGES:
            if lang_code not in self.LANGUAGE_CODES_MAPPING:
                raise ValueError(f"SUPPORTED_LANGUAGES ro'yxatidagi '{lang_code}' tili LANGUAGE_CODES_MAPPING lug'atida topilmadi.")
        return self


def get_settings() -> Settings:
    """Sozlamalarni yuklash va validatsiya qilish uchun yordamchi funksiya."""
    try:
        return Settings() # type: ignore
    except ValidationError as e:
        print(f"Konfiguratsiya xatosi: {e}\nIltimos, sozlamalarni tekshirib, to'g'rilang.")
        exit(1)

settings = get_settings()
