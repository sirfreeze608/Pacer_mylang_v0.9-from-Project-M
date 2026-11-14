// sudoku_game.ml  —  mylang v0.5.3
// Run this file with F5 in Pacer (or: mylang sudoku_game.ml)
// A fully playable Sudoku game launches in your default browser.
//
// Features:
//   - 4 difficulty levels (Easy / Medium / Hard / Expert) with progression unlocks
//   - Sign-in / guest mode with stats persisted in localStorage
//   - Backtracking puzzle generator with unique-solution guarantee
//   - Notes mode, 3 hints, mistake counter, live timer
//   - Win cascade animation, confetti particles, sign-in modal

// ── Page setup ─────────────────────────────────────────────────────────────
// Use a blank title — the game overrides all body/layout styles via html.raw()

html.page("Sudoku — mylang");

// ── CSS override — break out of the default 760px template wrapper ──────────
html.raw(
  "<style>" +
  "body{max-width:100vw!important;padding:0!important;margin:0!important;}" +
  "h1{display:none!important;}" +
  "footer{display:none!important;}" +
  "</style>"
);

// ── Design tokens and base styles ──────────────────────────────────────────
html.raw(
  "<style>" +
  ":root{" +
  "--bg:#0F1117;--surface:#1A1D27;--surface2:#21253A;--border:#2A2E42;" +
  "--accent:#E2543C;--accent-dim:rgba(226,84,60,0.15);" +
  "--teal:#4EC9B0;--teal-dim:rgba(78,201,176,0.12);" +
  "--parchment:#F2EBDD;--muted:#7A7F9A;--green:#6A9955;--amber:#CE9178;" +
  "--mono:'JetBrains Mono','Fira Code','Cascadia Code','Courier New',monospace;" +
  "--sans:'Inter',-apple-system,'Segoe UI',sans-serif;" +
  "--r:3px;" +
  "}" +
  "*,*::before,*::after{box-sizing:border-box;margin:0;padding:0;}" +
  "body{background:var(--bg);color:var(--parchment);font-family:var(--sans);" +
  "font-size:14px;line-height:1.5;min-height:100vh;display:flex;" +
  "flex-direction:column;align-items:center;}" +
  "</style>"
);

// ── Header ──────────────────────────────────────────────────────────────────
html.raw(
  "<style>" +
  ".site-header{width:100%;max-width:900px;display:flex;align-items:center;" +
  "justify-content:space-between;padding:18px 24px;border-bottom:1px solid var(--border);}" +
  ".logo{font-family:var(--mono);font-size:14px;color:var(--teal);" +
  "letter-spacing:.08em;display:flex;align-items:center;gap:8px;}" +
  ".logo-dot{color:var(--accent);}" +
  ".sign-in-btn{background:var(--accent);border:none;color:#1a0a07;" +
  "font-family:var(--mono);font-size:12px;font-weight:700;" +
  "padding:7px 16px;border-radius:var(--r);cursor:pointer;transition:background .15s;}" +
  ".sign-in-btn:hover{background:#ee6b53;}" +
  ".user-badge{display:flex;align-items:center;gap:8px;background:var(--surface);" +
  "border:1px solid var(--border);border-radius:var(--r);padding:6px 12px;" +
  "font-family:var(--mono);font-size:12px;cursor:pointer;transition:border-color .15s;}" +
  ".user-badge:hover{border-color:var(--teal);}" +
  ".user-avatar{width:22px;height:22px;border-radius:50%;" +
  "background:linear-gradient(135deg,var(--accent),var(--teal));" +
  "display:flex;align-items:center;justify-content:center;" +
  "font-size:10px;font-weight:700;color:#111;flex-shrink:0;}" +
  "</style>" +
  "<header class='site-header'>" +
  "<div class='logo'>my<span class='logo-dot'>.</span>lang" +
  "<span style='color:var(--border);font-size:10px;'>|</span>" +
  "<span style='color:var(--muted);font-size:11px;'>sudoku</span></div>" +
  "<div id='headerRight'>" +
  "<button class='sign-in-btn' id='signInBtn' onclick='showSignIn()'>Sign In</button>" +
  "</div>" +
  "</header>"
);

// ── Game layout shell ───────────────────────────────────────────────────────
html.raw(
  "<style>" +
  ".game-wrapper{width:100%;max-width:900px;padding:28px 24px 48px;" +
  "display:flex;flex-direction:column;align-items:center;gap:24px;}" +
  ".game-title{font-family:var(--mono);font-size:11px;letter-spacing:.16em;" +
  "text-transform:uppercase;color:var(--muted);align-self:flex-start;}" +
  ".game-layout{display:flex;gap:28px;align-items:flex-start;flex-wrap:wrap;justify-content:center;}" +
  "</style>" +
  "<div class='game-wrapper'>" +
  "<div class='game-title'>// select a difficulty to begin</div>"
);

