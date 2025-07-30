#!/usr/bin/env python3
"""
端口管理脚本
用于检查和关闭占用8000端口的进程
"""

import os
import sys
import subprocess
import signal
from datetime import datetime

def print_banner():
    """打印横幅"""
    print("\n" + "="*60)
    print("🔧 端口管理工具")
    print("="*60)
    print("🔧 功能:")
    print("  1. 检查端口占用情况")
    print("  2. 关闭占用8000端口的进程")
    print("  3. 重启网站服务")
    print("  4. 查看进程详情")
    print("="*60)

def check_port_usage(port=8000):
    """检查端口占用情况"""
    print(f"🔍 检查端口 {port} 占用情况...")
    
    try:
        # 使用netstat检查端口
        result = subprocess.run(['netstat', '-tlnp'], capture_output=True, text=True)
        if result.returncode == 0:
            lines = result.stdout.split('\n')
            port_processes = []
            
            for line in lines:
                if f':{port}' in line or f':{port} ' in line:
                    parts = line.split()
                    if len(parts) >= 7:
                        process_info = {
                            'protocol': parts[0],
                            'local_address': parts[3],
                            'state': parts[5] if len(parts) > 5 else 'LISTEN',
                            'pid': parts[6].split('/')[0] if '/' in parts[6] else 'unknown',
                            'process': parts[6].split('/')[1] if '/' in parts[6] else 'unknown'
                        }
                        port_processes.append(process_info)
            
            if port_processes:
                print(f"❌ 端口 {port} 被以下进程占用:")
                for i, proc in enumerate(port_processes, 1):
                    print(f"   {i}. PID: {proc['pid']}, 进程: {proc['process']}")
                    print(f"      协议: {proc['protocol']}, 地址: {proc['local_address']}")
                return port_processes
            else:
                print(f"✅ 端口 {port} 未被占用")
                return []
                
        else:
            print(f"❌ 无法检查端口占用: {result.stderr}")
            return None
            
    except FileNotFoundError:
        print("❌ netstat 命令不可用，尝试使用 lsof...")
        return check_port_usage_lsof(port)
    except Exception as e:
        print(f"❌ 检查端口失败: {e}")
        return None

def check_port_usage_lsof(port=8000):
    """使用lsof检查端口占用"""
    try:
        result = subprocess.run(['lsof', '-i', f':{port}'], capture_output=True, text=True)
        if result.returncode == 0 and result.stdout.strip():
            lines = result.stdout.split('\n')[1:]  # 跳过标题行
            port_processes = []
            
            for line in lines:
                if line.strip():
                    parts = line.split()
                    if len(parts) >= 9:
                        process_info = {
                            'command': parts[0],
                            'pid': parts[1],
                            'user': parts[2],
                            'fd': parts[3],
                            'type': parts[4],
                            'device': parts[5],
                            'size': parts[6],
                            'node': parts[7],
                            'name': parts[8]
                        }
                        port_processes.append(process_info)
            
            if port_processes:
                print(f"❌ 端口 {port} 被以下进程占用:")
                for i, proc in enumerate(port_processes, 1):
                    print(f"   {i}. PID: {proc['pid']}, 进程: {proc['command']}")
                    print(f"      用户: {proc['user']}, 类型: {proc['type']}")
                return port_processes
            else:
                print(f"✅ 端口 {port} 未被占用")
                return []
        else:
            print(f"✅ 端口 {port} 未被占用")
            return []
            
    except FileNotFoundError:
        print("❌ lsof 命令不可用")
        return None
    except Exception as e:
        print(f"❌ 检查端口失败: {e}")
        return None

def kill_process_by_pid(pid):
    """通过PID杀死进程"""
    try:
        # 先尝试优雅关闭
        os.kill(int(pid), signal.SIGTERM)
        print(f"✅ 已发送SIGTERM信号到进程 {pid}")
        
        # 等待3秒
        import time
        time.sleep(3)
        
        # 检查进程是否还存在
        try:
            os.kill(int(pid), 0)  # 检查进程是否存在
            print(f"⚠️  进程 {pid} 仍在运行，发送SIGKILL信号")
            os.kill(int(pid), signal.SIGKILL)
            print(f"✅ 已发送SIGKILL信号到进程 {pid}")
        except OSError:
            print(f"✅ 进程 {pid} 已成功关闭")
            
    except ValueError:
        print(f"❌ 无效的PID: {pid}")
    except OSError as e:
        print(f"❌ 无法关闭进程 {pid}: {e}")

