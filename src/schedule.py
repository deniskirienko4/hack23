from fastapi import APIRouter, Depends
from sqlalchemy import select
from database.models import Shift, Task, User

from src.auth import login_required
from database.database import get_session
from sqlalchemy.ext.asyncio import AsyncSession


schedule_router = APIRouter(
    prefix="/schedule"
)

@schedule_router.post("/view")
async def view(user=Depends(login_required),
               session: AsyncSession = Depends(get_session)):
    stmt = (select(Shift.id.label("shift_id"),
                  Shift.user_id.label("user_id"),
                  Shift.date.label("date"),
                  (User.first_name + ' ' + 
                   User.second_name + ' ' +
                   User.third_name).label("user_name"),
                  Shift.shift_time.label("shift_time"))
            .join(User, User.id == Shift.user_id))
    
    shifts = (await session.execute(stmt)).all()
    
    result = []
    
    for shift in shifts:
        shift = shift._mapping
        tasks = (await session.execute(
            select(Task.id, Task.value,
                   Task.begin, Task.end,
                   Task.status, Task.name)
            .where(shift.user_id == Task.user_id)
            .where(Task.begin <= shift.date)
            .where(Task.end >= shift.date)
        )).all()
        
        tasks = [task._mapping for task in tasks]
        
        result.append({"date": shift.date,
                       "user_name": shift.user_name,
                       "shift_time": shift.shift_time,
                       "tasks": tasks})
        
    return result


# @schedule_router.post("/complete")
# async def view(user=Depends(login_required),
#                session: AsyncSession = Depends(get_session)):