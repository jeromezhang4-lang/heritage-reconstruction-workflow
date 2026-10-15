"""Portable Persepolis recipe; approximate coordinates, not a new archaeological survey."""
import math
from heritage_workflow.geometry import Model

def create():
    M=Model();components=[]
    # Approximate manual digitisation of the inspected plan, not survey coordinates.
    # Local x/y follow the building axes, rotated approximately 15 degrees from true east/north.
    def xy(px,py):
     dx,dy=px-484,py-415;a=math.radians(15)
     return round((dx*math.cos(a)-dy*math.sin(a))*.57,1),round((-dx*math.sin(a)-dy*math.cos(a))*.57,1)
    def meta(id,px,py,size,source,tiers):
     x,y=xy(px,py);components.append({'id':id,'plan_pixel_center':[px,py],'local_center_m':[x,y],'dimensions_m':size,'sources':source,'reconstruction_tiers':tiers,'position_precision':'approximate manual plan digitisation; not survey'})
     return x,y
    stone=(164,162,150);plaster=(205,188,151);roof=(165,143,107);column=(183,178,156);tags=['all']
    def box(id,c,s,color=plaster):M.box(id,c,s,color)
    def col(id,x,y,z,h,r=.72):
     M.box(id+'_base',(x,y,z+.25),(2.25,2.25,.5),stone)
     M.cylinder(id+'_shaft',(x,y,z+.5),r,h-1.7,column,n=12,top_radius=r*.76)
     M.box(id+'_abacus',(x,y,z+h-1.1),(1.55,1.6,.55),stone)
     M.box(id+'_capital',(x,y,z+h-.45),(2.65,1.25,.9),stone)
    def hall(id,x,y,z,w,d,nx,ny,h,wall=True,portico=None):
     box(id+'_podium',(x,y,z-.35),(w+5,d+5,.7),stone)
     if wall:
      # Segmented walls leave real apertures rather than sealing every hall.
      for sy in [-1,1]:
       for sx in [-1,1]:box(id+f'_wall_y_{sy}_{sx}',(x+sx*(w/4+2),y+sy*d/2,z+h/2),(w/2-4,2,h),plaster)
      for sx in [-1,1]:
       for sy in [-1,1]:box(id+f'_wall_x_{sx}_{sy}',(x+sx*w/2,y+sy*(d/4+2),z+h/2),(2,d/2-4,h),plaster)
     for i in range(nx):
      for j in range(ny):col(id+f'_col_{i+1:02}_{j+1:02}',x+(i-(nx-1)/2)*(w-9)/max(nx-1,1),y+(j-(ny-1)/2)*(d-9)/max(ny-1,1),z,h)
     box(id+'_roof',(x,y,z+h+.45),(w+3,d+3,.9),roof)
     for i in range(nx):box(id+f'_beam_{i}',(x+(i-(nx-1)/2)*(w-9)/max(nx-1,1),y,z+h-.35),(.55,d,.55),(106,82,58))
    def portico(id,x,y,z,w,d,nx,ny,h):hall(id,x,y,z,w,d,nx,ny,h,wall=False)
    def rooms(id,x,y,z,w,d,h,nx,ny):
     # Block plan only for subsidiary rooms; not a fictional room-by-room survey.
     box(id+'_roof',(x,y,z+h),(w,d,.8),roof)
     for i in range(nx+1):box(id+f'_partition_x{i}',(x-w/2+i*w/nx,y,z+h/2),(1.3,d,h),plaster)
     for j in range(ny+1):box(id+f'_partition_y{j}',(x,y-d/2+j*d/ny,z+h/2),(w,1.3,h),plaster)
    M.ground('Marvdasht_plain',(-720,-620,530,670),color=(160,146,114),n=7)
    # Eastern mountain mass is contextual C-tier terrain: no DEM was acquired.
    M.ground('Eastern_Royal_Hill',(90,-390,570,380),fn=lambda x,y:max(0,(x-95)*.46)*(0.7+.3*math.cos(y/140)),color=(139,123,91),n=15)
    boundarypx=[(37,95),(215,58),(239,99),(293,91),(307,126),(535,48),(563,48),(574,125),(629,313),(710,662),(675,725),(389,785),(320,755),(264,716),(211,682),(159,511),(102,340),(92,298),(69,211)]
    boundary=[xy(*p) for p in boundarypx]
    v=[[x,y,z] for z in [0,12] for x,y in boundary];n=len(boundary)
    faces=[list(range(n,2*n))]+[[i,(i+1)%n,(i+1)%n+n,i+n] for i in range(n)]
    M.mesh('Complete_terrace_approximate_outline',v,faces,stone)
    for k,(p,q) in enumerate(zip(boundary,boundary[1:]+boundary[:1])):
     # Retaining walls are part of the platform; low stepped parapet abbreviated.
     length=math.hypot(q[0]-p[0], q[1]-p[1]);count=max(1,int(length/8))
     for j in range(count):
      t=(j+.5)/count;x=p[0]*(1-t)+q[0]*t;y=p[1]*(1-t)+q[1]*t
      box(f'Terrace_parapet_{k}_{j}',(x,y,12.6),(2.0,2.0,1.2),stone)
    # Main public structures.
    x,y=meta('Gate_of_All_Lands',155,245,[24.7,24.7,16.5],['S02','S03'],{'footprint_columns':'A/B','height':'B','roof':'C'})
    gate=(x,y);hall('Gate',x,y,12,24.7,24.7,2,2,16.5)
    for sx in [-1,1]:
     for sy in [-1,1]:box(f'Gate_portal_{sx}_{sy}',(x+sx*12.7,y+sy*4,20),(3.4,3.6,16),stone)
    # Western stair: abbreviated double reversed geometry, 111 shallow steps in four runs.
    stairx=x-57;stairy=y
    for sy in [-1,1]:
     for i in range(63):box(f'GrandStair_lower_{sy}_{i}',(stairx-8,stairy+sy*(4+i*.38),(.108*(i+1))/2),(6.7,.41,.108*(i+1)),stone)
     box(f'GrandStair_turn_landing_{sy}',(stairx-4,stairy+sy*29,6.8/2),(15,4,6.8),stone)
     for i in range(48):box(f'GrandStair_upper_{sy}_{i}',(stairx,stairy+sy*(28-i*.38),(6.8+.10833*(i+1))/2),(6.7,.41,6.8+.10833*(i+1)),stone)
    box('GrandStair_top_landing',(stairx+13,stairy,11.6),(29,26,.8),stone)
    x,y=meta('Apadana',246,434,[60,60,19.5],['S02','S03'],{'main_hall_and_36_columns':'A','plan_registration':'B','roof_towers':'C'})
    apadana=(x,y);box('Apadana_raised_platform',(x,y,13.5),(104,104,3),stone)
    hall('Apadana',x,y,15,60,60,6,6,19.5)
    portico('Apadana_N_portico',x,y+42,15,60,18,6,2,19.5)
    portico('Apadana_W_portico',x-42,y,15,18,60,2,6,19.5)
    portico('Apadana_E_portico',x+42,y,15,18,60,2,6,19.5)
    for sx in [-1,1]:
     for sy in [-1,1]:rooms(f'Apadana_corner_{sx}_{sy}',x+sx*43,y+sy*43,15,17,17,21,2,2)
    rooms('Apadana_S_service',x,y-43,15,60,17,8,7,1)
    for i in range(20):
     for label,c in [('north',(x,y+55-i*.3)),('east',(x+55-i*.3,y))]:
      size=(82,.35,.15*(i+1)) if label=='north' else(.35,82,.15*(i+1))
      box('Apadana_stairs_'+label+str(i),(c[0],c[1],12+size[2]/2),size,stone)
    x,y=meta('Hundred_Column_Hall',484,415,[68.5,68.5,14],['S02','S03'],{'100_column_grid':'A','height':'B','roof':'C'})
    hundred=(x,y);hall('Hundred',x,y,12,68.5,68.5,10,10,14)
    portico('Hundred_N_portico',x,y+46,12,68.5,19,8,2,14)
    # Residential cluster south of Apadana, distinct podiums and heights.
    x,y=meta('Tachara_Darius',256,560,[30,40,8],['S02','S03'],{'footprint':'A/B','wood_columns':'B','height_roof':'C'})
    tachara=(x,y);box('Tachara_platform',(x,y,15.1),(40,49,6.2),stone);hall('Tachara',x,y,18.2,25,25,3,4,8);portico('Tachara_S',x,y-19,18.2,25,10,4,2,8)
    x,y=meta('Tripylon',339,491,[15.46,15.46,9],['S02','S03'],{'four_columns':'A','roof_height':'C'})
    tripylon=(x,y);hall('Tripylon',x,y,14.6,15.46,15.46,2,2,9);portico('Tripylon_N',x,y+13,14.6,15.46,7,2,1,9)
    x,y=meta('Hadish_Xerxes',351,682,[55,40,9],['S02','S03'],{'36_column_hall':'A/B','height_roof':'C'})
    hadish=(x,y);box('Hadish_platform',(x,y,15),(65,50,6),stone);hall('Hadish',x,y,18,34,34,6,6,9);portico('Hadish_N',x,y+25,18,34,12,6,2,9)
    rooms('Hadish_W_apartments',x-26,y,18,14,34,8,1,3);rooms('Hadish_E_apartments',x+26,y,18,14,34,8,1,3)
    x,y=meta('Palace_H_early_core',256,710,[34,30,7],['S02','S03'],{'early_phase':'B/C','lost_upper_structure':'C'})
    hall('Palace_H',x,y,18,26,22,3,3,7)
    # Label D on the plan is Hadish; label G is not copied as a late monumental palace.
    # Harem is a modern conventional name; function is not asserted.
    x,y=meta('Southern_residential_range',438,721,[112,25,7],['S02','S03'],{'outline':'B','partition_and_function':'C'})
    rooms('Southern_range',x,y,12,112,25,7,12,2)
    nx,ny=xy(457,610);rooms('Southern_NorthSouth_wing',nx,ny,12,23,115,7,2,11)
    x,y=meta('Treasury',608,580,[110,145,7],['S01','S02','S03'],{'major_blocks':'A/B','rooms_roofs':'C'})
    treasury=(x,y)
    rooms('Treasury_N_hall',x,y+55,12,99,27,8,10,3)
    rooms('Treasury_W_hall',x-27,y+12,12,44,42,8,5,5)
    rooms('Treasury_E_rooms',x+32,y+16,12,40,53,7,4,4)
    rooms('Treasury_S_hall',x+10,y-42,12,50,35,8,6,4)
    rooms('Treasury_S_service',x-35,y-42,12,34,43,7,3,5)
    M.wall('Treasury_outer_wall',[(x-57,y-72,12),(x+57,y-72,12),(x+57,y+73,12),(x-57,y+73,12),(x-57,y-72,12)],2,8,plaster)
    # Courtyard stays open. Eastern service band follows an excavated band, coarse block forms.
    ex,ey=xy(582,330);rooms('Eastern_service_band',ex,ey,12,22,100,7,2,9)
    sx,sy=xy(406,570);rooms('Central_service_range',sx,sy,12,27,51,7,2,5)
    # Fortification context has schematic inferred heights; no later cliff tombs.
    M.wall('Eastern_fortification',[(80,185,12),(118,85,25),(140,-40,32),(135,-140,24),(110,-245,12)],4,7,plaster)
    # Human figures are scale tokens only, not a population estimate.
    for i,(x,y) in enumerate([(-100,90),(-110,92),(-92,94),(-35,82),(-30,90),(-60,115),(-156,144),(-160,140),(10,65),(-131,-70)]):
     M.cylinder(f'Scale_person_{i}',(x,y,12),.25,1.5,(113,72,53),n=6);M.cylinder(f'Scale_head_{i}',(x,y,13.5),.17,.25,(142,111,78),n=6)
    views=[
     ('PP01','完整宫殿群 · 西北鸟瞰','Complete terrace from the northwest',[-480,440,390],[-40,-25,16],26,'overall'),
     ('PP02','完整宫殿群 · 西南鸟瞰','Complete terrace from the southwest',[-465,-485,345],[-35,-10,16],30,'overall'),
     ('PP03','登上帝国高台','Ascending the monumental terrace',[gate[0]-105,gate[1]+58,1.75],[gate[0]-38,gate[1],15],24,'entrance'),
     ('PP04','万国门的巨型门廊','The monumental Gate of All Lands',[gate[0]-40,gate[1]-12,13.75],[gate[0]+8,gate[1]+1,25],24,'entrance'),
     ('PP05','阿帕达纳与朝见庭院','Apadana and its audience court',[apadana[0]+20,apadana[1]+108,13.75],[apadana[0],apadana[1],26],24,'hall'),
     ('PP06','阿帕达纳 · 柱林内部','Inside the Apadana',[apadana[0]-23,apadana[1]-19,16.75],[apadana[0]+20,apadana[1]+24,25],21,'interior'),
     ('PP07','百柱厅与北侧门廊','Hundred Column Hall and north portico',[48,118,13.75],[0,10,23],24,'hall'),
     ('PP08','百柱厅 · 深处的秩序','Within the Hundred Column Hall',[-28,-28,13.75],[25,25,19],21,'interior'),
     ('PP09','王宫台基与私庭','Royal palaces and raised courts',[tachara[0]-65,tachara[1]-100,49],[tachara[0]+18,tachara[1]-22,23],30,'palaces'),
     ('PP10','东侧山坡回望宫殿群','The terrace seen from the eastern hillside',[365,30,230],[-50,-10,19],26,'overall')]
    cameras=[]
    for id,zh,en,pos,target,focal,kind in views:cameras.append({'id':id,'title_zh':zh,'title_en':en,'position_m':pos,'look_at_m':target,'focal_mm':focal,'tags':['all'],'kind':kind,'camera_reconstruction_tier':'D','coordinate_frame':'local building axes, metre units; not georeferenced'})
    return M, components, cameras
