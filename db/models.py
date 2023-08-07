from datetime import datetime
import enum
from sqlalchemy import (
    BigInteger,
    Column,
    DateTime,
    Integer,
    VARCHAR,
    func,
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class ChannelPoints(Base):
    __tablename__ = "channel_points"
    user_id = Column(BigInteger, primary_key=True)
    points = Column(Integer, nullable=False, default=0)
    timestamp = Column(DateTime, default=func.now(), onupdate=func.now())

    def __repr__(self):
        return (
            f"ChannelPoints(user_id={self.user_id!r}, points={self.points!r},"
            f" timestamp={self.timestamp!r})"
        )


class ChannelReward(Base):
    __tablename__ = "channel_rewards"
    id = Column(Integer, primary_key=True)
    point_cost = Column(Integer, nullable=False)
    name = Column(VARCHAR(100), nullable=False)

    def __repr__(self):
        return (
            f"ChannelReward(id={self.id!r}, point_cost={self.point_cost!r},"
            f" name={self.name!r})"
        )

