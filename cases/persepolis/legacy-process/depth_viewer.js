function draw(){
 queued=false;
 const rect=canvas.getBoundingClientRect(),W=canvas.width=Math.min(900,Math.round(rect.width)),H=canvas.height=Math.round(W*rect.height/rect.width);
 const pixels=ctx.createImageData(W,H),rgba=new Uint32Array(pixels.data.buffer),depth=new Float32Array(W*H);rgba.fill(0xffb7c6c0);depth.fill(Infinity);
 const forward=norm(sub(target,pos)),right=norm(cross(forward,[0,0,1])),up=cross(right,forward),scale=W*focal/36;
 function clip(vs){let a=[];for(let i=0;i<vs.length;i++){let p=vs[i],q=vs[(i+1)%vs.length],ip=p[2]>=.2,iq=q[2]>=.2;if(ip)a.push(p);if(ip!==iq){let t=(.2-p[2])/(q[2]-p[2]);a.push(p.map((v,j)=>v+(q[j]-v)*t))}}return a}
 for(const m of mesh.objects){
  const vv=m.vertices.map(v=>{let a=sub(v,pos);return[dot(a,right),dot(a,up),dot(a,forward)]});
  for(const face of m.faces){
   const poly=clip(face.map(i=>vv[i]));if(poly.length<3)continue;
   const wp=face.map(i=>m.vertices[i]),normal=norm(cross(sub(wp[1],wp[0]),sub(wp[2],wp[0]))),light=.68+.32*Math.abs(dot(normal,[.35,-.4,.847])),col=m.color.map(v=>Math.round(v*light)),packed=(255<<24)|(col[2]<<16)|(col[1]<<8)|col[0];
   for(let j=1;j<poly.length-1;j++){
    const ps=[poly[0],poly[j],poly[j+1]].map(v=>({x:W/2+scale*v[0]/v[2],y:H/2-scale*v[1]/v[2],iz:1/v[2]})),[a,b,c]=ps;
    const den=(b.y-c.y)*(a.x-c.x)+(c.x-b.x)*(a.y-c.y);if(Math.abs(den)<1e-8)continue;
    const x0=Math.max(0,Math.floor(Math.min(a.x,b.x,c.x))),x1=Math.min(W-1,Math.ceil(Math.max(a.x,b.x,c.x))),y0=Math.max(0,Math.floor(Math.min(a.y,b.y,c.y))),y1=Math.min(H-1,Math.ceil(Math.max(a.y,b.y,c.y)));if(x0>x1||y0>y1)continue;
    const ax=(b.y-c.y)/den,ay=(c.x-b.x)/den,bx=(c.y-a.y)/den,by=(a.x-c.x)/den;
    for(let y=y0;y<=y1;y++){
     let u=ax*(x0+.5-c.x)+ay*(y+.5-c.y),v=bx*(x0+.5-c.x)+by*(y+.5-c.y),k=y*W+x0;
     for(let x=x0;x<=x1;x++,k++,u+=ax,v+=bx){const w=1-u-v;if(u<0||v<0||w<0)continue;const z=1/(u*a.iz+v*b.iz+w*c.iz);if(z<depth[k]){depth[k]=z;rgba[k]=packed}}
    }
   }
  }
 }
 ctx.putImageData(pixels,0,0);ctx.fillStyle='#203327';ctx.font='14px sans-serif';ctx.fillText(mesh===D.mesh?'高台参考网格 · 屋顶与上部含推定':'区域参考网格 · 外围建筑/密度为推定',15,26)
}
