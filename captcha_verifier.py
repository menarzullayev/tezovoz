# NEW-141
# captcha_verifier.py

import asyncio
import httpx
import random
import base64
import io
import os
from loguru import logger
from typing import Dict, Any, Optional

# Python-dotenv kutubxonasini import qilamiz
from dotenv import load_dotenv

# .env faylini yuklash
load_dotenv()

def generate_random_ip() -> str:
    """
    Tasodifiy IP-manzil yaratadi.
    """
    ips = ['46.227.123.', '37.110.212.', '46.255.69.', '62.209.128.', '37.110.214.', '31.135.209.', '37.110.213.']
    prefix = random.choice(ips)
    return prefix + str(random.randint(1, 255))

async def get_captcha_from_api() -> Optional[Dict[str, Any]]:
    """
    HTTP so'rov orqali CAPTCHA tasviri va kalitini olishga urinadi.
    """
    async with httpx.AsyncClient(timeout=10) as client:
        url = "https://openbudget.uz/api/v2/vote/captcha-2"
        random_ip = generate_random_ip()
        headers = {
            "REMOTE_ADDR": random_ip,
            "HTTP_X_FORWARDED_FOR": random_ip,
            "HTTP_X_REAL_IP": random_ip,
            "X-Forwarded-For": random_ip
        }
        
        try:
            logger.info("Captcha olish uchun so'rov yuborilmoqda...")
            logger.debug(f"So'rov URL: {url}")
            logger.debug(f"Headers: {headers}")

            response = await client.get(url, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            logger.success("Captcha muvaffaqiyatli olindi. HTTP Status: 200")
            return data
            
        except httpx.HTTPStatusError as e:
            logger.error(f"Captcha olishda HTTP xatolik: {e.response.status_code}. Javob: {e.response.text}")
            return None
        except Exception as e:
            logger.error(f"Captcha olishda kutilmagan xatolik yuz berdi: {e}", exc_info=True)
            return None

async def main():
    logger.info("Captcha verifikator skripti ishga tushirildi...")
    
    captcha_data = await get_captcha_from_api()
    
    if captcha_data:
        # CAPTCHA rasmini saqlash
        if 'image' in captcha_data:
            try:
                image_bytes = base64.b64decode(captcha_data['image'])
                
                # Agar 'data' papkasi mavjud bo'lmasa, yaratish
                if not os.path.exists('data'):
                    os.makedirs('data')
                
                # Rasmni diskka saqlash
                with open('data/captcha_test.jpg', 'wb') as f:
                    f.write(image_bytes)
                logger.success("Captcha rasmi 'data/captcha_test.jpg' fayliga saqlandi.")
            except Exception as e:
                logger.error(f"Rasmni saqlashda xatolik yuz berdi: {e}", exc_info=True)
        
        logger.info(f"Olingan captchaKey: {captcha_data.get('captchaKey', 'Kalit topilmadi')}")
    else:
        logger.error("Captcha olish muvaffaqiyatsiz tugadi. Loglarni tekshiring.")

if __name__ == "__main__":
    asyncio.run(main())