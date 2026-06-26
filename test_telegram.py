from telegram_client import client
import asyncio

async def main():
    await client.connect()

    authorized = await client.is_user_authorized()
    print("Authorized:", authorized)

    me = await client.get_me()
    print("ME:", me)

asyncio.run(main())