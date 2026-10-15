from pathlib import Path
import json,hashlib,shutil,ast
R=Path(__file__).resolve().parent;O=R.parents[1]/'outputs/Persepolis'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
manifest=json.loads((O/'04_Images/IMAGE_MANIFEST.json').read_text());assert len(manifest)==11
for m in manifest:assert sha(O/m['final_file'])==m['final_sha256'] and sha(O/m['native_file'])==m['native_sha256']
observations=[
 ('PP01','完整高台边界、主要柱厅与南部屋顶群可见；已去除独立兽像、外挡墙人物带，并修正双折返入口','台阶转折/步数、各门廊可见柱数和装饰不能作精确测量'),
 ('PP02','重生成后的西南视角与PP01不同；南部宫殿/库房近处，公共柱厅与入口远处','生成材质与边缘细部并非逐像素同构'),
 ('PP03','低人视角、高台挡墙、配对阶梯与高大门廊，人物提供尺度','个别台阶与转台简化；111级不是图像逐级验证结论'),
 ('PP04','西侧门洞前守护兽已由人头修改为牛头；保留有顶四柱厅的可见部分','完整原始门框雕刻、四柱同时可见与铭文均未认证'),
 ('PP05','阿帕达纳北门廊已针对柱序/间距修改；完整木顶、台基与人物比例清晰','六轴模型已核对；照片遮挡与可见柱序尚未独立精确验证'),
 ('PP06','阿帕达纳内部高柱、木梁、完整屋顶、门洞日光与小比例人物','36柱总数不能凭一个透视图确认；彩绘与木顶细部C'),
 ('PP07','百柱厅北门廊更低，宽大前庭、后墙门户和柱列相连','北廊8×2柱网为模型事实；图像可见柱数、兽雕范围未逐构件认证'),
 ('PP08','百柱厅密集柱阵、完整梁顶、长距离视线与小比例守卫/来宾','主厅100柱由模型确认，图像不保证全部柱数/位置精确吻合'),
 ('PP09','南部王宫多台基、门廊、内院与大型公共柱厅背景，统一材料','木/石柱细节、后期阶段过滤与失去的上部方案含推定'),
 ('PP10','东侧回望：库房靠近视点、百柱厅与阿帕达纳层次、入口更远','地形与外围平原非实测；微观门洞和屋顶差异C'),
 ('PP11','多公里区域中可辨认高台、台下建筑、低矮聚落、田园河流与远侧王陵背景','全景是主要区域解释；每座住宅、密度、活动与430BCE同期状态未知，远处王陵细部不作墓数/断代证明')]
q={'status':'PASS_WITH_DECLARED_LIMITATIONS','reviewer':'Primary agent visual inspection, not an independent archaeologist','actual_generated_views':11,'built_in_generation_calls':16,'native_pngs_preserved':len(list((O/'04_Images/Native').glob('*.png'))),'criteria':{'actual_assets_and_size_readback':'PASS','complete_terrace_in_two_distinct_aerials':'PASS','principal_activity_region_panorama':'PASS_AS_INTERPRETIVE_CONTEXT','monumental_human_scale':'PASS','functioning_intact_main_palaces':'PASS','no_obvious_modern_equipment':'PASS','reference_mesh_column_grids':'PASS','strict_photographic_column_counts':'UNVERIFIED','strict_camera_and_pixel_geometry_fit':'UNVERIFIED','independent_original_archaeological_accuracy':'UNVERIFIED','all_activity_areas_exhaustively_known':'NOT_CLAIMED','whole_city_population_and_occupancy':'NOT_CLAIMED','native4K':'NO_UPSCALED'},'per_image':[{'id':id,'observed':obs,'limitation':lim,'final_sha256':next(m['final_sha256'] for m in manifest if m['id']==id)} for id,obs,lim in observations],'core_obj_sha256':sha(O/'02_Model/Persepolis_430BCE_v1.obj'),'regional_obj_sha256':sha(O/'02_Model/Persepolis_Regional_Context.obj'),'version_note':'PP01 first-generation core1881objects then targeted stairs repair; final core1883objects. Main palace masses/column grids unchanged; inputOBJ/frame and repair prompts preserved.'}
(O/'06_Quality_Assurance/IMAGE_VISUAL_QA.json').write_text(json.dumps(q,ensure_ascii=False,indent=2))
original=json.loads((O/'06_Quality_Assurance/COLLECTION_FREEZE.json').read_text());archive=O/'06_Quality_Assurance/COLLECTION_ORIGINAL';readback=[]
tree=ast.parse((R/'prepare_research.py').read_text());rights=next(n.args[0].value for n in ast.walk(tree) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=='write_text' and n.args and isinstance(n.args[0],ast.Constant) and isinstance(n.args[0].value,str) and n.args[0].value.startswith('# 使用的平面与范围'))
for r in original['outputs']:
 p=archive/r['path'];p.parent.mkdir(parents=True,exist_ok=True)
 if r['path']=='00_Research/sources.json':p.write_text(json.dumps(json.loads((O/r['path']).read_text())[:7],ensure_ascii=False,indent=2))
 elif r['path']=='01_Maps_Plans/SOURCE_AND_RIGHTS.md':p.write_text(rights)
 else:shutil.copy2(O/r['path'],p)
 assert sha(p)==r['sha256'],r['path'];readback.append({'archived_path':str(p.relative_to(O)),'sha256':sha(p),'original_sha256_match':True})
