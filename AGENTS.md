# AI 协作入口：podcast-transcriber-cli

项目用途：播客解析、下载、转录与 Markdown 输出 CLI。

## 云端工作约定

1. 先读 `README.md`、本文件及目标目录的局部说明，再确认当前分支、工作区变化和任务范围。仓库文档与实际 manifest 不一致时以当前代码为准，并记录差异。
2. 不假设云端已有本机依赖、浏览器、全局 CLI、绝对路径或认证。按仓库锁文件和 manifest 安装；缺少能力时报告限制。
3. 用小范围分支和 PR 交付。PR 写清问题、修改、执行过的验证及仍待验证事项；文档存在不等于功能验证通过。
4. 保留无关工作区改动。修改公共接口时检查消费者，不顺手改部署配置或重构其他模块。
5. 密钥只从任务环境/secret 配置读取；日志脱敏。使用合成测试数据，不提交个人资料或运行输出。

## 项目地图

src/podcast_transcriber/、tests/、skills/podcast-transcriber/、.env.example。

## 环境与验证

Python >=3.11；python -m venv .venv；激活后 python -m pip install -e ".[dev]"。

```sh
python -m pytest -q
```

## 项目约束

输出目录显式指定 --output-dir，避免使用 README 中的个人本地路径。优先离线 fixture；不在一般代码验证时下载大模型或长音频。不要将转录文本、API key、音频缓存写入仓库。

## 云端验证边界

普通云端以 faster-whisper/CPU 为基础；MLX 需要 Apple Silicon/Metal。模型下载、真实音频和摘要 API 联调不能由离线单测替代。
