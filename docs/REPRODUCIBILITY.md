# 独立复现的范围

## 核心路线

可以克隆仓库，也可从 [v0.1.0 下载页](https://github.com/jeromezhang4-lang/heritage-reconstruction-workflow/releases/tag/v0.1.0) 下载完整项目 ZIP，解压到任意新目录。只需要 Python 3.9+，无需访问本项目原始工作区。先进入项目根目录；核心路线没有 pip 安装步骤。可以从未安装第三方包的虚拟环境运行：

```bash
python3 -m venv .venv
.venv/bin/python scripts/heritage.py verify --case cases/persepolis
.venv/bin/python scripts/heritage.py reproduce --case cases/persepolis --out build/persepolis
```

Windows 虚拟环境的解释器是 `.venv\Scripts\python.exe`。无需激活环境，也不需要设置 PYTHONPATH。

输出目录中的 `gallery.html` 可直接在浏览器打开，不需要启动本地服务器；`model/` 提供 OBJ/JSON 和相机，`case-release.zip` 是本次构建的展馆与模型包。检查命令的退出码和新生成的 JSON 报告，不要用历史 QA 文件代替本次结果。

从同一个发布版本复核时，可下载 Release 附件或在 Git 克隆后执行 `git checkout v0.1.0`。`main` 后续可能继续更新。Release 的 `Heritage_SHA256SUMS.txt` 对应附件字节；GitHub 自动生成的 Source code ZIP 是另一种归档，不能混用二者哈希。

验证对象：来源/主张/构件/场景引用，保留文件哈希，PNG/JPEG 尺寸，原生 4K 声明，未处理的审核失败；核心和区域几何重新计算，检查柱网及相机，输出独立 HTML、OBJ、SVG 和 ZIP。`technical-report.json` 与 `ZIP_VERIFICATION.json` 保存每次结果。

图库回放已保存的实际生成图。完整原生图、16 条调用/修改链、旧版本和源提示词位于 `cases/persepolis/recorded/`；公开规范化清单是 `case.json`，原制作记录位于 `recorded/06_Quality_Assurance/`。

## 不作出的复现承诺

- 不保证远程 AI 再次生成同一像素；原服务的模型/seed 未暴露。
- 不自动重新读完历史论文或判断来源结论是否正确。
- 不把模型柱数、文件哈希、网页测试当作图像或历史准确率。
- 不声称所有区域同期使用、全部住宅已知，或由图推算人口。
- 不把历史包中的旧 QA 当作本开源版的新验收；本版记录放在 `validation/`。
- 原核心 OBJ 可进行逐字节比较。JSON 浮点舍入和由其导出的区域几何按记录精度比较，不能仅用字节不同判定考古变化。

## 可选栅格路线

```bash
python3 -m venv .venv-render
.venv-render/bin/python -m pip install --no-cache-dir -r requirements-render.txt
.venv-render/bin/python scripts/heritage.py render-raster --build build/persepolis --scene PP01 --out build/raster-PP01
```

这一步从真实网格重新渲染 PNG，不调用 AI。NumPy/Pillow 版本在 `requirements-render.txt` 中固定；它不承诺在所有硬件上逐字节相同。SVG 机位包络图没有遮挡/深度求解，不能冒称 PNG 深度参考。单图默认 960×540、120 秒截止，可通过命令参数调整，范围受限。

FSRCNN 超分的原始脚本、算法、模型来源、权重哈希、OpenCV 版本和裁切参数作为历史记录保留。该模型权重不随本项目分发；默认路线回放已保存的超分结果，不宣称重跑了超分。新项目可选择其他处理方式，但要保留原生图并记录真实算法。

## 新图像生成路线

参见 WORKFLOW 的 `record-generation`。生成工具在当前智能体环境中运行；本项目用文件交换接入，以免把某个客户端私有接口伪装成公开 API。只有真实工具调用产生的文件才可记录成实际生成；服务信息不可见时保留未知。

## 本版实际验收

查看 `validation/ACCEPTANCE.md` 与相邻 JSON 记录。它们区分干净环境重跑、故障注入、独立技能使用、浏览器显示和未验证的平台。提供 CI 配置不等于远程 CI 已经运行；本机 macOS 验收也不等于 Windows/Linux 已实测。

可选 CI 模板在 `docs/ci/reproduce.yml`，包含 Linux、macOS、Windows 的核心测试、完整案例回放和自包含技能工具。本次 GitHub 登录凭据缺少写入工作流所需的 `workflow` 权限，因此没有注册 Actions，也不声称远程 CI 已运行。有对应权限的维护者可将模板复制到 `.github/workflows/reproduce.yml` 后提交，再查看实际运行结果。发布验收通过下载 GitHub 附件，在干净环境按文档执行；执行证据附在 Release 的 `Heritage_GitHub_Verification.json`。原始离线验收与本次发布版本的关系见 `validation/GITHUB_PUBLICATION_INPUTS.json`。
