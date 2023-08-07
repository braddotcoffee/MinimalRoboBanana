from __future__ import annotations
import asyncio
import logging
import discord
from discord import (
    app_commands,
    Client,
    Intents,
    Message,
)
from commands.mod_commands import ModCommands
from commands.viewer_commands import ViewerCommands
from config import Config
from controllers.point_accrual import PointAccrualController
from db import DB
from threading import Thread


discord.utils.setup_logging(level=logging.INFO, root=True)

STREAM_CHAT_ID = int(Config.CONFIG["Discord"]["StreamChannel"])
FOSSA_BOT_ID = 488164251249279037

LOG = logging.getLogger(__name__)


class RaffleBot(Client):
    def __init__(self):
        intents = Intents.default()
        intents.members = True
        intents.message_content = True
        intents.guilds = True

        # initialize DB for the first time
        DB()

        super().__init__(intents=intents)

    async def on_ready(self):
        logging.info(f"Logged in as {self.user} (ID: {self.user.id})")

    async def on_message(self, message: Message):
        # every single time that any message
        # find it's way into the discord
        if message.author == self.user or message.author.id == FOSSA_BOT_ID:
            return

        if message.channel.id == STREAM_CHAT_ID:
            PointAccrualController.accrue_channel_points(message.author.id)


client = RaffleBot()
tree = app_commands.CommandTree(client)


@client.event
async def on_guild_join(guild):
    tree.clear_commands(guild=guild)
    tree.copy_global_to(guild=guild)
    await tree.sync(guild=guild)


async def main():
    async with client:
        tree.add_command(ModCommands(tree, client))
        tree.add_command(ViewerCommands(tree, client))
        await client.start(Config.CONFIG["Discord"]["Token"])


if __name__ == "__main__":
    asyncio.run(main())
