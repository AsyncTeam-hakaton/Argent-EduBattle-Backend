from pydantic import BaseModel


class MatchPair(BaseModel):
    player1_id: int
    player2_id: int


class StartMatchRequest(BaseModel):
    room_id: int
    pairs: list[MatchPair]