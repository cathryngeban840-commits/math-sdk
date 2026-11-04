const $ = id => document.getElementById(id);
const reelsEl = $("reels"), message = $("message");
let balance=1000,wagered=0,roundWin=0,lastWin=0,featureName="",fsLeft=0,mult=1,auto=false,busy=false;
let stickyWildReels=new Set();
let soundEnabled=true,audioContext=null;
function playTone(frequency=440,duration=.09,type="sine",volume=.035){
  if(!soundEnabled)return;
  try{
    const AudioCtx=window.AudioContext||window.webkitAudioContext;
    if(!AudioCtx)return;
    audioContext ||= new AudioCtx();
    if(audioContext.state==="suspended") audioContext.resume();
    const oscillator=audioContext.createOscillator(),gain=audioContext.createGain();
    oscillator.type=type;oscillator.frequency.setValueAtTime(frequency,audioContext.currentTime);
    gain.gain.setValueAtTime(volume,audioContext.currentTime);
    gain.gain.exponentialRampToValueAtTime(.001,audioContext.currentTime+duration);
    oscillator.connect(gain);gain.connect(audioContext.destination);
    oscillator.start();oscillator.stop(audioContext.currentTime+duration);
  }catch(error){console.debug("Audio cue unavailable",error)}
}
function playCue(kind){
  const cues={spin:[[180,.08,"triangle"],[240,.07,"triangle"]],stop:[[330,.07,"sine"]],win:[[523,.12,"sine"],[659,.14,"sine"],[784,.2,"sine"]],bonus:[[392,.14,"triangle"],[523,.14,"triangle"],[659,.18,"triangle"],[784,.28,"triangle"]]};
  (cues[kind]||[]).forEach(([hz,dur,type],i)=>setTimeout(()=>playTone(hz,dur,type),i*95));
}

const money=n=>Number(n||0).toFixed(2);
const symbolGlyph = {MINER:"⛏️",CART:"🛒",GOLD:"🪙",PURPLE:"💎",BLUE:"🔷",RED:"🟥",GREEN:"🟩",PICKAXE:"🪓",LANTERN:"🏮",A:"A",K:"K",Q:"Q",J:"J","10":"10","9":"9",S:"S",W:"W"};
// Art is presentation-only. SDK symbol IDs remain the source of truth.
const symbolArt = {
  MINER:"miner", CART:"cart", GOLD:"gold", PURPLE:"purple", BLUE:"blue",
  RED:"red", GREEN:"green", PICKAXE:"pickaxe", LANTERN:"lantern",
  A:"a", K:"k", Q:"q", J:"j", "10":"10", "9":"9", S:"scatter", W:"w"
};
function draw(board){
  if(!Array.isArray(board)||board.length!==6) throw new Error("SDK reveal did not contain six reels.");
  reelsEl.innerHTML="";
  board.forEach((reel,i)=>{
    const col=document.createElement("div"); col.className="reel";
    reel.forEach(item=>{
      const name=typeof item==="string"?item:item?.name;
      const sym=symbolGlyph[name]||name||"?";
      const cell=document.createElement("div"); cell.className="cell";
      const artName=symbolArt[name];
      if(artName){
        const img=document.createElement("img");
        img.className="symbol-art"; img.alt=name; img.draggable=false;
        img.src="/demo/assets/symbols/"+artName+".png";
        img.onerror=()=>{img.remove();cell.textContent=sym;};
        cell.appendChild(img);
      } else cell.textContent=sym;
      if(["MINER","CART","GOLD","PURPLE"].includes(name)) cell.classList.add("high");
      if(name==="S") cell.classList.add("scatter");
      if(name==="W") cell.classList.add("wild");
      if(item?.winning) cell.classList.add("winning");
      if(item?.sticky) cell.classList.add("sticky");
      col.appendChild(cell);
    });
    reelsEl.appendChild(col);
  });
}

