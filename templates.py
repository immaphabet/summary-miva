HTML_LAYOUT = """
<!DOCTYPE html>
<html>
<head>
    <title>GistPulse | Campus Hub</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { font-family: -apple-system, sans-serif; margin: 0; padding: 0; background: #000000; color: #ffffff; min-height: 100vh; }
        #viewport-slider { display: flex; width: 200vw; min-height: 100vh; transition: transform 0.6s ease; }
        .page-screen-view, .dashboard-screen { width: 100vw; min-height: 100vh; box-sizing: border-box; display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 20px; }
        .dashboard-screen { justify-content: flex-start; }
        .agreement-pill-box { background: #11141b; border: 1px solid #1e293b; padding: 20px; border-radius: 16px; max-width: 340px; margin: 20px 0; }
        .enter-hub-btn { background: #38bdf8; color: #000000; border: none; padding: 12px 40px; border-radius: 20px; font-weight: bold; cursor: pointer; opacity: 0.5; pointer-events: none; }
        .enter-hub-btn.active { opacity: 1; pointer-events: auto; }
        .workspace-body { width: 100%; max-width: 500px; padding-bottom: 120px; }
        .summary-box { background: #11141b; border: 1px solid #1e293b; padding: 16px; border-radius: 12px; margin-bottom: 12px; }
        .card-tag { font-size: 11px; color: #38bdf8; font-weight: bold; }
        .card-title { font-size: 16px; font-weight: bold; margin: 4px 0; }
        .ai-markdown-bubble { color: #cbd5e1; font-size: 13px; }
        .read-more-btn { background: #005c4b; color: #ffffff; padding: 4px 12px; border-radius: 12px; text-decoration: none; font-size: 12px; display: inline-block; margin-top: 6px; }
        .bottom-dock { position: fixed; bottom: 0; left: 0; right: 0; background: #000000; padding: 16px; display: flex; flex-direction: column; align-items: center; }
        .console-pill { width: 90%; max-width: 500px; background: #11141b; border: 1px solid #1e293b; border-radius: 24px; padding: 6px 12px; display: flex; align-items: center; }
        textarea { flex: 1; height: 36px; background: transparent; border: none; color: #ffffff; resize: none; padding-top: 8px; }
        textarea:focus { outline: none; }
        .action-send-btn { width: 32px; height: 36px; background: #38bdf8; border: none; border-radius: 50%; display: flex; align-items: center; justify-content: center; cursor: pointer; }
    </style>
</head>
<body>
    <div id="viewport-slider">
        <div class="page-screen-view">
            <h2>GistPulse</h2>
            <p style="color:#64748b; text-align:center;">Unified campus data syndication pipeline.</p>
            <div class="agreement-pill-box">
                <input type="checkbox" id="consent-gate" onchange="togglePermission(this)">
                <label for="consent-gate" style="font-size:12px; color:#cbd5e1;">I agree to launch the GistPulse interface and accept that headlines are synced live.</label>
            </div>
            <button type="button" class="enter-hub-btn" id="gate-btn" onclick="slideView()">Enter Workspace</button>
        </div>
        <div class="dashboard-screen">
            <div class="workspace-body">
                <h3>GistPulse</h3>
                {% if articles %}
                    {% for item in articles %}
                    <div class="summary-box">
                        <div class="card-tag">Campus Wire</div>
                        <div class="card-title">{{ item.title }}</div>
                        <div class="ai-markdown-bubble">{{ item.summary }}</div>
                        <a href="{{ item.link }}" target="_blank" class="read-more-btn">Read Full Gist</a>
                    </div>
                    {% endfor %}
                {% else %}
                    <p style="color:#64748b; text-align:center;">No match found.</p>
                {% endif %}
            </div>
            <div class="bottom-dock">
                <p style="font-size:11px; color:#475569; margin:4px;">Developed by Emmanuel Olorunjuwonlo</p>
                <div class="console-pill">
                    <form method="POST" action="/" id="engine-form" style="width:100%; display:flex; gap:6px; margin:0;">
                        <textarea name="search_filter" placeholder="Filter gist..."></textarea>
                        <button type="submit" class="action-send-btn"><svg viewBox="0 0 24 24" style="width:16px; fill:#000;"><path d="M2,21L23,12L2,3V10L17,12L2,14V21Z"/></svg></button>
                    </form>
                </div>
            </div>
        </div>
    </div>
    <script>
        window.onload = function() {
            if ("{{ is_post }}" === "True") {
                document.getElementById("viewport-slider").style.transform = "translateX(-100vw)";
            }
        };
        function togglePermission(cb) {
            document.getElementById("gate-btn").classList.toggle("active", cb.checked);
        }
        function slideView() {
            document.getElementById("viewport-slider").style.transform = "translateX(-100vw)";
        }
    </script>
</body>
</html>
"""

ADMIN_LAYOUT = """
<!DOCTYPE html>
<html>
<head>
    <title>GistPulse | Admin</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { font-family: sans-serif; background: #000000; color: #ffffff; text-align: center; padding: 40px 20px; }
        .box { max-width: 400px; margin: auto; background: #11141b; border: 1px solid #1e293b; padding: 20px; border-radius: 12px; }
        .circle { width: 100px; height: 100px; border-radius: 50%; background: #005c4b; display: flex; align-items: center; justify-content: center; font-size: 32px; margin: 20px auto; border: 2px solid #38bdf8; }
        input { width: 80%; padding: 10px; background: #000000; border: 1px solid #1e293b; color: #ffffff; margin-bottom: 10px; text-align: center; border-radius: 6px; }
        button { background: #38bdf8; color: #000000; border: none; padding: 10px 20px; border-radius: 6px; font-weight: bold; }
    </style>
</head>
<body>
    <div class="box">
        <h3>Co-Founder Console</h3>
        {% if authenticated %}
            <div class="circle">{{ active_count }}</div>
            <p style="color:#64748b; font-size:13px;">Active browser sessions in memory.</p>
        {% else %}
            <form method="POST" action="/admin">
                <input type="password" name="admin_password" placeholder="Admin Key" required><br>
                <button type="submit">Verify</button>
            </form>
            {% if error %}<p style="color:#f43f5e; font-size:12px;">{{ error }}</p>{% endif %}
        {% endif %}
    </div>
</body>
</html>
"""
