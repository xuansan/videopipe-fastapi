"""
告警同步服务
从二级推理的 kafka_messages 表同步到后端的 alarm_records 表
"""
import asyncio
import json
import os
from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy import select, and_, text
from sqlalchemy.ext.asyncio import AsyncSession
from config.database import AsyncSessionLocal
from utils.log_util import logger


class AlertSyncService:
    """告警同步服务 - 从 kafka_messages 同步到 alarm_records"""
    
    def __init__(self):
        self.last_sync_id = 0  # 记录上次同步的最大 ID
        
    async def sync_new_alerts(self, batch_size: int = 100) -> Dict[str, Any]:
        """
        同步新告警
        
        Args:
            batch_size: 每批处理数量
            
        Returns:
            同步结果统计
        """
        try:
            synced_count = 0
            skipped_count = 0
            error_count = 0
            
            async with AsyncSessionLocal() as db:
                # 1. 从 kafka_messages 查询未同步的告警
                query = text("""
                    SELECT id, topic, message, created_at
                    FROM kafka_messages
                    WHERE id > :last_sync_id
                    ORDER BY id
                    LIMIT :batch_size
                """)
                
                result = await db.execute(
                    query, 
                    {"last_sync_id": self.last_sync_id, "batch_size": batch_size}
                )
                kafka_messages = result.fetchall()
                
                if not kafka_messages:
                    logger.debug("📭 没有新的告警需要同步")
                    return {
                        "success": True,
                        "synced": 0,
                        "skipped": 0,
                        "errors": 0
                    }
                
                logger.info(f"📥 获取到 {len(kafka_messages)} 条新告警，开始同步...")
                
                # 2. 遍历处理每条消息
                for msg in kafka_messages:
                    kafka_id = msg[0]
                    topic = msg[1]
                    message_data = msg[2]  # JSONB 数据
                    created_at = msg[3]
                    
                    try:
                        # 检查是否已同步
                        check_query = text(
                            "SELECT COUNT(*) FROM alarm_records WHERE kafka_msg_id = :kafka_id"
                        )
                        check_result = await db.execute(check_query, {"kafka_id": kafka_id})
                        if check_result.scalar() > 0:
                            logger.debug(f"⏭️ 跳过已同步的告警: kafka_id={kafka_id}")
                            skipped_count += 1
                            self.last_sync_id = max(self.last_sync_id, kafka_id)
                            continue
                        
                        # 转换并插入到 alarm_records
                        alarm_record = self._convert_to_alarm_record(
                            kafka_id, topic, message_data, created_at
                        )
                        
                        if alarm_record:
                            # 插入到 alarm_records
                            insert_query = text("""
                                INSERT INTO alarm_records (
                                    camera_name, location, time, details, 
                                    snapshot, kafka_msg_id, create_time, create_by
                                ) VALUES (
                                    :camera_name, :location, :time, :details,
                                    :snapshot, :kafka_msg_id, :create_time, :create_by
                                )
                            """)
                            
                            await db.execute(insert_query, alarm_record)
                            synced_count += 1
                            logger.debug(f"✅ 同步告警成功: {topic} | camera={alarm_record['camera_name']}")
                            
                            # 推送告警消息
                            try:
                                await self._push_alarm_notification(alarm_record)
                            except Exception as push_error:
                                logger.warning(f"⚠️ 推送告警通知失败: {push_error}")
                        else:
                            logger.warning(f"⚠️ 无法转换告警数据: kafka_id={kafka_id}")
                            skipped_count += 1
                        
                        # 更新最后同步ID
                        self.last_sync_id = max(self.last_sync_id, kafka_id)
                        
                    except Exception as e:
                        logger.error(f"❌ 同步单条告警失败 (kafka_id={kafka_id}): {e}")
                        error_count += 1
                        continue
                
                # 3. 提交事务
                await db.commit()
                
                logger.info(
                    f"🎉 告警同步完成: "
                    f"成功={synced_count}, 跳过={skipped_count}, 失败={error_count}"
                )
                
                return {
                    "success": True,
                    "synced": synced_count,
                    "skipped": skipped_count,
                    "errors": error_count,
                    "last_sync_id": self.last_sync_id
                }
                
        except Exception as e:
            logger.error(f"❌ 告警同步服务异常: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "synced": 0,
                "skipped": 0,
                "errors": 0
            }
    
    def _convert_to_alarm_record(
        self, 
        kafka_id: int, 
        topic: str, 
        message_data: Dict[str, Any], 
        created_at: datetime
    ) -> Optional[Dict[str, Any]]:
        """
        将 kafka_messages 的 JSONB 数据转换为 alarm_records 格式
        
        Args:
            kafka_id: kafka_messages 表的 ID
            topic: 告警主题（如 "周界入侵"）
            message_data: JSONB 消息数据
            created_at: 创建时间
            
        Returns:
            alarm_records 格式的字典，失败返回 None
        """
        try:
            # 提取字段
            event_type = message_data.get('event_type', 'unknown')
            camera_id = message_data.get('camera_id') or message_data.get('channel', '')
            timestamp = message_data.get('timestamp')
            
            # 时间处理
            if isinstance(timestamp, (int, float)):
                alarm_time = datetime.fromtimestamp(timestamp)
            elif isinstance(timestamp, str):
                try:
                    alarm_time = datetime.fromisoformat(timestamp)
                except:
                    alarm_time = created_at
            else:
                alarm_time = created_at
            
            # 构建详情描述
            details = self._build_details(topic, message_data)
            
            # 获取截图 URL
            snapshot_url = (
                message_data.get('snapshot_url') or 
                message_data.get('url') or 
                message_data.get('image_url') or 
                ''
            )
            
            # 位置信息
            location = f"{topic}@{camera_id}"
            
            # 摄像头名称（可以从配置映射获取，这里先用 camera_id）
            camera_name = self._get_camera_name(camera_id)
            
            return {
                'camera_name': camera_name,
                'location': location,
                'time': alarm_time.date(),
                'details': details,
                'snapshot': snapshot_url,
                'kafka_msg_id': kafka_id,
                'create_time': created_at,
                'create_by': 'system_sync'
            }
            
        except Exception as e:
            logger.error(f"❌ 转换告警数据失败: {e}")
            return None
    
    def _build_details(self, topic: str, message_data: Dict[str, Any]) -> str:
        """构建告警详情描述"""
        parts = [f"{topic}告警"]
        
        # 添加置信度
        if 'confidence' in message_data:
            conf = message_data['confidence']
            if isinstance(conf, (int, float)):
                parts.append(f"置信度: {conf:.2%}")
        
        # 添加检测对象
        if 'detected_object' in message_data:
            parts.append(f"对象: {message_data['detected_object']}")
        
        # 添加其他关键信息
        if 'description' in message_data:
            parts.append(message_data['description'])
        
        return " | ".join(parts)
    
    def _get_camera_name(self, camera_id: str) -> str:
        """
        根据 camera_id 获取摄像头名称
        TODO: 可以从数据库的摄像头配置表查询
        """
        # 简单映射（后续可以从 business_camera_device 表查询）
        return f"摄像头_{camera_id}"
    
    async def _push_alarm_notification(self, alarm_record: Dict[str, Any]):
        """
        推送告警通知
        
        Args:
            alarm_record: 告警记录数据
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
            title = f"🔔 告警通知 - {alarm_record['camera_name']}"
            
            # 格式化时间
            alarm_time = alarm_record['time']
            if isinstance(alarm_time, datetime):
                time_str = alarm_time.strftime("%Y-%m-%d %H:%M:%S")
            else:
                time_str = str(alarm_time)
            
            # 构建基础推送内容（在现有模板基础上追加告警信息）
            base_text = f"""
