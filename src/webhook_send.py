import asyncio, aiohttp, os
from discord import Webhook, Embed, File

async def send_msg(url, mega_url, name, cover_url):
    async with aiohttp.ClientSession() as session:
        webhook = Webhook.from_url(url, session = session)
        embed = Embed(title=name).set_image(url=cover_url).set_author(name = "By JNC-Nina").add_field(name = "Download link", value=mega_url)
        await webhook.send(embed = embed, username = "LNBot")

async def send_webhook(links, files, covers):
    if not links:
        return
    webhook_api = "https://discord.com/api/webhooks/"
    print("Discord msg send")

    webhook1 = webhook_api + os.environ.get("DISCORD_SCAN_WEBHOOK_ID") + "/" + os.environ.get("DISCORD_SCAN_WEBHOOK_TOKEN")
    # webhook2 = webhook_api + os.environ.get("DISCORD_SCAN_WEBHOOK_ID2") + "/" + os.environ.get("DISCORD_SCAN_WEBHOOK_TOKEN2")

    for i,link in enumerate(links):
        await send_msg(webhook1, link, files[i].replace(".epub", '').replace("done/", '').replace("  ", " "), covers[i])
        # await send_msg(webhook2, link, files[i].replace(".epub", '').replace("done/", '').replace("  ", " "), covers[i])