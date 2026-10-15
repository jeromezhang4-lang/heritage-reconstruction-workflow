# 制作记录勘误

## E001：PP04“人头改为牛头”的诊断未获图像支持

原制作的 IMAGE_VISUAL_QA 及修改提示词曾把西门守护兽记成“人头”，并要求改为牛头。公开版独立前向验收重新查看两张保留图后提出疑问；复核可见，修改前后都具有牛角、牛耳和牛吻，不能从保留图像支持“已经把人头纠正为牛头”的叙述。

因此，当前 case.json/F04 将该事件记为“诊断更正与未解决细部”，不再把原审核的话当作已证实的图像事实。原图、修改指令和历史审核保持不变，以便别人检查。GENERATION_PROVENANCE 证明真实发生过一次定向编辑，不证明当时诊断正确，也不证明目标问题已解决。

图像仍有门兽身体姿态和雕刻细部的生成失真，只作为门厅体量的解释性示意。这里没有重新生图，也没有取得独立考古专家认证。

证据：

- `cases/persepolis/recorded/04_Images/Native/PP04_initial.png`
- `cases/persepolis/recorded/04_Images/Native/PP04.png`
- `cases/persepolis/recorded/04_Images/Native/PP04_repair.prompt.txt`
- `cases/persepolis/recorded/06_Quality_Assurance/IMAGE_VISUAL_QA.json`

这项勘误是对过程记录的更正，不改变万国门西侧牛形守护兽、东侧人首翼牛的历史区分。它说明提示词要求、工具调用记录、审核者观察和真实图像必须分别核对。
