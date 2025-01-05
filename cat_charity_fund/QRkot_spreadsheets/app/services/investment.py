from datetime import datetime
from typing import Union

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.charity_project import CharityProject
from app.models.donation import Donation


def mark_as_invested(db_obj):
    db_obj.fully_invested = True

    db_obj.close_date = datetime.now()


async def investment_process(
    obj_in: Union[CharityProject, Donation], session: AsyncSession
):
    model = CharityProject if isinstance(obj_in, Donation) else Donation

    db_objects = await session.execute(
        select(model)
        .where(model.fully_invested.is_(False))
        .order_by(model.create_date.asc(), model.id.asc())
    )

    db_objects = db_objects.scalars().all()

    for db_obj in db_objects:
        if obj_in.invested_amount >= obj_in.full_amount:
            break

        available_funds = min(
            db_obj.full_amount - db_obj.invested_amount,
            obj_in.full_amount - obj_in.invested_amount,
        )

        db_obj.invested_amount += available_funds
        obj_in.invested_amount += available_funds

        if db_obj.invested_amount == db_obj.full_amount:
            mark_as_invested(db_obj)

        session.add(db_obj)

    if obj_in.invested_amount == obj_in.full_amount:
        mark_as_invested(obj_in)

    session.add(obj_in)

    await session.commit()

    await session.refresh(obj_in)

    return obj_in
