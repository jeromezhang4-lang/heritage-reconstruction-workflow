from pathlib import Path
import sys, json, hashlib, time, signal
import numpy as np
from PIL import Image

WORK=Path(__file__).resolve().parent
sys.path.insert(0,str(WORK/'vendor'))
import cv2
cv2.setNumThreads(2)
MODEL=WORK/'sr_models'/'FSRCNN_x3.pb'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def upscale(source,dest):
    source,dest=Path(source),Path(dest)
    started=time.time()
    with Image.open(source) as im:
        im.load();rgb=np.array(im.convert('RGB'));native=im.size
    sr=cv2.dnn_superres.DnnSuperResImpl_create();sr.readModel(str(MODEL));sr.setModel('fsrcnn',3)
    bgr=cv2.cvtColor(rgb,cv2.COLOR_RGB2BGR)
    # CPU inference, one image at a time. The neural network predicts luminance detail.
    out=sr.upsample(bgr)
    h,w=out.shape[:2];unit=min(w//16,h//9);nw,nh=unit*16,unit*9
    x,y=(w-nw)//2,(h-nh)//2
    removed=(w-nw)+(h-nh)
    if removed>max(w,h)*0.01:
        raise ValueError('Aspect mismatch exceeds 1%: return to image generation, do not silently crop architecture.')
    if nw<2048 or nh<1152:raise ValueError('Learned 2x output still below minimum resolution.')
    cropped=out[y:y+nh,x:x+nw]
    final=cv2.resize(cropped,(3840,2160),interpolation=cv2.INTER_AREA)
    dest.parent.mkdir(parents=True,exist_ok=True)
    ok=cv2.imwrite(str(dest),final,[cv2.IMWRITE_PNG_COMPRESSION,6])
    if not ok:raise RuntimeError('PNG write failed')
    with Image.open(dest) as im:im.verify()
    result={'algorithm':'FSRCNN x3 pretrained TensorFlow graph via OpenCV dnn_superres, followed by area downsampling to 3840x2160',
        'model_source':'https://github.com/Saafke/FSRCNN_Tensorflow/blob/master/models/FSRCNN_x3.pb',
        'model_sha256':sha(MODEL),'opencv_version':cv2.__version__,'native_size':list(native),
        'network_output_size':[w,h],'exact_aspect_crop_size':[nw,nh],'final_size':[3840,2160],'downsample':'OpenCV INTER_AREA from learned 3x prediction','crop_pixels':{'left':x,'right':w-nw-x,'top':y,'bottom':h-nh-y},
        'source_sha256':sha(source),'output_sha256':sha(dest),'elapsed_seconds':round(time.time()-started,3),
        'native_4k':False,'note':'学习型3倍超分辨率后面积缩减到3840×2160；原生尺寸与裁切如实记录。最终文件为4K尺寸，不是原生4K，放大不增加考古证据。',
        'cpu_threads':2,'gpu_used':False}
    dest.with_suffix('.sr.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    return result

if __name__=='__main__':
    if len(sys.argv)!=3:raise SystemExit('Usage: superresolve.py native.png output.png')
    def timeout_handler(signum, frame):
        raise TimeoutError('Super-resolution exceeded the 180 second deadline')
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(180)
    try:
        print(json.dumps(upscale(sys.argv[1],sys.argv[2]),ensure_ascii=False))
    finally:
        signal.alarm(0)
