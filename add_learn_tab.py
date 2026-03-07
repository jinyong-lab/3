import sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

base = os.path.dirname(os.path.abspath(__file__))
path = os.path.join(base, 'index.html')

with open(path, 'r', encoding='utf-8') as f:
    html = f.read()

# ── 1. Tab button ──────────────────────────────────────────────
OLD_KICHUL_BTN = "style=\"border-color:#f59e0b;color:#92400e;\">⭐ 기출문제</button>"
NEW_KICHUL_BTN = OLD_KICHUL_BTN + "\n  <button class=\"tab\" onclick=\"switchTab('learn')\" style=\"border-color:#10b981;color:#059669;\">📖 단어 학습</button>"
assert OLD_KICHUL_BTN in html, "kichul tab button not found"
html = html.replace(OLD_KICHUL_BTN, NEW_KICHUL_BTN, 1)

# ── 2. Flashcard CSS (before </style>) ────────────────────────
FLASHCARD_CSS = """
/* ── FLASHCARD (단어 학습) ── */
.flashcard-wrap{perspective:1000px;margin:12px 0 16px;}
.flashcard{
  width:100%;min-height:230px;position:relative;
  transform-style:preserve-3d;transition:transform .42s cubic-bezier(.4,0,.2,1);
  cursor:pointer;border-radius:16px;
}
.flashcard.flipped{transform:rotateY(180deg);}
.card-face{
  position:absolute;width:100%;min-height:230px;
  backface-visibility:hidden;-webkit-backface-visibility:hidden;
  border-radius:16px;padding:24px 20px;
  display:flex;flex-direction:column;align-items:center;justify-content:center;
  box-shadow:0 4px 18px rgba(0,0,0,.10);
}
.card-front{background:#fff;border:2px solid var(--primary);}
.card-back{background:#ede9fe;border:2px solid var(--primary);transform:rotateY(180deg);}
.fc-word{font-size:2rem;font-weight:800;color:var(--primary);margin:8px 0 4px;text-align:center;word-break:break-word;letter-spacing:-0.5px;}
.fc-hint{font-size:0.78rem;color:var(--muted);margin-top:10px;}
.fc-meaning{font-size:1.55rem;font-weight:800;color:#3730a3;text-align:center;margin:6px 0;}
.fc-detail{font-size:0.8rem;color:#4338ca;text-align:center;margin-top:6px;line-height:1.5;padding:0 8px;}
.l-assess-row{display:flex;gap:10px;margin-bottom:10px;}
.l-btn{
  flex:1;padding:14px 8px;border-radius:12px;border:none;
  font-size:0.92rem;font-weight:700;cursor:pointer;
  min-height:52px;touch-action:manipulation;-webkit-appearance:none;
  transition:opacity .15s;
}
.l-btn:active{opacity:.8;}
.l-btn-correct{background:#d1fae5;color:#065f46;}
.l-btn-wrong{background:#fee2e2;color:#991b1b;}
.l-nav-row{display:flex;gap:8px;margin-top:4px;}
"""
assert "</style>" in html
html = html.replace("</style>", FLASHCARD_CSS + "</style>", 1)

