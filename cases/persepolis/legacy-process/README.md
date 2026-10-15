# 历史过程脚本

这里保留本次制作实际使用的研究、建模、提示词、后处理、展馆、验收和打包代码。它们体现制作过程，部分路径与执行环境已经过时；带 `<SOURCE_PROJECT>`、`<BRONZE_PROJECT>`、`<LOCAL_RUNTIME>` 的路径是本机信息的显式脱敏。

不要用这些历史脚本代替项目 README 中的当前入口。可移植配方是案例根目录中的 model_recipe.py 与 context_recipe.py；通用入口是 scripts/heritage.py。原生生成由真实客户端工具执行；GENERATION_PROVENANCE 保存实际输入、提示词与输出，而不是伪造的重放脚本。

MIGRATION.json 同时保留原代码哈希、公开副本哈希与是否脱敏。历史报告的 PASS 仅属于当时对象；开源版验收在 validation/。
