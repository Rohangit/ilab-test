from datetime import datetime
from sqlalchemy.orm import Session
from models import Prompt

MAX_REQUESTS_PER_DAY = 10

def check_daily_limit(user_id: int, db: Session):
    today = datetime.utcnow().date()
    start = datetime.combine(today, datetime.min.time())
    count = db.query(Prompt).filter(Prompt.user_id == user_id, Prompt.timestamp >= start).count()
    return count < MAX_REQUESTS_PER_DAY
