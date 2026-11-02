'use strict';
const fs=require('fs'),vm=require('vm'),assert=require('assert');
const raw=fs.readFileSync(__dirname+'/../index.html','utf8');
const code=raw.match(/<script>([\s\S]*?)<\/script>/)[1];
const elements={main:{innerHTML:''}};
const storage={};
const ctx={
  document:{getElementById:id=>elements[id]||(elements[id]={innerHTML:'',value:'',checked:false}),
    querySelectorAll:()=>[],addEventListener:()=>{},visibilityState:'visible'},
  localStorage:{getItem:k=>storage[k]||null,setItem:(k,v)=>{storage[k]=v}},
  window:{scrollTo:()=>{}},navigator:{},location:{protocol:'file:'},
  console,structuredClone,Date,Math,Number,JSON,Array,Object,String,Intl,
  URL:{createObjectURL:()=>'',revokeObjectURL:()=>{}},setTimeout:()=>{},setInterval:()=>1,clearInterval:()=>{}
};
vm.createContext(ctx);
vm.runInContext(code,ctx);
assert(elements.main.innerHTML.includes('Próximo passo sugerido'));
vm.runInContext("tab='decks';render();",ctx);
assert(elements.main.innerHTML.includes('Cartas desta lista'));
vm.runInContext("state.inventory['Eevee']=2;save();render();",ctx);
assert(elements.main.innerHTML.includes('2/2'));
vm.runInContext("tab='android';render();",ctx);
assert(elements.main.innerHTML.includes('importar captura PNG'));
vm.runInContext("bridge.ocr={available:true,text:'Ampulhetas: 120',language:'por'};bridge.capture={file:'captura-20261102T123456-abcdef.png',size:12};bridge.online=true;render();",ctx);
assert(elements.main.innerHTML.includes('Ampulhetas: 120'));
vm.runInContext("tab='settings';render();",ctx);
assert(elements.main.innerHTML.includes('Saldos informados manualmente'));
console.log('JS smoke OK: dashboard, decks, inventory saved, visual reader and resources');

vm.runInContext(`tab='android';state.resources.hourglasses=120;state.resources.reserve=24;save();
  bridge.ocr={available:true,text:'Recursos',recognition:{screen:'resources',evidence:['Recursos'],
  warnings:['Confira <img src=x onerror=alert(1)>'],requires_review:true,
  candidates:{resources:{hourglasses:999},cards:[{name:'<script>bad</script>',quantity:2}],
  missions:[{text:'Abrir pacotes',current:1,target:2}]}}};`,ctx);
const stateBefore=vm.runInContext('JSON.stringify(state)',ctx), storageBefore=JSON.stringify(storage);
vm.runInContext('render()',ctx);
assert(elements.main.innerHTML.includes('Reconhecimento V3'));
assert(elements.main.innerHTML.includes('999'));
assert(elements.main.innerHTML.includes('Revisão obrigatória'));
assert(elements.main.innerHTML.includes('&lt;script&gt;bad&lt;/script&gt;'));
assert(!elements.main.innerHTML.includes('<img src=x onerror='));
assert.strictEqual(vm.runInContext('JSON.stringify(state)',ctx),stateBefore);
assert.strictEqual(JSON.stringify(storage),storageBefore);
vm.runInContext("bridge.ocr.recognition.screen='unknown';render()",ctx);
assert(elements.main.innerHTML.includes('Tela desconhecida'));
console.log('V3 UI OK: candidates escaped; reserve, resources, inventory and saved backup state unchanged');