def kill_processes_by_name(process_names):
    """通过进程名杀死进程"""
    for name in process_names:
        try:
            result = subprocess.run(['pkill', '-f', name], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ 已关闭进程: {name}")
            else:
                print(f"⚠️  未找到进程: {name}")
        except Exception as e:
            print(f"❌ 关闭进程失败 {name}: {e}")

def restart_website_service():
    """重启网站服务"""
    print("\n🔄 重启网站服务...")
    
    try:
        # 停止systemd服务
        result = subprocess.run(['systemctl', 'stop', 'website'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ 已停止website服务")
        else:
            print("⚠️  website服务未运行或停止失败")
        
        # 等待2秒
        import time
        time.sleep(2)
        
        # 启动systemd服务
        result = subprocess.run(['systemctl', 'start', 'website'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ 已启动website服务")
        else:
            print("❌ 启动website服务失败")
            
        # 检查服务状态
        result = subprocess.run(['systemctl', 'status', 'website'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ website服务运行正常")
        else:
            print("❌ website服务运行异常")
            
    except Exception as e:
        print(f"❌ 重启服务失败: {e}")

def create_port_management_script():
    """创建端口管理脚本"""
    print("\n📝 创建端口管理脚本...")
    
    script_content = '''#!/bin/bash
# port_manager.sh - 端口管理脚本

PORT=8000

echo "🔧 端口管理工具"
echo "=================="

# 检查端口占用
echo "🔍 检查端口 $PORT 占用情况..."
if command -v netstat &> /dev/null; then
    netstat -tlnp | grep ":$PORT"
elif command -v lsof &> /dev/null; then
    lsof -i :$PORT
else
    echo "❌ 无法检查端口占用"
    exit 1
fi

# 关闭占用端口的进程
echo ""
echo "🔧 关闭占用端口 $PORT 的进程..."
pids=$(lsof -ti :$PORT 2>/dev/null)
if [ -n "$pids" ]; then
    echo "找到进程: $pids"
    for pid in $pids; do
        echo "关闭进程 $pid..."
        kill -TERM $pid 2>/dev/null
        sleep 2
        if kill -0 $pid 2>/dev/null; then
            echo "强制关闭进程 $pid..."
            kill -KILL $pid 2>/dev/null
        fi
    done
    echo "✅ 端口 $PORT 已释放"
else
    echo "✅ 端口 $PORT 未被占用"
fi

# 重启网站服务
echo ""
echo "🔄 重启网站服务..."
systemctl stop website 2>/dev/null
sleep 2
systemctl start website 2>/dev/null

# 检查服务状态
echo ""
echo "📋 服务状态:"
systemctl status website --no-pager -l

echo ""
echo "🎉 端口管理完成！"
'''
    
    with open('port_manager.sh', 'w') as f:
        f.write(script_content)
    
    # 设置执行权限
    os.chmod('port_manager.sh', 0o755)
    print("✅ 端口管理脚本创建成功: port_manager.sh")

def main():
    """主函数"""
    print_banner()
    
    port = 8000
    
    # 1. 检查端口占用
    processes = check_port_usage(port)
    
    if processes is None:
        print("❌ 无法检查端口占用")
        return
    
    if not processes:
        print("✅ 端口未被占用，无需处理")
        return
    
    # 2. 询问用户是否关闭进程
    print(f"\n❓ 是否关闭占用端口 {port} 的进程？")
    print("1. 关闭所有占用进程")
    print("2. 关闭特定进程")
    print("3. 重启网站服务")
    print("4. 退出")
    
    try:
        choice = input("\n请选择操作 (1-4): ").strip()
        
        if choice == '1':
            # 关闭所有占用进程
            print("\n🔧 关闭所有占用进程...")
            for proc in processes:
                if 'pid' in proc and proc['pid'] != 'unknown':
                    kill_process_by_pid(proc['pid'])
            
            # 检查端口是否已释放
            print("\n🔍 重新检查端口占用...")
            remaining = check_port_usage(port)
            if not remaining:
                print("✅ 端口已成功释放")
            else:
                print("❌ 端口仍被占用")
                
        elif choice == '2':
            # 关闭特定进程
            print("\n📋 请选择要关闭的进程:")
            for i, proc in enumerate(processes, 1):
                print(f"   {i}. PID: {proc.get('pid', 'unknown')}, 进程: {proc.get('process', proc.get('command', 'unknown'))}")
            
            try:
                idx = int(input("\n请输入进程编号: ")) - 1
                if 0 <= idx < len(processes):
                    proc = processes[idx]
                    if 'pid' in proc and proc['pid'] != 'unknown':
                        kill_process_by_pid(proc['pid'])
                    else:
                        print("❌ 无法获取进程PID")
                else:
                    print("❌ 无效的选择")
            except ValueError:
                print("❌ 请输入有效的数字")
                
        elif choice == '3':
            # 重启网站服务
            restart_website_service()
            
        elif choice == '4':
            print("👋 退出")
            return
            
        else:
            print("❌ 无效的选择")
            
    except KeyboardInterrupt:
        print("\n👋 用户取消操作")
        return
    
    # 3. 创建端口管理脚本
    create_port_management_script()
    
    print("\n🎉 端口管理完成！")
    print("="*60)
    print("💡 使用方法:")
    print("   ./port_manager.sh (快速端口管理)")
    print("   python3 port_manager.py (交互式管理)")
    print("="*60)

if __name__ == '__main__':
    main() 