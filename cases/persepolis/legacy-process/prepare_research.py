from pathlib import Path
import json,hashlib,shutil,datetime
R=Path(__file__).resolve().parent;O=R.parents[1]/'outputs/Persepolis'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
sources=[
 {'id':'S01','title':'Schmidt 1939 · OIC21 原始发掘报告','url':'https://isac.uchicago.edu/publications/treasury-persepolis-and-other-discoveries-achaemenians','tier':'A','inspected':'PDF184pages; printed pp1–3, Fig5 PDFpage35 inspected; relevant indexed architectural passages','used_for':'原始总平面、南部建筑标签、百柱厅100柱与北门廊16柱、年代分歧','scope_limit':'1937年发掘状态图；不是公元前430年的同步图。功能与断代部分已被后续研究修订。','rights':'University of Chicago CC BY-NC-ND4.0; unannotated limited full-page figure reproduced as research reference; full book not redistributed'},
 {'id':'S02','title':'Shahbazi · Encyclopaedia Iranica: Persepolis','url':'https://www.iranicaonline.org/articles/persepolis/','tier':'B','inspected':'建筑章节与Figure2总平面实际像素','used_for':'总体尺度、各柱厅与住宅结构、复原时的建筑阶段过滤','scope_limit':'不是逐室原始测绘；部分细节与早期报告判断有差异。','rights':'Article and plan copyright retained; one unmodified plan as limited research reference'},
 {'id':'S03','title':'UNESCO · Persepolis','url':'https://whc.unesco.org/en/list/114','tier':'B','inspected':'官方遗产条目','used_for':'遗址定位、约13公顷纪念性宫殿群、历史与遗产状态','scope_limit':'遗产简介不等于逐构件尺寸或屋顶依据。'},
 {'id':'S04','title':'Schmidt 1953 · OIP68出版目录','url':'https://isac.uchicago.edu/publications/persepolis-i-structures-reliefs-inscriptions','tier':'A','inspected':'官方目录与下载地址；完整PDF下载两次到240秒截止，未完整取得','used_for':'原始建筑报告的书目信息与后续研究入口','scope_limit':'本次不将未读完整PDF作为新增几何证据。'},
 {'id':'S05','title':'Princeton · 薛西斯宫执杯侍从浮雕 y1949-115','url':'https://artmuseum.princeton.edu/art/collections/objects/23760','tier':'A/B','inspected':'博物馆对象条目，约486–465BCE，原位置推断的说明','used_for':'侍从服饰、执杯活动的有限比较','scope_limit':'原位没有已知照片；不复制精确位置，不据此宣称一次具体宴会。'},
 {'id':'S06','title':'Met · Procession relief 39.133','url':'https://www.metmuseum.org/art/collection/search/323723','tier':'A/B','inspected':'约405–359BCE对象条目','used_for':'年代排除检查','scope_limit':'晚于430BCE，不能直接移植其西侧阶梯雕刻到本次目标。'},
 {'id':'S07','title':'UChicago ISAC · Persian Gallery','url':'https://isac.uchicago.edu/persian-gallery','tier':'B','inspected':'官方馆藏介绍','used_for':'1931–39发掘史与来自波斯波利斯的柱头、浮雕背景','scope_limit':'馆藏介绍不验证整个复原模型。'}]
