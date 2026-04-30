from module_alarm.dao.alarmview_dao import AlarmViewDAO # 导入告警视图的数据访问对象（DAO）
from module_alarm.entity.vo.alarmview_vo import AlarmViewPageQueryModel # 导入告警视图的分页查询模型
from sqlalchemy.ext.asyncio import AsyncSession # 导入 AsyncSession 用于异步数据库会话

class AlarmViewService: # 定义 AlarmViewService 类，用于处理告警视图的业务逻辑
    @staticmethod # 声明 get_alarms 为静态方法，可以直接通过类名调用
    async def get_alarms(db: AsyncSession, query: dict): # 定义异步静态方法 get_alarms，接收数据库会话和查询字典
        dao = AlarmViewDAO(db) # 创建 AlarmViewDAO 实例，传入数据库会话
        query_model = AlarmViewPageQueryModel(**query) # 将查询字典转换为 AlarmViewPageQueryModel 实例，进行数据验证和类型转换
        result = await dao.get_alarms(query_model) # 调用 DAO 层的 get_alarms 方法获取数据
        return result # 返回查询结果