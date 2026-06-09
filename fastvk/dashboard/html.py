DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>FastVK Dashboard</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Inter:ital,opsz,wght@0,14..32,400;0,14..32,500;0,14..32,600;0,14..32,700&display=swap" rel="stylesheet">
  <style>
    /* ── Tokens (shadcn exact oklch→hex) ── */
    :root {
      --radius: 0.625rem;
      --bg:          #ffffff; --fg:          #09090b;
      --card:        #ffffff; --card-fg:     #09090b;
      --muted:       #f4f4f5; --muted-fg:    #71717a;
      --border:      #e4e4e7; --input:       #e4e4e7;
      --primary:     #0d9488; --primary-fg:  #ffffff;
      --destructive: #ef4444;
      --sb:          #fafafa; --sb-fg:       #09090b;
      --sb-acc:      #f4f4f5; --sb-acc-fg:   #18181b;
      --sb-border:   #e4e4e7; --sb-muted:    #71717a;
      --sb-primary:  #0d9488;
      --sw: 256px; --swi: 48px;
    }
    .dark {
      --bg:          #09090b; --fg:          #fafafa;
      --card:        #18181b; --card-fg:     #fafafa;
      --muted:       #27272a; --muted-fg:    #a1a1aa;
      --border:      rgba(255,255,255,.1);
      --primary:     #14b8a6; --primary-fg:  #fafafa;
      --destructive: #f87171;
      --sb:          #18181b; --sb-fg:       #fafafa;
      --sb-acc:      #27272a; --sb-acc-fg:   #fafafa;
      --sb-border:   rgba(255,255,255,.08); --sb-muted: #a1a1aa;
      --sb-primary:  #14b8a6;
    }

    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
    html, body { height: 100%; }
    body {
      font-family: 'Inter', system-ui, -apple-system, sans-serif;
      font-size: 14px; line-height: 1.5;
      background: var(--bg); color: var(--fg);
      -webkit-font-smoothing: antialiased;
    }
    ::-webkit-scrollbar { width: 4px; height: 4px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: var(--border); border-radius: 4px; }

    /* ════ LAYOUT ════ */
    .root { display: flex; height: 100svh; width: 100%; overflow: hidden; }

    /* ════ SIDEBAR GAP (holds space) ════ */
    .sb-gap {
      width: var(--sw); flex-shrink: 0;
      transition: width .2s ease-linear;
    }
    .sb-gap.c { width: var(--swi); }

    /* ════ SIDEBAR CONTAINER (fixed) ════ */
    .sb {
      position: fixed; inset-y: 0; left: 0; z-index: 20;
      width: var(--sw); height: 100svh;
      display: flex; flex-direction: column;
      background: var(--sb); border-right: 1px solid var(--sb-border);
      transition: width .2s ease-linear;
      overflow: hidden;
    }
    .sb.c { width: var(--swi); }

    /* ── Header ── */
    .sb-hd {
      display: flex; align-items: center; gap: 10px;
      padding: 14px 8px 12px; height: 64px; flex-shrink: 0;
      overflow: hidden;
    }
    .sb-mark {
      width: 28px; height: 28px; flex-shrink: 0; border-radius: 8px;
      background: var(--sb-primary); color: #fff;
      display: flex; align-items: center; justify-content: center;
      font-size: 11px; font-weight: 700; letter-spacing: -.5px;
    }
    .sb-wordmark {
      font-size: 15px; font-weight: 600; letter-spacing: -.03em;
      color: var(--sb-fg); white-space: nowrap;
      transition: opacity .15s, width .2s; overflow: hidden;
    }
    .sb-wordmark em { font-style: normal; color: var(--sb-primary); }
    .sb.c .sb-wordmark { opacity: 0; width: 0; }

    /* ── Content ── */
    .sb-body { flex: 1; padding: 8px; display: flex; flex-direction: column; gap: 4px; overflow-y: auto; overflow-x: hidden; min-height: 0; }

    /* Group label */
    .sb-lbl {
      height: 32px; padding: 0 8px; display: flex; align-items: center;
      font-size: 12px; font-weight: 500; color: var(--sb-fg); opacity: .6;
      white-space: nowrap; overflow: hidden;
      transition: margin-top .2s, opacity .15s;
    }
    .sb.c .sb-lbl { margin-top: -32px; opacity: 0; pointer-events: none; }

    /* Nav item */
    .sb-item {
      position: relative;
      display: flex; align-items: center; gap: 8px;
      width: 100%; padding: 0 8px; height: 32px;
      border-radius: 8px; border: none; background: none; cursor: pointer;
      font-size: 14px; font-weight: 400; color: var(--sb-fg);
      white-space: nowrap; overflow: hidden; text-align: left;
      transition: background .1s, color .1s;
    }
    .sb-item:hover { background: var(--sb-acc); color: var(--sb-acc-fg); }
    .sb-item.on    { background: var(--sb-acc); color: var(--sb-acc-fg); font-weight: 500; }
    .sb-item svg   { width: 16px; height: 16px; flex-shrink: 0; }
    .sb-item-label { overflow: hidden; text-overflow: ellipsis; flex: 1; }
    .sb-item-badge {
      display: inline-flex; align-items: center; justify-content: center;
      min-width: 18px; height: 18px; padding: 0 5px;
      border-radius: 9px; background: var(--muted); border: 1px solid var(--border);
      font-size: 10px; font-weight: 600; color: var(--muted-fg); flex-shrink: 0;
    }
    /* collapsed: icon only + tooltip */
    .sb.c .sb-item  { width: 32px; height: 32px; padding: 8px; justify-content: center; }
    .sb.c .sb-item-label,
    .sb.c .sb-item-badge { display: none; }
    /* tooltip */
    .sb.c .sb-item::after {
      content: attr(title);
      position: absolute; left: calc(100% + 10px); top: 50%; transform: translateY(-50%);
      padding: 5px 10px; border-radius: 6px;
      background: var(--fg); color: var(--bg);
      font-size: 12px; font-weight: 500;
      white-space: nowrap; pointer-events: none;
      opacity: 0; transition: opacity .1s;
      box-shadow: 0 4px 12px rgba(0,0,0,.15);
    }
    .sb.c .sb-item:hover::after { opacity: 1; }

    /* ── Separator ── */
    .sb-sep { height: 1px; background: var(--sb-border); margin: 4px 0; }

    /* ── Footer ── */
    .sb-ft { padding: 8px; flex-shrink: 0; border-top: 1px solid var(--sb-border); overflow: hidden; }

    /* Appearance dropdown trigger */
    .sb-app-wrap { position: relative; }
    .sb-app-btn {
      display: flex; align-items: center; gap: 8px;
      width: 100%; padding: 0 8px; height: 32px;
      border-radius: 8px; border: none; background: none; cursor: pointer;
      font-size: 14px; font-weight: 400; color: var(--sb-muted);
      white-space: nowrap; overflow: hidden; text-align: left;
      transition: background .1s, color .1s;
    }
    .sb-app-btn:hover { background: var(--sb-acc); color: var(--sb-acc-fg); }
    .sb-app-btn svg { width: 16px; height: 16px; flex-shrink: 0; }
    .sb.c .sb-app-btn { width: 32px; height: 32px; padding: 8px; justify-content: center; }
    .sb.c .app-lbl { display: none; }
    .sb.c .sb-app-btn::after {
      content: 'Appearance';
      position: absolute; left: calc(100% + 10px); top: 50%; transform: translateY(-50%);
      padding: 5px 10px; border-radius: 6px;
      background: var(--fg); color: var(--bg);
      font-size: 12px; font-weight: 500;
      white-space: nowrap; pointer-events: none;
      opacity: 0; transition: opacity .1s;
      box-shadow: 0 4px 12px rgba(0,0,0,.15);
    }
    .sb.c .sb-app-btn:hover::after { opacity: 1; }
    /* dropdown menu — fixed so sidebar overflow:hidden doesn't clip it */
    .app-menu {
      display: none; position: fixed;
      min-width: 160px;
      background: var(--card); border: 1px solid var(--border);
      border-radius: 8px; box-shadow: 0 8px 24px rgba(0,0,0,.15);
      overflow: hidden; z-index: 200;
    }
    .app-menu.open { display: block; }
    .app-menu-item {
      display: flex; align-items: center; gap: 8px;
      padding: 8px 12px; cursor: pointer; font-size: 13px;
      color: var(--fg); transition: background .1s;
    }
    .app-menu-item:hover { background: var(--muted); }
    .app-menu-item svg { width: 14px; height: 14px; color: var(--muted-fg); }
    .app-menu-item.cur { font-weight: 500; }
    .app-menu-item.cur svg { color: var(--primary); }

    /* Bot card (User.tsx) */
    .sb-bot {
      display: flex; align-items: center; gap: 10px;
      width: 100%; padding: 4px 8px; height: 48px;
      border-radius: 12px; border: none; background: none; overflow: hidden;
      margin-top: 2px; cursor: default;
    }
    .sb-av {
      width: 32px; height: 32px; flex-shrink: 0; border-radius: 8px;
      background: #52525b; color: #fff;
      display: flex; align-items: center; justify-content: center;
      font-size: 10px; font-weight: 700; letter-spacing: .03em;
    }
    .sb-bot-info { flex: 1; min-width: 0; display: flex; flex-direction: column; }
    .sb-bot-name { font-size: 13px; font-weight: 500; color: var(--sb-fg); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
    .sb-bot-sub  { font-size: 11px; color: var(--sb-muted); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
    .sb-chev svg { width: 16px; height: 16px; color: var(--sb-muted); flex-shrink: 0; }
    .sb.c .sb-bot-info, .sb.c .sb-chev { display: none; }
    .sb.c .sb-bot { padding: 8px; justify-content: center; }

    /* Rail */
    .sb-rail {
      position: absolute; inset-y: 0; right: -8px; z-index: 30;
      width: 16px; border: none; background: transparent; cursor: ew-resize;
    }
    .sb-rail::after {
      content: ''; position: absolute; inset-y: 0; left: 50%; width: 2px;
      background: transparent; transition: background .15s;
    }
    .sb-rail:hover::after { background: var(--sb-primary); opacity: .5; }

    /* ════ MAIN ════ */
    .main { flex: 1; display: flex; flex-direction: column; min-width: 0; overflow: hidden; }

    /* topbar */
    .topbar {
      position: sticky; top: 0; z-index: 5; height: 64px; flex-shrink: 0;
      display: flex; align-items: center; gap: 8px; padding: 0 24px;
      border-bottom: 1px solid var(--border); background: var(--bg);
    }
    /* PanelLeft trigger */
    .trig {
      width: 28px; height: 28px; border-radius: 6px;
      border: none; background: none; cursor: pointer; flex-shrink: 0;
      display: flex; align-items: center; justify-content: center;
      color: var(--muted-fg); transition: background .1s, color .1s;
    }
    .trig:hover { background: var(--muted); color: var(--fg); }
    .trig svg { width: 16px; height: 16px; }
    /* breadcrumb-style title */
    .tb-path { display: flex; align-items: center; gap: 6px; font-size: 14px; }
    .tb-seg { color: var(--muted-fg); }
    .tb-seg.cur { color: var(--fg); font-weight: 500; }
    .tb-slash { color: var(--border); font-size: 16px; }
    .tb-right { margin-left: auto; display: flex; align-items: center; gap: 10px; }
    /* running badge */
    .live-pill {
      display: flex; align-items: center; gap: 6px;
      padding: 4px 12px; border-radius: 20px;
      background: rgba(34,197,94,.08); border: 1px solid rgba(34,197,94,.15);
      font-size: 12px; font-weight: 500; color: #16a34a; letter-spacing: .01em;
    }
    .dark .live-pill { color: #4ade80; }
    .ldot { width: 6px; height: 6px; border-radius: 50%; background: #22c55e; animation: pulse 2s ease-in-out infinite; }
    @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:.3} }
    /* refresh */
    .rlbl { font-size: 11px; color: var(--muted-fg); display: flex; align-items: center; gap: 4px; }
    .rdot { width: 5px; height: 5px; border-radius: 50%; background: #22c55e; animation: pulse 3s infinite; }

    /* ════ CONTENT ════ */
    .content { flex: 1; overflow-y: auto; padding: 32px; }
    .ci { max-width: 1120px; margin: 0 auto; }

    /* page header */
    .ph { margin-bottom: 28px; }
    .ph h1 { font-size: 24px; font-weight: 700; letter-spacing: -.04em; }
    .ph p  { font-size: 14px; color: var(--muted-fg); margin-top: 4px; }

    /* chips */
    .chips { display: flex; gap: 6px; flex-wrap: wrap; margin-bottom: 24px; }
    .chip {
      display: inline-flex; align-items: center; gap: 6px;
      padding: 3px 10px; border-radius: 20px;
      background: var(--muted); border: 1px solid var(--border); font-size: 12px;
    }
    .ck { color: var(--muted-fg); }
    .cv { font-weight: 600; }

    /* ── Stat cards ── */
    .sg { display: grid; grid-template-columns: repeat(4,1fr); gap: 12px; margin-bottom: 20px; }
    .sc {
      background: var(--card); color: var(--card-fg);
      border: 1px solid var(--border); border-radius: calc(var(--radius)+4px);
      box-shadow: 0 1px 3px rgba(0,0,0,.04);
      padding: 20px 24px; display: flex; flex-direction: column; gap: 12px;
      transition: box-shadow .15s;
    }
    .sc:hover { box-shadow: 0 4px 12px rgba(0,0,0,.08); }
    .sc-top { display: flex; align-items: center; justify-content: space-between; }
    .sc-lbl { font-size: 13px; font-weight: 500; color: var(--muted-fg); }
    .sc-ico { width: 32px; height: 32px; border-radius: 8px; display: flex; align-items: center; justify-content: center; }
    .sc-ico svg { width: 16px; height: 16px; }
    .sc-val { font-size: 36px; font-weight: 700; letter-spacing: -.05em; line-height: 1; }
    .sc-sub { font-size: 12px; color: var(--muted-fg); }
    .i-blue  { background: rgba(59,130,246,.1);  color: #3b82f6; }
    .i-green { background: rgba(34,197,94,.1);   color: #22c55e; }
    .i-red   { background: rgba(239,68,68,.1);   color: #ef4444; }
    .i-zinc  { background: var(--muted);          color: var(--muted-fg); }
    .v-blue  { color: #2563eb; } .dark .v-blue  { color: #60a5fa; }
    .v-green { color: #16a34a; } .dark .v-green { color: #4ade80; }
    .v-red   { color: #dc2626; } .dark .v-red   { color: #f87171; }

    /* ── Card ── */
    .card {
      background: var(--card); color: var(--card-fg);
      border: 1px solid var(--border); border-radius: calc(var(--radius)+4px);
      box-shadow: 0 1px 3px rgba(0,0,0,.04); overflow: hidden;
    }
    .ch {
      padding: 16px 24px; border-bottom: 1px solid var(--border);
      display: flex; align-items: center; justify-content: space-between;
    }
    .ct { font-size: 14px; font-weight: 600; }
    .cd { font-size: 12px; color: var(--muted-fg); margin-top: 2px; }

    /* ── 2-col ── */
    .g2 { display: grid; grid-template-columns: 1fr 300px; gap: 16px; align-items: start; }

    /* ── Table ── */
    .tw { overflow-x: auto; }
    table { width: 100%; border-collapse: collapse; }
    thead { background: var(--muted); }
    th { padding: 10px 16px; text-align: left; font-size: 11px; font-weight: 600; color: var(--muted-fg); text-transform: uppercase; letter-spacing: .06em; white-space: nowrap; border-bottom: 1px solid var(--border); }
    td { padding: 12px 16px; border-bottom: 1px solid var(--border); font-size: 13px; vertical-align: middle; }
    tr:last-child td { border-bottom: none; }
    tbody tr { transition: background .08s; }
    tbody tr:hover td { background: var(--muted); }

    /* ── Badge ── */
    .badge {
      display: inline-flex; align-items: center; gap: 4px;
      padding: 2px 8px; border-radius: 20px;
      font-size: 11px; font-weight: 500; white-space: nowrap;
      border: 1px solid transparent;
    }
    .bd { width: 5px; height: 5px; border-radius: 50%; }
    .bm { background: rgba(59,130,246,.1); color: #1d4ed8; border-color: rgba(59,130,246,.2); }
    .be { background: rgba(34,197,94,.1);  color: #15803d; border-color: rgba(34,197,94,.2); }
    .bj { background: rgba(168,85,247,.1); color: #7e22ce; border-color: rgba(168,85,247,.2); }
    .bl { background: rgba(249,115,22,.1); color: #c2410c; border-color: rgba(249,115,22,.2); }
    .bw { background: rgba(236,72,153,.1); color: #be185d; border-color: rgba(236,72,153,.2); }
    .bx { background: var(--muted); color: var(--muted-fg); border-color: var(--border); }
    .dark .bm { background: rgba(59,130,246,.15);  color: #93c5fd; }
    .dark .be { background: rgba(34,197,94,.15);   color: #86efac; }
    .dark .bj { background: rgba(168,85,247,.15);  color: #d8b4fe; }
    .dark .bl { background: rgba(249,115,22,.15);  color: #fdba74; }
    .dark .bw { background: rgba(236,72,153,.15);  color: #f9a8d4; }
    .dm { background: #3b82f6; } .de { background: #22c55e; }
    .dj { background: #a855f7; } .dl { background: #f97316; }
    .dw { background: #ec4899; } .dx { background: #a1a1aa; }

    .tag { display: inline-flex; padding: 2px 8px; border-radius: 6px; font-size: 11px; font-weight: 500; background: var(--muted); color: var(--muted-fg); border: 1px solid var(--border); }
    .tags { display: flex; flex-wrap: wrap; gap: 4px; }
    code { font-family: 'Menlo','Monaco','Courier New',monospace; font-size: 12px; color: var(--primary); font-weight: 600; }
    .fn-sub { font-size: 11px; color: var(--muted-fg); margin-top: 2px; }

    /* ── Bars ── */
    .bar-row {
      display: flex; align-items: center; gap: 14px;
      padding: 11px 24px; border-bottom: 1px solid var(--border);
      transition: background .08s;
    }
    .bar-row:last-child { border-bottom: none; }
    .bar-row:hover { background: var(--muted); }
    .bar-name  { font-size: 13px; font-weight: 500; min-width: 124px; white-space: nowrap; }
    .bar-track { flex: 1; height: 6px; background: var(--muted); border-radius: 4px; overflow: hidden; }
    .bar-fill  { height: 100%; border-radius: 4px; transition: width .6s cubic-bezier(.4,0,.2,1); }
    .bar-count { font-size: 14px; font-weight: 600; min-width: 28px; text-align: right; }

    /* ── Info rows ── */
    .ir { display: flex; justify-content: space-between; align-items: center; padding: 12px 24px; border-bottom: 1px solid var(--border); font-size: 13px; }
    .ir:last-child { border-bottom: none; }
    .ik { color: var(--muted-fg); } .iv { font-weight: 500; }

    /* ── Skeleton ── */
    .skel {
      height: 16px; border-radius: 6px;
      background: linear-gradient(90deg, var(--muted) 25%, var(--border) 50%, var(--muted) 75%);
      background-size: 200% 100%;
      animation: shimmer 1.5s infinite;
    }
    @keyframes shimmer { 0%{background-position:200% 0} 100%{background-position:-200% 0} }

    /* ── Empty ── */
    .empty { padding: 48px 24px; text-align: center; color: var(--muted-fg); }
    .empty svg { width: 32px; height: 32px; margin: 0 auto 10px; opacity: .3; display: block; }
    .empty p { font-size: 13px; }

    /* ── View ── */
    .view { display: none; } .view.on { display: block; }

    /* ── Footer ── */
    .footer {
      border-top: 1px solid var(--border); padding: 14px 32px;
      font-size: 12px; color: var(--muted-fg);
      display: flex; align-items: center; justify-content: space-between; flex-shrink: 0;
      background: var(--bg);
    }
    .gh {
      display: flex; align-items: center; gap: 6px;
      padding: 4px 10px; border-radius: var(--radius);
      border: 1px solid var(--border); color: var(--muted-fg);
      text-decoration: none; font-size: 12px; font-weight: 500;
      transition: background .1s, color .1s;
    }
    .gh:hover { background: var(--muted); color: var(--fg); }
    .gh svg { width: 14px; height: 14px; fill: currentColor; }

    /* ── Responsive ── */
    @media(max-width:860px){ .sg{grid-template-columns:1fr 1fr;} .g2{grid-template-columns:1fr;} }
    @media(max-width:540px){ .content{padding:16px;} .sc-val{font-size:26px;} }
  </style>
  <script>
    /* init theme before render */
    (function(){
      var t=localStorage.getItem('fastvk-theme');
      if(!t){ t=window.matchMedia('(prefers-color-scheme:dark)').matches?'dark':'light'; }
      if(t==='dark') document.documentElement.classList.add('dark');
      window._theme=t;
    })();
  </script>
</head>
<body>
<div class="root">

<!-- ══════════════ SIDEBAR ══════════════ -->
<div class="sb-gap" id="sg">
  <aside class="sb" id="sb">

    <!-- Logo header -->
    <div class="sb-hd">
      <div class="sb-mark">VK</div>
      <span class="sb-wordmark">fast<em>VK</em></span>
    </div>

    <!-- Nav -->
    <div class="sb-body">
      <div class="sb-lbl">Platform</div>
      <button class="sb-item on" id="nav-overview" onclick="setView('overview',this)" title="Overview">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <rect width="7" height="7" x="3" y="3" rx="1"/><rect width="7" height="7" x="14" y="3" rx="1"/>
          <rect width="7" height="7" x="3" y="14" rx="1"/><rect width="7" height="7" x="14" y="14" rx="1"/>
        </svg>
        <span class="sb-item-label">Overview</span>
      </button>
      <button class="sb-item" id="nav-handlers" onclick="setView('handlers',this)" title="Handlers">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/>
        </svg>
        <span class="sb-item-label">Handlers</span>
        <span class="sb-item-badge" id="hn-badge">—</span>
      </button>
      <button class="sb-item" id="nav-updates" onclick="setView('updates',this)" title="Updates">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>
        </svg>
        <span class="sb-item-label">Updates</span>
        <span class="sb-item-badge" id="up-badge">0</span>
      </button>
    </div>

    <!-- Footer -->
    <div class="sb-ft">
      <div class="sb-sep"></div>
      <!-- Appearance dropdown -->
      <div class="sb-app-wrap" id="app-wrap">
        <button class="sb-app-btn" onclick="toggleAppMenu(event)">
          <svg id="i-moon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z"/></svg>
          <svg id="i-sun" style="display:none" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M6.34 17.66l-1.41 1.41M19.07 4.93l-1.41 1.41"/></svg>
          <svg id="i-mon" style="display:none" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="20" height="14" x="2" y="3" rx="2"/><path d="M8 21h8M12 17v4"/></svg>
          <span class="app-lbl">Appearance</span>
        </button>
        <div class="app-menu" id="app-menu">
          <div class="app-menu-item" onclick="setTheme('light')">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M6.34 17.66l-1.41 1.41M19.07 4.93l-1.41 1.41"/></svg>
            Light
          </div>
          <div class="app-menu-item" onclick="setTheme('dark')">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z"/></svg>
            Dark
          </div>
          <div class="app-menu-item" onclick="setTheme('system')">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="20" height="14" x="2" y="3" rx="2"/><path d="M8 21h8M12 17v4"/></svg>
            System
          </div>
        </div>
      </div>
      <!-- Bot card -->
      <div class="sb-bot">
        <div class="sb-av" title="FastVK Bot">VK</div>
        <div class="sb-bot-info">
          <span class="sb-bot-name">FastVK Bot</span>
          <span class="sb-bot-sub">v<span id="sb-ver">—</span> · <span id="sb-grp">—</span></span>
        </div>
        <span class="sb-chev">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="m7 15 5 5 5-5"/><path d="m7 9 5-5 5 5"/>
          </svg>
        </span>
      </div>
    </div>

    <button class="sb-rail" onclick="toggleSb()" aria-label="Toggle sidebar"></button>
  </aside>
</div>

<!-- ══════════════ MAIN ══════════════ -->
<div class="main">

  <!-- Topbar -->
  <header class="topbar">
    <button class="trig" onclick="toggleSb()" aria-label="Toggle sidebar" title="Toggle sidebar (⌘B)">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <rect width="18" height="18" x="3" y="3" rx="2"/><path d="M9 3v18"/>
      </svg>
    </button>
    <nav class="tb-path">
      <span class="tb-seg">FastVK</span>
      <span class="tb-slash">/</span>
      <span class="tb-seg cur" id="tb-cur">Overview</span>
    </nav>
    <div class="tb-right">
      <span class="rlbl"><span class="rdot"></span><span id="r-ago">live</span></span>
      <div class="live-pill"><div class="ldot"></div>running</div>
    </div>
  </header>

  <!-- Content -->
  <div class="content">
    <div class="ci">

      <!-- ── Overview ── -->
      <div id="view-overview" class="view on">
        <div class="ph">
          <h1>Dashboard</h1>
          <p>Real-time monitoring for your VK bot</p>
        </div>
        <div id="chips" class="chips"></div>
        <div class="sg">
          <div class="sc">
            <div class="sc-top"><span class="sc-lbl">Total Updates</span>
              <div class="sc-ico i-blue"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M13 2 3 14h9l-1 8 10-12h-9l1-8z"/></svg></div>
            </div>
            <div class="sc-val v-blue" id="s-total">—</div>
            <div class="sc-sub">since start</div>
          </div>
          <div class="sc">
            <div class="sc-top"><span class="sc-lbl">Handled</span>
              <div class="sc-ico i-green"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg></div>
            </div>
            <div class="sc-val v-green" id="s-handled">—</div>
            <div class="sc-sub">successfully</div>
          </div>
          <div class="sc">
            <div class="sc-top"><span class="sc-lbl">Errors</span>
              <div class="sc-ico i-red"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg></div>
            </div>
            <div class="sc-val v-red" id="s-errors">—</div>
            <div class="sc-sub">handler errors</div>
          </div>
          <div class="sc">
            <div class="sc-top"><span class="sc-lbl">Uptime</span>
              <div class="sc-ico i-zinc"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg></div>
            </div>
            <div class="sc-val" id="s-uptime">—</div>
            <div class="sc-sub">elapsed</div>
          </div>
        </div>
        <div class="g2">
          <div class="card">
            <div class="ch">
              <div><div class="ct">Updates by type</div><div class="cd">Event distribution</div></div>
            </div>
            <div id="ov-bars"><div class="empty"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg><p>No updates yet</p></div></div>
          </div>
          <div class="card">
            <div class="ch"><div class="ct">Bot info</div></div>
            <div id="bot-info"></div>
          </div>
        </div>
      </div>

      <!-- ── Handlers ── -->
      <div id="view-handlers" class="view">
        <div class="ph">
          <h1>Handlers</h1>
          <p>Registered event handlers and their filters</p>
        </div>
        <div class="card">
          <div class="tw">
            <table>
              <thead><tr>
                <th style="width:160px">Event</th>
                <th>Function</th>
                <th>Filters</th>
              </tr></thead>
              <tbody id="h-tbody">
                <tr><td colspan="3">
                  <div style="padding:24px;display:flex;flex-direction:column;gap:10px;">
                    <div class="skel" style="width:60%"></div>
                    <div class="skel" style="width:80%"></div>
                    <div class="skel" style="width:50%"></div>
                  </div>
                </td></tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- ── Updates ── -->
      <div id="view-updates" class="view">
        <div class="ph">
          <h1>Updates</h1>
          <p>Live event distribution</p>
        </div>
        <div class="g2">
          <div class="card">
            <div class="ch">
              <div class="ct">By type</div>
              <span class="rlbl"><span class="rdot"></span><span id="r-ago2">live</span></span>
            </div>
            <div id="up-bars"><div class="empty"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg><p>No updates yet</p></div></div>
          </div>
          <div class="card">
            <div class="ch"><div class="ct">Statistics</div></div>
            <div class="ir"><span class="ik">Total</span><span class="iv" id="u-total">—</span></div>
            <div class="ir"><span class="ik">Handled</span><span class="iv" id="u-handled">—</span></div>
            <div class="ir"><span class="ik">Errors</span><span class="iv" id="u-errors">—</span></div>
            <div class="ir"><span class="ik">Uptime</span><span class="iv" id="u-uptime">—</span></div>
          </div>
        </div>
      </div>

    </div>
  </div>

  <!-- Footer -->
  <footer class="footer">
    <span>FastVK <strong id="ft-ver">—</strong> &nbsp;·&nbsp; group <strong id="ft-grp">—</strong></span>
    <a href="https://github.com/ndugram/fastvk" class="gh" target="_blank" rel="noopener noreferrer">
      <svg viewBox="0 0 24 24"><path d="M12 0C5.374 0 0 5.373 0 12c0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23A11.509 11.509 0 0112 5.803c1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576C20.566 21.797 24 17.3 24 12c0-6.627-5.373-12-12-12z"/></svg>
      GitHub
    </a>
  </footer>
</div><!-- /main -->
</div><!-- /root -->

<script>
/* ── Theme ─────────────────────────────────────────────── */
var _theme = window._theme || 'dark';
function applyTheme(t) {
  _theme = t;
  var dark = t==='dark' || (t==='system' && window.matchMedia('(prefers-color-scheme:dark)').matches);
  document.documentElement.classList.toggle('dark', dark);
  document.getElementById('i-moon').style.display = t==='dark'  ? '' : 'none';
  document.getElementById('i-sun').style.display  = t==='light' ? '' : 'none';
  document.getElementById('i-mon').style.display  = t==='system'? '' : 'none';
  document.querySelectorAll('.app-menu-item').forEach(function(el,i){
    el.classList.toggle('cur', ['light','dark','system'][i]===t);
  });
  localStorage.setItem('fastvk-theme', t);
}
function setTheme(t){ applyTheme(t); closeAppMenu(); }
applyTheme(_theme);

/* System preference change */
window.matchMedia('(prefers-color-scheme:dark)').addEventListener('change', function(){
  if(_theme==='system') applyTheme('system');
});

/* ── Appearance menu ─────────────────────────────────── */
function toggleAppMenu(e){
  e.stopPropagation();
  var menu=document.getElementById('app-menu');
  var btn=document.querySelector('.sb-app-btn');
  var r=btn.getBoundingClientRect();
  menu.style.left=r.left+'px';
  menu.style.top=(r.top - menu.offsetHeight - 8)+'px';
  /* first open: offsetHeight may be 0, flip to bottom then re-calc */
  menu.classList.toggle('open');
  if(menu.classList.contains('open')){
    /* re-position after display:block so height is real */
    requestAnimationFrame(function(){
      var h=menu.offsetHeight;
      var top=r.top-h-8;
      if(top<8) top=r.bottom+4; /* flip down if no room */
      menu.style.top=top+'px';
    });
  }
}
function closeAppMenu(){ document.getElementById('app-menu').classList.remove('open'); }
document.addEventListener('click', function(e){
  if (!document.getElementById('app-wrap').contains(e.target)) closeAppMenu();
});

/* ── Sidebar ─────────────────────────────────────────── */
function toggleSb(){
  document.getElementById('sg').classList.toggle('c');
  document.getElementById('sb').classList.toggle('c');
  /* persist */
  var c=document.getElementById('sb').classList.contains('c');
  document.cookie='fastvk_sb='+(c?'0':'1')+';path=/;max-age=604800';
}
/* restore sidebar state from cookie */
(function(){
  var m=document.cookie.match(/fastvk_sb=([01])/);
  if(m&&m[1]==='0'){ document.getElementById('sg').classList.add('c'); document.getElementById('sb').classList.add('c'); }
})();

/* ── Keyboard shortcut ⌘B / Ctrl+B ──────────────────── */
document.addEventListener('keydown',function(e){
  if((e.metaKey||e.ctrlKey)&&e.key.toLowerCase()==='b'){ e.preventDefault(); toggleSb(); }
});

/* ── Views ───────────────────────────────────────────── */
var TITLES={overview:'Overview',handlers:'Handlers',updates:'Updates'};
function setView(name,btn){
  document.querySelectorAll('.view').forEach(function(v){v.classList.remove('on');});
  document.querySelectorAll('.sb-item').forEach(function(b){b.classList.remove('on');});
  document.getElementById('view-'+name).classList.add('on');
  btn.classList.add('on');
  document.getElementById('tb-cur').textContent=TITLES[name]||name;
}

/* ── Event helpers ───────────────────────────────────── */
var EB={message_new:'bm dm',message_event:'be de',group_join:'bj dj',group_leave:'bl dl',wall_post_new:'bw dw'};
var EC={message_new:'#3b82f6',message_event:'#22c55e',group_join:'#a855f7',group_leave:'#f97316',wall_post_new:'#ec4899'};
function evtCls(t){ return (EB[t]||'bx dx').split(' '); }
function evtClr(t){ return EC[t]||'#a1a1aa'; }
function evtBadge(t){
  var c=evtCls(t);
  return '<span class="badge '+c[0]+'"><span class="bd '+c[1]+'"></span>'+t+'</span>';
}

/* ── Uptime ──────────────────────────────────────────── */
function fmtUp(s){
  var h=Math.floor(s/3600),m=Math.floor((s%3600)/60),sc=Math.floor(s%60);
  if(h) return h+'h '+String(m).padStart(2,'0')+'m';
  if(m) return m+'m '+String(sc).padStart(2,'0')+'s';
  return sc+'s';
}
function fmtN(n){ return n>=1000?(n/1000).toFixed(1)+'k':String(n); }

/* ── Animated counter ────────────────────────────────── */
function animN(el,to){
  if(!el) return;
  var from=parseInt(el.dataset.v||'0',10); if(from===to) return; el.dataset.v=to;
  var d=to-from,dur=400,t0=performance.now();
  (function tick(now){
    var p=Math.min((now-t0)/dur,1),e=1-Math.pow(1-p,3);
    el.textContent=fmtN(Math.round(from+d*e));
    if(p<1) requestAnimationFrame(tick);
  })(t0);
}

/* ── Bars ────────────────────────────────────────────── */
function renderBars(id,byType){
  var el=document.getElementById(id);
  var entries=Object.entries(byType).sort(function(a,b){return b[1]-a[1];});
  var max=entries.length?entries[0][1]:1;
  if(!entries.length){
    el.innerHTML='<div class="empty"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg><p>No updates yet</p></div>';
    return;
  }
  var total=entries.reduce(function(a,e){return a+e[1];},0);
  el.innerHTML=entries.map(function(e){
    var type=e[0],count=e[1];
    var pct=Math.max(4,Math.round(count/max*100));
    var pctTxt=total?Math.round(count/total*100)+'%':'';
    var cls=evtCls(type)[1]; var clr=evtClr(type);
    return '<div class="bar-row">'
      +'<span class="bar-name">'+type+'</span>'
      +'<div class="bar-track"><div class="bar-fill '+cls+'" style="width:'+pct+'%"></div></div>'
      +'<span style="font-size:11px;color:var(--muted-fg);min-width:32px;text-align:right">'+pctTxt+'</span>'
      +'<span class="bar-count" style="color:'+clr+'">'+count+'</span>'
      +'</div>';
  }).join('');
}

/* ── Load info ───────────────────────────────────────── */
var lastR=Date.now(),_infoLoaded=false;
async function loadInfo(){
  if(_infoLoaded) return;
  var d=await fetch('/api/info').then(function(r){return r.json();}).catch(function(){return null;});
  if(!d) return;
  _infoLoaded=true;

  document.getElementById('chips').innerHTML=[
    ['group_id',d.group_id],['api',d.api_version],['fastvk',d.version]
  ].map(function(c){return '<div class="chip"><span class="ck">'+c[0]+'</span><span class="cv">'+c[1]+'</span></div>';}).join('');

  ['sb-ver','ft-ver'].forEach(function(i){document.getElementById(i).textContent=d.version;});
  ['sb-grp','ft-grp'].forEach(function(i){document.getElementById(i).textContent=d.group_id;});

  document.getElementById('bot-info').innerHTML=[
    ['Group ID',d.group_id],['API version',d.api_version],['FastVK',d.version],['Handlers',d.handlers.length]
  ].map(function(r){return '<div class="ir"><span class="ik">'+r[0]+'</span><span class="iv">'+r[1]+'</span></div>';}).join('');

  var cnt=d.handlers.length;
  document.getElementById('hn-badge').textContent=cnt;
  var tb=document.getElementById('h-tbody');
  if(!cnt){
    tb.innerHTML='<tr><td colspan="3"><div class="empty"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/></svg><p>No handlers registered</p></div></td></tr>';
    return;
  }
  tb.innerHTML=d.handlers.map(function(h){
    var f=h.filters.length
      ?'<div class="tags">'+h.filters.map(function(f){return '<span class="tag">'+f+'</span>';}).join('')+'</div>'
      :'<span style="color:var(--muted-fg);font-size:12px">—</span>';
    return '<tr><td>'+evtBadge(h.event)+'</td><td><code>'+h.handler+'()</code><div class="fn-sub">'+h.module+'</div></td><td>'+f+'</td></tr>';
  }).join('');
}

/* ── Load stats ──────────────────────────────────────── */
async function loadStats(){
  var d=await fetch('/api/stats').then(function(r){return r.json();}).catch(function(){return null;});
  if(!d) return;
  lastR=Date.now();
  animN(document.getElementById('s-total'),d.total);
  animN(document.getElementById('s-handled'),d.handled);
  animN(document.getElementById('s-errors'),d.errors);
  document.getElementById('s-uptime').textContent=fmtUp(d.uptime_seconds);
  var set=function(id,v){var e=document.getElementById(id);if(e)e.textContent=v;};
  set('u-total',fmtN(d.total)); set('u-handled',fmtN(d.handled));
  set('u-errors',fmtN(d.errors)); set('u-uptime',fmtUp(d.uptime_seconds));
  renderBars('ov-bars',d.by_type);
  renderBars('up-bars',d.by_type);
  document.getElementById('up-badge').textContent=fmtN(d.total);
  var lbl='just now';
  document.getElementById('r-ago').textContent=lbl;
  var r2=document.getElementById('r-ago2'); if(r2) r2.textContent=lbl;
}

/* ── Refresh ticker ──────────────────────────────────── */
setInterval(function(){
  var s=Math.round((Date.now()-lastR)/1000),lbl=s<5?'just now':s+'s ago';
  document.getElementById('r-ago').textContent=lbl;
  var r2=document.getElementById('r-ago2'); if(r2) r2.textContent=lbl;
},1000);

loadInfo();
loadStats();
setInterval(function(){ loadInfo(); loadStats(); },3000);
</script>
</body>
</html>
"""


def get_dashboard_html(*, version: str, group_id: int) -> str:
    return DASHBOARD_HTML.replace("__VERSION__", version).replace("__GROUP_ID__", str(group_id))
