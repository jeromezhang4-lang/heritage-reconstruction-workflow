# 技能分享与使用

本版包含两个独立技能目录：`heritage-reconstruct` 和 `heritage-audit`。每个目录都有 SKILL.md、agents/openai.yaml、说明与自带运行工具。无需本仓库路径或原作者的电脑环境。

## 安装

从 [v0.1.0 下载页](https://github.com/jeromezhang4-lang/heritage-reconstruction-workflow/releases/tag/v0.1.0) 获取 `Heritage_Skills_v0.1.0.zip`，解压后进入 `heritage-skills-v0.1.0`。两个完整技能目录位于 `skills/`。也可克隆完整项目后在项目根目录执行下列命令。

当前 [OpenAI 官方技能文档](https://developers.openai.com/codex/skills/#where-to-save-skills) 推荐用户目录 `~/.agents/skills` 和项目目录 `<project>/.agents/skills`。本项目显式复制到使用者选择的目录，不自动推断，也不会覆盖已有同名技能。

macOS/Linux 用户范围安装：

```bash
python3 scripts/install_skills.py --destination "$HOME/.agents/skills"
```

Windows PowerShell：

```powershell
py -3 scripts/install_skills.py --destination "$env:USERPROFILE\.agents\skills"
```

只为某个项目安装时，将目的地换成实际项目路径：

```bash
python3 scripts/install_skills.py --destination /path/to/your-project/.agents/skills
```

也可手动复制 `skills/heritage-reconstruct` 和 `skills/heritage-audit` 两个完整文件夹。不要只复制 SKILL.md，它们需要自带的脚本和运行文件。已有同名目录时，先明确管理旧版本或选择其他目的地；本工具会停止而不是覆盖。

安装后查看客户端技能选择器；没有出现时重启客户端。桌面端输入 `@` 选择技能；Codex CLI/IDE 使用 `/skills` 或 `$`。官方文档描述发现机制；本版执行证据验证的是文件安装和运行工具，没有冒称已验证所有客户端的发现与热加载。本项目发布过程没有替作者全局安装技能。

## 明确调用

```text
使用 $heritage-reconstruct 为这座历史建筑建立来源、未知项、模型和实际生成记录，再制作可离线查看的案例。
```

```text
使用 $heritage-audit 审查 /path/to/case，报告技术检查、已查看的图像问题与历史不确定性，不修改原始案例。
```

上述是 CLI/IDE 的明确调用示例。桌面端先用 `@` 选中对应技能，再输入同样的任务文字。

完整案例的离线重建：

```text
使用 $heritage-reconstruct，按这个项目的 README 重建 cases/persepolis，在一个新目录保存结果，明确说明实际重跑和回放的部分。
```

## 没有完整案例时练习

将 `<skill-dir>` 替换为实际技能目录：

```bash
python3 <skill-dir>/scripts/heritage.py init --out /tmp/heritage-demo --id demo --demo
python3 <skill-dir>/scripts/heritage.py reproduce --case /tmp/heritage-demo --out /tmp/heritage-demo-build
```

合成样例用于验证技能工具可运行，不能证明史料研究、生图或考古复原完成。完整波斯波利斯案例保留在项目包，避免给每个小型技能重复附加大型图像。

这两个技能允许按任务匹配选择，尚未验证所有智能体客户端的兼容性。新增网络生图仍依赖实际可用工具与账号；本技能不附带密钥、私有客户端接口或假装已执行的生成器。技能文件夹分享不等于已上架 OpenAI 插件目录。
