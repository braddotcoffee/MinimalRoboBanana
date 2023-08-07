from typing import Optional
from db.models import ChannelPoints
from sqlalchemy import select, update, insert
from sqlalchemy.orm import sessionmaker
from datetime import timedelta, datetime
from config import Config
from discord import Role

import discord

MIN_ACCRUAL_TIME = timedelta(minutes=15)
MAX_ACCRUAL_WINDOW = timedelta(minutes=30)
POINTS_PER_ACCRUAL = 50


ROLE_MULTIPLIERS: dict[str, int] = {
    int(Config.CONFIG["Discord"]["Tier1RoleID"]): 2,
    int(Config.CONFIG["Discord"]["GiftedTier1RoleID"]): 2,
    int(Config.CONFIG["Discord"]["Tier2RoleID"]): 3,
    int(Config.CONFIG["Discord"]["GiftedTier2RoleID"]): 3,
    int(Config.CONFIG["Discord"]["Tier3RoleID"]): 4,
    int(Config.CONFIG["Discord"]["GiftedTier3RoleID"]): 4,
}


def get_point_balance(user_id: int, session: sessionmaker) -> int:
    """Get the number of points a user has accrued

    Args:
        user_id (int): Discord user ID to give points to
        session (sessionmaker): Open DB session

    Returns:
        int: Number of points currently accrued
    """
    with session() as sess:
        result = sess.execute(
            select(ChannelPoints).where(ChannelPoints.user_id == user_id)
        ).first()
        if result is None:
            return 0

        channel_points: ChannelPoints = result[0]
        return channel_points.points


def withdraw_points(
    user_id: int, point_amount: int, session: sessionmaker
) -> tuple[bool, int]:
    """Withdraw points from user's current balance

    Args:
        user_id (int): Discord user ID to give points to
        point_amount (int): Number of points to withdraw
        session (sessionmaker): Open DB session

    Returns:
        tuple[bool, int]: True if points were successfully withdrawn. If so, return new balance
    """
    with session() as sess:
        result = sess.execute(
            select(ChannelPoints).where(ChannelPoints.user_id == user_id)
        ).first()
        if result is None:
            return False, -1

        channel_points: ChannelPoints = result[0]
        new_balance = channel_points.points - point_amount
        sess.execute(
            update(ChannelPoints)
            .where(ChannelPoints.user_id == user_id)
            .values(
                points=new_balance,
            )
        )
        return True, new_balance


def deposit_points(
    user_id: int, point_amount: int, session: sessionmaker
) -> tuple[bool, int]:
    """Deposit points into user's balance

    Args:
        user_id (int): Discord user ID to give points to
        point_amount (int): Number of points to withdraw
        session (sessionmaker): Open DB session

    Returns:
        tuple[bool, int]: True if points were successfully deposited. If so, return new balance
    """
    with session() as sess:
        result = sess.execute(
            select(ChannelPoints).where(ChannelPoints.user_id == user_id)
        ).first()
        if result is None:
            return False, -1

        channel_points: ChannelPoints = result[0]
        new_balance = channel_points.points + point_amount
        sess.execute(
            update(ChannelPoints)
            .where(ChannelPoints.user_id == user_id)
            .values(
                points=new_balance,
            )
        )
        return True, new_balance


def get_last_accrual(user_id: int, session: sessionmaker) -> Optional[datetime]:
    """Get timestamp of last point accrual

    Args:
        user_id (int): Discord user ID to get last accrual for
        session (sessionmaker): Open DB session

    Returns:
        Optional[datetime]: None if no point accruals found for user_id
    """
    with session() as sess:
        result = sess.execute(
            select(ChannelPoints).where(ChannelPoints.user_id == user_id)
        ).first()
        if result is None:
            return None
        channel_points: ChannelPoints = result[0]
        return channel_points.timestamp


def accrue_points(
    user_id: int, accrual_amount: int, accrual_time: datetime, session: sessionmaker
):
    """Accrue channel points for a given user

    Args:
        user_id (int): Discord user ID to accrue points for
        accrual_amount (int): Number of points to accrue for user
        accrual_time (datetime): Updated accrual timestamp
        session (sessionmaker): Open DB session
    """
    with session() as sess:
        result = sess.execute(
            select(ChannelPoints).where(ChannelPoints.user_id == user_id)
        ).first()
        if result is None:
            # First time chatters
            sess.execute(
                insert(ChannelPoints).values(
                    user_id=user_id, points=accrual_amount, timestamp=accrual_time
                )
            )
            return
        channel_points: ChannelPoints = result[0]
        sess.execute(
            update(ChannelPoints)
            .where(ChannelPoints.user_id == user_id)
            .values(
                points=channel_points.points + accrual_amount, timestamp=accrual_time
            )
        )