# ── 3. Learn tab HTML (after /tab-kichul) ─────────────────────
LEARN_HTML = """
<!-- ===== 단어 학습 탭 (플래시카드) ===== -->
<div id="tab-learn" class="screen">

  <!-- 범위 선택 -->
  <div id="learn-mode" class="screen active">
    <div class="card">
      <h2>학습 범위 선택</h2>
      <div class="mode-grid">
        <div class="mode-btn selected" data-lmode="30" onclick="lSelectMode(this)">
          <span class="emoji">⭐</span><span class="label">핵심 30개</span><span class="sub">빈도 상위 단어</span>
        </div>
        <div class="mode-btn" data-lmode="60" onclick="lSelectMode(this)">
          <span class="emoji">📚</span><span class="label">중급 60개</span><span class="sub">빈도 상위 단어</span>
        </div>
        <div class="mode-btn" data-lmode="all" onclick="lSelectMode(this)">
          <span class="emoji">💪</span><span class="label">전체 121개</span><span class="sub">모든 어휘</span>
        </div>
        <div class="mode-btn" data-lmode="terms" onclick="lSelectMode(this)">
          <span class="emoji">🔬</span><span class="label">전문용어</span><span class="sub">통계 용어 36개</span>
        </div>
      </div>
      <button class="start-btn" style="background:#059669;" onclick="lStart()">플래시카드 학습 시작 →</button>
    </div>
    <div class="card" style="background:#ecfdf5;border-color:#6ee7b7;">
      <p style="font-size:0.85rem;color:#065f46;line-height:1.7;">
        💡 <b>사용법</b><br>
        카드를 터치하면 한국어 뜻이 나타납니다.<br>
        <b style="color:#047857;">✔ 알아요</b> — 다음으로 넘어가요<br>
        <b style="color:#b91c1c;">✘ 몰라요</b> — 나중에 다시 볼게요
      </p>
    </div>
  </div>

  <!-- 플래시카드 -->
  <div id="learn-quiz" class="screen">
    <div class="progress-label" id="l-prog-label" style="text-align:right;font-size:0.78rem;color:var(--muted);margin-bottom:4px;">1 / 30</div>
    <div class="progress-bar-wrap"><div class="progress-bar" id="l-prog-bar" style="width:0%;background:#059669;"></div></div>

    <div class="flashcard-wrap">
      <div class="flashcard" id="l-card" onclick="lFlip()">
        <div class="card-face card-front">
          <div class="freq-badge" id="l-freq">빈도: -</div>
          <div class="fc-word" id="l-word">regression</div>
          <div class="fc-hint">터치하여 뜻 보기 👆</div>
        </div>
        <div class="card-face card-back">
          <div class="fc-meaning" id="l-meaning">회귀</div>
          <div class="fc-detail" id="l-detail"></div>
        </div>
      </div>
    </div>

    <div class="l-assess-row" id="l-assess-row" style="display:none;">
      <button class="l-btn l-btn-wrong" onclick="lAssess(false)">✘ 몰라요</button>
      <button class="l-btn l-btn-correct" onclick="lAssess(true)">✔ 알아요</button>
    </div>
    <div class="l-nav-row">
      <button class="btn btn-skip" onclick="lPrev()" id="l-prev-btn" style="flex:0 0 auto;padding:13px 18px;">← 이전</button>
      <button class="btn btn-skip" onclick="lShowMode()" style="flex:1;font-size:0.82rem;">목록으로</button>
      <button class="btn btn-skip" onclick="lNext()" id="l-next-btn" style="flex:0 0 auto;padding:13px 18px;">다음 →</button>
    </div>
  </div>

  <!-- 결과 -->
  <div id="learn-result" class="screen">
    <div class="card" style="text-align:center;border-color:#10b981;">
      <div class="score-circle" style="border-color:#059669;">
        <span class="score-pct" id="l-score-pct" style="color:#059669;">0%</span>
        <span class="score-sub" id="l-score-frac">0/0</span>
      </div>
      <div class="result-msg" id="l-result-msg"></div>
      <div class="result-btns">
        <button class="btn btn-skip" onclick="lShowMode()">처음으로</button>
        <button class="btn btn-primary" style="background:#059669;" onclick="lRetryWrong()" id="l-retry-btn">모르는 것만 다시</button>
      </div>
    </div>
    <div class="card" id="l-wrong-card" style="display:none;">
      <h3 style="font-size:0.85rem;color:var(--muted);margin-bottom:10px;">다시 볼 단어 목록</h3>
      <div id="l-wrong-body"></div>
    </div>
  </div>

</div><!-- /tab-learn -->
"""
assert "</div><!-- /tab-kichul -->" in html
html = html.replace("</div><!-- /tab-kichul -->", "</div><!-- /tab-kichul -->" + LEARN_HTML, 1)

# ── 4. Update switchTab ────────────────────────────────────────
OLD_SWITCH = (
    "  tabs[2].classList.toggle('active', tab==='kichul');\n"
    "  document.getElementById('tab-vocab').classList.toggle('active', tab==='vocab');\n"
    "  document.getElementById('tab-sentence').classList.toggle('active', tab==='sentence');\n"
    "  document.getElementById('tab-kichul').classList.toggle('active', tab==='kichul');\n"
    "}"
)
NEW_SWITCH = (
    "  tabs[2].classList.toggle('active', tab==='kichul');\n"
    "  if(tabs[3]) tabs[3].classList.toggle('active', tab==='learn');\n"
    "  document.getElementById('tab-vocab').classList.toggle('active', tab==='vocab');\n"
    "  document.getElementById('tab-sentence').classList.toggle('active', tab==='sentence');\n"
    "  document.getElementById('tab-kichul').classList.toggle('active', tab==='kichul');\n"
    "  document.getElementById('tab-learn').classList.toggle('active', tab==='learn');\n"
    "}"
)
assert OLD_SWITCH in html, "switchTab content not found"
html = html.replace(OLD_SWITCH, NEW_SWITCH, 1)

