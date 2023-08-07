from discord import app_commands, Interaction, Client
from discord.app_commands.errors import AppCommandError, CheckFailure
from db import DB
from views.rewards.add_reward_modal import AddRewardModal
import logging

LOG = logging.getLogger(__name__)


@app_commands.guild_only()
class ModCommands(app_commands.Group, name="mod"):
    def __init__(self, tree: app_commands.CommandTree, client: Client) -> None:
        super().__init__()
        self.tree = tree
        self.client = client

    async def on_error(self, interaction: Interaction, error: AppCommandError):
        if isinstance(error, CheckFailure):
            return await interaction.response.send_message(
                "Failed to perform command - please verify permissions.", ephemeral=True
            )
        logging.error(error)
        return await super().on_error(interaction, error)

    @app_commands.command(name="sync")
    @app_commands.checks.has_role("Mod")
    async def sync(self, interaction: Interaction) -> None:
        """Manually sync slash commands to guild"""

        guild = interaction.guild
        self.tree.clear_commands(guild=guild)
        self.tree.copy_global_to(guild=guild)
        await self.tree.sync(guild=guild)
        await interaction.response.send_message("Commands synced", ephemeral=True)

    @app_commands.command(name="add_reward")
    @app_commands.checks.has_role("Mod")
    async def add_reward(self, interaction: Interaction):
        """Creates new channel reward for redemption"""
        modal = AddRewardModal()
        await interaction.response.send_modal(modal)

    @app_commands.command(name="remove_reward")
    @app_commands.checks.has_role("Mod")
    @app_commands.describe(name="Name of reward to remove")
    async def remove_reward(self, interaction: Interaction, name: str):
        """Removes channel reward for redemption"""
        DB().remove_channel_reward(name)
        await interaction.response.send_message(
            f"Successfully removed {name}!", ephemeral=True
        )
