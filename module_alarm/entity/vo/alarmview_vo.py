from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Literal

class AlarmViewPageQueryModel(BaseModel):
    page: int = 1
    page_size: int = 10  # 默认改为 10，与前端默认值一致
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    camera_id: Optional[str] = None
    alert_type: Optional[str] = None
    order_by: Literal['time_asc', 'time_desc'] = 'time_desc'  # 排序方式：time_asc=时间正序，time_desc=时间倒序（默认）