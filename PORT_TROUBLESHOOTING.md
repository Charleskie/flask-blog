# 🔧 端口问题解决指南

## 问题描述
启动Flask应用时遇到 "Address already in use" 错误，端口5000被其他程序占用。

## 常见原因

### macOS系统
1. **AirPlay Receiver服务** - 系统偏好设置中的AirPlay接收器
2. **ControlCenter进程** - 系统控制中心
3. **其他开发服务器** - 之前启动的Flask/Django应用

### Windows系统
1. **IIS服务** - Internet Information Services
2. **其他Web服务器** - Apache, Nginx等
3. **开发工具** - VS Code Live Server等

### Linux系统
1. **系统服务** - 各种网络服务
2. **其他应用** - 占用端口的应用程序

## 解决方案

### 方案1：使用智能端口选择（推荐）
```bash
python start_server.py
```
这个脚本会自动查找可用端口（5000-5009）并启动服务器。

### 方案2：手动指定端口
```bash
# 使用端口5001
python run.py

# 或者直接运行app.py
python app.py
```

### 方案3：查找并关闭占用端口的程序

#### macOS
```bash
# 查看端口占用
lsof -i :5000

# 关闭AirPlay Receiver
# 系统偏好设置 -> 通用 -> AirDrop与接力 -> 关闭"AirPlay接收器"

# 或者关闭特定进程
kill -9 <PID>
```

#### Windows
```bash
# 查看端口占用
netstat -ano | findstr :5000

# 关闭进程
taskkill /PID <PID> /F
```

#### Linux
```bash
# 查看端口占用
netstat -tulpn | grep :5000

# 关闭进程
kill -9 <PID>
```

### 方案4：使用环境变量
```bash
# 设置端口
export FLASK_RUN_PORT=5001
python run.py
```

## 常用端口

| 端口 | 用途 | 状态 |
|------|------|------|
| 5000 | Flask默认端口 | 常被macOS AirPlay占用 |
| 5001 | Flask备用端口 | ✅ 推荐使用 |
| 8000 | Django默认端口 | ✅ 可用 |
| 3000 | Node.js常用端口 | ✅ 可用 |
| 8080 | 通用Web端口 | ✅ 可用 |

## 预防措施

1. **使用智能启动脚本**：`python start_server.py`
2. **配置固定端口**：在配置文件中设置端口
3. **使用虚拟环境**：避免全局包冲突
4. **定期清理进程**：关闭不需要的开发服务器

## 故障排除

### 检查端口状态
```bash
# 检查端口是否被占用
lsof -i :5000
netstat -an | grep 5000
```

### 查看Flask进程
```bash
# 查看Python进程
ps aux | grep python
ps aux | grep flask
```

### 重启网络服务
```bash
# macOS
sudo killall -HUP mDNSResponder

# Linux
sudo systemctl restart network
```

## 相关文件

- `start_server.py` - 智能端口选择脚本
- `run.py` - 标准启动脚本
- `app.py` - 主应用文件
- `config.py` - 配置文件

## 获取帮助

如果问题仍然存在，请：
1. 检查系统日志
2. 尝试重启计算机
3. 使用不同的端口范围
4. 联系技术支持 