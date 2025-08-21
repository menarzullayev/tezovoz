# app/config/settings.py
# FIX-104

import json
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional, Union, Tuple
from pydantic import Field, SecretStr, field_validator, model_validator, ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict
from loguru import logger # NEW-104: loguru import qilindi

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
    I18N_DOMAIN: str = "messages" # Babel va gettext uchun domen nomi
    
    LANGUAGE_CODES_MAPPING: Dict[str, Tuple[str, str]] = Field({
        "uz": ("O'zbek", "🇺🇿"),
        "ru": ("Русский", "🇷🇺"),
        "tg": ("Тоҷикӣ", "🇹🇯"),
    }, description="Til kodlarining tugma matni va emoji bilan bog'lanishi.")

    # Openbudget API Sozlamalari
    OPENBUDGET_API_URL: str = Field(..., description="Openbudget API asosiy manzili.")
    OPENBUDGET_PROJECT_ID: int = Field(..., description="Ovoz berish uchun loyiha identifikatori.")
    
    # NEW-103: Webhook sozlamalari (hozircha kommentda)
    # WEBHOOK_URL: Optional[str] = Field(None, description="Webhook URL manzili.")
    # WEBHOOK_PATH: Optional[str] = Field("/webhook", description="Webhook yo'li.")

    # --- Validatorlar ---
    @field_validator('ADMIN_IDS', 'SUPPORTED_LANGUAGES', mode='before')
    @classmethod
    def _parse_list_from_json_string(cls, v: Union[str, List[Any]]) -> List[Any]:
        """JSON satridan ro'yxatni ajratib oladi."""
        logger.debug(f"Validator: _parse_list_from_json_string chaqirildi, kiruvchi qiymat: {v}")
        if isinstance(v, str):
            try:
                parsed_list = json.loads(v)
                if not isinstance(parsed_list, list):
                    raise ValueError("JSON satri ro'yxat bo'lishi kerak.")
                logger.debug(f"Validator: JSON satri muvaffaqiyatli ro'yxatga aylantirildi: {parsed_list}")
                return parsed_list
            except json.JSONDecodeError as e:
                logger.error(f"Validator: JSONDecodeError - {e}, qiymat: {v}")
                raise ValueError(f"JSON formati noto'g'ri: {e}")
        logger.debug(f"Validator: Qiymat allaqachon ro'yxat, o'zgarishsiz qaytarilmoqda.")
        return v
    
    @model_validator(mode='after')
    def check_db_url_and_type(self) -> 'Settings':
        """DATABASE_TYPE va DB_URL bir-biriga mos kelishini tekshiradi."""
        logger.debug(f"Validator: check_db_url_and_type chaqirildi, DB_URL: {self.DB_URL}, DATABASE_TYPE: {self.DATABASE_TYPE}")
        if self.DATABASE_TYPE == "postgresql" and not self.DB_URL.startswith("postgresql"):
            logger.critical("Validator Error: PostgreSQL uchun DB_URL noto'g'ri.")
            raise ValueError("DATABASE_TYPE 'postgresql' bo'lganda, DB_URL 'postgresql' bilan boshlanishi kerak.")
        if self.DATABASE_TYPE == "mysql" and not self.DB_URL.startswith("mysql"):
            logger.critical("Validator Error: MySQL uchun DB_URL noto'g'ri.")
            raise ValueError("DATABASE_TYPE 'mysql' bo'lganda, DB_URL 'mysql' bilan boshlanishi kerak.")
        if self.DATABASE_TYPE == "sqlite" and not self.DB_URL.startswith("sqlite"):
            logger.critical("Validator Error: SQLite uchun DB_URL noto'g'ri.")
            raise ValueError("DATABASE_TYPE 'sqlite' bo'lganda, DB_URL 'sqlite' bilan boshlanishi kerak.")
        logger.debug("Validator: DB_URL va DATABASE_TYPE mosligi tekshirildi.")
        return self

    @model_validator(mode='after')
    def check_supported_languages_mapping(self) -> 'Settings':
        """SUPPORTED_LANGUAGES ro'yxatidagi til kodlari LANGUAGE_CODES_MAPPING lug'atida mavjudligini tekshiradi."""
        logger.debug("Validator: check_supported_languages_mapping chaqirildi.")
        for lang_code in self.SUPPORTED_LANGUAGES:
            if lang_code not in self.LANGUAGE_CODES_MAPPING:
                logger.critical(f"Validator Error: '{lang_code}' tili LANGUAGE_CODES_MAPPING lug'atida topilmadi.")
                raise ValueError(f"SUPPORTED_LANGUAGES ro'yxatidagi '{lang_code}' tili LANGUAGE_CODES_MAPPING lug'atida topilmadi.")
        logger.debug("Validator: Qo'llab-quvvatlanadigan tillar mapping'i tekshirildi.")
        return self


def get_settings() -> Settings:
    """Sozlamalarni yuklash va validatsiya qilish uchun yordamchi funksiya."""
    logger.info("Sozlamalarni yuklash boshlandi...")
    try:
        settings_instance = Settings() # type: ignore
        logger.success("Sozlamalar muvaffaqiyatli yuklandi va tasdiqlandi.")
        return settings_instance
    except ValidationError as e:
        logger.critical(f"Konfiguratsiya xatosi: {e}\nIltimos, sozlamalarni tekshirib, to'g'rilang.")
        print(f"Konfiguratsiya xatosi: {e}\nIltimos, sozlamalarni tekshirib, to'g'rilang.")
        exit(1)

settings = get_settings()
logger.info("Sozlamalar obyekti global o'zgaruvchiga o'rnatildi.")