📍 摄像头: {alarm_record['camera_name']}
📌 位置: {alarm_record['location']}
⏰ 时间: {time_str}
📝 详情: {alarm_record['details']}
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
                        camera_name=alarm_record['camera_name'],
                        location=alarm_record['location'],
                        time=time_str,
                        details=alarm_record['details']
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
                
                async with session.post(platform_url, json=payload, headers=headers, timeout=10) as resp:
                    if resp.status == 200:
                        logger.info(f"✅ 告警推送成功: {alarm_record['camera_name']}")
                    else:
                        logger.warning(f"⚠️ 告警推送失败: HTTP {resp.status}")
                        
        except Exception as e:
            logger.error(f"❌ 推送告警通知异常: {e}")
            # 推送失败不影响主流程
    
    async def run_continuous_sync(self, interval_seconds: int = 60):
        """
        持续运行同步任务
        
        Args:
            interval_seconds: 同步间隔（秒）
        """
        logger.info(f"🚀 告警同步服务启动，间隔: {interval_seconds}秒")
        
        while True:
            try:
                result = await self.sync_new_alerts()
                
                if result.get('synced', 0) > 0:
                    logger.info(f"📊 本次同步: {result}")
                    
            except Exception as e:
                logger.error(f"❌ 同步任务异常: {e}")
            
            # 等待下一次同步
            await asyncio.sleep(interval_seconds)


# 全局实例
alert_sync_service = AlertSyncService()