// ── Difficulty strip + timer row ────────────────────────────────────────────
html.raw(
  "<style>" +
  ".difficulty-strip{display:flex;gap:4px;background:var(--surface);" +
  "border:1px solid var(--border);border-radius:var(--r);padding:4px;}" +
  ".diff-btn{font-family:var(--mono);font-size:11px;font-weight:600;" +
  "letter-spacing:.06em;text-transform:uppercase;padding:6px 14px;" +
  "border:none;border-radius:2px;cursor:pointer;transition:all .15s;" +
  "background:transparent;color:var(--muted);}" +
  ".diff-btn:hover{color:var(--parchment);background:var(--surface2);}" +
  ".diff-btn.active{background:var(--accent);color:#1a0a07;}" +
  ".diff-btn.locked{opacity:.4;cursor:not-allowed;}" +
  ".meta-item{font-family:var(--mono);font-size:12px;color:var(--muted);" +
  "display:flex;align-items:center;gap:6px;}" +
  ".meta-value{color:var(--parchment);font-weight:600;font-variant-numeric:tabular-nums;}" +
  ".timer-digits{font-size:16px;letter-spacing:.05em;}" +
  "</style>" +
  "<div style='display:flex;gap:20px;align-items:center;flex-wrap:wrap;width:100%;'>" +
  "<div class='difficulty-strip' id='diffStrip'>" +
  "<button class='diff-btn active' data-diff='easy' onclick=\"selectDifficulty('easy')\">Easy</button>" +
  "<button class='diff-btn' data-diff='medium' onclick=\"selectDifficulty('medium')\">Medium</button>" +
  "<button class='diff-btn locked' data-diff='hard' onclick=\"selectDifficulty('hard')\">Hard &#x1F512;</button>" +
  "<button class='diff-btn locked' data-diff='expert' onclick=\"selectDifficulty('expert')\">Expert &#x1F512;</button>" +
  "</div>" +
  "<div style='display:flex;gap:16px;align-items:center;'>" +
  "<div class='meta-item'>&#9201;<span class='meta-value timer-digits' id='timerDisplay'>00:00</span></div>" +
  "<div class='meta-item'>&#10007;<span class='meta-value' id='mistakeDisplay'>0 / 3</span></div>" +
  "</div></div>"
);

// ── Grid styles ─────────────────────────────────────────────────────────────
html.raw(
  "<style>" +
  ".sudoku-grid{display:grid;grid-template-columns:repeat(9,1fr);" +
  "border:2px solid var(--parchment);border-radius:var(--r);overflow:hidden;user-select:none;}" +
  ".cell{width:52px;height:52px;display:flex;align-items:center;justify-content:center;" +
  "font-family:var(--mono);font-size:20px;font-weight:500;cursor:pointer;position:relative;" +
  "transition:background .1s;border:1px solid var(--border);background:var(--surface);color:var(--parchment);}" +
  ".cell.given{color:var(--teal);background:var(--teal-dim);font-weight:700;}" +
  ".cell.selected{background:rgba(226,84,60,.18)!important;box-shadow:inset 0 0 0 2px var(--accent);}" +
  ".cell.highlight{background:rgba(78,201,176,.08);}" +
  ".cell.error{color:var(--accent)!important;background:var(--accent-dim)!important;}" +
  ".cell.box-right{border-right:2px solid var(--parchment);}" +
  ".cell.box-bottom{border-bottom:2px solid var(--parchment);}" +
  ".cell-notes{display:grid;grid-template-columns:repeat(3,1fr);width:100%;height:100%;padding:2px;}" +
  ".cell-note{font-size:8px;font-family:var(--mono);display:flex;align-items:center;" +
  "justify-content:center;color:var(--muted);line-height:1;}" +
  "@keyframes correctFlash{0%{background:rgba(106,153,85,.4);transform:scale(1.06)}" +
  "60%{background:rgba(106,153,85,.2);transform:scale(1.02)}100%{background:var(--surface);transform:scale(1)}}" +
  "@keyframes shake{0%,100%{transform:translateX(0)}20%{transform:translateX(-5px)}" +
  "40%{transform:translateX(5px)}60%{transform:translateX(-4px)}80%{transform:translateX(3px)}}" +
  "@keyframes winWave{0%{background:var(--surface)}30%{background:rgba(78,201,176,.4);transform:scale(1.05)}" +
  "60%{background:rgba(226,84,60,.3)}100%{background:rgba(78,201,176,.15)}}" +
  ".correct-flash{animation:correctFlash .4s ease forwards;}" +
  ".shake{animation:shake .35s ease;}" +
  ".win-wave{animation:winWave .6s ease forwards;}" +
  "</style>"
);

// ── Control panel styles ────────────────────────────────────────────────────
html.raw(
  "<style>" +
  ".control-panel{display:flex;flex-direction:column;gap:14px;min-width:180px;max-width:220px;}" +
  ".panel-section{background:var(--surface);border:1px solid var(--border);border-radius:var(--r);padding:14px;}" +
  ".panel-label{font-family:var(--mono);font-size:10px;letter-spacing:.12em;" +
  "text-transform:uppercase;color:var(--accent);margin-bottom:10px;}" +
  ".numpad{display:grid;grid-template-columns:repeat(3,1fr);gap:6px;}" +
  ".num-btn{background:var(--surface2);border:1px solid var(--border);color:var(--parchment);" +
  "font-family:var(--mono);font-size:18px;font-weight:600;height:46px;border-radius:var(--r);" +
  "cursor:pointer;transition:all .12s;display:flex;align-items:center;justify-content:center;position:relative;}" +
  ".num-btn:hover{border-color:var(--teal);color:var(--teal);background:var(--teal-dim);}" +
  ".num-btn.used{opacity:.35;}" +
  ".num-count{position:absolute;top:3px;right:5px;font-size:8px;color:var(--muted);font-weight:400;}" +
  ".action-btns{display:flex;flex-direction:column;gap:6px;}" +
  ".action-btn{background:var(--surface2);border:1px solid var(--border);color:var(--parchment);" +
  "font-family:var(--mono);font-size:12px;padding:9px 14px;border-radius:var(--r);" +
  "cursor:pointer;text-align:left;transition:all .12s;display:flex;align-items:center;gap:8px;}" +
  ".action-btn:hover{border-color:var(--teal);color:var(--teal);}" +
  ".action-btn.danger:hover{border-color:var(--accent);color:var(--accent);}" +
  ".action-btn.note-active{border-color:var(--amber);color:var(--amber);background:rgba(206,145,120,.1);}" +
  ".stat-row{display:flex;justify-content:space-between;font-size:12px;padding:4px 0;border-bottom:1px solid var(--border);}" +
  ".stat-row:last-child{border-bottom:none;}" +
  ".stat-label{color:var(--muted);}" +
  ".stat-val{font-family:var(--mono);color:var(--parchment);}" +
  "</style>"
);

