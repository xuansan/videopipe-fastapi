#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
独立的机器ID获取工具
此工具可以单独分发给用户，无需依赖整个项目
用户运行后即可获取机器ID，用于申请许可证
"""

import platform
import subprocess
import hashlib
import uuid
import sys
from typing import Optional


class SimpleMachineID:
    """简化的机器ID生成器（独立工具）"""
    
    @staticmethod
    def get_cpu_id() -> Optional[str]:
        """获取CPU ID"""
        try:
            system = platform.system()
            if system == "Windows":
                result = subprocess.check_output(
                    "wmic cpu get ProcessorId", 
                    shell=True, 
                    stderr=subprocess.DEVNULL
                ).decode().strip()
                lines = [line.strip() for line in result.split('\n') if line.strip()]
                if len(lines) > 1:
                    return lines[1]
            elif system == "Linux":
                with open('/proc/cpuinfo', 'r') as f:
                    for line in f:
                        if 'Serial' in line or 'serial' in line:
                            return line.split(':')[1].strip()
                with open('/proc/cpuinfo', 'r') as f:
                    for line in f:
                        if 'model name' in line:
                            return line.split(':')[1].strip()
            elif system == "Darwin":
                result = subprocess.check_output(
                    "sysctl -n machdep.cpu.brand_string",
                    shell=True,
                    stderr=subprocess.DEVNULL
                ).decode().strip()
                return result
        except Exception:
            pass
        return None
    
    @staticmethod
    def get_motherboard_serial() -> Optional[str]:
        """获取主板序列号"""
        try:
            system = platform.system()
            if system == "Windows":
                result = subprocess.check_output(
                    "wmic baseboard get SerialNumber",
                    shell=True,
                    stderr=subprocess.DEVNULL
                ).decode().strip()
                lines = [line.strip() for line in result.split('\n') if line.strip()]
                if len(lines) > 1:
                    return lines[1]
            elif system == "Linux":
                try:
                    result = subprocess.check_output(
                        "sudo dmidecode -s baseboard-serial-number",
                        shell=True,
                        stderr=subprocess.DEVNULL
                    ).decode().strip()
                    return result if result else None
                except Exception:
                    try:
                        with open('/sys/class/dmi/id/board_serial', 'r') as f:
                            return f.read().strip()
                    except Exception:
                        pass
            elif system == "Darwin":
                result = subprocess.check_output(
                    "system_profiler SPHardwareDataType | grep 'Serial Number (system)'",
                    shell=True,
                    stderr=subprocess.DEVNULL
                ).decode().strip()
                if ':' in result:
                    return result.split(':')[1].strip()
        except Exception:
            pass
        return None
    
    @staticmethod
    def get_gpu_serial() -> Optional[str]:
        """获取显卡序列号"""
        try:
            system = platform.system()
            if system == "Windows":
                # Windows使用wmic获取显卡序列号
                result = subprocess.check_output(
                    "wmic path win32_VideoController get PNPDeviceID",
                    shell=True,
                    stderr=subprocess.DEVNULL
                ).decode().strip()
                lines = [line.strip() for line in result.split('\n') 
                         if line.strip() and 'PNPDeviceID' not in line]
                if lines:
                    device_id = lines[0]
                    if '\\' in device_id:
                        return device_id.split('\\')[-1]
                    return device_id
            elif system == "Linux":
                # Linux使用lspci获取显卡信息
                try:
                    result = subprocess.check_output(
                        "lspci | grep -i 'vga\\|3d\\|display'",
                        shell=True,
                        stderr=subprocess.DEVNULL
                    ).decode().strip()
                    if result:
                        return result.split('\n')[0]
                except Exception:
                    pass
            elif system == "Darwin":  # macOS
                result = subprocess.check_output(
                    "system_profiler SPDisplaysDataType | grep 'Serial Number'",
                    shell=True,
                    stderr=subprocess.DEVNULL
                ).decode().strip()
                if ':' in result:
                    return result.split(':')[1].strip()
        except Exception:
            pass
        return None
    
    @staticmethod
    def get_disk_serial() -> Optional[str]:
        """获取硬盘序列号"""
        try:
            system = platform.system()
            if system == "Windows":
                result = subprocess.check_output(
                    "wmic diskdrive get SerialNumber",
                    shell=True,
                    stderr=subprocess.DEVNULL
                ).decode().strip()
                lines = [line.strip() for line in result.split('\n') if line.strip() and line.strip() != 'SerialNumber']
                if lines:
                    return lines[0]
            elif system == "Linux":
                try:
                    result = subprocess.check_output(
                        "sudo hdparm -I /dev/sda 2>/dev/null | grep 'Serial Number'",
                        shell=True,
                        stderr=subprocess.DEVNULL
                    ).decode().strip()
                    if ':' in result:
                        return result.split(':')[1].strip()
                except Exception:
                    pass
            elif system == "Darwin":
                result = subprocess.check_output(
                    "system_profiler SPSerialATADataType | grep 'Serial Number'",
                    shell=True,
                    stderr=subprocess.DEVNULL
                ).decode().strip()
                if ':' in result:
                    return result.split(':')[1].strip()
        except Exception:
            pass
        return None
    
    @staticmethod
    def get_machine_id() -> str:
        """获取机器唯一ID（基于CPU ID、主板序列号、硬盘序列号、显卡SN码）"""
        info_parts = []
        
        # 1. CPU ID（处理器ID）
        cpu_id = SimpleMachineID.get_cpu_id()
        if cpu_id:
            info_parts.append(f"CPU:{cpu_id}")
        
        # 2. 主板序列号
        mb_serial = SimpleMachineID.get_motherboard_serial()
        if mb_serial and mb_serial not in ['To Be Filled By O.E.M.', 'Default string', 'None']:
            info_parts.append(f"MB:{mb_serial}")
        
        # 3. 硬盘序列号
        disk_serial = SimpleMachineID.get_disk_serial()
        if disk_serial and disk_serial not in ['To Be Filled By O.E.M.', 'Default string']:
            info_parts.append(f"DISK:{disk_serial}")
        
        # 4. 显卡SN码
        gpu_serial = SimpleMachineID.get_gpu_serial()
        if gpu_serial:
            info_parts.append(f"GPU:{gpu_serial}")
        
        # 如果所有硬件信息都获取失败，使用系统标识作为后备
        if len(info_parts) == 0:
            info_parts.append(f"FALLBACK:{platform.system()}-{platform.node()}-{uuid.getnode()}")
        
        combined_info = '|'.join(info_parts)
        machine_hash = hashlib.sha256(combined_info.encode()).hexdigest()
        
        return machine_hash


def main():
    """主函数"""
    print("=" * 80)
    print("                      机器ID获取工具")
    print("=" * 80)
    print()
    print("此工具用于获取当前机器的唯一硬件标识（机器ID）")
    print("请将下方的机器ID提供给系统管理员以申请软件许可证")
    print()
    print("=" * 80)
    print()
    
    # 获取基本系统信息
    print("系统信息:")
    print(f"  操作系统:    {platform.system()}")
    print(f"  平台:        {platform.platform()}")
    print(f"  主机名:      {platform.node()}")
    print(f"  处理器:      {platform.processor() or '未知'}")
    print()
    
    # 获取硬件信息
    print("硬件信息 (用于生成机器ID):")
    cpu_id = SimpleMachineID.get_cpu_id()
    print(f"  CPU ID:      {cpu_id if cpu_id else '(未获取到)'}")
    
    mb_serial = SimpleMachineID.get_motherboard_serial()
    print(f"  主板序列号:  {mb_serial if mb_serial else '(未获取到)'}")
    
    disk_serial = SimpleMachineID.get_disk_serial()
    print(f"  硬盘序列号:  {disk_serial if disk_serial else '(未获取到)'}")
    
    gpu_serial = SimpleMachineID.get_gpu_serial()
    print(f"  显卡序列号:  {gpu_serial if gpu_serial else '(未获取到)'}")
    print()
    
    # 生成并显示机器ID
    machine_id = SimpleMachineID.get_machine_id()
    
    print("=" * 80)
    print("【重要】请将以下机器ID提供给管理员:")
    print("=" * 80)
    print()
    print(f"    {machine_id}")
    print()
    print("=" * 80)
    print()
    print("注意事项:")
    print("  1. 机器ID基于以下硬件信息生成：CPU ID、主板序列号、硬盘序列号、显卡SN码")
    print("  2. 更换上述任何硬件可能导致机器ID变化，需要重新申请许可证")
    print("  3. 请妥善保管此机器ID，用于申请和管理许可证")
    print("  4. 虚拟机环境可能无法获取完整硬件信息，建议在物理机上运行")
    print()
    print("=" * 80)
    
    # 保存到文件
    try:
        output_file = "machine_id.txt"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("机器ID信息\n")
            f.write("=" * 80 + "\n\n")
            f.write(f"生成时间: {platform.node()}\n")
            f.write(f"操作系统: {platform.system()} {platform.platform()}\n")
            f.write(f"主机名: {platform.node()}\n\n")
            f.write("机器ID:\n")
            f.write(f"{machine_id}\n\n")
            f.write("=" * 80 + "\n")
        
        print(f"✅ 机器ID已保存到文件: {output_file}")
        print()
    except Exception as e:
        print(f"⚠️  保存文件失败: {e}")
        print()
    
    # 等待用户按键
    if sys.platform == 'win32':
        input("按任意键退出...")


if __name__ == "__main__":
    main()
