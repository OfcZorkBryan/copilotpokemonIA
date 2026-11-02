'use strict';
const fs=require('fs'),vm=require('vm'),assert=require('assert');
const code=fs.readFileSync(__dirname+'/../index.html','utf8').match(/<script>([\s\S]*?)<\/script>/)[1];
function context(){
  const elements={},storage={};
  const ctx={document:{getElementById:id=>elements[id]||(elements[id]={innerHTML:''}),
    querySelectorAll:()=>[],addEventListener:()=>{},visibilityState:'visible'},
    localStorage:{getItem:k=>storage[k]||null,setItem:(k,v)=>{storage[k]=v}},window:{},
    location:{protocol:'file:'},console,structuredClone,setTimeout:()=>{},setInterval:()=>1,clearInterval:()=>{}};
  vm.createContext(ctx);vm.runInContext(code,ctx);return {ctx,elements,storage};
}
const near=context();
vm.runInContext(`DECKS.splice(0,DECKS.length,
  {id:'near',name:'Near',win:10,cards:[['Near',2,100,'Pack',.1]]},
  {id:'far',name:'Far',win:99,cards:[['Far',2,100,'Pack',.1]]});state.inventory={Near:1};`,near.ctx);
assert.strictEqual(vm.runInContext('ranked()[0].id',near.ctx),'near',
  'Fewer missing copies must take priority over an unverified win percentage');
const costs=context();
vm.runInContext(`DECKS.splice(0,DECKS.length,
  {id:'expensive',name:'Expensive',win:99,cards:[['X',1,500,'Pack',.1]]},
  {id:'cheap',name:'Cheap',win:10,cards:[['Y',1,35,'Pack',.1]]});state.inventory={};`,costs.ctx);
assert.strictEqual(vm.runInContext('ranked()[0].id',costs.ctx),'cheap');
const blocked=context();
vm.runInContext(`DECKS.splice(0,DECKS.length,
  {id:'promo',name:'Promo',win:99,cards:[['X',1,null,'Somente promo',0]]},
  {id:'available',name:'Available',win:10,cards:[['Y',1,500,'Pack',.1]]});state.inventory={};`,blocked.ctx);
assert.strictEqual(vm.runInContext('ranked()[0].id',blocked.ctx),'available');
const original=context();
assert.strictEqual(vm.runInContext('metaReference(DECKS[0]).matches',original.ctx),259);
assert(Math.abs(vm.runInContext('metaReference(DECKS[0]).winRate',original.ctx)-53.67)<.01);
assert.strictEqual(vm.runInContext('META_SNAPSHOT.queried_on',original.ctx),'2026-11-01');
assert(original.elements.main.innerHTML.includes('Referência do arquétipo'));
assert(!original.elements.main.innerHTML.includes('58,3%'));
assert(!original.elements.main.innerHTML.includes('Tier A'));
assert(vm.runInContext('DECKS.every(d=>d.cards.reduce((n,c)=>n+c[1],0)===20)',original.ctx));
const before=vm.runInContext('JSON.stringify(state)',original.ctx),saved=JSON.stringify(original.storage);
vm.runInContext('ranked();render()',original.ctx);
assert.strictEqual(vm.runInContext('JSON.stringify(state)',original.ctx),before);
assert.strictEqual(JSON.stringify(original.storage),saved);
console.log('Decks OK: collection/cost priority, promo constraints, sourced archetype snapshot, no state mutation');