// ── Game layout: grid + panel ───────────────────────────────────────────────
html.raw(
  "<div class='game-layout'>" +
  "<div style='position:relative;flex-shrink:0;'>" +
  "<div class='sudoku-grid' id='grid'></div>" +
  "</div>" +
  "<div class='control-panel'>" +
  "<div class='panel-section'>" +
  "<div class='panel-label'>Numbers</div>" +
  "<div class='numpad' id='numpad'></div>" +
  "</div>" +
  "<div class='panel-section'>" +
  "<div class='panel-label'>Actions</div>" +
  "<div class='action-btns'>" +
  "<button class='action-btn' id='noteToggle' onclick='toggleNoteMode()'>" +
  "&#9999; Notes <span style='margin-left:auto;font-size:10px;color:var(--muted)' id='noteStatus'>OFF</span></button>" +
  "<button class='action-btn' onclick='useHint()'>" +
  "&#128161; Hint <span style='margin-left:auto;font-size:10px;color:var(--muted)' id='hintCount'>3 left</span></button>" +
  "<button class='action-btn' onclick='eraseCell()'>&#9003; Erase</button>" +
  "<button class='action-btn danger' onclick='newGame()'>&#8635; New Game</button>" +
  "</div></div>" +
  "<div class='panel-section'>" +
  "<div class='panel-label'>Session</div>" +
  "<div class='stat-row'><span class='stat-label'>Solved</span><span class='stat-val' id='statSolved'>0</span></div>" +
  "<div class='stat-row'><span class='stat-label'>Best time</span><span class='stat-val' id='statBest'>--:--</span></div>" +
  "<div class='stat-row'><span class='stat-label'>Streak</span><span class='stat-val' id='statStreak'>0</span></div>" +
  "<div class='stat-row'><span class='stat-label'>Difficulty</span><span class='stat-val' id='statDiff' style='color:var(--teal)'>Easy</span></div>" +
  "</div></div></div>" +
  "</div>"
);

// ── Sign-in modal ───────────────────────────────────────────────────────────
html.raw(
  "<style>" +
  ".modal-backdrop{position:fixed;inset:0;background:rgba(15,17,23,.85);" +
  "backdrop-filter:blur(4px);display:flex;align-items:center;justify-content:center;" +
  "z-index:1000;animation:fadeIn .2s ease;}" +
  ".modal-backdrop.hidden{display:none;}" +
  ".modal{background:var(--surface);border:1px solid var(--border);border-radius:4px;" +
  "padding:32px;width:100%;max-width:380px;animation:slideUp .25s ease;}" +
  "@keyframes fadeIn{from{opacity:0}to{opacity:1}}" +
  "@keyframes slideUp{from{transform:translateY(16px);opacity:0}to{transform:translateY(0);opacity:1}}" +
  ".modal-logo{font-family:var(--mono);font-size:18px;color:var(--teal);margin-bottom:4px;}" +
  ".modal-title{font-size:18px;font-weight:600;margin-bottom:4px;}" +
  ".modal-sub{font-size:13px;color:var(--muted);margin-bottom:20px;}" +
  ".input-group{display:flex;flex-direction:column;gap:6px;margin-bottom:14px;}" +
  ".input-label{font-size:12px;color:var(--muted);font-family:var(--mono);}" +
  ".modal-input{background:var(--bg);border:1px solid var(--border);color:var(--parchment);" +
  "font-family:var(--mono);font-size:13px;padding:10px 12px;border-radius:var(--r);" +
  "outline:none;transition:border-color .15s;width:100%;}" +
  ".modal-input:focus{border-color:var(--accent);}" +
  ".modal-submit{width:100%;background:var(--accent);border:none;color:#1a0a07;" +
  "font-family:var(--mono);font-size:13px;font-weight:700;padding:11px;" +
  "border-radius:var(--r);cursor:pointer;transition:background .15s;}" +
  ".modal-submit:hover{background:#ee6b53;}" +
  ".modal-guest{background:none;border:1px solid var(--border);color:var(--muted);" +
  "font-family:var(--mono);font-size:12px;padding:9px;border-radius:var(--r);" +
  "cursor:pointer;transition:all .15s;width:100%;margin-top:8px;}" +
  ".modal-guest:hover{border-color:var(--teal);color:var(--teal);}" +
  ".modal-divider{display:flex;align-items:center;gap:10px;margin:14px 0;" +
  "color:var(--muted);font-size:11px;font-family:var(--mono);}" +
  ".modal-divider::before,.modal-divider::after{content:'';flex:1;height:1px;background:var(--border);}" +
  ".modal-switch{margin-top:14px;font-size:12px;color:var(--muted);text-align:center;}" +
  ".modal-switch a{color:var(--teal);cursor:pointer;text-decoration:none;}" +
  "</style>" +
  "<div class='modal-backdrop' id='signInModal'>" +
  "<div class='modal'>" +
  "<div class='modal-logo'>my<span style='color:var(--accent)'>.</span>lang</div>" +
  "<div class='modal-title' id='modalTitle'>Welcome back</div>" +
  "<div class='modal-sub' id='modalDesc'>Sign in to save progress, unlock levels, and track stats.</div>" +
  "<div class='input-group' id='usernameGroup' style='display:none'>" +
  "<label class='input-label'>Username</label>" +
  "<input type='text' class='modal-input' id='usernameInput' placeholder='Choose a username'></div>" +
  "<div class='input-group'><label class='input-label'>Email</label>" +
  "<input type='email' class='modal-input' id='emailInput' placeholder='you@example.com'></div>" +
  "<div class='input-group'><label class='input-label'>Password</label>" +
  "<input type='password' class='modal-input' id='passwordInput' placeholder='&#9679;&#9679;&#9679;&#9679;&#9679;&#9679;&#9679;&#9679;'></div>" +
  "<button class='modal-submit' id='modalSubmit' onclick='handleSignIn()'>Sign In</button>" +
  "<div class='modal-divider'>or</div>" +
  "<button class='modal-guest' onclick='continueAsGuest()'>Continue as Guest</button>" +
  "<div class='modal-switch' id='modalSwitch'>No account? <a onclick='toggleAuthMode()'>Create one</a></div>" +
  "</div></div>"
);

