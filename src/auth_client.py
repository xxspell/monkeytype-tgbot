import aiohttp
import json
import time

from config import settings
from database.db import store_tokens, load_tokens
from logger import auth_logger as logger


class AuthClient:
    def __init__(self):
        self.api_key = settings.MONKEYTYPE_AUTH_TOKEN
        self.token_url = settings.TOKEN_URL
        self.email = settings.EMAIL
        self.password = settings.PASSWORD
        self.refresh_token = None
        self.id_token = None
        self.expires_at = None

    async def authenticate(self):
        auth_url = f'https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={self.api_key}'
        headers = {
            'Accept': '*/*',
            'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
            'Content-Type': 'application/json',
            'Origin': 'https://monkeytype.com',
            'Priority': 'u=1, i',
            'Sec-CH-UA': '"Not)A;Brand";v="99", "Google Chrome";v="127", "Chromium";v="127"',
            'Sec-CH-UA-Mobile': '?0',
            'Sec-CH-UA-Platform': '"Windows"',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'cross-site',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',

            'X-Client-Version': 'Chrome/JsCore/10.8.0/FirebaseCore-web',
            'X-Firebase-GMPID': '1:789788471140:web:7e31b15959d68ac0a51471'
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(auth_url, json={
                'returnSecureToken': True,
                'email': self.email,
                'password': self.password,
                'clientType': 'CLIENT_TYPE_WEB'
            }, headers=headers) as response:
                data = await response.json()
                if 'idToken' in data:
                    self.refresh_token = data['refreshToken']
                    self.id_token = data['idToken']
                    expires_in = data['expiresIn']
                    await store_tokens(self.refresh_token, self.id_token, expires_in)
                    logger.debug(f"Authenticated successfully: id_token={self.id_token}")
                    return self.id_token
                logger.error(f"Authentication failed: {data}")
                return None

    async def get_auth_token(self):
        tokens = await load_tokens()
        if tokens:
            self.refresh_token, self.id_token, self.expires_at = tokens
            if self.id_token and int(time.time()) < self.expires_at:
                logger.debug(f"Using existing token: {self.id_token}")
                return self.id_token

        if self.refresh_token:
            if await self._refresh_token():
                return self.id_token

        return await self.authenticate()

    async def _refresh_token(self):
        logger.debug("Refreshing token...")
        async with aiohttp.ClientSession() as session:
            async with session.post(self.token_url, json={
                'grant_type': 'refresh_token',
                'refresh_token': self.refresh_token
            }) as response:
                data = await response.json()
                if 'id_token' in data:
                    self.id_token = data['id_token']
                    expires_in = data['expires_in']
                    await store_tokens(self.refresh_token, self.id_token, expires_in)
                    logger.debug(f"Token refreshed successfully: id_token={self.id_token}")
                    return True
                logger.error(f"Token refresh failed: {data}")
                return False
