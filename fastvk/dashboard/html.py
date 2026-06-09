DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FastVK Dashboard</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700&family=Urbanist:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --font-u: 'Urbanist', system-ui, sans-serif;
            --font-m: 'Manrope', system-ui, sans-serif;
            --blue:   #2e73ff;
            --green:  #30fc9d;
            --red:    #ff5c5c;
            --purple: #a855f7;
            --orange: #fb923c;
            --pink:   #ec4899;

            --bg0: #f0f0f0;
            --bg1: #ffffff;
            --bg2: #f4f4f4;
            --text1: #1e1e1e;
            --text2: #888888;
            --border: #e0e0e0;
        }
        [data-theme="dark"] {
            --bg0: #0d0d0d;
            --bg1: #1a1a1a;
            --bg2: #111111;
            --text1: #f0f0f0;
            --text2: #666666;
            --border: #2a2a2a;
        }

        *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
        html { background: var(--bg0); }
        body {
            background: var(--bg0);
            color: var(--text1);
            font-family: var(--font-m), system-ui, sans-serif;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            transition: background 0.3s, color 0.3s;
        }
        .wrap { width: 100%; max-width: 1320px; padding: 0 24px; margin: 0 auto; }

        /* ── Header ── */
        .header {
            position: relative;
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 10px 16px 10px 14px;
            height: 54px;
            border-radius: 16px;
            overflow: hidden;
            margin: 20px auto;
            max-width: calc(1320px - 48px);
            width: calc(100% - 48px);
        }
        .hbg-l {
            position: absolute; inset: 0; right: auto; width: 40%;
            background: var(--bg1);
            border-top-left-radius: 16px;
            border-bottom-left-radius: 28px;
            transform: skewX(-14deg);
            transform-origin: bottom left;
            z-index: 0;
            transition: background 0.3s;
        }
        .hbg-r {
            position: absolute; inset: 0; left: auto; width: 82%;
            background: var(--bg1);
            border-radius: 16px;
            z-index: 0;
            transition: background 0.3s;
        }
        .logo {
            font-family: var(--font-u);
            font-size: 19px; font-weight: 700;
            letter-spacing: -0.02em;
            position: relative; z-index: 2;
            color: var(--text1);
        }
        .logo em { font-style: normal; color: var(--blue); }
        .hright {
            display: flex; align-items: center; gap: 10px;
            position: relative; z-index: 2;
        }
        .live {
            display: flex; align-items: center; gap: 6px;
            padding: 5px 12px; border-radius: 20px;
            background: rgba(48, 252, 157, 0.08);
            border: 1px solid rgba(48, 252, 157, 0.2);
            font-size: 12px; font-weight: 600;
            color: var(--green);
        }
        .live-dot {
            width: 7px; height: 7px; border-radius: 50%;
            background: var(--green);
            box-shadow: 0 0 6px var(--green);
            animation: blink 2s ease-in-out infinite;
        }
        @keyframes blink { 0%,100%{opacity:1} 50%{opacity:.3} }
        .btn-theme {
            width: 34px; height: 34px; border-radius: 10px;
            background: var(--bg2); border: 1px solid var(--border);
            cursor: pointer; display: flex; align-items: center; justify-content: center;
            transition: all 0.2s;
        }
        .btn-theme:hover { border-color: var(--blue); background: rgba(46,115,255,.08); }
        .btn-theme svg { width: 16px; height: 16px; fill: var(--text2); transition: fill 0.2s; }
        .btn-theme:hover svg { fill: var(--blue); }
        .ic-moon { display: block; }
        .ic-sun  { display: none; }
        [data-theme="dark"] .ic-moon { display: none; }
        [data-theme="dark"] .ic-sun  { display: block; }

        /* ── Main ── */
        main { flex: 1; padding-bottom: 48px; }

        /* chips row */
        .chips { display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 22px; }
        .chip {
            display: inline-flex; align-items: center; gap: 6px;
            padding: 5px 12px; border-radius: 10px;
            background: var(--bg1); border: 1px solid var(--border);
            font-size: 12px; font-weight: 500;
            transition: background 0.3s;
        }
        .chip-k { color: var(--text2); }
        .chip-v { color: var(--text1); font-weight: 700; }

        /* stat cards */
        .stats { display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; margin-bottom: 24px; }
        .scard {
            background: var(--bg1); border: 1px solid var(--border);
            border-radius: 18px; padding: 20px 22px;
            display: flex; flex-direction: column; gap: 10px;
            transition: background 0.3s, border-color 0.2s;
            position: relative; overflow: hidden;
        }
        .scard::before {
            content: '';
            position: absolute; top: 0; left: 0; right: 0; height: 2px;
            border-radius: 18px 18px 0 0;
            opacity: 0.6;
        }
        .scard.c-blue::before  { background: var(--blue); }
        .scard.c-green::before { background: var(--green); }
        .scard.c-red::before   { background: var(--red); }
        .scard.c-text::before  { background: var(--text2); }
        .scard-top { display: flex; align-items: center; justify-content: space-between; }
        .scard-label {
            font-size: 11px; font-weight: 600;
            text-transform: uppercase; letter-spacing: 0.07em;
            color: var(--text2);
        }
        .scard-icon {
            width: 32px; height: 32px; border-radius: 10px;
            display: flex; align-items: center; justify-content: center;
        }
        .scard-icon svg { width: 16px; height: 16px; }
        .c-blue  .scard-icon { background: rgba(46,115,255,.12); }
        .c-blue  .scard-icon svg { stroke: var(--blue); }
        .c-green .scard-icon { background: rgba(48,252,157,.12); }
        .c-green .scard-icon svg { stroke: var(--green); }
        .c-red   .scard-icon { background: rgba(255,92,92,.12); }
        .c-red   .scard-icon svg { stroke: var(--red); }
        .c-text  .scard-icon { background: rgba(136,136,136,.1); }
        .c-text  .scard-icon svg { stroke: var(--text2); }
        .scard-val {
            font-family: var(--font-u);
            font-size: 38px; font-weight: 700;
            letter-spacing: -0.04em; line-height: 1;
        }
        .c-blue  .scard-val { color: var(--blue); }
        .c-green .scard-val { color: var(--green); }
        .c-red   .scard-val { color: var(--red); }
        .c-text  .scard-val { color: var(--text1); }

        /* two-col layout */
        .grid2 { display: grid; grid-template-columns: 1fr 340px; gap: 18px; align-items: start; }

        /* section */
        .section { background: var(--bg1); border: 1px solid var(--border); border-radius: 18px; overflow: hidden; transition: background 0.3s; }
        .section-head {
            display: flex; align-items: center; justify-content: space-between;
            padding: 16px 20px;
            border-bottom: 1px solid var(--border);
        }
        .section-title {
            font-family: var(--font-u);
            font-size: 15px; font-weight: 700;
            letter-spacing: -0.01em;
            color: var(--text1);
            display: flex; align-items: center; gap: 8px;
        }
        .count-badge {
            font-size: 11px; font-weight: 700;
            padding: 2px 8px; border-radius: 20px;
            background: rgba(46,115,255,.12); color: var(--blue);
        }
        .refresh-label {
            font-size: 11px; color: var(--text2);
            display: flex; align-items: center; gap: 5px;
        }
        .refresh-dot { width: 5px; height: 5px; border-radius: 50%; background: var(--green); animation: blink 3s infinite; }

        /* handlers table */
        table { width: 100%; border-collapse: collapse; }
        th {
            padding: 10px 20px;
            text-align: left; font-size: 11px; font-weight: 600;
            text-transform: uppercase; letter-spacing: 0.07em;
            color: var(--text2);
            background: var(--bg2);
            border-bottom: 1px solid var(--border);
        }
        td { padding: 0; border-bottom: 1px solid var(--border); vertical-align: middle; }
        tr:last-child td { border-bottom: none; }
        .row-inner {
            display: flex; align-items: stretch;
            transition: background 0.15s;
        }
        tr:hover .row-inner { background: rgba(46,115,255,.04); }
        .row-accent {
            width: 3px; flex-shrink: 0;
            border-radius: 2px;
            margin: 10px 0 10px 12px;
        }
        .row-content {
            flex: 1; padding: 12px 16px 12px 12px;
            display: grid; grid-template-columns: 130px 1fr 1fr; gap: 10px;
            align-items: center;
        }
        .evt-badge {
            display: inline-flex; align-items: center; gap: 5px;
            padding: 3px 9px; border-radius: 8px;
            font-size: 11px; font-weight: 600;
            white-space: nowrap;
        }
        .evt-dot { width: 5px; height: 5px; border-radius: 50%; }
        .fn-name {
            font-family: 'Menlo','Monaco','Courier New',monospace;
            font-size: 13px; color: var(--blue); font-weight: 600;
        }
        .fn-module { font-size: 11px; color: var(--text2); margin-top: 2px; }
        .filters-wrap { display: flex; flex-wrap: wrap; gap: 5px; }
        .filter-tag {
            font-size: 11px; font-weight: 500;
            padding: 2px 8px; border-radius: 6px;
            background: var(--bg2); border: 1px solid var(--border);
            color: var(--text2);
        }
        .no-filters { font-size: 12px; color: var(--text2); }

        /* empty state */
        .empty {
            padding: 48px 20px; text-align: center;
            color: var(--text2); font-size: 14px;
        }

        /* update types */
        .type-list { padding: 8px 0; }
        .type-row {
            display: flex; align-items: center; gap: 10px;
            padding: 10px 20px;
            border-bottom: 1px solid var(--border);
            transition: background 0.15s;
        }
        .type-row:last-child { border-bottom: none; }
        .type-row:hover { background: rgba(46,115,255,.04); }
        .type-name {
            font-size: 12px; font-weight: 600;
            white-space: nowrap; flex-shrink: 0; min-width: 110px;
            color: var(--text1);
        }
        .type-bar-wrap { flex: 1; height: 6px; background: var(--bg2); border-radius: 4px; overflow: hidden; }
        .type-bar { height: 100%; border-radius: 4px; transition: width 0.6s cubic-bezier(.4,0,.2,1); }
        .type-count {
            font-family: var(--font-u); font-weight: 700;
            font-size: 14px; flex-shrink: 0; min-width: 30px;
            text-align: right;
        }
        .type-empty { padding: 28px 20px; text-align: center; color: var(--text2); font-size: 13px; }

        /* event type color map */
        .e-message_new    { background: rgba(46,115,255,.12);  color: #2e73ff; }
        .e-message_event  { background: rgba(48,252,157,.12);  color: #20c97a; }
        .e-group_join     { background: rgba(168,85,247,.12);  color: #a855f7; }
        .e-group_leave    { background: rgba(251,146,60,.12);  color: #fb923c; }
        .e-wall_post_new  { background: rgba(236,72,153,.12);  color: #ec4899; }
        .e-default        { background: rgba(136,136,136,.1);  color: #888888; }

        .e-message_new-bar    { background: #2e73ff; }
        .e-message_event-bar  { background: #30fc9d; }
        .e-group_join-bar     { background: #a855f7; }
        .e-group_leave-bar    { background: #fb923c; }
        .e-wall_post_new-bar  { background: #ec4899; }
        .e-default-bar        { background: #888888; }

        .e-message_new-dot    { background: #2e73ff; }
        .e-message_event-dot  { background: #30fc9d; }
        .e-group_join-dot     { background: #a855f7; }
        .e-group_leave-dot    { background: #fb923c; }
        .e-wall_post_new-dot  { background: #ec4899; }
        .e-default-dot        { background: #888888; }

        .e-message_new-acc    { background: #2e73ff; }
        .e-message_event-acc  { background: #30fc9d; }
        .e-group_join-acc     { background: #a855f7; }
        .e-group_leave-acc    { background: #fb923c; }
        .e-wall_post_new-acc  { background: #ec4899; }
        .e-default-acc        { background: #555555; }

        .e-message_new-cnt    { color: #2e73ff; }
        .e-message_event-cnt  { color: #20c97a; }
        .e-group_join-cnt     { color: #a855f7; }
        .e-group_leave-cnt    { color: #fb923c; }
        .e-wall_post_new-cnt  { color: #ec4899; }
        .e-default-cnt        { color: #888888; }

        /* bot info rows */
        .binfo-row {
            display: flex; justify-content: space-between; align-items: center;
            padding: 10px 20px; border-bottom: 1px solid var(--border);
            font-size: 13px;
        }
        .binfo-row:last-child { border-bottom: none; }

        /* footer */
        .footer { padding: 24px 0; }
        .footer-in {
            display: flex; align-items: center; justify-content: space-between;
            flex-wrap: wrap; gap: 12px;
        }
        .footer-txt { font-size: 12px; color: var(--text2); }
        .footer-txt strong { color: var(--text1); }
        .gh-link {
            display: flex; align-items: center; justify-content: center;
            width: 36px; height: 36px; border-radius: 10px;
            background: var(--bg1); border: 1px solid var(--border);
            color: var(--text2); text-decoration: none;
            transition: all 0.2s;
        }
        .gh-link:hover { background: var(--blue); border-color: var(--blue); color: white; transform: translateY(-1px); }
        .gh-link svg { width: 18px; height: 18px; fill: currentColor; }

        @media (max-width: 900px) {
            .stats { grid-template-columns: 1fr 1fr; }
            .grid2 { grid-template-columns: 1fr; }
            .row-content { grid-template-columns: 110px 1fr; }
        }
        @media (max-width: 560px) {
            .stats { grid-template-columns: 1fr 1fr; }
            .scard-val { font-size: 28px; }
            .row-content { grid-template-columns: 1fr; }
        }
    </style>
    <script>
        (function() {
            const t = localStorage.getItem('fastvk-theme') || 'dark';
            document.documentElement.setAttribute('data-theme', t);
            window.toggleTheme = function() {
                const n = document.documentElement.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
                document.documentElement.setAttribute('data-theme', n);
                localStorage.setItem('fastvk-theme', n);
            };
        })();
    </script>
</head>
<body>
<div class="wrap">
    <!-- Header -->
    <header class="header">
        <div class="hbg-l"></div>
        <div class="hbg-r"></div>
        <div class="logo">fast<em>VK</em></div>
        <div class="hright">
            <div class="live"><div class="live-dot"></div>running</div>
            <button class="btn-theme" onclick="toggleTheme()" aria-label="Toggle theme">
                <svg class="ic-moon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12.79A9 9 0 1111.21 3 7 7 0 0021 12.79z" fill="currentColor" stroke="none"/></svg>
                <svg class="ic-sun" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <circle cx="12" cy="12" r="5" fill="currentColor" stroke="none"/>
                    <line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/>
                    <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/>
                    <line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/>
                    <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/>
                </svg>
            </button>
        </div>
    </header>

    <main>
        <!-- Info chips -->
        <div id="chips" class="chips"></div>

        <!-- Stat cards -->
        <div class="stats">
            <div class="scard c-blue">
                <div class="scard-top">
                    <span class="scard-label">Total updates</span>
                    <div class="scard-icon">
                        <svg viewBox="0 0 24 24" fill="none" stroke-width="2"><path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z" stroke-linecap="round" stroke-linejoin="round"/></svg>
                    </div>
                </div>
                <div class="scard-val" id="s-total">—</div>
            </div>
            <div class="scard c-green">
                <div class="scard-top">
                    <span class="scard-label">Handled</span>
                    <div class="scard-icon">
                        <svg viewBox="0 0 24 24" fill="none" stroke-width="2"><polyline points="20 6 9 17 4 12" stroke-linecap="round" stroke-linejoin="round"/></svg>
                    </div>
                </div>
                <div class="scard-val" id="s-handled">—</div>
            </div>
            <div class="scard c-red">
                <div class="scard-top">
                    <span class="scard-label">Errors</span>
                    <div class="scard-icon">
                        <svg viewBox="0 0 24 24" fill="none" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12" stroke-linecap="round"/><line x1="12" y1="16" x2="12.01" y2="16" stroke-linecap="round" stroke-width="2.5"/></svg>
                    </div>
                </div>
                <div class="scard-val" id="s-errors">—</div>
            </div>
            <div class="scard c-text">
                <div class="scard-top">
                    <span class="scard-label">Uptime</span>
                    <div class="scard-icon">
                        <svg viewBox="0 0 24 24" fill="none" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14" stroke-linecap="round" stroke-linejoin="round"/></svg>
                    </div>
                </div>
                <div class="scard-val" id="s-uptime">—</div>
            </div>
        </div>

        <!-- Two columns -->
        <div class="grid2">
            <!-- Handlers -->
            <div class="section">
                <div class="section-head">
                    <div class="section-title">
                        Handlers <span class="count-badge" id="h-count">0</span>
                    </div>
                </div>
                <table>
                    <colgroup>
                        <col style="width:140px">
                        <col>
                        <col>
                    </colgroup>
                    <thead>
                        <tr>
                            <th>Event</th>
                            <th>Function</th>
                            <th>Filters</th>
                        </tr>
                    </thead>
                    <tbody id="h-tbody">
                        <tr><td colspan="3"><div class="empty">Loading...</div></td></tr>
                    </tbody>
                </table>
            </div>

            <!-- Right col -->
            <div style="display:flex;flex-direction:column;gap:18px;">
                <!-- Updates by type -->
                <div class="section">
                    <div class="section-head">
                        <div class="section-title">Updates by type</div>
                        <div class="refresh-label">
                            <div class="refresh-dot"></div>
                            <span id="refresh-ago">live</span>
                        </div>
                    </div>
                    <div id="type-list" class="type-list">
                        <div class="type-empty">No updates yet</div>
                    </div>
                </div>

                <!-- Quick info -->
                <div class="section">
                    <div class="section-head">
                        <div class="section-title">Bot info</div>
                    </div>
                    <div id="bot-info" style="padding:4px 0;"></div>
                </div>
            </div>
        </div>
    </main>

    <footer class="footer">
        <div class="footer-in">
            <span class="footer-txt">FastVK <strong>__VERSION__</strong> &nbsp;·&nbsp; group <strong>__GROUP_ID__</strong></span>
            <a href="https://github.com/ndugram/fastvk" class="gh-link" target="_blank" rel="noopener noreferrer" aria-label="GitHub">
                <svg viewBox="0 0 24 24"><path d="M12 0C5.374 0 0 5.373 0 12c0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23A11.509 11.509 0 0112 5.803c1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576C20.566 21.797 24 17.3 24 12c0-6.627-5.373-12-12-12z"/></svg>
            </a>
        </div>
    </footer>
</div>

<script>
    const EVT_CLASS = {
        message_new:   'e-message_new',
        message_event: 'e-message_event',
        group_join:    'e-group_join',
        group_leave:   'e-group_leave',
        wall_post_new: 'e-wall_post_new',
    };
    function evtCls(evt) { return EVT_CLASS[evt] || 'e-default'; }

    function fmtUptime(s) {
        const h = Math.floor(s / 3600), m = Math.floor((s % 3600) / 60), sec = Math.floor(s % 60);
        if (h > 0) return h + 'h ' + String(m).padStart(2,'0') + 'm';
        if (m > 0) return m + 'm ' + String(sec).padStart(2,'0') + 's';
        return sec + 's';
    }

    function animNum(el, to) {
        const from = parseInt(el.dataset.val || '0', 10);
        if (from === to) return;
        el.dataset.val = to;
        const diff = to - from, dur = 400, start = performance.now();
        function tick(now) {
            const p = Math.min((now - start) / dur, 1);
            const ease = 1 - Math.pow(1 - p, 3);
            el.textContent = Math.round(from + diff * ease);
            if (p < 1) requestAnimationFrame(tick);
        }
        requestAnimationFrame(tick);
    }

    let lastRefresh = Date.now();

    async function loadInfo() {
        const d = await fetch('/api/info').then(r => r.json());

        // chips
        document.getElementById('chips').innerHTML = [
            ['group_id', d.group_id],
            ['api', d.api_version],
            ['fastvk', d.version],
        ].map(([k,v]) =>
            '<div class="chip"><span class="chip-k">' + k + '</span><span class="chip-v">' + v + '</span></div>'
        ).join('');

        // bot info section
        document.getElementById('bot-info').innerHTML = [
            ['Group ID', d.group_id],
            ['API version', d.api_version],
            ['FastVK version', d.version],
            ['Handlers', d.handlers.length],
        ].map(([k,v]) =>
            '<div class="binfo-row">' +
            '<span style="color:var(--text2)">' + k + '</span>' +
            '<span style="font-weight:600">' + v + '</span></div>'
        ).join('');

        // handlers table
        document.getElementById('h-count').textContent = d.handlers.length;
        const tbody = document.getElementById('h-tbody');
        if (!d.handlers.length) {
            tbody.innerHTML = '<tr><td colspan="3"><div class="empty">No handlers registered yet</div></td></tr>';
            return;
        }
        tbody.innerHTML = d.handlers.map(h => {
            const cls = evtCls(h.event);
            const filters = h.filters.length
                ? h.filters.map(f => '<span class="filter-tag">' + f + '</span>').join('')
                : '<span class="no-filters">—</span>';
            return '<tr><td>' +
                '<div class="row-inner">' +
                '<div class="row-accent ' + cls + '-acc"></div>' +
                '<div class="row-content">' +
                '<span class="evt-badge ' + cls + '"><span class="evt-dot ' + cls + '-dot"></span>' + h.event + '</span>' +
                '<div><div class="fn-name">' + h.handler + '()</div><div class="fn-module">' + h.module + '</div></div>' +
                '<div class="filters-wrap">' + filters + '</div>' +
                '</div></div></td></tr>';
        }).join('').replace(/<tr><td>/g, '<tr><td colspan="3">');
    }

    async function loadStats() {
        const d = await fetch('/api/stats').then(r => r.json());

        animNum(document.getElementById('s-total'),   d.total);
        animNum(document.getElementById('s-handled'), d.handled);
        animNum(document.getElementById('s-errors'),  d.errors);
        document.getElementById('s-uptime').textContent = fmtUptime(d.uptime_seconds);

        // refresh label
        lastRefresh = Date.now();
        document.getElementById('refresh-ago').textContent = 'just now';

        // type bars
        const entries = Object.entries(d.by_type).sort((a,b) => b[1]-a[1]);
        const max = entries.length ? entries[0][1] : 1;
        const list = document.getElementById('type-list');
        if (!entries.length) {
            list.innerHTML = '<div class="type-empty">No updates yet</div>';
            return;
        }
        list.innerHTML = entries.map(([type, count]) => {
            const cls = evtCls(type);
            const pct = Math.max(4, Math.round(count / max * 100));
            return '<div class="type-row">' +
                '<span class="type-name">' + type + '</span>' +
                '<div class="type-bar-wrap"><div class="type-bar ' + cls + '-bar" style="width:' + pct + '%"></div></div>' +
                '<span class="type-count ' + cls + '-cnt">' + count + '</span>' +
                '</div>';
        }).join('');
    }

    // update "X ago" label
    setInterval(() => {
        const sec = Math.round((Date.now() - lastRefresh) / 1000);
        document.getElementById('refresh-ago').textContent = sec < 5 ? 'just now' : sec + 's ago';
    }, 1000);

    loadInfo();
    loadStats();
    setInterval(loadStats, 3000);
</script>
</body>
</html>
"""


def get_dashboard_html(*, version: str, group_id: int) -> str:
    return DASHBOARD_HTML.replace("__VERSION__", version).replace("__GROUP_ID__", str(group_id))
