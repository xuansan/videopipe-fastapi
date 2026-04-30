from datetime import date, datetime
from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel
from typing import Optional
from module_admin.annotation.pydantic_annotation import as_query




class AlarmModel(BaseModel):
    """
    告警信息表对应pydantic模型
    """
    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True)

    id: Optional[int] = Field(default=None, description='ID')
    create_by: Optional[str] = Field(default=None, description='创建者')
    create_time: Optional[datetime] = Field(default=None, description='创建时间')
    update_by: Optional[str] = Field(default=None, description='更新者')
    update_time: Optional[datetime] = Field(default=None, description='更新时间')
    remark: Optional[str] = Field(default=None, description='备注')
    camera_name: Optional[str] = Field(default=None, description='报警摄像头名称')
    review_video: Optional[str] = Field(default=None, description='复核视频存储路径/URL')
    location: Optional[str] = Field(default=None, description='告警位置')
    time: Optional[date] = Field(default=None, description='告警触发时间')
    details: Optional[str] = Field(default=None, description='告警内容')
    snapshot: Optional[str] = Field(default=None, description='快照的minIO url地址')






class AlarmQueryModel(AlarmModel):
    """
    告警信息不分页查询模型
    """
    pass


@as_query
class AlarmPageQueryModel(AlarmQueryModel):
    """
    告警信息分页查询模型
    """

    page_num: int = Field(default=1, description='当前页码')
    page_size: int = Field(default=10, description='每页记录数')


class DeleteAlarmModel(BaseModel):
    """
    删除告警信息模型
    """

    model_config = ConfigDict(alias_generator=to_camel)

    ids: str = Field(description='需要删除的ID')
