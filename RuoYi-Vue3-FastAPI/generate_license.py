#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
许可证生成工具
用于为客户生成软件许可证
"""

import sys
import os
import argparse
from datetime import datetime

# 添加路径以便导入项目模块
sys.path.insert(0, 'ruoyi-fastapi-backend')

try:
    from utils.machine_id import MachineIDGenerator
    from utils.license_validator import LicenseValidator
except ImportError as e:
    print(f"错误：无法导入必要的模块: {e}")
    print("请确保在项目根目录运行此脚本")
    sys.exit(1)


def print_banner():
    """打印横幅"""
    print("=" * 80)
    print(" " * 25 + "RuoYi-FastAPI 许可证生成工具")
    print("=" * 80)
    print()


def show_machine_info():
    """显示当前机器信息"""
    print("=" * 80)
    print("                    当前机器硬件信息")
    print("=" * 80)
    print()
    
    info = MachineIDGenerator.get_machine_info()
    
    # 显示机器ID
    print("🔑 机器ID (Machine ID):")
    print(f"   {info['machine_id']}")
    print()
    
    # 显示系统信息
    print("💻 系统信息:")
    for key in ['system', 'platform', 'node_name', 'machine', 'processor']:
        label = {
            'system': '操作系统',
            'platform': '平台',
            'node_name': '主机名',
            'machine': '架构',
            'processor': '处理器'
        }.get(key, key)
        print(f"   {label:12s}  {info.get(key, '未知')}")
    print()
    
    # 显示硬件信息
    print("🔧 硬件信息 (用于生成机器ID):")
    for key in ['cpu_id', 'motherboard_serial', 'disk_serial', 'gpu_serial']:
        label = {
            'cpu_id': 'CPU ID',
            'motherboard_serial': '主板序列号',
            'disk_serial': '硬盘序列号',
            'gpu_serial': '显卡序列号'
        }.get(key, key)
        print(f"   {label:12s}  {info.get(key, '未获取到')}")
    print()
    
    print("=" * 80)
    print()


def interactive_generate():
    """交互式生成许可证"""
    print_banner()
    print("📝 交互式许可证生成")
    print()
    
    # 获取机器ID
    print("步骤 1/5: 输入目标机器ID")
    print("-" * 80)
    use_current = input("是否为当前机器生成许可证？(y/n，默认y): ").strip().lower()
    
    if use_current in ['', 'y', 'yes', '是']:
        machine_id = MachineIDGenerator.get_machine_id()
        print(f"✅ 使用当前机器ID: {machine_id}")
    else:
        machine_id = input("请输入目标机器ID (64位十六进制字符串): ").strip()
        if not machine_id or len(machine_id) != 64:
            print("❌ 错误：机器ID无效（应为64位十六进制字符串）")
            return
    print()
    
    # 获取公司名称
    print("步骤 2/5: 输入授权公司名称")
    print("-" * 80)
    company = input("请输入公司名称 (默认: 未指定): ").strip()
    if not company:
        company = "未指定"
    print(f"✅ 授权对象: {company}")
    print()
    
    # 设置过期日期
    print("步骤 3/5: 设置许可证有效期")
    print("-" * 80)
    print("选项:")
    print("  1. 永久有效")
    print("  2. 30天试用")
    print("  3. 1年期")
    print("  4. 自定义天数")
    expire_choice = input("请选择 (默认1): ").strip()
    
    expire_days = None
    if expire_choice == '2':
        expire_days = 30
    elif expire_choice == '3':
        expire_days = 365
    elif expire_choice == '4':
        days_input = input("请输入天数: ").strip()
        try:
            expire_days = int(days_input)
        except ValueError:
            print("❌ 错误：天数无效")
            return
    
    if expire_days:
        print(f"✅ 有效期: {expire_days}天")
    else:
        print("✅ 有效期: 永久")
    print()
    
    # 设置最大用户数
    print("步骤 4/5: 设置最大用户数限制")
    print("-" * 80)
    print("选项:")
    print("  1. 不限制")
    print("  2. 10用户")
    print("  3. 50用户")
    print("  4. 100用户")
    print("  5. 自定义数量")
    user_choice = input("请选择 (默认1): ").strip()
    
    max_users = None
    if user_choice == '2':
        max_users = 10
    elif user_choice == '3':
        max_users = 50
    elif user_choice == '4':
        max_users = 100
    elif user_choice == '5':
        users_input = input("请输入用户数: ").strip()
        try:
            max_users = int(users_input)
        except ValueError:
            print("❌ 错误：用户数无效")
            return
    
    if max_users:
        print(f"✅ 最大用户数: {max_users}")
    else:
        print("✅ 最大用户数: 不限制")
    print()
    
    # 设置输出路径
    print("步骤 5/5: 设置输出路径")
    print("-" * 80)
    default_path = "ruoyi-fastapi-backend/license.lic"
    output_path = input(f"请输入输出路径 (默认: {default_path}): ").strip()
    if not output_path:
        output_path = default_path
    print(f"✅ 输出路径: {output_path}")
    print()
    
    # 确认信息
    print("=" * 80)
    print("                    许可证信息确认")
    print("=" * 80)
    print(f"  机器ID:      {machine_id}")
    print(f"  授权对象:    {company}")
    print(f"  有效期:      {f'{expire_days}天' if expire_days else '永久'}")
    print(f"  最大用户数:  {max_users if max_users else '不限制'}")
    print(f"  输出路径:    {output_path}")
    print("=" * 80)
    print()
    
    confirm = input("确认生成许可证？(y/n): ").strip().lower()
    if confirm not in ['y', 'yes', '是']:
        print("❌ 已取消")
        return
    
    # 生成许可证
    try:
        print()
        print("正在生成许可证...")
        
        license_data = LicenseValidator.generate_license(
            machine_id=machine_id,
            company=company,
            expire_days=expire_days,
            max_users=max_users,
            output_path=output_path
        )
        
        print("=" * 80)
        print("✅ 许可证生成成功！")
        print("=" * 80)
        print(f"  文件路径:    {os.path.abspath(output_path)}")
        print(f"  颁发时间:    {license_data['issue_date']}")
        print(f"  过期时间:    {license_data['expire_date'] if license_data['expire_date'] else '永久'}")
        print("=" * 80)
        print()
        print("📋 下一步:")
        print("  1. 将 license.lic 文件发送给客户")
        print("  2. 客户将文件放到应用程序同级目录")
        print("  3. 客户启动应用即可自动验证")
        print()
        
    except Exception as e:
        print(f"❌ 生成失败: {str(e)}")


def command_line_generate(args):
    """命令行方式生成许可证"""
    try:
        print_banner()
        print("🔧 命令行模式生成许可证")
        print()
        
        # 生成许可证
        output_path = args.output if args.output else "ruoyi-fastapi-backend/license.lic"
        
        license_data = LicenseValidator.generate_license(
            machine_id=args.machine_id,
            company=args.company if args.company else "未指定",
            expire_days=args.days if args.days else None,
            max_users=args.max_users if args.max_users else None,
            output_path=output_path
        )
        
        print("=" * 80)
        print("✅ 许可证生成成功！")
        print("=" * 80)
        print(f"  机器ID:      {license_data['machine_id']}")
        print(f"  授权对象:    {license_data['company']}")
        print(f"  颁发时间:    {license_data['issue_date']}")
        print(f"  过期时间:    {license_data['expire_date'] if license_data['expire_date'] else '永久'}")
        print(f"  最大用户数:  {license_data['max_users'] if license_data['max_users'] else '不限制'}")
        print(f"  文件路径:    {os.path.abspath(output_path)}")
        print("=" * 80)
        print()
        
    except Exception as e:
        print(f"❌ 生成失败: {str(e)}")
        sys.exit(1)


def verify_license():
    """验证许可证"""
    print_banner()
    print("🔍 验证当前许可证")
    print()
    
    try:
        # 获取当前机器ID
        machine_id = MachineIDGenerator.get_machine_id()
        print(f"当前机器ID: {machine_id}")
        print()
        
        # 验证许可证
        result = LicenseValidator.validate_license(raise_error=False)
        
        print("=" * 80)
        if result['valid']:
            print("✅ 许可证验证成功")
            print("=" * 80)
            
            # 获取许可证信息
            info = LicenseValidator.get_license_info()
            if info.get('exists'):
                print(f"  授权对象:    {info.get('company', '未知')}")
                print(f"  颁发日期:    {info.get('issue_date', '未知')}")
                print(f"  过期日期:    {info.get('expire_date') if info.get('expire_date') else '永久'}")
                print(f"  最大用户数:  {info.get('max_users') if info.get('max_users') else '不限制'}")
                print(f"  许可证版本:  {info.get('version', '未知')}")
        else:
            print("❌ 许可证验证失败")
            print("=" * 80)
            print(f"  失败原因: {result['message']}")
        
        print("=" * 80)
        print()
        
    except Exception as e:
        print(f"❌ 验证过程出错: {str(e)}")
        print()


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='RuoYi-FastAPI 许可证生成工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:

  1. 查看当前机器信息:
     python generate_license.py --show

  2. 交互式生成许可证:
     python generate_license.py --generate

  3. 命令行快速生成:
     python generate_license.py --machine-id <ID> --company "公司名" --days 365

  4. 验证当前许可证:
     python generate_license.py --verify

  5. 生成永久许可证:
     python generate_license.py --machine-id <ID> --company "公司名"
        """
    )
    
    parser.add_argument('--show', action='store_true', help='显示当前机器硬件信息')
    parser.add_argument('--generate', action='store_true', help='交互式生成许可证')
    parser.add_argument('--verify', action='store_true', help='验证当前许可证')
    parser.add_argument('--machine-id', type=str, help='目标机器ID')
    parser.add_argument('--company', type=str, help='授权公司名称')
    parser.add_argument('--days', type=int, help='许可证有效期（天数），不指定则永久有效')
    parser.add_argument('--max-users', type=int, help='最大用户数限制')
    parser.add_argument('--output', type=str, help='输出文件路径')
    
    args = parser.parse_args()
    
    # 如果没有参数，显示帮助
    if len(sys.argv) == 1:
        parser.print_help()
        print()
        print("提示：使用 --show 查看当前机器ID，使用 --generate 交互式生成许可证")
        return
    
    # 执行对应的操作
    if args.show:
        show_machine_info()
    elif args.generate:
        interactive_generate()
    elif args.verify:
        verify_license()
    elif args.machine_id:
        command_line_generate(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print()
        print("用户取消操作")
        sys.exit(0)
    except Exception as e:
        print(f"发生错误: {str(e)}")
        sys.exit(1)

