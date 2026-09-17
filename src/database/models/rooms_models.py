import enum
from typing import Any

from sqlalchemy import BigInteger, ForeignKey, String
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.base import Base


class RoomStatus(str, enum.Enum):
    WAITING = "WAITING"
    PREPARATION = 'PREPARATION'
    ACTIVE = "ACTIVE"
    FINISHED = "FINISHED"

class ParticipantStatus(str, enum.Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"

class Room(Base):
    __tablename__ = "rooms"

    id: Mapped[int] = mapped_column(BigInteger,primary_key=True)
    code: Mapped[str] = mapped_column(String(8), unique=True, index=True)
    topic: Mapped[str] = mapped_column(String(256))
    creator_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.max_id"))

    status: Mapped[RoomStatus] = mapped_column(
        SQLEnum(RoomStatus, native_enum=True, name = "room_status"),
        default=RoomStatus.WAITING,
        nullable=False
    )

    questions: Mapped[list[dict[str, Any]]] = mapped_column(JSONB, nullable=False)

    participants: Mapped[list["RoomParticipant"]] = relationship(back_populates="room")

class RoomParticipant(Base):
    __tablename__ = "room_participants"

    room_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("rooms.id", ondelete="CASCADE"), primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.max_id", ondelete="CASCADE"), primary_key=True)

    status: Mapped[ParticipantStatus] = mapped_column(
        SQLEnum(ParticipantStatus, native_enum=True, name = "student_status"),
        default=ParticipantStatus.PENDING,
        nullable=False
    )

    room: Mapped["Room"] = relationship(back_populates="participants")


class RoomMatch(Base):
    __tablename__ = "room_matches"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    room_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("rooms.id", ondelete="CASCADE"))

    player1_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.max_id"))
    player2_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.max_id"), nullable=True) # Nullable для автопрохода при нечетном кол-ве
    
    player1_score: Mapped[int] = mapped_column(default=0)
    player2_score: Mapped[int] = mapped_column(default=0)
    
    winner_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.max_id"), nullable=True)