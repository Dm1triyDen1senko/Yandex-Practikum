from datetime import datetime
from typing import Optional

from pydantic import BaseModel, PositiveInt


class DonationBase(BaseModel):
    comment: Optional[str]
    full_amount: PositiveInt


class DonationDB(DonationBase):
    id: int
    comment: Optional[str]
    create_date: datetime

    class Config:
        orm_mode = True


class AllDonations(DonationDB):
    user_id: int
    full_amount: PositiveInt
    invested_amount: int = 0
    fully_invested: bool
    create_date: datetime
    close_date: Optional[datetime]