# ── 5. Learn JS (before </script>) ────────────────────────────
LEARN_JS = """
// ============================================================
// 단어 학습 (플래시카드)
// ============================================================
let lPool=[], lCur=0, lKnownSet=new Set(), lWrongList=[], lSelectedMode='30', lFlipped=false;

function lSelectMode(el){
  document.querySelectorAll('#learn-mode .mode-btn').forEach(b=>b.classList.remove('selected'));
  el.classList.add('selected');
  lSelectedMode = el.dataset.lmode;
}

function lStart(){
  const vocab = VOCAB.slice();
  if(lSelectedMode==='30')      lPool = vocab.slice(0,30);
  else if(lSelectedMode==='60') lPool = vocab.slice(0,60);
  else if(lSelectedMode==='terms') lPool = TERMS.slice();
  else lPool = vocab;
  // shuffle
  for(let i=lPool.length-1;i>0;i--){const j=Math.floor(Math.random()*(i+1));[lPool[i],lPool[j]]=[lPool[j],lPool[i]];}
  lCur=0; lKnownSet=new Set(); lWrongList=[];
  lShowScreen('quiz');
  lLoad();
}

function lShowScreen(name){
  ['mode','quiz','result'].forEach(s=>{
    const el=document.getElementById('learn-'+s);
    if(el) el.classList.toggle('active', s===name);
  });
}

function lLoad(){
  if(lCur>=lPool.length){lShowResult();return;}
  const item=lPool[lCur];
  document.getElementById('l-prog-label').textContent=`${lCur+1} / ${lPool.length}`;
  document.getElementById('l-prog-bar').style.width=((lCur/lPool.length)*100)+'%';
  document.getElementById('l-freq').textContent = item.f!=='-' ? `빈도 ${item.f}위` : '전문용어';
  document.getElementById('l-word').textContent = item.w;
  document.getElementById('l-meaning').textContent = item.m;
  const parts = item.mf.split('|');
  document.getElementById('l-detail').textContent = parts.length>1 ? parts[1].trim() : '';
  // reset
  lFlipped=false;
  document.getElementById('l-card').classList.remove('flipped');
  document.getElementById('l-assess-row').style.display='none';
  document.getElementById('l-prev-btn').disabled = (lCur===0);
}

function lFlip(){
  lFlipped=!lFlipped;
  document.getElementById('l-card').classList.toggle('flipped', lFlipped);
  if(lFlipped) document.getElementById('l-assess-row').style.display='flex';
}

function lAssess(known){
  if(known) lKnownSet.add(lCur);
  else { if(!lKnownSet.has(lCur)) lWrongList.push(lPool[lCur]); }
  lCur++;
  if(lCur>=lPool.length) lShowResult();
  else lLoad();
}

function lNext(){
  if(lCur<lPool.length-1){ lCur++; lLoad(); }
  else lShowResult();
}

function lPrev(){
  if(lCur>0){ lCur--; lLoad(); }
}

function lShowResult(){
  const total=lPool.length, known=lKnownSet.size;
  const pct=total>0?Math.round(known/total*100):0;
  document.getElementById('l-score-pct').textContent=pct+'%';
  document.getElementById('l-score-frac').textContent=`${known} / ${total}`;
  const msgs=[[90,'완벽해요! 시험 볼 준비 됐어요!'],[70,'잘 알고 있어요! 조금만 더!'],[50,'절반 이상! 모르는 것 집중 복습!'],[0,'모르는 단어를 집중 복습하세요']];
  for(const[t,msg] of msgs){if(pct>=t){document.getElementById('l-result-msg').textContent=msg;break;}}
  // deduplicate wrong list
  const seen=new Set();
  const uniq=lWrongList.filter(it=>{if(seen.has(it.w))return false;seen.add(it.w);return true;});
  lWrongList=uniq;
  const wc=document.getElementById('l-wrong-card'), wb=document.getElementById('l-wrong-body');
  wb.innerHTML='';
  if(uniq.length>0){
    wc.style.display='block';
    document.getElementById('l-retry-btn').style.display='';
    uniq.forEach(it=>{
      const d=document.createElement('div'); d.className='wrong-item';
      d.innerHTML=`<div class="wrong-word">${it.w}</div><div style="font-size:0.82rem;color:#7f1d1d;margin-top:2px;">${it.m}</div>`;
      wb.appendChild(d);
    });
  } else {
    wc.style.display='none';
    document.getElementById('l-retry-btn').style.display='none';
  }
  lShowScreen('result');
}

function lRetryWrong(){
  if(!lWrongList.length) return;
  lPool=lWrongList.slice();
  for(let i=lPool.length-1;i>0;i--){const j=Math.floor(Math.random()*(i+1));[lPool[i],lPool[j]]=[lPool[j],lPool[i]];}
  lCur=0; lKnownSet=new Set(); lWrongList=[];
  lShowScreen('quiz');
  lLoad();
}

function lShowMode(){ lShowScreen('mode'); }
"""
assert "</script>" in html
html = html.replace("</script>", LEARN_JS + "\n</script>", 1)

with open(path, 'w', encoding='utf-8') as f:
    f.write(html)

print(f'Done. {len(html)} chars ({len(html.encode())//1024} KB)')
