import logging
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.utils import executor
from aiogram.types import ParseMode
from aiogram.dispatcher.filters import Text

API_TOKEN = '7487124463:AAH4-2miGWJWrTElrFtb5Ma1fWgnl-LRZlY'

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())

class Bypass:
    def __init__(self, cookie) -> None:
        self.cookie = cookie
    
    def start_process(self):
        self.xcsrf_token = self.get_csrf_token()
        self.rbx_authentication_ticket = self.get_rbx_authentication_ticket()
        return self.get_set_cookie()
        
    def get_set_cookie(self):
        response = requests.post(
            "https://auth.roblox.com/v1/authentication-ticket/redeem",
            headers={"rbxauthenticationnegotiation": "1"},
            json={"authenticationTicket": self.rbx_authentication_ticket}
        )
        set_cookie_header = response.headers.get("set-cookie")
        if not set_cookie_header:
            return "Invalid Cookie"
        
        valid_cookie = set_cookie_header.split(".ROBLOSECURITY=")[1].split(";")[0]
        return f"_|WARNING:-DO-NOT-SHARE-THIS.--Sharing-this-will-allow-someone-to-log-in-as-you-and-to-steal-your-ROBUX-and-items.|_{valid_cookie}"
        
    def get_rbx_authentication_ticket(self):
        response = requests.post(
            "https://auth.roblox.com/v1/authentication-ticket",
            headers={
                "rbxauthenticationnegotiation": "1",
                "referer": "https://www.roblox.com/camel",
                "Content-Type": "application/json",
                "x-csrf-token": self.xcsrf_token
            },
            cookies={".ROBLOSECURITY": self.cookie}
        )
        assert response.headers.get("rbx-authentication-ticket"), "An error occurred while getting the rbx-authentication-ticket"
        return response.headers.get("rbx-authentication-ticket")
        
    def get_csrf_token(self) -> str:
        response = requests.post("https://auth.roblox.com/v2/logout", cookies={".ROBLOSECURITY": self.cookie})
        xcsrf_token = response.headers.get("x-csrf-token")
        assert xcsrf_token, "An error occurred while getting the X-CSRF-TOKEN. Could be due to an invalid Roblox Cookie"
        return xcsrf_token


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    await message.reply("Welcome! Send me a Roblox cookie, and I will return a new one for you.\nType /cancel to stop.")


@dp.message_handler(commands=['cancel'])
async def cancel(message: types.Message):
    await message.reply("Operation canceled. Send a new Roblox cookie to start again.")


@dp.message_handler(lambda message: message.text)
async def process_cookie(message: types.Message):
    cookie = message.text.strip()

    bypass = Bypass(cookie)

    try:
        result = bypass.start_process()
        await message.reply(f"Result:\n`{result}`", parse_mode=ParseMode.MARKDOWN)
    except Exception as e:
        await message.reply(f"Error: {e}")


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