// ── Win overlay + toast + particles ────────────────────────────────────────
html.raw(
  "<style>" +
  ".win-overlay{position:fixed;inset:0;background:rgba(15,17,23,.9);" +
  "display:flex;align-items:center;justify-content:center;z-index:900;animation:fadeIn .3s ease;}" +
  ".win-overlay.hidden{display:none;}" +
  ".win-card{background:var(--surface);border:1px solid var(--teal);border-radius:4px;" +
  "padding:36px;text-align:center;max-width:340px;" +
  "animation:winCardIn .45s cubic-bezier(.34,1.56,.64,1);" +
  "box-shadow:0 0 40px rgba(78,201,176,.12);}" +
  "@keyframes winCardIn{from{transform:scale(.7);opacity:0}to{transform:scale(1);opacity:1}}" +
  ".win-emoji{font-size:48px;margin-bottom:12px;display:block;animation:spinIn .6s ease;}" +
  "@keyframes spinIn{from{transform:rotate(-20deg) scale(.5)}to{transform:rotate(0) scale(1)}}" +
  ".win-title{font-size:24px;font-weight:700;margin-bottom:6px;}" +
  ".win-sub{font-size:13px;color:var(--muted);margin-bottom:20px;}" +
  ".win-stats{display:flex;gap:20px;justify-content:center;margin-bottom:24px;}" +
  ".win-stat{text-align:center;}" +
  ".win-stat-val{font-family:var(--mono);font-size:22px;font-weight:700;color:var(--teal);display:block;margin-bottom:2px;}" +
  ".win-stat-label{font-size:11px;color:var(--muted);font-family:var(--mono);}" +
  ".win-btn-primary{background:var(--accent);border:none;color:#1a0a07;font-family:var(--mono);" +
  "font-size:13px;font-weight:700;padding:11px;border-radius:var(--r);cursor:pointer;" +
  "transition:background .15s;width:100%;margin-bottom:8px;}" +
  ".win-btn-primary:hover{background:#ee6b53;}" +
  ".win-btn-secondary{background:var(--surface2);border:1px solid var(--border);" +
  "color:var(--parchment);font-family:var(--mono);font-size:12px;padding:9px;" +
  "border-radius:var(--r);cursor:pointer;transition:all .15s;width:100%;}" +
  ".win-btn-secondary:hover{border-color:var(--teal);color:var(--teal);}" +
  ".toast{position:fixed;bottom:28px;left:50%;transform:translateX(-50%);" +
  "background:var(--surface);border:1px solid var(--border);color:var(--parchment);" +
  "font-family:var(--mono);font-size:12px;padding:10px 20px;border-radius:var(--r);" +
  "z-index:800;animation:toastIn .25s ease;white-space:nowrap;}" +
  ".toast.hidden{display:none;}" +
  ".toast.terror{border-color:var(--accent);color:var(--accent);}" +
  ".toast.tsuccess{border-color:var(--green);color:var(--green);}" +
  "@keyframes toastIn{from{opacity:0;transform:translateX(-50%) translateY(12px)}" +
  "to{opacity:1;transform:translateX(-50%) translateY(0)}}" +
  ".particle{position:fixed;width:6px;height:6px;border-radius:50%;pointer-events:none;" +
  "z-index:850;animation:particleFly 1s ease forwards;}" +
  "@keyframes particleFly{0%{opacity:1;transform:translate(0,0) scale(1)}" +
  "100%{opacity:0;transform:translate(var(--tx),var(--ty)) scale(0)}}" +
  "@media(max-width:680px){" +
  ".cell{width:38px;height:38px;font-size:15px;}" +
  ".control-panel{max-width:100%;min-width:unset;width:100%;flex-direction:row;flex-wrap:wrap;}" +
  ".panel-section{flex:1 1 140px;}" +
  "}" +
  "@media(prefers-reduced-motion:reduce){*,*::before,*::after{animation:none!important;transition:none!important;}}" +
  "</style>" +
  "<div class='win-overlay hidden' id='winOverlay'>" +
  "<div class='win-card'>" +
  "<span class='win-emoji'>&#127881;</span>" +
  "<div class='win-title'>Puzzle Solved!</div>" +
  "<div class='win-sub'>Well done on <span id='winDiff'>Easy</span> difficulty</div>" +
  "<div class='win-stats'>" +
  "<div class='win-stat'><span class='win-stat-val' id='winTime'>--:--</span><span class='win-stat-label'>time</span></div>" +
  "<div class='win-stat'><span class='win-stat-val' id='winMistakes'>0</span><span class='win-stat-label'>mistakes</span></div>" +
  "<div class='win-stat'><span class='win-stat-val' id='winStreak'>1</span><span class='win-stat-label'>streak</span></div>" +
  "</div>" +
  "<div id='unlockMsg' style='font-size:12px;color:var(--teal);font-family:var(--mono);margin-bottom:18px;display:none;'></div>" +
  "<button class='win-btn-primary' onclick='newGame()'>Play Again</button>" +
  "<button class='win-btn-secondary' onclick='closeWin()'>Keep Board</button>" +
  "</div></div>" +
  "<div class='toast hidden' id='toast'></div>"
);

