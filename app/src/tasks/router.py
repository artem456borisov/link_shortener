from fastapi import APIRouter, BackgroundTasks
from .tasks import send_mail

router = APIRouter(prefix = "/report")

@router.get("/send")
def emailer(background_tasks: BackgroundTasks):

    try:
        # background_tasks.add_task(send_mail, 'artem')
        send_mail.delay('artem')
    except Exception as e:
        return {
            "status":503,
            "detail": str(e)
        }

    return {
        'status': 200,
        "details": "Email is ok"
    }