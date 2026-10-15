# 新案例的实际工作流

## 研究与范围

先确定地点、主体年代、复原范围和读者用途。把宫殿、城址与区域景观区分清楚；未知平面不能证明建筑规模很小，也不能授权创造巨大建筑群。

在 `case.json` 中维护来源、主张、构件和镜头四类编号。一个来源的学术级别与某项复原的确定程度不是同一字段。记录实际读过的章节/图版、作者的论点与自己的推断；目录和下载失败不能写成全文已读。

确定性采用 A/B/C/D/UNKNOWN：直接遗存或测绘支持、研究支持的推断、缺失部分的类比推定、表现性安排、未知。这是项目约定，不是国际认证或百分制准确率。主体与跨期细节分别记录，不把不同年代建筑拼成一个有确定日期的全貌。

`init` 创建的来源带有 `placeholder: true`，不能通过正式验证。完成研究后用真实来源替换，并移除该标记。尺寸和相机也是示例，必须依据研究修改。

## 模型与机位

小案例可编辑 `geometry.json` 的 boxes / column_grids。复杂遗址可使用可审查的 Python 配方，`geometry.recipe` 指向一个提供 `create()` 的相对路径；它返回 Model、组件列表和相机列表。区域配方可返回 Model、分区列表和相机。配方是可执行代码，仅运行已审阅、可信的案例配方。

模型要固定主要位置、尺度、柱网、开放庭院与入口路线。地形、完整屋顶及附属房间的推定单独记录。相机只是表现选择，不能把模型当成高精度测绘或真实 DEM。

```bash
python3 scripts/heritage.py verify --case work/my-site --no-hashes
python3 scripts/heritage.py freeze --case work/my-site
python3 scripts/heritage.py prepare --case work/my-site --out build/my-site-preparation
```

`freeze` 只为已审阅的有意修改建立快照，不要用它掩盖意外哈希变化。`prepare` 校验已冻结输入并重建模型和机位包络 SVG；需要实际栅格结构/深度/边缘图时使用可选 `render-raster`。

## 生图交接与留痕

选择当前环境真实可用的图像生成工具。结构图、相机、风格图和史料图分别说明角色，不假定工具支持 ControlNet、seed 或严格几何绑定。无工具时交付准备材料并说明生成尚未执行，不制造“实际调用”记录。

在工具中提交真实提示词和输入图，保存返回的原生输出，然后记录本地输入和结果：

```bash
python3 scripts/heritage.py record-generation --case work/my-site --scene SC01 --image /path/to/actual-output.png --prompt /path/to/actual-prompt.txt --tool actual-tool-name --reference /path/to/actual-reference.png
```

可见时添加 `--model`、`--seed`；不可见则保留 UNVERIFIED。该命令复制文件、读取原生尺寸并记录哈希，不伪造服务端证明、不自动把图变成 4K、不直接调用 AI。每次调用形成新 attempt，旧输出保留。来源受限的参考图在公开分享前须移出公开包并保留外部资源记录。

## 审查与修正

检查实际图像的年代、入口、主要几何、柱网、尺度、材料、动物解剖、现代混入物和区域密度。主模型与某张图必须分别检查。不要让漂亮画面抵消关键结构错误。

```bash
python3 scripts/heritage.py record-review --case work/my-site --scene SC01 --criterion geometry --status FAIL --note "入口位置与底图相反" --reviewer "reviewer-name"
```

新导入的图至少需要 geometry 和 chronology 两项审查。每项记录绑定实际图像字节与当前证据/相机上下文；换图或改变依据后，旧审核不会自动转给新对象。修正后追加同一 criterion 的新审核，而非删除旧记录。当前对象的最新 FAIL 会阻止正式构建。PASS 只代表该审核者记录的该项目，不自动升级成独立专家认证。无法确认时记 UNVERIFIED 并解释展示边界；保留重要失败的前后图、处理方法和未解决问题。

## 交付

所有场景有实际结果且关键失败已处理后，再次冻结，使用 `reproduce` 构建。记录技术 PASS、历史 UNVERIFIED 和未执行项；原生尺寸、超分过程、服务可见参数与外部素材权利分别披露。先验证产物，再选择本地分享或另行授权的公开发布。

v0.1.0 的展示模式是带明确边界的案例研究，并非考古认证。波斯波利斯 PP04 的原“人头改牛头”诊断已作勘误，并保留残余生成失真说明，不能作为门兽雕塑的精确复原图。提示词想修什么，不证明原图确有该问题。
