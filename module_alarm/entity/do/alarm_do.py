from sqlalchemy import DateTime, Column, String, Integer, Date
from config.database import Base


class BusinessAlarm(Base):
    """
    告警信息表
    """

    __tablename__ = 'alarm_records'

    id = Column(Integer, primary_key=True, nullable=False, comment='ID')
    create_by = Column(String, nullable=True, comment='创建者')
    create_time = Column(DateTime, nullable=True, comment='创建时间')
    update_by = Column(String, nullable=True, comment='更新者')
    update_time = Column(DateTime, nullable=True, comment='更新时间')
    remark = Column(String, nullable=True, comment='备注')
    camera_name = Column(String, nullable=True, comment='报警摄像头名称')
    review_video = Column(String, nullable=True, comment='复核视频存储路径/URL')
    location = Column(String, nullable=True, comment='告警位置')
    time = Column(Date, nullable=True, comment='告警触发时间')
    details = Column(String, nullable=True, comment='告警内容')
    snapshot = Column(String, nullable=True, comment='快照的minIO url地址')




