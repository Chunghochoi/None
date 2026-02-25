import asyncio
import re
import time
from typing import Optional, Dict, Any, List

import aiohttp
from telethon import TelegramClient, events

# ====== CONFIG (SỬA Ở ĐÂY) ======
API_ID = 123456
API_HASH = "YOUR_API_HASH"
SESSION_NAME = "user_session"
BOT_USERNAME = "@rinmoney_bot"

SERVER_BASE = "https://render-teletools.onrender.com"  # <-- URL Render của bạn
API_KEY = "9f4c2a8e7b1d6c3f0a5e9d2b7c8f1a6e3d4b9c0f2a7e6d1c8b5f0a9e2d7c4b1"  # <-- trùng với API_KEY trên Render

POLL_SECONDS = 2.0
UPTOLINK_RE = re.compile(r"https?://uptolink\.one/[A-Za-z0-9]+")

# ====== STATE ======
client = TelegramClient(SESSION_NAME, API_ID, API_HASH)
bot_entity = None
bot_id: Optional[int] = None

# buffer link để gửi theo lô
pending_links: List[str] = []
pending_lock = asyncio.Lock()


async def push_links(session: aiohttp.ClientSession, urls: List[str]):
    if not urls:
        return
    try:
        async with session.post(
            f"{SERVER_BASE}/api/push_links",
            json={"links": urls},
            headers={"X-API-Key": API_KEY},
            timeout=aiohttp.ClientTimeout(total=15),
        ) as r:
            await r.json()
    except Exception:
        # server sleep/offline: bỏ qua, sẽ đẩy lại lần sau nếu bạn muốn.
        pass


@client.on(events.NewMessage(incoming=True))
async def on_incoming(event):
    global bot_id
    if bot_id is None or event.sender_id != bot_id:
        return
    text = event.raw_text or ""
    found = UPTOLINK_RE.findall(text)
    if not found:
        return
    async with pending_lock:
        pending_links.extend(found)


@client.on(events.MessageEdited(incoming=True))
async def on_edited(event):
    global bot_id
    if bot_id is None or event.sender_id != bot_id:
        return
    text = event.raw_text or ""
    found = UPTOLINK_RE.findall(text)
    if not found:
        return
    async with pending_lock:
        pending_links.extend(found)


async def command_worker():
    global bot_entity
    async with aiohttp.ClientSession() as session:
        while True:
            # 1) poll command
            cmd_obj = None
            try:
                async with session.post(
                    f"{SERVER_BASE}/api/pull",
                    headers={"X-API-Key": API_KEY},
                    timeout=aiohttp.ClientTimeout(total=15),
                ) as r:
                    data = await r.json()
                    cmd_obj = (data or {}).get("command")
            except Exception:
                cmd_obj = None

            # 2) execute if exists
            if cmd_obj:
                cmd = cmd_obj.get("cmd")
                count = int(cmd_obj.get("count", 1))
                delay = float(cmd_obj.get("delay", 5.0))

                for i in range(count):
                    try:
                        await client.send_message(bot_entity, cmd)
                    except Exception:
                        break
                    if i < count - 1:
                        await asyncio.sleep(delay)

            # 3) flush links to server (batch)
            to_send = []
            async with pending_lock:
                if pending_links:
                    # dedupe nhẹ (giữ thứ tự)
                    seen = set()
                    for u in pending_links:
                        if u not in seen:
                            seen.add(u)
                            to_send.append(u)
                    pending_links.clear()

            if to_send:
                await push_links(session, to_send)

            await asyncio.sleep(POLL_SECONDS)


async def main():
    global bot_entity, bot_id
    await client.start()
    bot_entity = await client.get_entity(BOT_USERNAME)
    bot_id = bot_entity.id
    print(f"[OK] Agent signed in. Bot={BOT_USERNAME}, bot_id={bot_id}")
    print(f"[OK] Relay={SERVER_BASE}")
    await command_worker()


if __name__ == "__main__":
    asyncio.run(main())