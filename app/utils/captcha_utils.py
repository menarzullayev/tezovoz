# FIX-154
# app/utils/captcha_utils.py

import asyncio
from typing import Optional, Dict
import base64
from io import BytesIO
import re
from loguru import logger
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

async def get_captcha_data_from_browser() -> Optional[Dict[str, str]]:
    """
    Selenium yordamida brauzer orqali CAPTCHA tasviri va uning kalitini oladi.
    """
    def _sync_get_captcha():
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36")
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        
        driver = None
        try:
            logger.debug("Selenium brauzeri ishga tushirilmoqda...")
            service = ChromeService(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            driver.implicitly_wait(10)
            
            main_page_url = "https://openbudget.uz/budget-system"
            driver.get(main_page_url)
            
            wait = WebDriverWait(driver, 15)
            login_button = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "sign-in")))
            login_button.click()
            logger.debug("'Kirish' tugmasi bosildi.")

            wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "captcha-img")))
            logger.debug("CAPTCHA rasmi modal oynada paydo bo'ldi.")
            
            captcha_element = driver.find_element(By.CLASS_NAME, "captcha-img")
            img_base64 = captcha_element.get_attribute("src")

            # JavaScript kodini bajarib, captchaKey'ni olamiz
            captcha_key = driver.execute_script(
                "return document.querySelector('img.captcha-img').getAttribute('src').split('base64,')[0].split('/').pop().split('?')[0]"
            )
            
            if "base64," in img_base64 and captcha_key:
                base64_string = img_base64.split("base64,")[1]
                logger.success(f"CAPTCHA rasmi va kaliti muvaffaqiyatli olindi. Kalit: {captcha_key}")
                return {"image": base64_string, "captchaKey": captcha_key}
                
            return None

        except Exception as e:
            logger.error(f"CAPTCHA olishda Selenium xatolik: {e}")
            if driver:
                driver.save_screenshot("error_screenshot.png")
            return None
        finally:
            if driver:
                driver.quit()

    return await asyncio.to_thread(_sync_get_captcha)