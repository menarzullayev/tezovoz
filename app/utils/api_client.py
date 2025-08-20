# FIX-152 (YAKUNIY "GZIP DECOMPRESSION" BILAN)
# app/utils/api_client.py

import asyncio
from typing import Dict, Any, Optional
import httpx
from loguru import logger
from app.config.settings import settings
from app.utils.helpers import retry_on_exception
import random
import json
import gzip # GZIP arxivini ochish uchun kutubxonani qo'shamiz

# Endi oddiy selenium o'rniga selenium-wire dan foydalanamiz
from seleniumwire import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class OpenbudgetAPI:
    """Openbudget API bilan ishlash uchun sinf."""
    def __init__(self):
        self.base_url = "https://openbudget.uz"
        self.async_client = httpx.AsyncClient(base_url=self.base_url, timeout=30)

    async def get_captcha(self) -> Optional[Dict[str, Any]]:
        """
        selenium-wire yordamida brauzerning network trafigini tinglab,
        tayyor CAPTCHA javobini "tutib oladi" va Gzip'dan ochadi.
        """
        
        def _sync_get_captcha_via_interception():
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
            chrome_options.add_argument(f'user-agent={user_agent}')
            chrome_options.add_experimental_option('excludeSwitches', ['enable-automation', 'enable-logging'])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            seleniumwire_options = {'disable_capture': True}

            driver = None
            try:
                logger.debug("Yakuniy usul: Network trafigini tinglash rejimi yoqilmoqda...")
                service = ChromeService(ChromeDriverManager().install())
                driver = webdriver.Chrome(service=service, options=chrome_options, seleniumwire_options=seleniumwire_options)
                
                driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
                driver.scopes = ['.*openbudget.uz/api/v2/vote/captcha-2.*']

                main_page_url = "https://openbudget.uz/budget-system"
                driver.get(main_page_url)
                
                wait = WebDriverWait(driver, 20)
                login_button = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "sign-in")))
                login_button.click()
                logger.debug("'Kirish' tugmasi bosildi.")

                logger.info("Brauzerning o'zi CAPTCHA so'rovini yuborishini kutyapmiz...")
                request = driver.wait_for_request('/api/v2/vote/captcha-2', timeout=20)
                
                if request and request.response:
                    logger.success("Muvaffaqiyat! CAPTCHA javobi networkdan to'g'ridan-to'g'ri 'tutib olindi'.")
                    
                    # ---- YECHIM: GZIP DEKOMPRESSIYA ----
                    # Javob Gzip bilan siqilgan bo'lsa, uni arxivdan ochamiz
                    response_body_bytes = request.response.body
                    if request.response.headers.get('Content-Encoding') == 'gzip':
                        logger.debug("Javob Gzip formatida. Dekompressiya qilinmoqda...")
                        response_body_bytes = gzip.decompress(response_body_bytes)
                    
                    # Endi toza ma'lumotni matnga va keyin JSONga o'giramiz
                    decoded_body = response_body_bytes.decode('utf-8')
                    captcha_data = json.loads(decoded_body)
                    return captcha_data
                else:
                    logger.error("Networkdan CAPTCHA so'rovi topilmadi yoki javob bo'sh.")
                    return None

            except Exception as e:
                logger.error(f"Networkni tinglashda xatolik yuz berdi: {e}", exc_info=True)
                if driver:
                    driver.save_screenshot("error_screenshot.png")
                return None
            finally:
                if driver:
                    driver.quit()

        return await asyncio.to_thread(_sync_get_captcha_via_interception)

    @retry_on_exception(retries=2, delay=2, exceptions=(httpx.RequestError,))
    async def send_otp(self, captcha_key: str, captcha_result: int, phone_number: str) -> Optional[Dict[str, Any]]:
        logger.info(f"OTP yuborish uchun so'rov yuborilmoqda: {phone_number}")
        url = "/api/v1/login/send-otp"
        payload = {"captcha_key": captcha_key, "captcha_result": int(captcha_result), "phone_number": phone_number}
        try:
            response = await self.async_client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
            logger.success("OTP kodi muvaffaqiyatli yuborildi.")
            return data
        except httpx.HTTPStatusError as e:
            logger.error(f"OTP yuborishda HTTP xatolik: {e.response.status_code}. Javob: {e.response.text}")
            return e.response.json()
        except Exception as e:
            logger.error(f"OTP yuborishda kutilmagan xatolik: {e}", exc_info=True)
            return None

    @retry_on_exception(retries=2, delay=2, exceptions=(httpx.RequestError,))
    async def verify_otp_and_vote(self, phone_number: str, otp_code: str, otp_key: str) -> Optional[Dict[str, Any]]:
        logger.info(f"OTPni tasdiqlash uchun so'rov yuborilmoqda: {phone_number}")
        
        phone_number_for_payload = phone_number
        if phone_number.startswith('998') and len(phone_number) == 12:
            phone_number_for_payload = phone_number[3:]
        
        url = "/api/v1/login/verify-otp"
        payload = {
            "phone_number": phone_number_for_payload,
            "otp_code": otp_code,
            "otp_key": otp_key,
            "application": settings.OPENBUDGET_PROJECT_ID
        }
        try:
            response = await self.async_client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
            logger.success("Ovoz muvaffaqiyatli tasdiqlandi (verify-otp).")
            return data
        except httpx.HTTPStatusError as e:
            logger.error(f"OTPni tasdiqlashda HTTP xatolik: {e.response.status_code}. Javob: {e.response.text}")
            return None
        except Exception as e:
            logger.error(f"OTPni tasdiqlashda kutilmagan xatolik: {e}", exc_info=True)
            return None

openbudget_api = OpenbudgetAPI()