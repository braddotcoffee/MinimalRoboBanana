from db import DB
from datetime import datetime, timedelta

MIN_ACCRUAL_TIME = timedelta(minutes=15)
POINTS_PER_ACCRUAL = 50


class PointAccrualController:
    @staticmethod
    def accrue_channel_points(user_id: int):
        """Accrue channel points for the given user_id

        Args:
            user_id (int): Discord user ID to accrue points for
        """
        # find the last time we gave this person points
        last_accrued = DB().get_last_accrual(user_id)
        now = datetime.now()

        # handle first time chatters
        if last_accrued is None:
            DB().accrue_points(user_id, POINTS_PER_ACCRUAL, now)
            return

        # Calculate whether or not it's been long enough to give points
        time_difference = now - last_accrued
        if time_difference < MIN_ACCRUAL_TIME:
            # Do not give any points
            return

        # Give them points
        DB().accrue_points(user_id, POINTS_PER_ACCRUAL, now)
