from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, Column, String, DateTime, Integer, JSON, case
from sqlalchemy.orm import declarative_base, aliased
from module_alarm.entity.vo.alarmview_vo import AlarmViewPageQueryModel

# 使用临时 Base 来声明模型字段（无需单独 model 文件）
Base = declarative_base()

class BusinessAlarmRecord(Base):
    __tablename__ = 'alarm_records'

    id = Column(Integer, primary_key=True)
    create_by = Column(String)
    create_time = Column(DateTime)
    update_by = Column(String)
    update_time = Column(DateTime)
    camera_name = Column(String)
    camera_id = Column(String)  # 用于关联摄像头表
    location = Column(String)
    time = Column(DateTime)
    details = Column(String)
    snapshot = Column(String)
    # 边界框坐标
    bbox_x = Column(Integer)
    bbox_y = Column(Integer)
    bbox_width = Column(Integer)
    bbox_height = Column(Integer)

class BusinessCameraDevice(Base):
    __tablename__ = 'business_camera_device'
    
    id = Column(Integer, primary_key=True)
    camera_id = Column(String)
    camera_name = Column(String)


class AlarmViewDAO:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_alarms(self, query: AlarmViewPageQueryModel):
        # 别名引用
        alarm_record = aliased(BusinessAlarmRecord)
        camera_device = aliased(BusinessCameraDevice)

        # 构建主查询 - 关联摄像头表获取摄像头名称作为告警位置
        stmt = (
            select(
                alarm_record.id,
                alarm_record.snapshot.label("image"),
                alarm_record.details.label("alertType"),
                # 🔧 格式化时间为 YYYY-MM-DD HH:MM:SS
                func.to_char(alarm_record.time, 'YYYY-MM-DD HH24:MI:SS').label("time"),
                alarm_record.camera_name.label("camera_id"),
                # 🔧 从摄像头表获取摄像头名称作为告警位置，如果没有则使用 alarm_records.location
                case(
                    (camera_device.camera_name != None, camera_device.camera_name),
                    else_=alarm_record.location
                ).label("location"),
                # 🔧 添加边界框坐标
                alarm_record.bbox_x,
                alarm_record.bbox_y,
                alarm_record.bbox_width,
                alarm_record.bbox_height,
            )
            .select_from(alarm_record)
            .outerjoin(
                camera_device,
                alarm_record.camera_id == camera_device.camera_id
            )
        )
        
        # 根据参数动态设置排序（默认时间倒序，最新的在前面）
        if query.order_by == 'time_asc':
            stmt = stmt.order_by(alarm_record.time.asc())  # 时间正序（旧→新）
        else:  # time_desc 或默认
            stmt = stmt.order_by(alarm_record.time.desc())  # 时间倒序（新→旧）

        # 添加筛选条件
        if query.start_time:
            stmt = stmt.where(alarm_record.time >= query.start_time)
        if query.end_time:
            stmt = stmt.where(alarm_record.time <= query.end_time)
        if query.camera_id:
            stmt = stmt.where(alarm_record.camera_name == query.camera_id)
        if query.alert_type:
            stmt = stmt.where(alarm_record.details == query.alert_type)

        # 分页处理
        paginated_stmt = (
            stmt.offset((query.page - 1) * query.page_size)
            .limit(query.page_size)
        )

        # 执行主数据查询
        result = await self.db.execute(paginated_stmt)
        rows = result.all()

        # 获取总记录数（基于原始查询 count）
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_result = await self.db.execute(count_stmt)
        total = total_result.scalar_one()

        # 转换为字典格式
        alarms = [dict(row._mapping) for row in rows]

        return {
            "total": total,
            "alarms": alarms
        }