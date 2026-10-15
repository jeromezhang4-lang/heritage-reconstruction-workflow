# 首版候选包独立前向验收

结论：首版软件回放、两项独立技能和离线展馆可运行。它仍是解释性案例，不能称为历史准确性认证。最终发布判断转由后续 R2 验收作出，本报告保留首版原始观察。

## 对象与隔离

唯一材料为 candidate-v0.1.0.zip，SHA256：`8761f700cac82a119a60da0a2622ae9123df261df6c4b07a46929c2b2552a420`。解压至本报告所在新目录。没有读取原制作目录、父任务结论或记忆；没有联网、新生图、全局安装或外部发布。运行环境为 /usr/bin/python3 创建的 --without-pip 虚拟环境，Python 3.9.6，不含 NumPy/Pillow。

## 影响使用/发布的发现

1. **FAIL：文档提及的验收材料缺失。** README 列出 validation/，docs/REPRODUCIBILITY.md 要求查看 validation/ACCEPTANCE.md；此候选 ZIP 的 256 项中没有 validation 目录。因此首次读者无法核对文档声称附带的本版验收。它不阻止实际重建，但应补齐或更正文案。
2. **UNVERIFIED：PP04 失败叙述与对照图不完全自证。** F04 写原图出现人头；本次实际打开 Native/PP04_initial.png 与 PP04.png，修改前已可见动物长吻和弯角，修改后耳、鼻更明确。单凭保留的这对图不能明确证实原先人头，建议复核版本映射或把文字改为与可见问题吻合的表述。本次不由此推断西门实际雕像形制。
3. **UNVERIFIED：历史证据。** 第三方原图以 NOT_BUNDLED_RIGHTS 排除；本次按禁止联网的范围，无法实际核对原考古图、完整论文及服务端调用。S04 明确记录完整 OIP68 未取得。账本与来源说明可审查，不能替代原文。

## 实际执行

从项目根目录，使用新虚拟环境解释器运行 README 的 verify --case cases/persepolis、reproduce --case cases/persepolis --out <本目录>/build/persepolis，均返回 0 / PASS。生成核心 1883、区域 2530 个对象、11 个 SVG、离线 HTML、OBJ 和 case-release.zip；8 项柱网不变量通过。独立读回 ZIP：22 成员 CRC 正常、成员与磁盘 SHA256 全匹配；核心 OBJ 与记录版逐字节一致。未重新调用 AI，也未重跑超分。

文档的 unittest 命令通过 15 项。审查者最初额外添加 -I 令 unittest 缺少项目导入路径；回到文档原命令后通过，这是验收参数问题。完整具体命令、PID、截止秒数、stdout/stderr 和退出码见 execution.jsonl。

分别复制 skills/heritage-reconstruct 与 skills/heritage-audit 到 skills-only/，从无项目 PYTHONPATH 的目录，以各自 scripts/heritage.py 执行 demo init、verify、reproduce 和 audit，全部通过。合成图只是 16×9 的软件夹具。独立 audit 技能对完整 Persepolis 的 audit 通过，仍明确输出 historical_accuracy=UNVERIFIED 和人工审查要求。reconstruct 技能另对完整案例完成受限文件访问重建；仅允本次独立树、Python 标准库和 /dev/null，曾拒绝 /dev/urandom 后标准库继续完成；没有允许原制作目录读取。该限制仅是本次文件访问仪器，不是操作系统全面隔离认证。

## 展馆与图像审查

Playwright 自带 Chromium 151.0.7922.34 以 offline 模式打开 file://gallery.html，HTTP(S) 请求另行阻断，实际 0 网络请求、0 页面错误。23 项检查通过：11 图解码、类型过滤、PP04 模态框及残余警示、缩放、前后切换、分享图下载、8 条过程记录/4 组对照、9 来源/23 主张、WebGL 模型、拖动、区域切换、OBJ 下载。两个下载均与目标文件哈希相同；空闲 400ms 渲染计数不变。已查看核心/区域截图，可见模型和屋顶；没有逐机位或逐像素认证。浏览器在 finally 内关闭。

首次 Chromium 在沙箱因 MachPort Permission denied 退出；同一固定脚本经工具权限批准后运行。首次过滤断言误以为 entrance 只有一张，实际 PP03/PP04 均属入口；修正验收脚本后通过，候选源码未改。失败记录保留在 browser/ 和 execution.jsonl。

人工实际查看 FINAL_CONTACT_SHEET.jpg 的 11 幅概览，以及 PP01/PP02/PP04/PP05 四组原生前后图。PP01 可见独立门兽和直梯变为折返入口；PP02 可见视点变化；PP05 可见前排柱序减少/重排，但遮挡与视角使准确柱数仍未认证。PP04 的直立身体/腿部混合形态仍明显，不可作为雕塑复原依据；展馆卡片与大图都醒目标出限制。其他 7 幅只完成联系表概览，未逐图精查人体、铭文、所有柱数及年代。所有原生/成图哈希不等于生成服务证明。

独立核对记录的 16 阶段共有 62 个 prompt/input/output 文件引用：58 个存在并哈希匹配，4 个输入引用缺失且对应已披露的第三方图，共涉及 2 个不同文件；0 哈希冲突。此结论只说明本地记录一致性。

## 软件与人工判断边界

verify/audit 检查字段、编号引用、文件、哈希、声明尺寸和已登记的未解决 FAIL；audit 实际是 verify 加人工审查提示。reproduce 再检验模型与打包。工具不会阅读史料含义、识别图中动物、统计可见柱数或确认权利。人工能从包中追踪来源→主张→构件/场景→提示词/输入→结果→审核；PP04 的 T04/T05/T16/T17 主要支撑柱厅、屋顶、配色与材料，并不直接记录西门兽头的逐条证据；该场景关联所有 9 构件也偏宽。应继续做有精确页码/图版的语义核对。

未执行：可选 NumPy/Pillow 栅格重渲染、AI 服务、外部论文/地图访问、重新超分、Windows/Linux、客户端自动发现/热加载和专业考古审查。无需为本次运行全局安装技能。

## 收尾

所有记录的子进程均有限截止且已回收；所有浏览器成功实例已关闭，无服务/端口启动。256 个候选条目与 ZIP 原字节哈希相同。证据：execution-summary.json、execution.jsonl、reports/、browser/、build/persepolis/。