(O/'00_Research/sources.json').write_text(json.dumps(sources,ensure_ascii=False,indent=2))
claims=[
 ('T01','约430BCE作为本次同步快照','S01/S02','C','制作选择；主建筑已存在，局部阶段仍不确定'),
 ('T02','完整宫殿高台约12.5–13公顷；概略包络约300×455m','S02/S03','B','不把包络长宽相乘当精确面积；本模型边界为人工近似'),
 ('T03','西北入口、西侧阿帕达纳、东侧百柱厅、东南库房、南侧王宫','S01 Figure5 / S02 Figure2','A/B','平面相对关系直接可见；数值坐标是近似注册'),
 ('T04','西北双折返阶梯；万国门四柱厅','S01/S02','A/B','模型保留每侧111阶的简化形制；AI不保证每级可逐一计数'),
 ('T05','万国门柱高约16.5m及木梁屋顶','S02','B/C','保存构件支持尺度；完整屋顶构造为推定'),
 ('T06','阿帕达纳60×60m主厅、6×6柱阵、三面各12柱门廊','S01/S02','A/B','模型明确36+36柱；生成图只审宏观关系，不认证可见柱总数'),
 ('T07','阿帕达纳柱高约19.5m、抬高台基','S02/S03','B','人物1.75m比例；不加虚构超高层'),
 ('T08','百柱厅68.5×68.5m、10×10柱阵、北门廊2×8柱','S01 printedp2 / S02','A/B','主厅与库房中的另一座100柱库厅严格区分'),
 ('T09','百柱厅柱约14m，比阿帕达纳低','S02','B','屋顶高度与墙体细节仍为C'),
 ('T10','塔查拉位于阿帕达纳南侧、12柱主厅与南侧门廊','S01/S02','A/B','早期木柱方案；精确高度与漆饰C'),
 ('T11','哈迪什王宫36柱主厅与北侧12柱门廊','S01/S02','A/B','墙高、屋顶C'),
 ('T12','中央门厅Tripylon四柱，约15.46m见方','S02','A/B','早期报告功能/年代不同；采用后续ArtaxerxesI完成判断'),
 ('T13','库房大型封闭多室区与内部庭院','S01 Figure5 / S02 Figure2','A/B/C','只锁定大体区块；未逐室数字化，各屋顶及分隔为C'),
 ('T14','南部住宅区传统名Harem，具体功能不能等同现代含义','S01/S02','B/C','几何只表示房间带，不绘虚构后宫仪式'),
 ('T15','PalaceH的430BCE具体阶段有分歧','S01 printedp3 / S02','C','本模型仅保留假设早期体块，不复制ArtaxerxesIII后加阶梯'),
 ('T16','彩绘与彩色砖存在，但整套配色不完整','S01/S02','B/C','有色局部作为推定；不把现存灰白石材等同古代全貌'),
 ('T17','木梁、灰石构件、泥砖墙与抹灰组合','S01/S02','B/C','屋顶做低坡/近水平木梁系统，禁止穹顶与希腊山花'),
 ('T18','东面山体、城防关系','S01 Figure5 / S02','B/C','未取得DEM；山形与完整防御线高度是示意'),
 ('T19','礼仪来宾与侍从可用浮雕作服饰比较','S05/S01','B/D','不标成已证实的诺鲁孜或具体朝贡事件；人数D'),
 ('T20','排除ArtaxerxesII/III山坡王陵、完成状态的晚期未完成门及后世建筑','S01/S02/S06','B','古图是多期累积，先过滤再建模')]
