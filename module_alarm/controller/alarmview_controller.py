from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from module_alarm.service.alarmview_service import AlarmViewService
from config.get_db import get_db
from module_alarm.entity.vo.alarmview_vo import AlarmViewPageQueryModel
from datetime import datetime  # ✅ 新增
from typing import Optional, Literal     # ✅ 新增

router = APIRouter(prefix="/alarmview")

@router.get("/list")
async def get_all_alarms(
    start_time: Optional[datetime] = Query(None),
    end_time: Optional[datetime] = Query(None),
    camera_id: Optional[str] = Query(None),
    alert_type: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),  # 限制最大为 100
    order_by: Literal['time_asc', 'time_desc'] = Query('time_desc', description="排序方式：time_asc=时间正序，time_desc=时间倒序"),
    db: AsyncSession = Depends(get_db)
):
    query = AlarmViewPageQueryModel(
        start_time=start_time,
        end_time=end_time,
        camera_id=camera_id,
        alert_type=alert_type,
        page=page,
        page_size=page_size,
        order_by=order_by
    )

    result = await AlarmViewService.get_alarms(db, query.dict())
    return {
        "code": 200,
        "data": result
    }

alarmviewController = router