# v0.1.0 实际验收

2026-10-15：核心离线重建、两个自包含技能及展馆技术验收通过。实测环境为 macOS，核心使用新建的 Python 3.9.6 虚拟环境。此结论不构成考古准确性认证。

| 检查 | 结果与实际范围 | 执行证据 |
|---|---|---|
| 全新目录与环境 | PASS：R3 ZIP 重定位、新虚拟环境，无 NumPy/Pillow/YAML、无 PYTHONPATH，按 README 重建完整案例 | [COLD_READER.json](COLD_READER.json) |
| 独立读者 | PASS：独立智能体只拿候选包和公开说明，在另一工作目录执行；R1/R2 保留原始发现，R3 按最终案例复核 | [独立报告](independent/ACCEPTANCE.md) |
| 自动测试 | PASS：17 项，包括文件篡改、路径逃逸、无效引用、占位草稿、错误尺寸声明、未解决审核失败、图像及证据版本变化后旧审核失效 | COLD_READER 的 documented_unit_tests 与独立执行回执 |
| 模型重建 | PASS：核心 1883、区域 2530 个对象；核心 OBJ 与原制作版逐字节一致，八项柱网不变量通过；JSON/区域坐标差异在记录精度范围内 | [technical-report.json](reader/technical-report.json) |
| 技能结构与可移植工具 | PASS：两个 SKILL.md 通过官方结构校验；自带运行代码与本版核心逐字节相同；独立复制后运行合成练习、完整案例审核 | [SKILLS_QA.json](SKILLS_QA.json)、独立报告 |
| 可选 PNG 栅格 | PASS：固定 NumPy 2.0.2 / Pillow 11.3.0，重渲染 PP01 鸟瞰与 PP08 室内的 Structure/Depth/Edges；正式案例 JSON schema 校验通过 | [OPTIONAL_CHECKS.json](optional/OPTIONAL_CHECKS.json) |
| 离线浏览器 | PASS：仅一份 HTML、离线 Chromium、零外部请求和页面错误；11 图均解码为 3840×2160，过滤、键盘、缩放、八条过程/四组对照、九来源/23 主张、深度测试模型、拖动与相机切换、同哈希下载、移动端均已检查 | [BROWSER_QA.json](browser/BROWSER_QA.json)、相邻截图 |
| 构建文件包 | PASS：重建所得 case-release.zip 的 CRC、22 个成员哈希与磁盘文件一致 | [ZIP_VERIFICATION.json](reader/ZIP_VERIFICATION.json) |

源文件、案例数据、保留图像与技能共 261 个文件在 R3 冻结后逐项回读；验收材料另行加入。见 [SOURCE_FREEZE.json](SOURCE_FREEZE.json)。对应离线展馆 SHA256 为 `12739dab4ac72a6434e957243ec5a766076e3e212d1a27a263db756f1ba48fb2`。

实际交付的源码 ZIP 与技能 ZIP 会再进行完整成员回读、解压及文档命令运行。其校验记录位于下载包旁的 `Heritage_Release_v0.1.0.json` 与 `Heritage_SHA256SUMS.txt`，避免把文件自己的哈希递归写入自身。上述冻结不把验收文档冒充历史制作证据。

## 独立检查改变了什么

独立读者实际查看前后图，指出 PP04 原先“人头改成牛头”的诊断缺乏保存图像支持。公开说明已更正；原提示词、旧审核、修改前后图均保留。门兽身体、姿态和雕刻细部的残余失真继续醒目标注。见 [勘误](../docs/ERRATA.md) 及独立报告。

首版候选文档指向未附带的验收目录，也已补齐。R1/R2 的报告只证明各自候选，不能替代 R3 的执行证据。独立者为另一智能体，不是另一名考古专家，也没有冒称另一台实体电脑测试。

## 尚未证明或执行的范围

- 历史准确性、全套图片与模型严格吻合、人物与雕塑全部细节：UNVERIFIED。自动 audit 是结构检查加人工提示，不会自动阅读史料或识别动物。
- 重新调用原 AI 服务、重跑超分、未来逐像素重现：NOT_RUN。此次重建会重新生成模型/相机/预览，并回放已保存的图片。
- 所有 11 机位的可选栅格重渲染：NOT_RUN；本次仅实测两个不同类型机位。
- 第三方图与外部论文全文重新访问、独立考古专家审查：NOT_RUN。排除的地图保留来源、哈希和权利说明。
- Windows/Linux 真机运行、各客户端自动发现与热加载：UNVERIFIED。
- 全局技能安装、远程 CI、公开 GitHub 发布：NOT_RUN。

本轮浏览器实例均已关闭；临时预览没有启动服务器。独立读者的有限子进程终态见相应执行回执。可选依赖仅装在任务虚拟环境中；核心路线不需要它们。


## GitHub 发布版本的文档变更

发布前依据当前官方文档，将技能安装示例修正为用户或项目的 `.agents/skills`，并增加仓库克隆、Release 下载、桌面端/CLI 调用方法。原案例、图像、提示词、运行代码和两个技能目录均未修改。另加入保持原文件字节的 `.gitattributes` 与可选核心复现 CI 模板。变更前后哈希见 [GITHUB_PUBLICATION_INPUTS.json](GITHUB_PUBLICATION_INPUTS.json)，原 R3 快照另存于 `baseline/SOURCE_FREEZE_R3.json`，当前发布输入见 `SOURCE_FREEZE.json`。历史报告的未执行状态保留其当时含义；新增远程 CI 以 GitHub Actions 的实际运行结果为准，GitHub 下载回读另附于 Release。

GitHub 首次推送明确返回缺少 `workflow` scope；没有扩大凭据权限，CI 改为 `docs/ci/reproduce.yml` 模板。本次远程 CI 为 NOT_RUN，发布下载复核另附实际证据。
