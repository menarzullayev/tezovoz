# FIX-152
# app/utils/api_client.py

from typing import Dict, Any, Optional
import httpx
from loguru import logger
from app.config.settings import settings
from app.utils.helpers import retry_on_exception
import random
import ipaddress
import base64
import io
from app.utils.captcha_utils import get_captcha_data_from_browser # Selenium funksiyasini import qilamiz

def generate_random_ip() -> str:
    """
    Tasodifiy IP-manzil yaratadi.
    """
    ips = ['46.227.123.', '37.110.212.', '46.255.69.', '62.209.128.', '37.110.214.', '31.135.209.', '37.110.213.']
    prefix = random.choice(ips)
    return prefix + str(random.randint(1, 255))

class OpenbudgetAPI:
    """
    Openbudget API bilan ishlash uchun sinf.
    """
    def __init__(self):
        self.base_url = settings.OPENBUDGET_API_URL
        self.async_client = httpx.AsyncClient(base_url=self.base_url, timeout=10)

    async def get_captcha(self) -> Optional[Dict[str, Any]]:
        """
        CAPTCHA rasmi va uning kalitini selenium orqali olish funksiyasi.
        """
        return await get_captcha_data_from_browser()

    @retry_on_exception(retries=3, delay=2, exceptions=(httpx.RequestError,))
    async def send_otp(self, captcha_key: str, captcha_result: int, phone_number: str) -> Optional[Dict[str, Any]]:
        """
        SMS orqali OTP kodini yuborish uchun so'rov yuboradi.
        """
        logger.info(f"OTP yuborish uchun so'rov yuborilmoqda: {phone_number}")
        url = "/v1/login/send-otp"
        payload = {
            "captcha_key": captcha_key,
            "captcha_result": captcha_result,
            "phone_number": phone_number
        }
        random_ip = generate_random_ip()
        headers = {
            "Host": "admin.openbudget.uz",
            "REMOTE_ADDR": random_ip,
            "HTTP_X_FORWARDED_FOR": random_ip,
            "HTTP_X_REAL_IP": random_ip,
            "X-Forwarded-For": random_ip
        }
        try:
            response = await self.async_client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            logger.success("OTP kodi muvaffaqiyatli yuborildi.")
            return data
        except httpx.HTTPStatusError as e:
            logger.error(f"OTP yuborishda HTTP xatolik: {e.response.status_code}. Javob: {e.response.text}")
            return None
        except Exception as e:
            logger.error(f"OTP yuborishda kutilmagan xatolik yuz berdi: {e}", exc_info=True)
            return None

    @retry_on_exception(retries=3, delay=2, exceptions=(httpx.RequestError,))
    async def verify_otp_and_vote(self, phone_number: str, otp_code: str, otp_key: str) -> Optional[Dict[str, Any]]:
        """
        OTP kodini tasdiqlash va ovoz berish uchun so'rov yuboradi.
        """
        logger.info(f"OTPni tasdiqlash va ovoz berish uchun so'rov yuborilmoqda: {phone_number}")
        url = "/v1/login/verify-otp"
        payload = {
            "phone_number": phone_number,
            "otp_code": otp_code,
            "otp_key": otp_key,
            "application": settings.OPENBUDGET_PROJECT_ID
        }
        random_ip = generate_random_ip()
        headers = {
            "Host": "admin.openbudget.uz",
            "REMOTE_ADDR": random_ip,
            "HTTP_X_FORWARDED_FOR": random_ip,
            "HTTP_X_REAL_IP": random_ip,
            "X-Forwarded-For": random_ip
        }
        try:
            response = await self.async_client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            logger.success("Ovoz muvaffaqiyatli tasdiqlandi.")
            return data
        except httpx.HTTPStatusError as e:
            logger.error(f"OTPni tasdiqlashda HTTP xatolik: {e.response.status_code}. Javob: {e.response.text}")
            return None
        except Exception as e:
            logger.error(f"OTPni tasdiqlashda kutilmagan xatolik yuz berdi: {e}", exc_info=True)
            return None

openbudget_api = OpenbudgetAPI()