// ── Complete game JavaScript engine ────────────────────────────────────────
html.raw(
  "<script>" +
  "(function(){" +

  // ── State ────────────────────────────────────────────────────────────────
  "const S={user:null,isGuest:false,diff:'easy',puzzle:null,solution:null,board:null," +
  "notes:null,selected:-1,noteMode:false,hints:3,mistakes:0,maxMistakes:3,solved:false," +
  "timerSecs:0,timerInt:null,stats:{solved:0,best:null,streak:0}," +
  "unlocked:{easy:true,medium:false,hard:false,expert:false}};" +
  "const DIFF_CLUES={easy:40,medium:32,hard:26,expert:22};" +

  // ── Storage ──────────────────────────────────────────────────────────────
  "function saveState(){try{localStorage.setItem('pacer_sudoku_v2',JSON.stringify(" +
  "{user:S.user,isGuest:S.isGuest,unlocked:S.unlocked,stats:S.stats}));}catch(e){}}" +
  "function loadState(){try{const r=localStorage.getItem('pacer_sudoku_v2');" +
  "if(!r)return;const d=JSON.parse(r);" +
  "if(d.user)S.user=d.user;if(d.isGuest)S.isGuest=d.isGuest;" +
  "if(d.unlocked)Object.assign(S.unlocked,d.unlocked);" +
  "if(d.stats)Object.assign(S.stats,d.stats);}catch(e){}}" +

  // ── Auth ─────────────────────────────────────────────────────────────────
  "let authMode='signin';" +
  "function showSignIn(){document.getElementById('signInModal').classList.remove('hidden');}" +
  "function hideSignIn(){document.getElementById('signInModal').classList.add('hidden');}" +
  "function toggleAuthMode(){" +
  "authMode=authMode==='signin'?'signup':'signin';" +
  "document.getElementById('modalTitle').textContent=authMode==='signin'?'Welcome back':'Create account';" +
  "document.getElementById('modalSubmit').textContent=authMode==='signin'?'Sign In':'Create Account';" +
  "document.getElementById('modalSwitch').innerHTML=authMode==='signin'?" +
  "'No account? <a onclick=\"toggleAuthMode()\">Create one</a>':" +
  "'Have an account? <a onclick=\"toggleAuthMode()\">Sign in</a>';" +
  "document.getElementById('usernameGroup').style.display=authMode==='signup'?'':'none';}" +

  "function handleSignIn(){" +
  "const email=document.getElementById('emailInput').value.trim();" +
  "const pass=document.getElementById('passwordInput').value;" +
  "const uname=document.getElementById('usernameInput').value.trim();" +
  "if(!email||!pass){showToast('Please fill in all fields','terror');return;}" +
  "const name=authMode==='signup'?(uname||email.split('@')[0]):email.split('@')[0];" +
  "S.user={name,email};S.isGuest=false;S.unlocked.medium=true;" +
  "saveState();hideSignIn();updateHeaderUser();updateDiffButtons();" +
  "showToast('Welcome, '+name+'! \uD83D\uDC4B','tsuccess');}" +

  "function continueAsGuest(){S.user=null;S.isGuest=true;" +
  "hideSignIn();updateHeaderUser();showToast('Playing as guest');}" +

  "function updateHeaderUser(){const hr=document.getElementById('headerRight');" +
  "if(S.user){const ini=S.user.name.slice(0,2).toUpperCase();" +
  "hr.innerHTML='<div class=\"user-badge\" onclick=\"handleSignOut()\">'+" +
  "'<div class=\"user-avatar\">'+ini+'</div>'+" +
  "'<span>'+S.user.name+'</span>'+" +
  "'<span style=\"color:var(--muted);font-size:10px;\">\u21A9</span></div>';}" +
  "else if(S.isGuest){hr.innerHTML='<div class=\"user-badge\" onclick=\"showSignIn()\">'+" +
  "'<div class=\"user-avatar\" style=\"background:var(--border);\">?</div>'+" +
  "'<span style=\"color:var(--muted)\">Guest</span></div>';}" +
  "else{hr.innerHTML='<button class=\"sign-in-btn\" onclick=\"showSignIn()\">Sign In</button>';}}" +

  "function handleSignOut(){S.user=null;S.isGuest=false;saveState();updateHeaderUser();" +
  "showToast('Signed out');}" +

  // ── Difficulty ────────────────────────────────────────────────────────────
  "function selectDifficulty(diff){" +
  "if(!S.unlocked[diff]){" +
  "if(!S.user&&!S.isGuest){showSignIn();return;}" +
  "if(diff==='medium'){showToast('Solve 1 Easy puzzle to unlock Medium \uD83D\uDD12');return;}" +
  "if(diff==='hard'){showToast('Win 3 Medium puzzles to unlock Hard \uD83D\uDD12');return;}" +
  "if(diff==='expert'){showToast('Win 5 Hard puzzles to unlock Expert \uD83D\uDD12');return;}" +
  "}S.diff=diff;updateDiffButtons();" +
  "document.getElementById('statDiff').textContent=diff.charAt(0).toUpperCase()+diff.slice(1);" +
  "newGame();}" +

  "function updateDiffButtons(){" +
  "document.querySelectorAll('.diff-btn').forEach(b=>{" +
  "const d=b.dataset.diff;b.classList.remove('active','locked');" +
  "if(d===S.diff)b.classList.add('active');" +
  "if(!S.unlocked[d])b.classList.add('locked');" +
  "b.innerHTML=d.charAt(0).toUpperCase()+d.slice(1)+(S.unlocked[d]?'':' \uD83D\uDD12');});}" +

  // ── Generator ─────────────────────────────────────────────────────────────
  "function shuffle(a){for(let i=a.length-1;i>0;i--){const j=Math.floor(Math.random()*(i+1));[a[i],a[j]]=[a[j],a[i]];}return a;}" +
  "function isValid(b,idx,n){const row=Math.floor(idx/9),col=idx%9;" +
  "const br=Math.floor(row/3)*3,bc=Math.floor(col/3)*3;" +
  "for(let c=0;c<9;c++)if(b[row*9+c]===n&&c!==col)return false;" +
  "for(let r=0;r<9;r++)if(b[r*9+col]===n&&r!==row)return false;" +
  "for(let r=br;r<br+3;r++)for(let c=bc;c<bc+3;c++)" +
  "{if(r===row&&c===col)continue;if(b[r*9+c]===n)return false;}" +
  "return true;}" +
  "function fillBoard(b){const nums=shuffle([1,2,3,4,5,6,7,8,9]);" +
  "for(let i=0;i<81;i++){if(b[i]===0){for(const n of nums){" +
  "if(isValid(b,i,n)){b[i]=n;if(fillBoard(b))return true;b[i]=0;}}return false;}}return true;}" +
  "function countSolutions(b,limit=2){let c=0;" +
  "function s(b){for(let i=0;i<81;i++){if(b[i]===0){" +
  "for(let n=1;n<=9;n++){if(isValid(b,i,n)){b[i]=n;s([...b]);b[i]=0;if(c>=limit)return;}}return;}}c++;}" +
  "s([...b]);return c;}" +
  "function generatePuzzle(clues){const sol=Array(81).fill(0);fillBoard(sol);" +
  "const puz=[...sol];const idxs=shuffle([...Array(81).keys()]);" +
  "let removed=0,target=81-clues;" +
  "for(const idx of idxs){if(removed>=target)break;const bk=puz[idx];puz[idx]=0;" +
  "if(countSolutions(puz)===1){removed++;}else{puz[idx]=bk;}}" +
  "return{puzzle:puz,solution:sol};}" +

  // ── Lifecycle ─────────────────────────────────────────────────────────────
  "function newGame(){closeWin();stopTimer();" +
  "S.selected=-1;S.noteMode=false;S.hints=3;S.mistakes=0;S.solved=false;S.timerSecs=0;" +
  "const{puzzle,solution}=generatePuzzle(DIFF_CLUES[S.diff]);" +
  "S.puzzle=puzzle;S.solution=solution;S.board=[...puzzle];" +
  "S.notes=Array(81).fill(null).map(()=>new Set());" +
  "renderGrid();updateNumpad();updateNoteBtn();updateHintCount();updateMistakeDisplay();" +
  "updateTimerDisplay();startTimer();}" +

  // ── Render ────────────────────────────────────────────────────────────────
  "function renderGrid(){const g=document.getElementById('grid');g.innerHTML='';" +
  "for(let i=0;i<81;i++){const c=document.createElement('div');" +
  "c.className='cell';c.dataset.idx=i;" +
  "c.dataset.row=Math.floor(i/9);c.dataset.col=i%9;" +
  "const row=Math.floor(i/9),col=i%9;" +
  "if(col===2||col===5)c.classList.add('box-right');" +
  "if(row===2||row===5)c.classList.add('box-bottom');" +
  "c.addEventListener('click',()=>selectCell(i));" +
  "renderCellContent(c,i);g.appendChild(c);}}" +

  "function renderCellContent(c,i){" +
  "c.classList.remove('given','error','correct-flash','shake','win-wave');" +
  "const boxR=c.classList.contains('box-right'),boxB=c.classList.contains('box-bottom');" +
  "c.innerHTML='';" +
  "if(boxR)c.classList.add('box-right');if(boxB)c.classList.add('box-bottom');" +
  "if(S.puzzle[i]!==0){c.textContent=S.puzzle[i];c.classList.add('given');}" +
  "else if(S.board[i]!==0){c.textContent=S.board[i];" +
  "if(S.board[i]!==S.solution[i])c.classList.add('error');}" +
  "else if(S.notes[i].size>0){const ng=document.createElement('div');" +
  "ng.className='cell-notes';" +
  "for(let n=1;n<=9;n++){const nd=document.createElement('div');" +
  "nd.className='cell-note';nd.textContent=S.notes[i].has(n)?n:'';" +
  "ng.appendChild(nd);}c.appendChild(ng);}}" +

  "function refreshCell(i){const c=document.querySelector('.cell[data-idx=\"'+i+'\"]');" +
  "if(c)renderCellContent(c,i);}" +

  "function updateHighlights(){" +
  "document.querySelectorAll('.cell').forEach(c=>{" +
  "c.classList.remove('selected','highlight');" +
  "const i=+c.dataset.idx,row=Math.floor(i/9),col=i%9;" +
  "if(S.selected===-1)return;" +
  "const sr=Math.floor(S.selected/9),sc=S.selected%9;" +
  "const sv=S.board[S.selected]||S.puzzle[S.selected];" +
  "if(i===S.selected){c.classList.add('selected');}" +
  "else if(row===sr||col===sc||" +
  "(Math.floor(row/3)===Math.floor(sr/3)&&Math.floor(col/3)===Math.floor(sc/3)))" +
  "{c.classList.add('highlight');}" +
  "else if(sv&&(S.board[i]===sv||S.puzzle[i]===sv)){c.classList.add('highlight');}});}" +

  "function updateNumpad(){const p=document.getElementById('numpad');p.innerHTML='';" +
  "const counts=Array(10).fill(0);" +
  "for(let i=0;i<81;i++){const v=S.board[i]||S.puzzle[i];if(v)counts[v]++;}" +
  "for(let n=1;n<=9;n++){const b=document.createElement('button');" +
  "b.className='num-btn'+(counts[n]>=9?' used':'');" +
  "b.innerHTML=n+'<span class=\"num-count\">'+(9-counts[n])+'</span>';" +
  "b.addEventListener('click',()=>placeNumber(n));p.appendChild(b);}}" +

  "function updateNoteBtn(){const b=document.getElementById('noteToggle')," +
  "s=document.getElementById('noteStatus');" +
  "if(S.noteMode){b.classList.add('note-active');s.textContent='ON';s.style.color='var(--amber)';}" +
  "else{b.classList.remove('note-active');s.textContent='OFF';s.style.color='var(--muted)';}}" +
  "function updateHintCount(){document.getElementById('hintCount').textContent=S.hints+' left';}" +
  "function updateMistakeDisplay(){document.getElementById('mistakeDisplay').textContent=S.mistakes+' / '+S.maxMistakes;}" +

  // ── Interaction ────────────────────────────────────────────────────────────
  "function selectCell(i){if(S.solved)return;" +
  "S.selected=(S.selected===i)?-1:i;updateHighlights();}" +

  "function placeNumber(n){if(S.solved)return;" +
  "const i=S.selected;if(i===-1||S.puzzle[i]!==0)return;" +
  "if(S.noteMode){if(S.board[i]!==0)return;" +
  "S.notes[i].has(n)?S.notes[i].delete(n):S.notes[i].add(n);" +
  "refreshCell(i);return;}" +
  "S.board[i]=n;S.notes[i].clear();clearRelatedNotes(i,n);refreshCell(i);" +
  "const c=document.querySelector('.cell[data-idx=\"'+i+'\"]');" +
  "if(n!==S.solution[i]){S.mistakes++;updateMistakeDisplay();" +
  "c.classList.add('shake');setTimeout(()=>c.classList.remove('shake'),400);" +
  "showToast('Mistake! '+S.mistakes+'/'+S.maxMistakes,'terror');" +
  "if(S.mistakes>=S.maxMistakes){showToast('Too many mistakes — resetting!','terror');" +
  "setTimeout(()=>newGame(),1400);return;}}" +
  "else{c.classList.add('correct-flash');" +
  "setTimeout(()=>c.classList.remove('correct-flash'),450);checkWin();}" +
  "updateNumpad();updateHighlights();}" +

  "function clearRelatedNotes(idx,n){" +
  "const row=Math.floor(idx/9),col=idx%9,br=Math.floor(row/3)*3,bc=Math.floor(col/3)*3;" +
  "for(let c=0;c<9;c++)if(c!==col){S.notes[row*9+c].delete(n);refreshCell(row*9+c);}" +
  "for(let r=0;r<9;r++)if(r!==row){S.notes[r*9+col].delete(n);refreshCell(r*9+col);}" +
  "for(let r=br;r<br+3;r++)for(let c=bc;c<bc+3;c++)" +
  "if(r!==row||c!==col){S.notes[r*9+c].delete(n);refreshCell(r*9+c);}}" +

  "function eraseCell(){const i=S.selected;" +
  "if(i===-1||S.puzzle[i]!==0||S.solved)return;" +
  "S.board[i]=0;S.notes[i].clear();refreshCell(i);updateNumpad();updateHighlights();}" +

  "function toggleNoteMode(){S.noteMode=!S.noteMode;updateNoteBtn();}" +

  "function useHint(){if(S.hints<=0||S.solved){showToast('No hints remaining!');return;}" +
  "if(S.selected===-1){showToast('Select a cell first');return;}" +
  "const i=S.selected;if(S.puzzle[i]!==0){showToast('That cell is a given');return;}" +
  "S.hints--;S.board[i]=S.solution[i];S.notes[i].clear();" +
  "clearRelatedNotes(i,S.solution[i]);refreshCell(i);" +
  "updateNumpad();updateHighlights();updateHintCount();" +
  "const c=document.querySelector('.cell[data-idx=\"'+i+'\"]');" +
  "c.classList.add('correct-flash');setTimeout(()=>c.classList.remove('correct-flash'),450);" +
  "showToast('Hint used — '+S.hints+' remaining','tsuccess');checkWin();}" +

  // ── Keyboard ─────────────────────────────────────────────────────────────
  "document.addEventListener('keydown',e=>{" +
  "if(!document.getElementById('signInModal').classList.contains('hidden'))return;" +
  "if(e.key>='1'&&e.key<='9')placeNumber(+e.key);" +
  "if(e.key==='Backspace'||e.key==='Delete')eraseCell();" +
  "if(e.key==='n'||e.key==='N')toggleNoteMode();" +
  "const arrows={ArrowUp:-9,ArrowDown:9,ArrowLeft:-1,ArrowRight:1};" +
  "if(arrows[e.key]!==undefined&&S.selected!==-1){" +
  "const nx=S.selected+arrows[e.key];" +
  "if(nx>=0&&nx<81){S.selected=nx;updateHighlights();}e.preventDefault();}});" +

  // ── Win ──────────────────────────────────────────────────────────────────
  "function checkWin(){for(let i=0;i<81;i++){" +
  "if((S.board[i]||S.puzzle[i])!==S.solution[i])return;}S.solved=true;stopTimer();" +
  "S.stats.solved++;S.stats.streak++;" +
  "if(!S.stats.best||S.timerSecs<S.stats.best)S.stats.best=S.timerSecs;" +
  "let msg='';" +
  "if(S.diff==='easy'&&!S.unlocked.medium){S.unlocked.medium=true;msg='\uD83D\uDD13 Medium unlocked!';}" +
  "if(S.diff==='medium'&&S.stats.streak>=3&&!S.unlocked.hard){S.unlocked.hard=true;msg='\uD83D\uDD13 Hard unlocked!';}" +
  "if(S.diff==='hard'&&S.stats.streak>=5&&!S.unlocked.expert){S.unlocked.expert=true;msg='\uD83D\uDD13 Expert unlocked!';}" +
  "updateDiffButtons();if(S.user)saveState();updateSessionStats();" +
  "document.querySelectorAll('.cell').forEach((c,i)=>{" +
  "const r=Math.floor(i/9),col=i%9;" +
  "setTimeout(()=>c.classList.add('win-wave'),(r+col)*35);});" +
  "setTimeout(launchParticles,400);" +
  "setTimeout(()=>{" +
  "document.getElementById('winTime').textContent=fmtTime(S.timerSecs);" +
  "document.getElementById('winMistakes').textContent=S.mistakes;" +
  "document.getElementById('winStreak').textContent=S.stats.streak;" +
  "document.getElementById('winDiff').textContent=S.diff.charAt(0).toUpperCase()+S.diff.slice(1);" +
  "const ul=document.getElementById('unlockMsg');" +
  "if(msg){ul.textContent=msg;ul.style.display='';}else ul.style.display='none';" +
  "document.getElementById('winOverlay').classList.remove('hidden');" +
  "},1200);}" +

  "function closeWin(){document.getElementById('winOverlay').classList.add('hidden');}" +

  "function launchParticles(){const cols=['#E2543C','#4EC9B0','#F2EBDD','#6A9955','#CE9178'];" +
  "const cx=window.innerWidth/2,cy=window.innerHeight/2;" +
  "for(let p=0;p<40;p++){const el=document.createElement('div');" +
  "el.className='particle';el.style.left=cx+'px';el.style.top=cy+'px';" +
  "el.style.background=cols[p%cols.length];" +
  "const a=Math.random()*Math.PI*2,d=80+Math.random()*200;" +
  "el.style.setProperty('--tx',Math.cos(a)*d+'px');" +
  "el.style.setProperty('--ty',Math.sin(a)*d+'px');" +
  "el.style.animationDelay=(Math.random()*.3)+'s';" +
  "document.body.appendChild(el);setTimeout(()=>el.remove(),1500);}}" +

  // ── Timer ─────────────────────────────────────────────────────────────────
  "function startTimer(){S.timerInt=setInterval(()=>{S.timerSecs++;updateTimerDisplay();},1000);}" +
  "function stopTimer(){clearInterval(S.timerInt);}" +
  "function updateTimerDisplay(){document.getElementById('timerDisplay').textContent=fmtTime(S.timerSecs);}" +
  "function fmtTime(s){return String(Math.floor(s/60)).padStart(2,'0')+':'+String(s%60).padStart(2,'0');}" +

  // ── Stats ─────────────────────────────────────────────────────────────────
  "function updateSessionStats(){" +
  "document.getElementById('statSolved').textContent=S.stats.solved;" +
  "document.getElementById('statBest').textContent=S.stats.best?fmtTime(S.stats.best):'--:--';" +
  "document.getElementById('statStreak').textContent=S.stats.streak;}" +

  // ── Toast ─────────────────────────────────────────────────────────────────
  "let _tt=null;" +
  "function showToast(msg,type=''){const t=document.getElementById('toast');" +
  "t.textContent=msg;t.className='toast '+(type||'');" +
  "clearTimeout(_tt);_tt=setTimeout(()=>t.classList.add('hidden'),2800);}" +

  // ── Init ──────────────────────────────────────────────────────────────────
  "loadState();updateHeaderUser();updateDiffButtons();updateSessionStats();newGame();" +
  "if(!S.user&&!S.isGuest)setTimeout(()=>showSignIn(),700);" +

  // expose globals for HTML onclick attributes
  "Object.assign(window,{selectDifficulty,toggleNoteMode,useHint,eraseCell,newGame," +
  "showSignIn,handleSignIn,continueAsGuest,toggleAuthMode,closeWin,handleSignOut});" +
  "})();" +
  "</script>"
);

// ── Launch ─────────────────────────────────────────────────────────────────
html.show(["browser", "file"]);
print("Sudoku game launched in browser. Have fun!");
