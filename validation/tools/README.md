# 可重跑的浏览器验收

核心重建与 Python 测试不需要 Node.js。这里额外提供本案例实际使用的离线浏览器验收代码。

在这个目录安装可选依赖并安装 Playwright 自带 Chromium：

```bash
npm install
npx playwright install chromium
```

然后从项目根目录运行：

```bash
node validation/tools/persepolis_browser_check.cjs --html build/persepolis/gallery.html --case cases/persepolis --out build/browser-check
```

该脚本针对波斯波利斯的 11 场景回归检查，不能直接把固定数量断言当作其他遗址的标准。它把一份 HTML 复制到独立临时目录，关闭浏览器网络，检查大图、对照记录、来源、模型操作、下载哈希和移动端布局；180 秒截止，finally 关闭浏览器并清理本次临时目录。不启动服务，不设置系统 Chrome executablePath。

在提供预装 Playwright 的环境中，可用任务专属环境变量 `HERITAGE_PLAYWRIGHT_MODULE` 指定已有模块目录；这是依赖定位，不是浏览器可执行文件路径。默认使用本目录 npm 安装的包。

本版实测 Playwright 1.62.1 / Node.js v24.19.0；其他 Node/浏览器版本及 Windows/Linux 尚未实测。脚本 PASS 和截图检查仍不等于历史准确性证明。
