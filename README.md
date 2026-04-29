AI Video Intelligent Analysis Platform
通用型全栈 AI 视频分析与智能预警系统 | Full-stack AI-powered video analytics & intelligent early warning system
基于实时视频流、多算法并行推理、消息队列异步处理、向量数据库检索与云边协同架构，提供开箱即用的智能视频分析能力，适用于安防、工业、园区、交通等通用场景。
项目定位
一套生产级、可私有化部署的 AI 视频分析平台，支持 RTSP 摄像头统一接入、多算法并行检测、智能报警过滤、轨迹检索、模型自训练、云端协同，提供完整 Web 管理后台，零代码即可完成 AI 能力部署。
核心技术栈
前端：Vue3 + Element Plus
后端：FastAPI (Python 3.10) + PostgreSQL
AI 推理：YOLOv8n / PP-YOLOE / YOLO-Pose / TSM / Qwen-VL2.5
向量检索：Milvus
消息队列：Kafka 2.1
对象存储：MinIO（本地）、阿里云 OSS（云端）
视频处理：VideoPipe 推理管道
加速硬件：NVIDIA GPU（CUDA 加速）
远程运维：FRP 内网穿透、SSH
技术架构
视频接入层：RTSP 流拉取、多路并行、帧采样
算法推理层：检测 / 跟踪 / 分类 / 姿态 / 行为识别并行处理
消息队列层：Kafka 异步解耦、报警过滤、流量削峰
数据存储层：PostgreSQL (业务)、Milvus (向量)、MinIO (媒体)
应用服务层：FastAPI 接口、权限管理、任务调度
前端层：设备管理、算法部署、报警中心、数据大屏
云端协同层：大模型二次确认、云存储、远程推送
核心技术能力
1. 视频流处理
RTSP 实时拉取与解码
多路视频并行分析
自适应帧率采样（1/5 帧）
异常断流自动重连
2. AI 算法体系
目标检测：人体、车辆、烟火、刀具、棍棒
多目标跟踪：Tracker 稳定追踪，减少重复报警
姿态识别：YOLO-Pose 骨骼点，摔倒检测
行为分类：TSM 视频分类，打架 / 异常动作
人脸分析：检测 + 特征编码，重点人员布控
区域分析：入侵、跨越、徘徊、聚集、越线
车辆分析：违停、超速、轨迹检索
3. 报警过滤引擎
按区域 / 时段 / 置信度多级过滤
按人 / 按目标去重
布防时间自定义
报警防抖与间隔控制
4. 向量检索系统
基于 Milvus 实现跨摄像头轨迹追踪
以图搜人 / 目标检索
重点人员布控与实时告警
5. 大模型二次确认
对接 Qwen-VL2.5 等视觉大模型
对高风险报警进行图像复核
大幅降低误报率
6. 模型自训练平台
数据集管理（YOLO/COCO）
自动标注、人工标注
模型微调、训练可视化
模型一键部署到推理端
7. 媒体存储与合成
报警自动录制视频
快照抓取
MinIO 本地存储
云端 OSS 同步、循环覆盖
8. 消息推送体系
短信推送
钉钉 / 企业微信 Webhook
语音电话通知
自定义 API 接口推送
9. 系统管理能力
用户 / 角色 / 菜单 / 权限细粒度管控
部门组织架构
操作日志、登录日志审计
摄像头 RTSP 统一管理
算法一键部署、区域标定、参数配置
管道负载监控、多节点均衡
核心功能模块
设备管理
摄像头增删改查
RTSP 地址配置、状态监控
批量导入导出
算法部署
算法仓库多版本管理
可视化区域标定
布防时间、灵敏度、阈值配置
单摄像头多算法并行
报警中心
实时报警列表
快照 / 视频回放
报警统计、趋势分析
数据大屏可视化
轨迹查询
人员 / 目标跨摄像头轨迹
时间 / 区域筛选
轨迹回放与导出
模型训练
数据集上传与管理
训练任务创建与监控
模型测试与下载
管道监控
推理管道状态
负载、摄像头挂载情况
实时运行日志
推送管理
多渠道推送配置
接收人管理
报警等级联动
系统管理
用户、角色、权限
菜单、部门、参数
日志审计、系统设置
技术优势
全链路异步架构：Kafka 解耦，高并发、低延迟
GPU 硬件加速：支持 NVIDIA 显卡，多路并行推理
插件化算法：算法独立开发，快速接入新能力
大模型复核：小模型检测 + 大模型确认，高精度
云边协同：本地推理 + 云端管理，安全可控
开箱即用：完整 Web 后台，无需开发直接部署
私有化安全：数据本地存储，支持内网隔离
高度可扩展：支持分布式、多节点、负载均衡
部署环境要求
系统：Linux x86_64（推荐 Ubuntu 20.04+）
Python：3.10+
GPU：NVIDIA CUDA（推荐≥8GB 显存）
内存：≥16GB
存储：≥100GB（根据录像时长扩展）
依赖服务：PostgreSQL、Milvus、Kafka、MinIO
快速开始
克隆项目
bash
运行
git clone https://github.com/yourname/ai-video-platform.git
cd ai-video-platform
配置环境变量与依赖
bash
运行
pip install -r requirements.txt
启动基础中间件
bash
运行
docker-compose up -d postgres milvus kafka minio
启动后端服务
bash
运行
uvicorn main:app --host 0.0.0.0 --port 8000
启动前端
bash
运行
cd web
npm install
npm run dev
访问后台
plaintext
http://localhost:8080
项目结构
plaintext
ai-video-platform/
├── backend/          # FastAPI后端
├── web/              # Vue3前端
├── algorithm/        # 算法推理模块
├── tracker/          # 跟踪器
├── videopipe/        # 视频处理管道
├── train/            # 模型训练平台
├── docker/           # 部署脚本
├── docs/             # 文档
└── README.md
适用场景
智慧园区 / 工厂 / 社区安防
周界入侵、翻越、徘徊监测
重点区域无人值守
摔倒、打架、聚集、烟火等异常预警
车辆违停、超速、交通治理
重点人员布控、轨迹回溯
贡献指南
欢迎提交 Issue 与 PR：
报告 Bug
提出新功能
优化文档
贡献算法插件
许可证
MIT License
联系方式
如有问题或商业支持，请通过 Issue 联系。