(O/'00_Research/claim_ledger.json').write_text(json.dumps([dict(zip(['id','claim','source','reconstruction_tier','boundary'],c)) for c in claims],ensure_ascii=False,indent=2))
shutil.copy2(R/'OIC21_page35.png',O/'01_Maps_Plans/OIC21_Figure5_1937_Terrace_Plan.png')
(O/'01_Maps_Plans/SOURCE_AND_RIGHTS.md').write_text('''# 使用的平面与范围\n\nOIC21 Figure5，PDF第35页，原书图5：截至1937年底发现的高台建筑。测绘John S. Bolles，补图Eliot F. Noyes、R. Carl Haines，标注比例1:2000。来源S01，原始报告PDF SHA256: 8aad1ddfd6a1eb155130f454e1cf82bfbb85bf8177456577fd635ca71c2f521a。图版保持完整，未在原像素上增画。\n\nIranica Figure2：本次人工注册的主要底图，原像素已实际查看，版权保留。源图包含后期王陵、未完成门等，不能全部作为430BCE同期遗存。本模型以百柱厅已知尺度和建筑轴线约15度做近似注册；不是精密GIS。\n\n仅附两张制作所需研究图版，完整书籍与网页留在work不重分发。官方链接见sources.json，图版版权不随AI作品转移。\n''')
report='''# 波斯波利斯 · 完整宫殿群复原研究\n\n目标为约公元前430年，阿契美尼德王朝主要宫殿群已建成的使用状态。复原范围为宫殿高台及东侧山体背景，完整城市、平原上的居住区与古代人口不在模型范围内。\n\n## 文明背景\n阿契美尼德王朝以跨区域统治与多种语言的行政实践著称。宫殿建筑将来自不同地区的工艺组织在同一王权空间中：石构柱列、泥砖墙、木梁与雕刻共同形成其建筑语言。波斯波利斯应作为宫廷、礼仪、住宅、库房和防御相连的建筑群理解，而非单独一座柱厅。[S01,S03,S07]\n\n本系列呈现的是一座正在使用的王宫群。朝见、侍从与来宾是解释建筑尺度的情境推定；画面不宣称记录了一场真实发生的节庆、战争或朝贡典礼。[S01,S05]\n\n## 遗址历史\n大流士一世开建高台，薛西斯及阿尔塔薛西斯一世继续扩展。阿帕达纳与百柱厅的规模、南部王宫的台阶关系、库房与入口动线共同构成主体。约330BCE的焚毁属于后来阶段，本次画面采用完好使用状态。[S01,S03]\n\n遗址包含多个时期。原始总平面上的晚期山坡王陵、未完成门和后加阶梯不能不加区分地放入430BCE。1930年代发掘与后来的保护、重组也不能直接充当古代建筑全貌。[S01,S02,S06,S07]\n\n## 已确认、推定与未知\n总平面与保存构件支持主要建筑间的关系，柱网可固定在统一模型中。完整木屋顶、墙高、房间用途、彩绘组合、山地形态及人群安排仍有推定。近似平面注册不得写成厘米级实测。\n\n两种证据等级分开：来源A原始考古、B学术/机构综合、C后世文献、D现代艺术；复原A直接遗存、B间接支持、C学术推定、D画面安排。某网页是官方来源，不代表其所有建筑细节均为直接测量。逐项边界见claim_ledger.json。\n\n## 宏伟尺度的表现门禁\n完整高台边界、主要柱厅、宫殿、库房和山体须在总览中形成连续整体。阿帕达纳与百柱厅的不同高度需能看出；广场与庭院不能被虚构密集小屋填满。人视角使用约1.75米成年人的尺度，不通过夸大建筑超过已知尺度制造宏伟。\n\n## 文献获取限制\nOIC21完整PDF取得并核对，总平面图5与相关正文实际阅读。OIP68的旧下载路径404；新官方PDF约259MB，在两次240秒截止内未完整取得，本次仅作出版目录，不宣称完整阅读该书。采用已读取的原始报告与后续图文综合，正式文件不附不完整PDF。\n\n## English guide\nThe snapshot is approximately 430 BCE. The reconstruction covers the monumental terrace and its principal completed palace groups, with eastern hillside context. It is not a reconstruction of the entire city or a census of its people. The shared mesh fixes the broad plan and column grids; reconstructed roofs, wall heights, colours, subsidiary rooms and terrain remain hypotheses. Modern restorations and later royal tombs are excluded. Human activity illustrates scale rather than documenting a particular historical festival.\n'''
(O/'00_Research/RESEARCH_REPORT.md').write_text(report)
files=list((O/'00_Research').glob('*'))+list((O/'01_Maps_Plans').glob('*'))
freeze={'stage':'collection','status':'PASS_WITH_DECLARED_LIMITATIONS','primary_plan_actual_pixels_inspected':True,'source_count':len(sources),'claims':len(claims),'inputs':{'OIC21_pdf_sha256':sha(R/'sources/OIC21.pdf'),'Iranica_html_sha256':sha(R/'sources/Iranica_Persepolis.html'),'UNESCO_html_sha256':sha(R/'sources/UNESCO_Persepolis.html')},'outputs':[{'path':str(p.relative_to(O)),'sha256':sha(p)} for p in files],'OIP68_fulltext':'NOT_ACQUIRED','thread_decision':'CONTINUE; same bounded site objective, frozen evidence now supports model construction','review_scope':'primary agent, not independent archaeological certification'}
(O/'06_Quality_Assurance/COLLECTION_FREEZE.json').write_text(json.dumps(freeze,ensure_ascii=False,indent=2))
assert all(sha(O/r['path'])==r['sha256'] for r in freeze['outputs']);print('Collection frozen/readback:',len(files),'files;',len(sources),'sources;',len(claims),'claims')
