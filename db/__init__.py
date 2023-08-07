from datetime import datetime
from typing import Optional
from discord import Role
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import Config


from .point_accrual import (
    accrue_points,
    deposit_points,
    get_last_accrual,
    get_point_balance,
    withdraw_points,
)
from .channel_rewards import (
    add_channel_reward,
    get_channel_rewards,
    get_cost_for_reward,
    remove_channel_reward,
)
from .models import (
    Base,
)


class DB:
    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super(DB, cls).__new__(cls)
            cls.__instance.__initialized = False
        return cls.__instance

    def __init__(self):
        if self.__initialized:
            return

        self.__initialized = True

        username = Config.CONFIG["MySQL"]["Username"]
        password = Config.CONFIG["MySQL"]["Password"]
        db_host = Config.CONFIG["MySQL"]["Host"]
        db_name = Config.CONFIG["MySQL"]["Name"]

        self.engine = create_engine(
            f"mysql+pymysql://{username}:{password}@{db_host}/{db_name}"
        )
        self.session = sessionmaker(self.engine, autoflush=True, autocommit=True)

        Base.metadata.create_all(self.engine)

    def get_last_accrual(self, user_id: int) -> Optional[datetime]:
        """Get timestamp of last point accrual

        Args:
            user_id (int): Discord user ID to get last accrual for

        Returns:
            Optional[datetime]: None if no point accruals found for user_id
        """
        return get_last_accrual(user_id, self.session)

    def accrue_points(self, user_id: int, accrual_amount: int, accrual_time: datetime):
        """Accrue channel points for a given user

        Args:
            user_id (int): Discord user ID to accrue points for
            accrual_amount (int): Number of points to accrue for user
            accrual_time (datetime): Updated accrual timestamp
        """
        return accrue_points(user_id, accrual_amount, accrual_time, self.session)

    def get_point_balance(self, user_id: int) -> int:
        """Get the number of points a user has accrued

        Args:
            user_id (int): Discord user ID to give points to

        Returns:
            int: Number of points currently accrued
        """
        return get_point_balance(user_id, self.session)

    def withdraw_points(self, user_id: int, point_amount: int) -> tuple[bool, int]:
        """Withdraw points from user's current balance

        Args:
            user_id (int): Discord user ID to give points to
            point_amount (int): Number of points to withdraw
            session (sessionmaker): Open DB session

        Returns:
            tuple[bool, int]: True if points were successfully withdrawn. If so, return new balance
        """
        return withdraw_points(user_id, point_amount, self.session)

    def deposit_points(self, user_id: int, point_amount: int) -> tuple[bool, int]:
        """Deposit points into user's current balance

        Args:
            user_id (int): Discord user ID to give points to
            point_amount (int): Number of points to withdraw
            session (sessionmaker): Open DB session

        Returns:
            tuple[bool, int]: True if points were successfully deposited. If so, return new balance
        """
        return deposit_points(user_id, point_amount, self.session)

    def add_channel_reward(self, name: str, point_cost: int):
        """Add new reward that can be redeemed for ChannelPoints

        Args:
            name (str): Name of channel reward
            point_cost (int): Number of ChannelPoints required to redeem
        """
        return add_channel_reward(name, point_cost, self.session)

    def remove_channel_reward(self, name: str):
        """Delete channel reward with matching name

        Args:
            name (str): Name of channel reward to delete
        """
        return remove_channel_reward(name, self.session)

    def get_channel_rewards(self):
        """Get all available channel rewards

        Returns:
            list[ChannelReward]: All currently available channel rewards
        """
        return get_channel_rewards(self.session)

    def get_cost_for_reward(self, name: str) -> Optional[int]:
        """Get cost for channel reward with given name

        Args:
            name (str): Name of reward to get cost for
        """
        return get_cost_for_reward(name, self.session)
