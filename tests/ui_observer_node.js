'use strict';
const fs=require('fs'),vm=require('vm'),assert=require('assert');
const code=fs.readFileSync(__dirname+'/../index.html','utf8').match(/<script>([\s\S]*?)<\/script>/)[1];
function context(){
  const elements={},storage={},timers=[];
  const ctx={document:{getElementById:id=>elements[id]||(elements[id]={innerHTML:'',value:'',checked:false}),
    querySelectorAll:()=>[],addEventListener:()=>{},visibilityState:'visible'},
    localStorage:{getItem:k=>storage[k]||null,setItem:(k,v)=>{storage[k]=v}},
    window:{scrollTo:()=>{}},navigator:{},location:{protocol:'http:'},console,structuredClone,
    setTimeout:()=>{},setInterval:fn=>{timers.push(fn);return timers.length},clearInterval:()=>{},
    URL:{createObjectURL:()=>'',revokeObjectURL:()=>{}}};
  vm.createContext(ctx);vm.runInContext(code,ctx);
  vm.runInContext("tab='android';bridge.online=true;bridge.serial='fake-device';",ctx);
  return {ctx,elements,storage,timers};
}
async function tests(){
  const {ctx,elements,storage,timers}=context(),requests=[];
  ctx.bridgeApi=async(path,body)=>{
    requests.push({path,body});
    if(path==='/api/capture')return {capture:{file:'new.png',size:100}};
    if(path==='/api/ocr')return {available:true,text:'Missões\nAbrir pacotes 2/2',
      recognition:{screen:'missions',candidates:{resources:{},cards:[],missions:[]}},
      plan:{budget:{hourglasses:0,reserve:12,above_reserve:0,max_automatic_spend:0},warnings:[],
        recommendations:[{title:'Conferir <recompensa>',detail:'Sem resgate executado',source:'unconfirmed_observation'}]}};
    throw Error('Unexpected endpoint '+path);
  };
  const before=vm.runInContext('JSON.stringify(state)',ctx),saved=JSON.stringify(storage);
  vm.runInContext('toggleMonitor()',ctx);
  await timers[0]();
  assert.deepStrictEqual(requests.map(x=>x.path),['/api/capture','/api/ocr']);
  assert.strictEqual(requests[1].body.state.resources.reserve,12);
  assert(elements.main.innerHTML.includes('Sugestões automáticas'));
  assert(elements.main.innerHTML.includes('Conferir &lt;recompensa&gt;'));
  assert.strictEqual(vm.runInContext('JSON.stringify(state)',ctx),before);
  assert.strictEqual(JSON.stringify(storage),saved);
  vm.runInContext('state.resources.reserve=24;render()',ctx);
  assert(elements.main.innerHTML.includes('Registro alterado'));
  assert(!elements.main.innerHTML.includes('Conferir &lt;recompensa&gt;'));

  const failed=context(),failureCalls=[];
  failed.ctx.bridgeApi=async(path)=>{failureCalls.push(path);throw Error('Capture failed')};
  vm.runInContext("bridge.capture={file:'old.png'};toggleMonitor()",failed.ctx);
  await failed.timers[0]();
  assert.deepStrictEqual(failureCalls,['/api/capture']);
  assert(vm.runInContext('bridge.error',failed.ctx).includes('Capture failed'));

  const busy=context(),calls=[];
  busy.ctx.bridgeApi=async(path)=>{calls.push(path);return {capture:{file:'new.png'}}};
  vm.runInContext('toggleMonitor();bridge.busy=true;',busy.ctx);
  await busy.timers[0]();
  vm.runInContext("bridge.busy=false;document.visibilityState='hidden'",busy.ctx);
  await busy.timers[0]();
  vm.runInContext("document.visibilityState='visible';tab='settings'",busy.ctx);
  await busy.timers[0]();
  assert.deepStrictEqual(calls,[]);

  const overlap=context(),overlapCalls=[];let releaseCapture;
  overlap.ctx.bridgeApi=path=>{overlapCalls.push(path);return new Promise(resolve=>{releaseCapture=resolve})};
  vm.runInContext('toggleMonitor()',overlap.ctx);
  const firstTick=overlap.timers[0]();
  const stopButton=overlap.elements.main.innerHTML.match(/<button id="monitorToggle"[^>]*>/)[0];
  assert(!stopButton.includes('disabled'),'Stop must remain available while capture/OCR is busy');
  await overlap.timers[0]();
  vm.runInContext('toggleMonitor()',overlap.ctx); // Stop during pending capture.
  releaseCapture({capture:{file:'after-stop.png'}});
  await firstTick;
  assert.deepStrictEqual(overlapCalls,['/api/capture']);

  const stale=context();let releaseOCR;
  stale.ctx.bridgeApi=()=>new Promise(resolve=>{releaseOCR=resolve});
  vm.runInContext("bridge.capture={file:'original.png'}",stale.ctx);
  const analysis=vm.runInContext('analyzeImage()',stale.ctx);
  vm.runInContext("bridge.capture={file:'different.png'};bridge.ocr=null",stale.ctx);
  releaseOCR({available:true,text:'Wrong image',plan:{budget:{hourglasses:0,reserve:12},recommendations:[],warnings:[]},
    recognition:{screen:'resources',candidates:{resources:{},cards:[],missions:[]}}});
  await analysis;
  assert.strictEqual(vm.runInContext('bridge.ocr',stale.ctx),null);
  assert.strictEqual(vm.runInContext('bridge.plan',stale.ctx),null);

  const importing=context(),importCalls=[];
  importing.ctx.URL.createObjectURL=()=> 'blob:new-image';
  importing.ctx.FileReader=class {readAsDataURL(){this.result='data:image/png;base64,TEST';this.onload()}};
  importing.ctx.bridgeApi=async path=>{importCalls.push(path);throw Error('Import failed')};
  vm.runInContext("bridge.capture={file:'old.png'}",importing.ctx);
  await vm.runInContext("importPng({type:'image/png',size:100})",importing.ctx);
  assert.strictEqual(vm.runInContext('bridge.capture',importing.ctx),null);
  await vm.runInContext('analyzeImage()',importing.ctx);
  assert.deepStrictEqual(importCalls,['/api/import'],'Import failure must not analyze the old image');

  const readiness=context(),readinessCalls=[];
  readiness.ctx.bridgeApi=async path=>{
    readinessCalls.push(path);
    if(path==='/api/health')return {ok:true};
    if(path==='/api/captures')return {captures:[]};
    if(path==='/api/readiness')return {devices:[],capture_ready:false,ocr_ready:true,
      live_analysis_ready:false,game_validation:'pending',blockers:['Nenhum Android autorizado']};
    throw Error('Unexpected readiness endpoint '+path);
  };
  await vm.runInContext('refreshBridge()',readiness.ctx);
  assert.strictEqual(vm.runInContext('bridge.online',readiness.ctx),true);
  assert.strictEqual(vm.runInContext('bridge.readiness.live_analysis_ready',readiness.ctx),false);
  assert(readiness.elements.main.innerHTML.includes('Validação no jogo: pendente'));
  console.log('Observer OK: automatic capture/OCR/plan; no stale capture, no saved-state mutation, visibility and busy guards');
}
tests().catch(e=>{console.error(e);process.exitCode=1});