(O/'06_Quality_Assurance/COLLECTION_ORIGINAL_ARCHIVE.json').write_text(json.dumps({'status':'PASS','reason':'urban addendum superseded source-index/rights paths; original frozen versions preserved and verified here','files':readback},indent=2))
for r in json.loads((O/'06_Quality_Assurance/MODEL_FREEZE.json').read_text())['outputs']:assert sha(O/r['path'])==r['sha256'],r['path']
for r in json.loads((O/'06_Quality_Assurance/URBAN_ADDENDUM_FREEZE.json').read_text())['outputs']:assert sha(O/r['path'])==r['sha256'],r['path']
report='''# 波斯波利斯复原交付\n\n## 实际完成\n11幅实际内置ImageGen生成图，16次生成/定向修改调用。全部最终PNG3840×2160，原生1672×941；使用FSRCNN×3学习型超分、极少量16:9裁切及面积缩减，不是原生4K。原生最终与弃用版本均保留，提示词/实际输入/逐图SHA可追踪。\n\n三张宫殿群总览、入口与宫门、两座柱厅的外部与内部、王宫内院，以及一张主要活动区域全景。浏览顺序先PP11区域，再进入PP01–10宫殿细部。\n\n真实核心参考网格1883对象；区域层2530对象，沿用同一高台体量。OBJ、组件、摄像机、结构/深度/边缘图与ARMS已导出。主要柱网在真实模型中逐项核对；AI图像的细部柱数、几何和摄像机逐像素吻合仍UNVERIFIED。\n\n9项来源、20条主体证据约束、区域补充、实际读过的原始/区域图、文明与遗址史、11份双语逐图导览。来源级别和复原级别分别记录。\n\n## 区域全景的含义\n高台只是更广景观中的王室核心。PP11包含目前研究辨认出的主要分区及农田/王陵地理背景，不宣称已经确认所有活动区域、每栋住宅或完整同期人口。住宅密度与上部、田园、地形、人物和Firuzi的430BCE使用情况存在推定。远处王陵细部不得用于确认当时墓数或具体外观。\n\n## 图像与模型的限制\n主体布局参考发掘平面，人工近似注册，不是高精度测绘/DEM。完整木屋顶、墙高、彩绘、附属房间及PalaceH早期阶段尚不确定。装饰和服饰不是原物逐件摹本。内置工具未公开provider模型/seed，未取得独立考古专家认证，不报告“考古准确率百分比”。\n\n## 文件与验收\n独立HTML内嵌4K分享JPEG、文字、来源和实际模型，可用过滤、放大、键盘切换、模型查看与下载。完整包保留4K PNG和原生图。外部来源链接需要网络。浏览器验收、ZIP CRC/逐成员SHA和最终SHA记录独立放置，本文不嵌入自身HTML/ZIP哈希，避免自引用失效。最终结论以SINGLE_FILE_QA.json、ZIP_VERIFICATION.json与DELIVERY_MANIFEST.json的同对象回读为准。\n\n## English\nEleven actual generated views present the royal terrace and a wider regional context. Final3840x2160PNG files are learned upscales from1672x941 originals, not native4K. The real mesh fixes broad layout and column grids; rendered photographs do not certify every visible column or decorative detail. Regional houses, density and synchronous occupation remain hypotheses. Source plans, native images, prompts, models and evidence boundaries are preserved.\n'''
(O/'FINAL_REPORT.md').write_text(report)
(O/'README.md').write_text('# 波斯波利斯 · 11景复原\n\n打开同包的Persepolis_Single_File.html即可离线浏览。4K PNG与原生图在04_Images，逐图双语导览在05_Metadata，证据与原始图在00_Research/01_Maps_Plans，实际网格与摄像机在02_Model。模型脚本是原执行记录，路径指向本任务布局；OBJ不依赖脚本即可查看。\n\n主体约430BCE，区域全景含明确标注的跨期/密度未知。图像生成使用内置image_gen；完整提示词在04_Images/Native。PNG为学习型超分至4K，分享JPEG有损。全部限制与验收见FINAL_REPORT及06_Quality_Assurance。\n')
(O/'06_Quality_Assurance/MODEL_VERSION_NOTE.md').write_text('PP01使用初版1881对象网格开始生成，入口连接后来修订为1883对象；初版OBJ与输入结构图保留在本目录。主宫殿体量、柱网及摄像机未随入口修订改变。PP02–10使用最后冻结的核心结构参考；PP11使用包含同一核心的区域模型。生成图只核查宏观布局，细部柱数、台阶和严格像素符合性未认证。\n')
print('Image review/actual files PASS with declared limits; current model/addendum readbacks PASS; original collection archive SHA PASS')
