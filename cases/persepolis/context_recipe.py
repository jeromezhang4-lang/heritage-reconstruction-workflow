"""Regional interpretation; houses and terrain are hypotheses, not measured urban data."""
import math, random
from heritage_workflow.geometry import Model

def create_context(core):
    M=Model()
    for m in core['objects']:
     if m['id'] not in ['Marvdasht_plain','Eastern_Royal_Hill']:M.mesh(m['id'],m['vertices'],m['faces'],m['color'])
    a=math.radians(15)
    def loc(x,y):return (x*math.cos(a)+y*math.sin(a),-x*math.sin(a)+y*math.cos(a))
    def boxtrue(id,x,y,z,w,d,h,color):
     lx,ly=loc(x,y);M.box(id,(lx,ly,z+h/2),(w,d,h),color,rotation_deg=-15)
    M.ground('Regional_plain',(-5500,-2400,2900,8200),color=(152,157,112),n=9)
    M.ground('Kuh_Rahmat_context',(140,-1000,1600,6800),fn=lambda x,y:max(0,x-140)*(.24+.14*math.cos(y/650)),color=(137,120,91),n=20)
    M.ground('Naqsh_Rustam_cliff_context',(-2600,6100,-600,7600),fn=lambda x,y:max(0,y-6100)*.35,color=(144,128,96),n=12)
    regions=[{'id':'terrace','name':'宫殿高台','true_xy_m':[0,0],'tier':'A/B','detail':'约13公顷；沿用主模型'}, {'id':'royal_south','name':'台下南部大型建筑区','true_xy_m':[0,-500],'tier':'B/C','detail':'考古发现大型建筑群，示意上部与台下联系'}, {'id':'royal_north','name':'北侧官方建筑区','true_xy_m':[0,700],'tier':'B/C','detail':'约500m以北的探测复合建筑；模型近似位置'}, {'id':'west','name':'西侧居住与工匠活动区','true_xy_m':[-1250,350],'tier':'B/C/D','detail':'区域与沟渠网络有证据；住宅位置、数量和密度均推定'}, {'id':'firuzi','name':'菲鲁齐早期纪念性区','true_xy_m':[-3500,-550],'tier':'B/C','detail':'早期建筑分布区；430BCE具体使用状态未知'}, {'id':'necropolis','name':'北侧王陵地区','true_xy_m':[-1500,5800],'tier':'B/C','detail':'约6km北侧Naqsh-eRustam；只示意早期王陵，不画萨珊浮雕'}, {'id':'agriculture','name':'园地、果园与农田','true_xy_m':[-2000,2400],'tier':'B/C/D','detail':'开敞城市景观有研究依据；作物、分块与人物均推定'}]
    # Ten southern large-building proxies: count derives from sector description, not ten complete measured buildings.
    for i in range(10):
     x=(i%2-.5)*100;y=-300-(i//2)*85
     boxtrue(f'Context_south_hall_{i}',x,y,0,54,42,8,(196,178,141));boxtrue(f'Context_south_roof_{i}',x,y,8,58,46,.8,(161,140,102))
    boxtrue('Context_north_complex',0,700,0,92,94,7,(194,179,142))
    # Named urban sectors are evidence-based; every individual residential footprint below is a D-tier illustration.
    rng=random.Random(430)
    for cluster in range(16):
     cx=-1000-(cluster%4)*180;cy=-50+(cluster//4)*190
     for j in range(rng.randint(8,15)):
      x=cx+rng.uniform(-55,55);y=cy+rng.uniform(-55,55);w=rng.uniform(9,17);d=rng.uniform(8,15);h=rng.uniform(3.3,5.4)
      boxtrue(f'Context_west_house_{cluster}_{j}',x,y,0,w,d,h,(185,162,122));boxtrue(f'Context_west_roof_{cluster}_{j}',x,y,h,w+1,d+1,.45,(161,138,100))
    for i in range(12):
     x=-3500+(i%4-1.5)*240;y=-550+(i//4-1)*270
     boxtrue(f'Context_firuzi_early_volume_{i}',x,y,0,38,32,6,(177,155,114));boxtrue(f'Context_firuzi_early_roof_{i}',x,y,6,41,35,.5,(151,134,99))
    for row in range(9):
     for col in range(8):
      x=-4400+col*480;y=-900+row*700
      if -1800<x<-800 and -200<y<850:continue
      boxtrue(f'Context_field_{row}_{col}',x,y,0,360,510,.1,[(144,153,91),(172,163,103),(133,150,90),(152,159,107)][(row+col)%4])
      if (row+col)%3==0:
       for k in range(6):
        lx,ly=loc(x-140+k*50,y+170);M.cylinder(f'Context_orchard_{row}_{col}_{k}',(lx,ly,.2),7,9,(80,110,65),n=8)
    # A schematic road/drainage network; road alignments and individual parcels are not surveyed here.
    for x in [-250,-850,-1750,-2800,-3900]:
     pts=[(*loc(x,y),.2) for y in [-1500,1800,4900]];M.wall('Context_track_'+str(x),pts,7,.1,(168,151,109))
    river=[(*loc(x,y),.15) for x,y in [(-4900,800),(-3900,1700),(-3000,2600),(-2400,3600),(-1500,4700),(-650,5650)]];M.wall('Pulvar_river_schematic',river,24,.15,(93,127,134))
    # Only two unobtrusive early facade markers; NOT the later complete royal necropolis or Sasanian reliefs.
    for i in range(2):boxtrue(f'Context_early_tomb_marker_{i}',-1500+i*60,5850,80,12,1,12,(165,151,119))
    camera={'id':'PP11','title_zh':'主要活动区域 · 区域全景','title_en':'Regional panorama of the principal activity areas','position_m':[-7100,-6300,6800],'look_at_m':[-1000,2150,0],'focal_mm':36,'tags':['all'],'kind':'regional','camera_reconstruction_tier':'D','coordinate_frame':'same local building axes as core; approximate true-north rotation15deg','scope':'multi-kilometre Achaemenid settlement landscape, no claim of every known/unknown activity or synchronous430BCE occupancy'}
    return M, regions, camera
