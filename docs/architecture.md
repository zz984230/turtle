# 架构与模块职责（A股投研与资产管理系统）

## 分层架构
- 数据层（app/data/）
  - akshare适配：指数/行业资金流/个股资金流/融资融券/涨停池
  - 缓存与存储：Parquet分区与`meta.json`，统一字段与时区
- 文本层（app/ingest/）
  - 政策/公告与主流媒体新闻爬取；HTML解析、去噪、分段、标签与情感
- 分析层（app/analysis/）
  - 市场温度：成交量变化、融资融券余额变化、涨停占比、波动率；归一化与EWMA平滑
  - 技术面指标：pandas-ta/ta-lib 指标聚合
- 策略层（app/strategies/）
  - 风险平价：逆波动权重、约束与目标年化波动；动态再平衡
  - 止损止盈与风控联动（温度→再平衡/降权）
- 组合层（app/portfolio/）
  - 权重生成、持仓记录、交易与绩效评估
- 风控层（app/risk/）
  - 最大回撤监控、目标波动管理、阈值/止损止盈
- LLM层（app/llm/）
  - GPT-4/Claude连接器、提示模板；输入融合与输出解析
- 回测层（app/backtest/）
  - 多周期回测引擎（1m/5m/日线）；交易日志与复现；绩效指标
- 仪表盘（app/dashboard/）
  - 技术面/消息面/建议/回测可视化；响应式与报表下载
- 自动化（app/scheduler/）
  - 每日收盘后数据更新、策略计算、报告与备份
- 备份回滚（app/backup/）
  - 指定目录全量备份（`/d:/code/turtle/app/bond/`、`/d:/code/turtle/app/turtle_algo/`、`data/`）与版本回滚
- 通用（app/utils/）
  - 日志、异常、配置、安全与加密

## 现有代码对接
- 债券数据抓取与缓存：`d:\\code\\turtle\\app\\bond\\bond_data.py:7`, `d:\\code\\turtle\\app\\bond\\bond_data.py:49`
- 海龟策略示例：`d:\\code\\turtle\\app\\turtle_algo\\turtle_strategy.py:5`, `d:\\code\\turtle\\app\\turtle_algo\\turtle_strategy.py:47`, `d:\\code\\turtle\\app\\turtle_algo\\turtle_strategy.py:72`
- CLI入口：`d:\\code\\turtle\\main.py:6`

## 数据流与接口
- 数据采集→清洗标准化→缓存/存储→分析（温度/技术）→策略（权重/再平衡/风控）→组合绩效→回测引擎→仪表盘展示→备份与回滚→自动化编排
- LLM输入融合技术面与消息面，输出建议报告与风险评估，反馈机制闭环优化

## 安全与合规
- 密钥仅环境变量与安全存储；敏感数据加密；HTTPS与最小权限
- 日志脱敏与审计；备份与回滚可审计