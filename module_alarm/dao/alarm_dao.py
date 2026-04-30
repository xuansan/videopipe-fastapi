from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from module_alarm.entity.do.alarm_do import BusinessAlarm
from module_alarm.entity.vo.alarm_vo import AlarmModel, AlarmPageQueryModel
from utils.page_util import PageUtil


class AlarmDao:
    """
    告警信息模块数据库操作层
    """

    @classmethod
    async def get_alarm_detail_by_id(cls, db: AsyncSession, id: int):
        """
        根据ID获取告警信息详细信息

        :param db: orm对象
        :param id: ID
        :return: 告警信息信息对象
        """
        alarm_info = (
            (
                await db.execute(
                    select(BusinessAlarm)
                    .where(
                        BusinessAlarm.id == id
                    )
                )
            )
            .scalars()
            .first()
        )

        return alarm_info

    @classmethod
    async def get_alarm_detail_by_info(cls, db: AsyncSession, alarm: AlarmModel):
        """
        根据告警信息参数获取告警信息信息

        :param db: orm对象
        :param alarm: 告警信息参数对象
        :return: 告警信息信息对象
        """
        alarm_info = (
            (
                await db.execute(
                    select(BusinessAlarm).where(
                    )
                )
            )
            .scalars()
            .first()
        )

        return alarm_info

    @classmethod
    async def get_alarm_list(cls, db: AsyncSession, query_object: AlarmPageQueryModel, is_page: bool = False):
        """
        根据查询参数获取告警信息列表信息

        :param db: orm对象
        :param query_object: 查询参数对象
        :param is_page: 是否开启分页
        :return: 告警信息列表信息对象
        """
        query = (
            select(BusinessAlarm)
            .where(
                BusinessAlarm.camera_name.like(f'%{query_object.camera_name}%') if query_object.camera_name else True,
                BusinessAlarm.review_video == query_object.review_video if query_object.review_video else True,
                BusinessAlarm.location == query_object.location if query_object.location else True,
                BusinessAlarm.time == query_object.time if query_object.time else True,
                BusinessAlarm.details == query_object.details if query_object.details else True,
                BusinessAlarm.snapshot == query_object.snapshot if query_object.snapshot else True,
            )
            .order_by(BusinessAlarm.id)
            .distinct()
        )
        alarm_list = await PageUtil.paginate(db, query, query_object.page_num, query_object.page_size, is_page)

        return alarm_list

    @classmethod
    async def add_alarm_dao(cls, db: AsyncSession, alarm: AlarmModel):
        """
        新增告警信息数据库操作

        :param db: orm对象
        :param alarm: 告警信息对象
        :return:
        """
        db_alarm = BusinessAlarm(**alarm.model_dump(exclude={}))
        db.add(db_alarm)
        await db.flush()

        return db_alarm

    @classmethod
    async def edit_alarm_dao(cls, db: AsyncSession, alarm: dict):
        """
        编辑告警信息数据库操作

        :param db: orm对象
        :param alarm: 需要更新的告警信息字典
        :return:
        """
        await db.execute(update(BusinessAlarm), [alarm])

    @classmethod
    async def delete_alarm_dao(cls, db: AsyncSession, alarm: AlarmModel):
        """
        删除告警信息数据库操作

        :param db: orm对象
        :param alarm: 告警信息对象
        :return:
        """
        await db.execute(delete(BusinessAlarm).where(BusinessAlarm.id.in_([alarm.id])))