const featureArt = {
  "GOLD RUSH": {file:"gold_rush.png", tagline:"10 FREE SPINS · STEADY GOLD"},
  "CRYSTAL CAVERN": {file:"crystal_cavern.png", tagline:"12 FREE SPINS · GROWING MULTIPLIER"},
  "DEEP MINE JACKPOT": {file:"deep_mine_jackpot.png", tagline:"15 FREE SPINS · 0.50× MULTIPLIER STEPS"}
};
let introTimer;
function showFeatureIntro(name, spins){
  const panel=$("featureIntro"), art=featureArt[name];
  if(!panel||!art)return;
  $("featureIntroTitle").textContent=name;
  $("featureIntroSubtitle").textContent=art.tagline+" · "+spins+" SPINS";
  const img=$("featureIntroArt");
  img.src="/demo/assets/bonus/"+art.file;
  img.alt=name+" bonus artwork";
  img.onerror=()=>{img.hidden=true;$("featureIntroFallback").hidden=false;};
  img.onload=()=>{img.hidden=false;$("featureIntroFallback").hidden=true;};
  $("featureIntroFallback").hidden=false;
  panel.hidden=false;
  clearTimeout(introTimer);
  introTimer=setTimeout(()=>{panel.hidden=true;},3200);
}

function update(){
  $("balance").textContent=money(balance); $("wagered").textContent=money(wagered);
  $("roundwin").textContent=money(roundWin); $("lastwin").textContent=money(lastWin);
  $("feature").textContent=featureName||"BASE GAME"; $("spins").textContent=featureName?fsLeft:"—";
  $("mult").textContent=mult.toFixed(2)+"×";
}
function setBusy(value){busy=value;$("spin").disabled=value;$("bet").disabled=value;$("auto").disabled=value}
const delay=ms=>new Promise(resolve=>setTimeout(resolve,ms));
async function renderOutcome(outcome,bet){
  if(!Array.isArray(outcome.events)) throw new Error("SDK response is missing its event sequence.");
  roundWin=0; lastWin=0; featureName=""; fsLeft=0; mult=1; stickyWildReels=new Set(); update();
  for(const event of outcome.events){
    if(event.type==="reveal"){
      const board=event.board.map(reel=>reel.slice(1,-1));
      board.forEach((reel,index)=>{if(reel.some(item=>(typeof item==="string"?item:item?.name)==="W"))stickyWildReels.add(index)});
      board.forEach((reel,index)=>{if(stickyWildReels.has(index))board[index]=reel.map(()=>({name:"W",sticky:true}))});
      draw(board);
      await delay(160);
    } else if(event.type==="freeSpinTrigger"){
      playCue("bonus");
      const n=Number(event.totalFs||0);
      featureName=n>=15?"DEEP MINE JACKPOT":n===12?"CRYSTAL CAVERN":"GOLD RUSH";
      fsLeft=n; mult=1;
      message.textContent=featureName+" triggered — "+n+" free spins!";
      showFeatureIntro(featureName,n);
    } else if(event.type==="freeSpinRetrigger"){
      fsLeft=Number(event.totalFs||fsLeft);
      message.textContent="Free spins retriggered — "+fsLeft+" total spins.";
    } else if(event.type==="updateFreeSpin"){
      fsLeft=Math.max(0,Number(event.total||0)-Number(event.amount||0));
      if(featureName){
        // Derive feature progression even on dead spins with no winInfo event.
        const increment=featureName==="CRYSTAL CAVERN" ? 0.25 : featureName==="DEEP MINE JACKPOT" ? 0.50 : 0;
        mult=Math.min(5,1+Math.max(0,Number(event.amount||1)-1)*increment);
        message.textContent="Free spin "+event.amount+" of "+event.total;
      }
    } else if(event.type==="winInfo"){
      const wins=Array.isArray(event.wins)?event.wins:[];
      const boardCells=[...reelsEl.querySelectorAll(".reel")].map(reel=>[...reel.querySelectorAll(".cell")]);
      let shown=0;
      for(const win of wins){
        const amount=Number(win.win||0)/100;
        shown+=amount;
        for(const pos of (win.positions||[])){
          const cell=boardCells[Number(pos.reel)]?.[Number(pos.row)-1];
          if(cell) cell.classList.add("winning");
        }
      }
      if(shown>0) message.textContent="WIN! "+money(shown)+"× bet across "+wins.length+" winning symbol"+(wins.length===1?"":"s");
      const seen=wins.flatMap(w=>w.meta?[Number(w.meta.globalMult||1)]:[]);
      if(seen.length) mult=Math.max(mult,...seen);
    } else if(event.type==="updateGlobalMult"){
      mult=Number(event.globalMult||mult);
    } else if(event.type==="finalWin"){
      if(Number(event.amount||0)>0)playCue("win");
      roundWin=Number(event.amount||0)/100*bet;
      lastWin=roundWin;
    } else if(event.type==="freeSpinEnd"){
      fsLeft=0;
    }
    update();
  }
  // payoutMultiplier is the SDK book's round-wide result in bet units.
  // Prefer it over reconstructing money from the finalWin event's cent amount.
  const sdkPayout=Number(outcome.payoutMultiplier);
  if(!Number.isFinite(sdkPayout)||sdkPayout<0) throw new Error("SDK returned an invalid payout multiplier.");
  roundWin=Math.round(sdkPayout*bet*100)/100;
  lastWin=roundWin;
  balance+=roundWin; message.textContent=roundWin>0?"SDK round win: "+money(roundWin):"No win — the SDK outcome paid 0.";
  if(featureName&&fsLeft===0) message.textContent+=(roundWin>0?" ":" ")+ "Feature complete.";
  update();
}
async function spin(){
  if(busy)return;
  const bet=Number($("bet").value);
  if(!Number.isFinite(bet)||bet<.1||bet>1000){message.textContent="Enter a bet between 0.10 and 1,000.";return}
  if(balance<bet){message.textContent="Not enough demo balance.";stopAuto();return}
  setBusy(true); playCue("spin"); balance-=bet; wagered+=bet; roundWin=0;lastWin=0;update();
  try{
    const response=await fetch("/api/spin",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({bet})});
    const data=await response.json();
    if(!response.ok) throw new Error(data.detail||data.error||"SDK request failed.");
    await renderOutcome(data,bet);
  }catch(error){
    balance+=bet; message.textContent="SDK error: "+error.message+" — wager refunded.";
    console.error(error);
  }finally{setBusy(false)}
}
function stopAuto(){auto=false;$("auto").textContent="AUTO: OFF"}
async function autoLoop(){while(auto){if(balance<=0){stopAuto();break}await spin();if(auto)await delay(650)}}
$("spin").onclick=spin;
$("sound").onclick=()=>{soundEnabled=!soundEnabled;$("sound").textContent="SOUND: "+(soundEnabled?"ON":"OFF");$("sound").setAttribute("aria-pressed",String(soundEnabled));if(soundEnabled)playTone(660,.08)};
$("fullscreen").onclick=async()=>{try{if(!document.fullscreenElement)await document.documentElement.requestFullscreen();else await document.exitFullscreen()}catch(e){message.textContent="Fullscreen is unavailable in this browser."}};
$("half").onclick=()=>{$("bet").value=Math.max(.1,Number($("bet").value)/2).toFixed(2)};
$("double").onclick=()=>{$("bet").value=Math.min(1000,Number($("bet").value)*2).toFixed(2)};
$("rules").onclick=()=> $("help").showModal();
$("close").onclick=()=> $("help").close();
$("auto").onclick=()=>{if(auto){stopAuto();return}auto=true;$("auto").textContent="AUTO: ON";autoLoop()};
async function init(){
  reelsEl.innerHTML="";
  try{const r=await fetch("/health");if(!r.ok)throw new Error("API unavailable");const h=await r.json();if(!h.ok)throw new Error("SDK server not ready");message.textContent="SDK connected. Ready to descend?";}
  catch(e){message.textContent="Start the local SDK server to play: python games/mining_slot/server.py";$("spin").disabled=true;console.error(e)}
  update();
}
init();
