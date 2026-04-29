# AI Video Intelligent Analysis Platform
生产级通用 AI 视频分析与智能预警系统 | Full-stack AI-powered video analytics & intelligent early-warning system

## 简介
基于 FastAPI + Vue3 + YOLOv8 + Milvus + Kafka 构建的通用AI视频分析平台，支持实时RTSP流分析、多算法检测、轨迹检索、智能报警与云边协同，私有化部署开箱即用。

## 技术栈
Vue3 | Element Plus | FastAPI | Python3.10 | PostgreSQL  
YOLOv8n | PP-YOLOE | YOLO-Pose | TSM | Qwen-VL2.5  
Milvus | Kafka 2.1 | MinIO | OSS | VideoPipe | FRP

## 核心能力
✅ RTSP 视频流实时拉取、解码、多路并行分析  
✅ 异常断流自动重连、自适应帧率采样优化  
✅ 目标检测 / 多目标跟踪 / 分类一体化  
✅ 区域入侵 / 跨越 / 长时间徘徊检测  
✅ 摔倒识别（骨骼点）/ 吸烟检测 / 打架识别（TSM）  
✅ 持械检测 / 烟火检测 / 人群聚集密度统计  
✅ 车辆违停 / 车辆超速 / 轨迹分析  
✅ 人脸检测 + 人脸编码 + 重点人员布控  
✅ Milvus 跨摄像头轨迹检索、以图搜人  
✅ Kafka 异步消息队列、报警过滤、去重、防抖  
✅ 报警视频合成、快照抓取、MinIO 本地存储  
✅ 阿里云 OSS 云端同步、循环覆盖存储  
✅ 短信 / 钉钉 / 企业微信 / 语音多渠道推送  
✅ 可视化区域标定、布防时间、灵敏度配置  
✅ 算法仓库多版本管理（TensorRT/ONNX）  
✅ 模型训练 / 自动标注 / 数据集管理  
✅ 云边协同、Qwen-VL2.5 大模型二次确认  
✅ FRP 内网穿透、远程 SSH 运维  
✅ 用户 / 角色 / 菜单 / 部门 / 权限全管理  
✅ 操作日志 / 登录日志完整审计  
✅ 数据大屏可视化、报警统计分析  
✅ 摄像头统一管理、状态监控、批量导出

## 架构亮点
云边一体 | 异步解耦 | GPU 加速 | 大模型复核  
插件化算法 | 多路并行 | 低误报 | 私有化部署 | 开箱即用

## 项目定位
一套可私有化部署、高并发、低延迟的通用 AI 视频分析平台，支持 RTSP 摄像头统一接入、多算法并行检测、智能报警过滤、轨迹检索、模型自训练、云端协同，提供完整 Web 管理后台，零代码即可完成 AI 能力部署。

## 技术架构
- 视频接入层：RTSP 流拉取、多路并行、帧采样（1/5 帧）
- 算法推理层：检测 / 跟踪 / 分类 / 姿态 / 行为识别并行处理
- 消息队列层：Kafka 异步解耦、报警过滤、流量削峰
- 数据存储层：PostgreSQL (业务)、Milvus (向量)、MinIO (媒体)
- 应用服务层：FastAPI 接口、权限管理、任务调度
- 前端层：设备管理、算法部署、报警中心、数据大屏
- 云端协同层：大模型二次确认、云存储、远程推送

## 核心功能模块
- 设备管理：摄像头增删改查、RTSP 配置、状态监控
- 算法部署：算法仓库、可视化标定、布防策略、灵敏度配置
- 报警中心：实时报警、快照 / 视频、统计分析、数据大屏
- 轨迹查询：跨摄像头轨迹、时间筛选、轨迹回放
- 模型训练：数据集、训练任务、可视化监控、模型导出
- 管道监控：推理状态、负载均衡、运行日志
- 推送管理：多渠道推送配置、接收人管理
- 系统管理：用户、角色、菜单、部门、日志、参数

## 技术优势
- 全链路异步架构：Kafka 解耦，高并发、低延迟
- GPU 硬件加速：支持 NVIDIA 显卡，多路并行推理
- 插件化算法：算法独立开发，快速接入新能力
- 大模型复核：小模型检测 + 大模型确认，高精度
- 云边协同：本地推理 + 云端管理，安全可控
- 开箱即用：完整 Web 后台，无需开发直接部署
- 私有化安全：数据本地存储，支持内网隔离
- 高度可扩展：支持分布式、多节点、负载均衡

## 部署环境要求
- 系统：Linux x86_64（推荐 Ubuntu 20.04+）
- Python：3.10+
- GPU：NVIDIA CUDA（推荐≥8GB 显存）
- 内存：≥16GB
- 存储：≥100GB（根据录像时长扩展）
- 依赖服务：PostgreSQL、Milvus、Kafka、MinIO

## 快速开始
```bash
# 1. 克隆项目
git clone https://github.com/yourname/ai-video-platform.git
cd ai-video-platform

# 2. 安装依赖
pip install -r requirements.txt

# 3. 启动中间件
docker-compose up -d postgres milvus kafka minio

# 4. 启动后端
uvicorn main:app --host 0.0.0.0 --port 8000

# 5. 启动前端
cd web
npm install
npm run dev

通过网盘分享的文件：videopipe-fastapi
链接: https://pan.baidu.com/s/1VaNQOr9I9XHOy_6AXqwXZQ?pwd=i4cy 提取码: i4cy



具体看文件内容AI写的有问题还没改完
