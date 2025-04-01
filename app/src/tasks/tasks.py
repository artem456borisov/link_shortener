import smtplib
import datetime
import asyncio
from celery import Celery
from celery.schedules import crontab
from email.message import EmailMessage
from src.linker.models import links_table
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import get_async_session
from sqlalchemy import delete


from src.config import SMTP_USER, SMTP_PASSWORD, REDIS_URL

SMTP_HOST='smtp.gmail.com'
SMTP_PORT=465

# celery = Celery('tasks', broker='redis://localhost:6379')
celery = Celery('tasks',
                broker=REDIS_URL,
                backend=REDIS_URL)


celery.conf.beat_schedule = {
    'check-expired-links-hourly': {
        'task': 'src.tasks.tasks.check_expired_links',
        'schedule': crontab(minute='*'), 
    },
}
celery.conf.timezone = 'UTC'


def get_template_email(username: str):
    email = EmailMessage()
    email['Subject'] = 'Привет'
    email['From'] = SMTP_USER
    email['To'] = SMTP_USER
    email.set_content(
        '<div>'
        f'<h1 style="color: red;">Здравствуйте, {username}</h1>'
        '</div>',
        subtype='html'
    )
    return email

@celery.task
def send_mail(username: str):
    email = get_template_email(username)
    with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as server:
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.send_message(email)


# @celery.task
# def check_expired_links():
#     async def _check_expired_links():
#         current_time = datetime.datetime.now(datetime.timezone.utc)  # Use UTC
#         async with get_async_session() as session:
#             try:
#                 stmt = delete(links_table).where(links_table.c.expires_at <= current_time)
#                 result = await session.execute(stmt)
#                 await session.commit()
#                 return {"status": "success", "deleted_count": result.rowcount}
#             except Exception as e:
#                 await session.rollback()
#                 print(f"Error deleting expired links: {e}")
#                 return {"status": "error", "message": str(e)}
    
#     # Create new event loop for each task
#     loop = asyncio.new_event_loop()
#     asyncio.set_event_loop(loop)
#     try:
#         return loop.run_until_complete(_check_expired_links())
#     finally:
#         loop.close()




@celery.task
def check_expired_links():
    async def _check_expired_links():
        async with get_async_session() as session:
            current_time = datetime.datetime.now(datetime.timezone.utc)
            stmt = delete(links_table).where(links_table.c.expires_at <= current_time)
            result = await session.execute(stmt)
            await session.commit()
            return {"status": "success", "deleted_count": result.rowcount}
    
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(_check_expired_links())
    except Exception as e:
        print(f"Error deleting expired links: {e}")
        return {"status": "error", "message": str(e)}
    finally:
        loop.close()

# check_expired_links.apply_async(countdown=60*60)
# check_expired_links.apply_async(countdown=10)


