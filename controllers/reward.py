from discord import Interaction

from db import DB


class RewardController:
    @staticmethod
    async def redeem_reward(name: str, interaction: Interaction):
        # how much does the reward cost? -- what if there's no reward?
        cost = DB().get_cost_for_reward(name)
        if cost is None:
            return await interaction.response.send_message(
                f"Could not find reward {name=}", ephemeral=True
            )

        # do we have enough points?
        user_id = interaction.user.id
        point_balance = DB().get_point_balance(user_id)
        if point_balance < cost:
            return await interaction.response.send_message(
                f"You do not have enough points for {name}. Point Balance: {point_balance}, Cost: {cost}",
                ephemeral=True,
            )

        # Redeem the reward by subtracting points
        DB().withdraw_points(user_id, cost)
        await interaction.response.send_message(
            f"{interaction.user.mention} redeemed {name}!"
        )
