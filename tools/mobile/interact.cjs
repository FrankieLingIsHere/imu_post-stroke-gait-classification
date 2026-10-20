// Reusable emulator interaction console and JSON scenario runner (no physical devices).
const fs=require('node:fs'),path=require('node:path'),{execFileSync}=require('node:child_process');
const root=path.resolve(__dirname,'../..'),serial='emulator-5560';
const args=process.argv.slice(2),arg=(key,fallback)=>{const i=args.indexOf(key);return i<0?fallback:args[i+1];};
const pkg=arg('--package','com.gaitsteps.app'),scenario=arg('--scenario',null);
const commands=scenario?JSON.parse(fs.readFileSync(scenario,'utf8')):[{action:args[0]||'source',label:arg('--label',''),value:arg('--value','')}];
if(!Array.isArray(commands))throw new Error('Scenario must be an array of actions.');
const out=path.join(root,'android/dist/emulator-lab/interactions',new Date().toISOString().replace(/[:.]/g,'-'));
const startedAt=Date.now();
fs.mkdirSync(out,{recursive:true});
const adb=path.join(root,'android/dist/native-distance-tools/android-sdk/platform-tools/adb.exe');
const device=(...values)=>execFileSync(adb,['-s',serial,...values],{encoding:'utf8',timeout:30000});
let session,installedApkSha256;const replies=[];
async function http(method,url,body){
 const r=await fetch('http://127.0.0.1:4725'+url,{method,headers:{'Content-Type':'application/json'},body:body===undefined?undefined:JSON.stringify(body),signal:AbortSignal.timeout(120000)});
 const j=await r.json();if(!r.ok||j.value?.error)throw new Error(JSON.stringify(j.value));return j.value;
}
const request=(m,u,b)=>http(m,'/session/'+session+u,b);
async function find(label){
 const accessible=await request('POST','/elements',{using:'accessibility id',value:label});
 if(accessible.length)return accessible[0]['element-6066-11e4-a52e-4f735466cecf'];
 // Android UIAutomator exact visible text lookup also works for editable fields.
 const result=await request('POST','/elements',{using:'-android uiautomator',value:`new UiSelector().text(${JSON.stringify(label)})`});
 if(!result.length)throw new Error('Element not found: '+label);
 return result[0]['element-6066-11e4-a52e-4f735466cecf'];
}
async function scrollContent(direction='down',percent=.7){
 if(!(percent>=.1&&percent<=1))throw new Error('Scroll percent must be 0.1 to 1.');
 const views=await request('POST','/elements',{using:'class name',value:'android.widget.ScrollView'});
 if(!views.length)throw new Error('No visible content scroll view.');
 const id=views[0]['element-6066-11e4-a52e-4f735466cecf'];
 const rect=await request('GET','/element/'+id+'/rect');
 await request('POST','/execute/sync',{script:'mobile: scrollGesture',args:[{left:rect.x+10,top:rect.y+10,width:Math.max(1,rect.width-20),height:Math.max(1,rect.height-20),direction,percent}]});
}
async function main(){
 device('get-state');
 const installedPath=device('shell','pm','path',pkg).trim().split('\n').find(line=>line.trim().endsWith('/base.apk'))?.trim().replace(/^package:/,'');
 if(!installedPath||!/^[/A-Za-z0-9._~+=-]+$/.test(installedPath))throw new Error('Unexpected installed APK path');
 installedApkSha256=device('shell','sha256sum',installedPath).trim().split(/\s+/)[0].toUpperCase();

 const result=await http('POST','/session',{capabilities:{alwaysMatch:{platformName:'Android','appium:automationName':'UiAutomator2','appium:udid':serial,'appium:appPackage':pkg,'appium:appActivity':'.MainActivity','appium:noReset':true},firstMatch:[{}]}});session=result.sessionId;
 await request('POST','/timeouts',{implicit:4000});
 for(const [index,command] of commands.entries()){
  let reply;
  switch(command.action){
   case 'tap':await request('POST','/element/'+await find(command.label)+'/click',{});break;
   case 'tap-scroll':{
    if(command.value&&!['up','down'].includes(command.value))throw new Error('Use up or down for control search.');
    let id,scrolls=0;
    await request('POST','/timeouts',{implicit:500});
    try {
    for(;scrolls<=5;scrolls++){
     try{id=await find(command.label);break;}catch(error){if(!error.message.startsWith('Element not found:'))throw error;}
     if(scrolls<5)await scrollContent(command.value||'down');
    }
    if(!id)throw new Error('Control not visible after five scrolls: '+command.label);
    const areas=await request('POST','/elements',{using:'class name',value:'android.widget.ScrollView'});
    if(areas.length){
     const area=await request('GET','/element/'+areas[0]['element-6066-11e4-a52e-4f735466cecf']+'/rect'),target=await request('GET','/element/'+id+'/rect');
     if(target.y<area.y+area.height&&target.y+target.height>=area.y+area.height-2){
      await request('POST','/execute/sync',{script:'mobile: scrollGesture',args:[{left:area.x+10,top:area.y+10,width:Math.max(1,area.width-20),height:Math.max(1,area.height-20),direction:'down',percent:.35}]});
      id=await find(command.label);scrolls++;
     }
    }
    await request('POST','/element/'+id+'/click',{});reply={selectedControl:command.label,scrolls};
    } finally { await request('POST','/timeouts',{implicit:4000}); }
    break;
   }
   case 'tap-choice':{
    const items=await request('POST','/elements',{using:'xpath',value:`//*[@text=${JSON.stringify(command.group)}]/following-sibling::*[@content-desc=${JSON.stringify(command.label)}][1]`});
    if(!items.length)throw new Error('Choice not visible: '+command.group+' / '+command.label);
    await request('POST','/element/'+items[0]['element-6066-11e4-a52e-4f735466cecf']+'/click',{});break;
   }
   case 'tap-first-checkbox':{const items=await request('POST','/elements',{using:'-android uiautomator',value:'new UiSelector().className("android.widget.CheckBox")'});if(!items.length)throw new Error('No visible checkbox');const id=items[0]['element-6066-11e4-a52e-4f735466cecf'];reply={selectedControl:await request('GET','/element/'+id+'/attribute/contentDescription')};await request('POST','/element/'+id+'/click',{});break;}
   case 'tap-first-radio':{let items=[],scrolls=0;for(;scrolls<=4;scrolls++){items=await request('POST','/elements',{using:'-android uiautomator',value:'new UiSelector().className("android.widget.RadioButton")'});if(items.length)break;if(scrolls<4)await request('POST','/execute/sync',{script:'mobile: scrollGesture',args:[{left:50,top:300,width:850,height:1000,direction:'down',percent:.7}]});}if(!items.length)throw new Error('No radio choice after scrolling');await request('POST','/element/'+items[0]['element-6066-11e4-a52e-4f735466cecf']+'/click',{});reply={selectedFirstVisibleCriterion:true,scrolls};break;}
   case 'tap-file-row':{
    const rows=await request('POST','/elements',{using:'xpath',value:`//*[@content-desc=${JSON.stringify('Preview the file '+command.label)}]/..`});if(!rows.length)throw new Error('Native file row not found: '+command.label);
    const rect=await request('GET','/element/'+rows[0]['element-6066-11e4-a52e-4f735466cecf']+'/rect');
    await request('POST','/execute/sync',{script:'mobile: clickGesture',args:[{x:Math.round(rect.x+rect.width*.3),y:Math.round(rect.y+rect.height*.5)}]});reply={file:command.label,selectedRow:rect};break;
   }
   case 'tap-if-present':{const all=await request('POST','/elements',{using:'accessibility id',value:command.label});const fallback=all.length?all:await request('POST','/elements',{using:'-android uiautomator',value:`new UiSelector().text(${JSON.stringify(command.label)})`});if(fallback.length){await request('POST','/element/'+fallback[0]['element-6066-11e4-a52e-4f735466cecf']+'/click',{});reply='Optional control found and tapped';}else reply='Optional control absent';break;}
   case 'type':{const id=await find(command.label);await request('POST','/element/'+id+'/click',{});await request('POST','/element/'+id+'/clear',{});await request('POST','/element/'+id+'/value',{text:String(command.value).replaceAll('{runId}',String(startedAt))});break;}
   case 'back':device('shell','input','keyevent','4');break;
   case 'dismiss-keyboard':if(await request('GET','/appium/device/is_keyboard_shown'))device('shell','input','keyevent','4');break;
   case 'wait':if(!(command.seconds>=0&&command.seconds<=60))throw new Error('Wait must be 0ÃƒÆ’Ã†â€™Ãƒâ€ Ã¢â‚¬â„¢ÃƒÆ’Ã¢â‚¬Â ÃƒÂ¢Ã¢â€šÂ¬Ã¢â€žÂ¢ÃƒÆ’Ã†â€™ÃƒÂ¢Ã¢â€šÂ¬Ã…Â¡ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â¢ÃƒÆ’Ã†â€™Ãƒâ€ Ã¢â‚¬â„¢ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â¢ÃƒÆ’Ã†â€™Ãƒâ€šÃ‚Â¢ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã…Â¡Ãƒâ€šÃ‚Â¬ÃƒÆ’Ã¢â‚¬Â¦Ãƒâ€šÃ‚Â¡ÃƒÆ’Ã†â€™ÃƒÂ¢Ã¢â€šÂ¬Ã…Â¡ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â¬ÃƒÆ’Ã†â€™Ãƒâ€ Ã¢â‚¬â„¢ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â¢ÃƒÆ’Ã†â€™Ãƒâ€šÃ‚Â¢ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬Ãƒâ€¦Ã‚Â¡ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â¬ÃƒÆ’Ã†â€™ÃƒÂ¢Ã¢â€šÂ¬Ã‚Â¦ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬Ãƒâ€¦Ã¢â‚¬Å“60 seconds.');await new Promise(r=>setTimeout(r,command.seconds*1000));break;
   case 'wait-visible':{if(!(command.seconds>0&&command.seconds<=180))throw new Error('UI wait must be bounded at 180 seconds.');const began=Date.now();let found=false;while(Date.now()-began<command.seconds*1000){try{await find(command.label);found=true;break;}catch{await new Promise(r=>setTimeout(r,500));}}if(!found)throw new Error('Timed out waiting for '+command.label);reply={visible:command.label,waitSeconds:(Date.now()-began)/1000};break;}
   case 'sensor-wave':{
    // Deliberately synthetic gait-like virtual inputs, never physical measurements.
    if(!(command.seconds>0&&command.seconds<=60))throw new Error('Wave must be 0ÃƒÆ’Ã†â€™Ãƒâ€ Ã¢â‚¬â„¢ÃƒÆ’Ã¢â‚¬Â ÃƒÂ¢Ã¢â€šÂ¬Ã¢â€žÂ¢ÃƒÆ’Ã†â€™ÃƒÂ¢Ã¢â€šÂ¬Ã…Â¡ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â¢ÃƒÆ’Ã†â€™Ãƒâ€ Ã¢â‚¬â„¢ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â¢ÃƒÆ’Ã†â€™Ãƒâ€šÃ‚Â¢ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã…Â¡Ãƒâ€šÃ‚Â¬ÃƒÆ’Ã¢â‚¬Â¦Ãƒâ€šÃ‚Â¡ÃƒÆ’Ã†â€™ÃƒÂ¢Ã¢â€šÂ¬Ã…Â¡ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â¬ÃƒÆ’Ã†â€™Ãƒâ€ Ã¢â‚¬â„¢ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â¢ÃƒÆ’Ã†â€™Ãƒâ€šÃ‚Â¢ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬Ãƒâ€¦Ã‚Â¡ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â¬ÃƒÆ’Ã†â€™ÃƒÂ¢Ã¢â€šÂ¬Ã‚Â¦ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬Ãƒâ€¦Ã¢â‚¬Å“60 seconds.');
    const began=Date.now();let sent=0;
    while(Date.now()-began<command.seconds*1000){const t=(Date.now()-began)/1000;
     device('emu','sensor','set','acceleration',`${(9.81+2*Math.sin(t*3*Math.PI)).toFixed(4)}:0:0`);
     device('emu','sensor','set','gyroscope',`0:${(.3*Math.sin(t*3*Math.PI)).toFixed(4)}:0`);sent++;
     await new Promise(r=>setTimeout(r,20));
    }
    device('emu','sensor','set','acceleration','9.81:0:0');device('emu','sensor','set','gyroscope','0:0:0');
    reply={simulated:true,seconds:(Date.now()-began)/1000,updates:sent,notPatientData:true};break;
   }
   case 'home':device('shell','input','keyevent','3');break;
   case 'resume':await request('POST','/execute/sync',{script:'mobile: activateApp',args:[{appId:pkg}]});break;
   case 'rotate':
    if(!['LANDSCAPE','PORTRAIT'].includes(command.value))throw new Error('Use LANDSCAPE or PORTRAIT.');
    try{await request('POST','/orientation',{orientation:command.value});reply=await request('GET','/orientation');}
    catch(error){if(!command.expectErrorContains||!error.message.includes(command.expectErrorContains))throw error;reply={expectedRefusal:true,error:error.message,actualOrientation:await request('GET','/orientation')};}
    break;
   case 'scroll':await scrollContent(command.value||'down',command.percent??.7);break;
   case 'sensor':if(!/^[a-z-]+$/.test(command.label)||!/^[-0-9.:]+$/.test(command.value))throw new Error('Use a virtual sensor name and numeric colon-separated values.');reply=device('emu','sensor','set',command.label,command.value)+'\n'+device('emu','sensor','get',command.label);break;
   case 'font':if(!(Number(command.value)>=.85&&Number(command.value)<=2))throw new Error('Font scale must be 0.85 to 2.');reply=device('shell','settings','put','system','font_scale',String(command.value));break;
   case 'display-size':if(command.value!=='reset'&&!/^\d{3,4}x\d{3,4}$/.test(command.value))throw new Error('Use a virtual display size such as 720x1280, or reset.');reply=device('shell','wm','size',command.value);break;
   case 'assert':await find(command.label);reply='Visible: '+command.label;break;
   case 'assert-in-bounds':{
    const rect=await request('GET','/element/'+await find(command.label)+'/rect'),window=await request('GET','/window/rect');
    if(rect.x<window.x||rect.y<window.y||rect.x+rect.width>window.x+window.width||rect.y+rect.height>window.y+window.height)throw new Error('Control outside window: '+command.label+' '+JSON.stringify({rect,window}));
    reply={rect,window,reportedRectInsideWindow:true};break;
   }
   case 'assert-readable-layout':{
    const views=await request('POST','/elements',{using:'class name',value:'android.widget.ScrollView'});
    if(views.length<2)throw new Error('Expected content and action scroll regions');
    const content=await request('GET','/element/'+views[0]['element-6066-11e4-a52e-4f735466cecf']+'/rect'),actions=await request('GET','/element/'+views.at(-1)['element-6066-11e4-a52e-4f735466cecf']+'/rect'),window=await request('GET','/window/rect');
    if(actions.height>window.height*.31||content.height<window.height*.4||content.y+content.height>actions.y+2)throw new Error('Content crowded by actions: '+JSON.stringify({content,actions,window}));
    reply={content,actions,window,contentRemainsReadable:true};break;
   }
   case 'assert-recording-visible':{
    const items=await request('POST','/elements',{using:'-android uiautomator',value:'new UiSelector().descriptionStartsWith("Open ")'});
    if(!items.length)throw new Error('No recording card visible');
    const rect=await request('GET','/element/'+items[0]['element-6066-11e4-a52e-4f735466cecf']+'/rect');
    const footers=await request('POST','/elements',{using:'-android uiautomator',value:'new UiSelector().className("android.widget.ScrollView")'});
    const footer=await request('GET','/element/'+footers.at(-1)['element-6066-11e4-a52e-4f735466cecf']+'/rect');
    if(rect.height<100||rect.y+rect.height>footer.y)throw new Error('First recording obstructed: '+JSON.stringify({rect,footer}));
    reply={recording:rect,footer,firstRecordingEntryVisible:true};break;
   }
   case 'set-switch':{const desired=String(command.value);if(!['true','false'].includes(desired))throw Error('Switch value must be true or false');const id=await find(command.label);let checked=String(await request('GET','/element/'+id+'/attribute/checked'));if(checked!==desired)await request('POST','/element/'+id+'/click',{});checked=String(await request('GET','/element/'+id+'/attribute/checked'));if(checked!==desired)throw Error('Switch did not change: '+command.label);reply={selectedControl:command.label,checked};break;}
   case 'assert-checked':{reply=await request('GET','/element/'+await find(command.label)+'/attribute/checked');if(String(reply)!==String(command.value))throw new Error('Wrong checked state for '+command.label+': '+reply);break;}
   case 'assert-enabled':{reply=await request('GET','/element/'+await find(command.label)+'/attribute/enabled');if(String(reply)!==String(command.value))throw new Error('Wrong enabled state for '+command.label+': '+reply);break;}
   case 'source':break;
   default:throw new Error('Unknown action: '+command.action);
  }
  const source=await request('GET','/source');fs.writeFileSync(path.join(out,index+'.xml'),source);
  const screenshot=await request('GET','/screenshot');fs.writeFileSync(path.join(out,index+'.png'),Buffer.from(screenshot,'base64'));
  replies.push({command,at:new Date().toISOString(),elapsedSeconds:(Date.now()-startedAt)/1000,reply:reply??'Action completed; UI reply captured.',passed:true});
  fs.writeFileSync(path.join(out,'replies.json'),JSON.stringify({physicalPhoneUsed:false,serial,installedApkSha256,replies},null,2));
  console.log(JSON.stringify(replies.at(-1)));
 }
 console.log('Screens, UI hierarchy and replies: '+out);
}
main().catch(async e=>{if(session){try{fs.writeFileSync(path.join(out,'failed.xml'),await request('GET','/source'));fs.writeFileSync(path.join(out,'failed.png'),Buffer.from(await request('GET','/screenshot'),'base64'));}catch{}}fs.writeFileSync(path.join(out,'failure.json'),JSON.stringify({physicalPhoneUsed:false,serial,installedApkSha256,error:e.message,replies},null,2));console.error(e.message);process.exitCode=1;}).finally(async()=>{if(session)await request('DELETE','').catch(()=>{});});
