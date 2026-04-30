from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import asyncio
import json
import os
from config.constant import CommonConstant
from exceptions.exception import ServiceException
from module_admin.entity.vo.common_vo import CrudResponseModel
from module_alarm.dao.alarm_dao import AlarmDao
from module_alarm.entity.vo.alarm_vo import DeleteAlarmModel, AlarmModel, AlarmPageQueryModel
from utils.common_util import CamelCaseUtil
from utils.excel_util import ExcelUtil
from utils.log_util import logger


class AlarmService:
    """
    告警信息模块服务层
    """

    @classmethod
    async def get_alarm_list_services(
        cls, query_db: AsyncSession, query_object: AlarmPageQueryModel, is_page: bool = False
    ):
        """
        获取告警信息列表信息service

        :param query_db: orm对象
        :param query_object: 查询参数对象
        :param is_page: 是否开启分页
        :return: 告警信息列表信息对象
        """
        alarm_list_result = await AlarmDao.get_alarm_list(query_db, query_object, is_page)

        return alarm_list_result


    @classmethod
    async def add_alarm_services(cls, query_db: AsyncSession, page_object: AlarmModel):
        """
        新增告警信息信息service

        :param query_db: orm对象
        :param page_object: 新增告警信息对象
        :return: 新增告警信息校验结果
        """
        try:
            await AlarmDao.add_alarm_dao(query_db, page_object)
            await query_db.commit()
            
            # 推送告警消息
            try:
                await cls._push_alarm_notification(page_object)
            except Exception as push_error:
                logger.warning(f"⚠️ 推送告警通知失败: {push_error}")
            
            return CrudResponseModel(is_success=True, message='新增成功')
        except Exception as e:
            await query_db.rollback()
            raise e

    @classmethod
    async def edit_alarm_services(cls, query_db: AsyncSession, page_object: AlarmModel):
        """
        编辑告警信息信息service

        :param query_db: orm对象
        :param page_object: 编辑告警信息对象
        :return: 编辑告警信息校验结果
        """
        edit_alarm = page_object.model_dump(exclude_unset=True, exclude={'create_by', 'create_time', })
        alarm_info = await cls.alarm_detail_services(query_db, page_object.id)
        if alarm_info.id:
            try:
                await AlarmDao.edit_alarm_dao(query_db, edit_alarm)
                await query_db.commit()
                return CrudResponseModel(is_success=True, message='更新成功')
            except Exception as e:
                await query_db.rollback()
                raise e
        else:
            raise ServiceException(message='告警信息不存在')

    @classmethod
    async def delete_alarm_services(cls, query_db: AsyncSession, page_object: DeleteAlarmModel):
        """
        删除告警信息信息service

        :param query_db: orm对象
        :param page_object: 删除告警信息对象
        :return: 删除告警信息校验结果
        """
        if page_object.ids:
            id_list = page_object.ids.split(',')
            try:
                for id in id_list:
                    await AlarmDao.delete_alarm_dao(query_db, AlarmModel(id=id))
                await query_db.commit()
                return CrudResponseModel(is_success=True, message='删除成功')
            except Exception as e:
                await query_db.rollback()
                raise e
        else:
            raise ServiceException(message='传入ID为空')

    @classmethod
    async def alarm_detail_services(cls, query_db: AsyncSession, id: int):
        """
        获取告警信息详细信息service

        :param query_db: orm对象
        :param id: ID
        :return: ID对应的信息
        """
        alarm = await AlarmDao.get_alarm_detail_by_id(query_db, id=id)
        if alarm:
            result = AlarmModel(**CamelCaseUtil.transform_result(alarm))
        else:
            result = AlarmModel(**dict())

        return result

    @staticmethod
    async def export_alarm_list_services(alarm_list: List):
        """
        导出告警信息信息service

        :param alarm_list: 告警信息信息列表
        :return: 告警信息信息对应excel的二进制数据
        """
        # 创建一个映射字典，将英文键映射到中文键
        mapping_dict = {
            'id': 'ID',
            'createBy': '创建者',
            'createTime': '创建时间',
            'updateBy': '更新者',
            'updateTime': '更新时间',
            'remark': '备注',
            'cameraName': '报警摄像头名称',
            'reviewVideo': '复核视频存储路径/URL',
            'location': '告警位置',
            'time': '告警触发时间',
            'details': '告警内容',
            'snapshot': '快照的minIO url地址',
        }
        binary_data = ExcelUtil.export_list2excel(alarm_list, mapping_dict)

        return binary_data

    @classmethod
    async def _push_alarm_notification(cls, alarm_model: AlarmModel):
        """
        推送告警通知
        
        Args:
            alarm_model: 告警模型对象
        """
        import aiohttp
        
        try:
            # 读取推送配置
            config_file = "push_platform_config.json"
            if not os.path.exists(config_file):
                logger.warning("⚠️ 推送配置文件不存在，跳过推送")
                return
                
            with open(config_file, "r", encoding="utf-8") as f:
                config = json.load(f)
            
            token = config.get("token", "")
            platform_url = config.get("url", "http://43.140.34.34:8000/api/v1/message/send")
            
            if not token:
                logger.warning("⚠️ 推送token为空，跳过推送")
                return
            
            # 构建推送内容
            title = f"🔔 告警通知 - {alarm_model.camera_name}"
            
            # 格式化时间
            alarm_time = alarm_model.time
            if hasattr(alarm_time, 'strftime'):
                time_str = alarm_time.strftime("%Y-%m-%d %H:%M:%S")
            else:
                time_str = str(alarm_time)
            
            # 构建基础推送内容（在现有模板基础上追加告警信息）
            base_text = f"""
📍 摄像头: {alarm_model.camera_name}
📌 位置: {alarm_model.location}
⏰ 时间: {time_str}
📝 详情: {alarm_model.details}
""".strip()
            
            # 如果配置中有标题和内容模板，使用配置的，并在后面追加告警信息
            if config.get("title"):
                title = config.get("title")
            
            if config.get("text"):
                # 使用配置的模板，并在后面追加告警信息
                template_text = config.get("text")
                try:
                    # 尝试模板变量替换
                    text = template_text.format(
                        camera_name=alarm_model.camera_name,
                        location=alarm_model.location,
                        time=time_str,
                        details=alarm_model.details
                    ) + f"\n\n{base_text}"
                except:
                    # 如果模板替换失败，直接在原模板后追加
                    text = template_text + f"\n\n{base_text}"
            else:
                # 没有配置模板，直接使用基础内容
                text = base_text
            
            # 发送推送请求
            async with aiohttp.ClientSession() as session:
                headers = {"Content-Type": "application/json"}
                payload = {
                    "token": token,
                    "title": title,
                    "text": text
                }

                # 应该放这
                
                # 调用音柱报警接口 - 基于精确匹配条件
                try:
                    logger.info(f"🔊 音柱报警条件检查 - 摄像头: {alarm_model.camera_name}, 告警详情: {alarm_model.details}")
                    
                    # 获取基础数据
                    camera_name = alarm_model.camera_name or ""
                    details = alarm_model.details or ""
                    
                    # 检查是否满足音柱报警触发条件
                    # 条件1: camera_name 必须匹配 (对应接口的 camera_id 参数)
                    # 条件2: details 必须包含 "fanyue" (对应接口的 alarm_type 参数)
                    if not camera_name:
                        logger.info("🚫 摄像头名称为空，跳过音柱报警")
                    elif "fanyue" not in details.lower():
                        logger.info(f"🚫 告警详情不包含'fanyue'关键词，跳过音柱报警 - 详情: {details}")
                    else:
                    
                        logger.info(f"✅ 音柱报警条件满足 - 摄像头: {camera_name}, 触发类型: fanyue")
                        
                        # 调用翻越报警接口
                        speaker_payload = {
                            "camera_id": camera_name,  # 使用 camera_name 作为 camera_id
                            "alarm_type": "fanyue"     # 固定为翻越报警类型
                        }
                        
                        # 获取后端服务地址（应该从配置读取）
                        backend_host = "127.0.0.1"
                        backend_port = "8080"
                        speaker_url = f"http://{backend_host}:{backend_port}/dev-api/push/speaker-binding/fanyue-alarm"
                        
                        logger.info(f"🎯 准备触发翻越报警 - URL: {speaker_url}, 载荷: {speaker_payload}")
                        
                        # 发送翻越报警请求
                        async with session.post(speaker_url, json=speaker_payload, headers=headers, timeout=10) as speaker_resp:
                            if speaker_resp.status == 200:
                                logger.info(f"✅ 翻越报警触发成功: {camera_name}")
                            else:
                                logger.warning(f"⚠️ 翻越报警触发失败: HTTP {speaker_resp.status}")
                                
                except Exception as speaker_e:
                    logger.error(f"❌ 音柱报警调用异常: {speaker_e}")
                    # 音柱报警失败不影响主流程
                
                async with session.post(platform_url, json=payload, headers=headers, timeout=10) as resp:
                    if resp.status == 200:
                        logger.info(f"✅ 告警推送成功: {alarm_model.camera_name}")
                    else:
                        logger.warning(f"⚠️ 告警推送失败: HTTP {resp.status}")
                        
        except Exception as e:
            logger.error(f"❌ 推送告警通知异常: {e}")
            # 推送失败不影响主流程
