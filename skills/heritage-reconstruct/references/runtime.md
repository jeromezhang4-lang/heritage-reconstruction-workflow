# 自带工具

将 `<skill-dir>` 换成本技能实际目录。入口 scripts/heritage.py 自带 assets/runtime，需要 Python 3.9+，不依赖原项目仓库。

```bash
python3 <skill-dir>/scripts/heritage.py verify --case /path/to/case
python3 <skill-dir>/scripts/heritage.py audit --case /path/to/case --report /path/to/audit.json
python3 <skill-dir>/scripts/heritage.py reproduce --case /path/to/case --out /path/to/new-build
```

verify/audit 不会修复、重新冻结或生图。reproduce 重新计算参考模型，并使用已保存图像构建展馆；不会再次调用 AI。技术 PASS 不是历史认证。

没有现成案例时可验证工具：

```bash
python3 <skill-dir>/scripts/heritage.py init --out /tmp/heritage-demo --id demo --demo
python3 <skill-dir>/scripts/heritage.py reproduce --case /tmp/heritage-demo --out /tmp/heritage-demo-build
```

这是软件合成样例。新遗址不带 --demo 的 init 会产生研究草稿，须填真实来源、主张和几何后才能冻结。已有审阅完毕的修改，先 verify --no-hashes 检查结构，再 freeze；不要用 freeze 掩盖意外哈希变化。完整参数见 --help 与各子命令的 --help。

可选 PNG 结构/深度/边缘渲染需要 assets/runtime/requirements-render.txt 的依赖；标准库路线只生成机位包络 SVG，并保留案例中的原 PNG 参考。
