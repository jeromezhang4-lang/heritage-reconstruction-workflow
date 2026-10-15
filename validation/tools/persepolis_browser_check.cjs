const fs=require('fs'),path=require('path'),crypto=require('crypto'),assert=require('assert');
const {chromium}=require(process.env.HERITAGE_PLAYWRIGHT_MODULE||'playwright');
const options=Object.fromEntries(Array.from({length:Math.floor((process.argv.length-2)/2)},(_,i)=>[process.argv[2+i*2],process.argv[3+i*2]]));
if(!options['--html']||!options['--case']||!options['--out']){console.error('Usage: node persepolis_browser_check.cjs --html gallery.html --case cases/persepolis --out browser-report');process.exit(2)}
const source=path.resolve(options['--html']),caseDir=path.resolve(options['--case']),output=path.resolve(options['--out']);
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
fs.mkdirSync(output,{recursive:true});
(async()=>{
 let browser,timer,closed=false;const checks={},errors=[],requests=[];
 const isolated=fs.mkdtempSync(path.join(output,'.browser-isolated-'));
 const file=path.join(isolated,'gallery.html');
 try{
  fs.copyFileSync(source,file);
  timer=setTimeout(()=>{errors.push('180-second deadline');if(browser)browser.close().catch(()=>{});process.exitCode=2},180000);
  browser=await chromium.launch({headless:true,timeout:30000,args:['--use-angle=swiftshader','--enable-unsafe-swiftshader']});
  const context=await browser.newContext({viewport:{width:1440,height:1000},acceptDownloads:true});await context.setOffline(true);
  const page=await context.newPage();page.setDefaultTimeout(15000);
  page.on('pageerror',e=>errors.push(e.message));page.on('request',r=>{if(!r.url().startsWith('file:')&&!r.url().startsWith('data:'))requests.push(r.url().split('?')[0])});
  await page.goto('file://'+file,{waitUntil:'load',timeout:60000});
  checks.cards=await page.locator('.card').count();assert.equal(checks.cards,11);
  await page.locator('.card img').evaluateAll(async ims=>{for(const im of ims){im.loading='eager';await im.decode()}});
  await page.screenshot({path:path.join(output,'desktop-results.png')});
  checks.modal_dimensions=[];
  for(let i=0;i<11;i++){
   await page.locator('.imagebutton').nth(i).click();await page.locator('#full').evaluate(im=>im.decode());
   const size=await page.locator('#full').evaluate(im=>[im.naturalWidth,im.naturalHeight]);assert.deepEqual(size,[3840,2160]);checks.modal_dimensions.push(size);
   if((await page.locator('#viewerTitle').textContent()).startsWith('PP04')){const warning=await page.locator('#description .issue').textContent();assert(warning.includes('原先“人头改牛头”')&&warning.includes('缺乏保留图像支持')&&!warning.includes('\\u'));checks.pp04_warning_readable=true;await page.locator('#description .issue').screenshot({path:path.join(output,'PP04-readable-warning.png')})}
   await page.keyboard.press('Escape');
  }
  await page.locator('.imagebutton').first().click();let title=await page.locator('#viewerTitle').textContent();await page.keyboard.press('ArrowRight');assert.notEqual(await page.locator('#viewerTitle').textContent(),title);checks.keyboard_switch=true;
  await page.locator('#zoom').click();assert(await page.locator('.imageViewport').evaluate(n=>n.classList.contains('zoomed')));checks.zoom=true;await page.locator('#zoom').click();
  const imageEvent=page.waitForEvent('download');await page.locator('#downloadImage').click();const imageDownload=await imageEvent;const downloadedImage=path.join(isolated,'download-image');await imageDownload.saveAs(downloadedImage);
  const imageMeta=JSON.parse(fs.readFileSync(path.join(caseDir,'recorded/04_Images/PP01.metadata.json')));
  assert.equal(sha(fs.readFileSync(downloadedImage)),imageMeta.sharing_derivative.sha256);checks.image_download_same_sha=true;await page.keyboard.press('Escape');
  checks.filters={};for(const k of ['regional','overall','entrance','hall','interior','palaces']){await page.locator('#filter').selectOption(k);const count=await page.locator('.card:visible').count();assert(count>0&&count<11);checks.filters[k]=count}await page.locator('#filter').selectOption('all');
  await page.locator('nav button[data-tab="process"]').click();checks.failures=await page.locator('.failure').count();checks.comparisons=await page.locator('.comparison').count();assert.equal(checks.failures,8);assert.equal(checks.comparisons,4);await page.screenshot({path:path.join(output,'desktop-process.png')});await page.locator('.comparison').first().screenshot({path:path.join(output,'comparison-PP01.png')});
  await page.locator('nav button[data-tab="evidence"]').click();checks.sources=await page.locator('.source').count();checks.claims=await page.locator('.claim').count();assert.equal(checks.sources,9);assert.equal(checks.claims,23);
  await page.locator('nav button[data-tab="model"]').click();await page.waitForFunction(()=>Number(document.querySelector('#modelCanvas').dataset.renderCount)>0);
  checks.depth_test=await page.locator('#modelCanvas').getAttribute('data-depth-test');assert.equal(checks.depth_test,'true');
  let before=await page.locator('#modelCanvas').evaluate(c=>c.toDataURL());await page.locator('#cameraSelect').selectOption('PP02');await page.waitForTimeout(100);let after=await page.locator('#modelCanvas').evaluate(c=>c.toDataURL());assert.notEqual(before,after);checks.camera_changes_model=true;
  await page.locator('#modelCanvas').screenshot({path:path.join(output,'desktop-model-core.png')});
  const box=await page.locator('#modelCanvas').boundingBox();before=after;await page.mouse.move(box.x+box.width*.5,box.y+box.height*.5);await page.mouse.down();await page.mouse.move(box.x+box.width*.62,box.y+box.height*.53,{steps:5});await page.mouse.up();await page.waitForTimeout(100);after=await page.locator('#modelCanvas').evaluate(c=>c.toDataURL());assert.notEqual(before,after);checks.drag_changes_model=true;
  const objEvent=page.waitForEvent('download');await page.locator('#downloadObj').click();const objDownload=await objEvent;const downloadedObj=path.join(isolated,'download.obj');await objDownload.saveAs(downloadedObj);assert.equal(sha(fs.readFileSync(downloadedObj)),'1124885e01038307b5195256a12cd2ed501b0fe05275cb5e40325eca1f3a6aaf');checks.obj_download_same_sha=true;
  await page.locator('#modelSelect').selectOption('context');await page.waitForTimeout(100);assert((await page.locator('#modelStatus').textContent()).includes('2530'));await page.locator('#modelCanvas').screenshot({path:path.join(output,'desktop-model-context.png')});
  let n=await page.locator('#modelCanvas').getAttribute('data-render-count');await page.waitForTimeout(400);assert.equal(await page.locator('#modelCanvas').getAttribute('data-render-count'),n);checks.no_idle_render_loop=true;
  await page.locator('nav button[data-tab="results"]').click();await page.setViewportSize({width:390,height:844});await page.waitForTimeout(100);assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));checks.mobile_no_overflow=true;await page.screenshot({path:path.join(output,'mobile-results.png')});
  await page.locator('nav button[data-tab="process"]').click();assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));checks.mobile_process_no_overflow=true;
  assert.equal(requests.length,0);assert.equal(errors.length,0);checks.status='PASS';
 }catch(e){errors.push(e.message);checks.status='FAIL';process.exitCode=1}
 finally{
  if(timer)clearTimeout(timer);
  if(browser){try{await browser.close();closed=true}catch(e){errors.push('browser close: '+e.message)}}
  fs.rmSync(isolated,{recursive:true,force:true});
  checks.offline=true;checks.only_html_in_isolated_directory=true;checks.external_requests=requests;checks.errors=errors;checks.owned_browser_closed=closed;checks.preview_server_started=false;checks.html_sha256=sha(fs.readFileSync(source));checks.node_pid=process.pid;checks.browser='Playwright bundled Chromium, no executablePath or system Chrome';
  fs.writeFileSync(path.join(output,'BROWSER_QA.json'),JSON.stringify(checks,null,2)+'\n');console.log(JSON.stringify(checks));
 }
})();
