from models.base import async_session
from models.metric import Metric


async def log_metric(user_id, action, data=None):
    async with async_session() as session:
        async with session.begin():
            metric = Metric(user_id=user_id, action=action, data=data)
            session.add(metric)
