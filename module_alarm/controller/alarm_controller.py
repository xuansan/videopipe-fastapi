from datetime import datetime
from fastapi import APIRouter, Depends, Form, Request
from pydantic_validation_decorator import ValidateFields
from sqlalchemy.ext.asyncio import AsyncSession
from config.enums import BusinessType
from config.get_db import get_db
from module_admin.annotation.log_annotation import Log
from module_admin.aspect.interface_auth import CheckUserInterfaceAuth
from module_admin.entity.vo.user_vo import CurrentUserModel
from module_admin.service.login_service import LoginService
from module_alarm.service.alarm_service import AlarmService
from module_alarm.entity.vo.alarm_vo import DeleteAlarmModel, AlarmModel, AlarmPageQueryModel
from utils.common_util import bytes2file_response
from utils.log_util import logger
from utils.page_util import PageResponseModel
from utils.response_util import ResponseUtil


alarmController = APIRouter(prefix='/alarm/alarm', dependencies=[Depends(LoginService.get_current_user)])


@alarmController.get(
    '/list', response_model=PageResponseModel, dependencies=[Depends(CheckUserInterfaceAuth('alarm:alarm:list'))]
)
async def get_alarm_alarm_list(
    request: Request,
alarm_page_query: AlarmPageQueryModel = Depends(AlarmPageQueryModel.as_query),
    query_db: AsyncSession = Depends(get_db),
):
    # 获取分页数据
    alarm_page_query_result = await AlarmService.get_alarm_list_services(query_db, alarm_page_query, is_page=True)
    logger.info('获取成功')

    return ResponseUtil.success(model_content=alarm_page_query_result)


@alarmController.post('', dependencies=[Depends(CheckUserInterfaceAuth('alarm:alarm:add'))])
@ValidateFields(validate_model='add_alarm')
@Log(title='告警信息', business_type=BusinessType.INSERT)
async def add_alarm_alarm(
    request: Request,
    add_alarm: AlarmModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    add_alarm.create_by = current_user.user.user_name
    add_alarm.create_time = datetime.now()
    add_alarm.update_by = current_user.user.user_name
    add_alarm.update_time = datetime.now()
    add_alarm_result = await AlarmService.add_alarm_services(query_db, add_alarm)
    logger.info(add_alarm_result.message)

    return ResponseUtil.success(msg=add_alarm_result.message)


@alarmController.put('', dependencies=[Depends(CheckUserInterfaceAuth('alarm:alarm:edit'))])
@ValidateFields(validate_model='edit_alarm')
@Log(title='告警信息', business_type=BusinessType.UPDATE)
async def edit_alarm_alarm(
    request: Request,
    edit_alarm: AlarmModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    edit_alarm.update_by = current_user.user.user_name
    edit_alarm.update_time = datetime.now()
    edit_alarm_result = await AlarmService.edit_alarm_services(query_db, edit_alarm)
    logger.info(edit_alarm_result.message)

    return ResponseUtil.success(msg=edit_alarm_result.message)


@alarmController.delete('/{ids}', dependencies=[Depends(CheckUserInterfaceAuth('alarm:alarm:remove'))])
@Log(title='告警信息', business_type=BusinessType.DELETE)
async def delete_alarm_alarm(request: Request, ids: str, query_db: AsyncSession = Depends(get_db)):
    delete_alarm = DeleteAlarmModel(ids=ids)
    delete_alarm_result = await AlarmService.delete_alarm_services(query_db, delete_alarm)
    logger.info(delete_alarm_result.message)

    return ResponseUtil.success(msg=delete_alarm_result.message)


@alarmController.get(
    '/{id}', response_model=AlarmModel, dependencies=[Depends(CheckUserInterfaceAuth('alarm:alarm:query'))]
)
async def query_detail_alarm_alarm(request: Request, id: int, query_db: AsyncSession = Depends(get_db)):
    alarm_detail_result = await AlarmService.alarm_detail_services(query_db, id)
    logger.info(f'获取id为{id}的信息成功')

    return ResponseUtil.success(data=alarm_detail_result)


@alarmController.post('/export', dependencies=[Depends(CheckUserInterfaceAuth('alarm:alarm:export'))])
@Log(title='告警信息', business_type=BusinessType.EXPORT)
async def export_alarm_alarm_list(
    request: Request,
    alarm_page_query: AlarmPageQueryModel = Form(),
    query_db: AsyncSession = Depends(get_db),
):
    # 获取全量数据
    alarm_query_result = await AlarmService.get_alarm_list_services(query_db, alarm_page_query, is_page=False)
    alarm_export_result = await AlarmService.export_alarm_list_services(alarm_query_result)
    logger.info('导出成功')

    return ResponseUtil.streaming(data=bytes2file_response(alarm_export_result))
