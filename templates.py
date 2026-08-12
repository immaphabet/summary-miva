HTML_LAYOUT = """
<!DOCTYPE html>
<html>
<head>
    <title>GistPulse | Campus News & Gist Hub</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 0; background: #ffffff; color: #111827; min-height: 100vh; display: flex; flex-direction: column; align-items: center; justify-content: flex-start; }
        #app-screen { width: 100%; max-width: 600px; padding: 20px; box-sizing: border-box; display: flex; flex-direction: column; min-height: 100vh; }
        
        .app-header { width: 100%; border-bottom: 3px solid #dc2626; padding-bottom: 12px; margin-bottom: 20px; text-align: left; }
        .brand-logo { font-size: 32px; font-weight: 900; color: #dc2626; letter-spacing: -1px; text-transform: uppercase; }
        .brand-sub { font-size: 12px; color: #4b5563; margin-top: 4px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; }
        
        .publisher-card { background: #f8fafc; border: 1px solid #e2e8f0; border-left: 4px solid #dc2626; padding: 14px 16px; border-radius: 8px; margin-bottom: 20px; box-sizing: border-box; }
        .publisher-title { font-size: 14px; font-weight: 700; color: #111827; margin: 0 0 4px 0; }
        .publisher-text { font-size: 12px; color: #4b5563; margin: 0; line-height: 1.5; }
        
        /* News List Stream Container */
        .news-stream { width: 100%; display: flex; flex-direction: column; gap: 16px; padding-bottom: 140px; }
        
        .news-card { background: #ffffff; border: 1px solid #e5e7eb; padding: 20px; border-radius: 12px; box-sizing: border-box; display: flex; flex-direction: column; gap: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.02); }
        .card-tag { font-size: 11px; color: #dc2626; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; }
        .card-title { font-size: 19px; font-weight: 800; color: #111827; line-height: 1.35; margin: 2px 0; }
        .card-excerpt { color: #374151; font-size: 14px; line-height: 1.6; text-align: left; }
        
        .action-link { align-self: flex-start; margin-top: 4px; font-size: 13px; color: #dc2626; text-decoration: none; font-weight: 700; }
        .action-link:hover { text-decoration: underline; }
        .no-results { color: #6b7280; font-size: 14px; text-align: center; padding: 30px; width: 100%; }
        
        /* FIXED: Static Credit Footer text placed right inside the scrolling list sequence */
        .static-footer-credit { width: 100%; padding: 20px 0; font-size: 11px; color: #9ca3af; text-align: center; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; border-top: 1px dashed #e5e7eb; margin-top: 10px; }
        
        /* Clean Floating Input Search Bar Dock Layout with zero overlapping text elements */
        .search-dock { position: fixed; bottom: 0; left: 0; right: 0; background: linear-gradient(transparent, #ffffff 30%); padding: 25px 0; display: flex; flex-direction: column; align-items: center; z-index: 10; }
        .search-pill-bar { width: 92%; max-width: 600px; background: #ffffff; border: 2px solid #e5e7eb; border-radius: 30px; padding: 4px 6px 4px 16px; box-sizing: border-box; display: flex; align-items: center; gap: 10px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); }
        .search-pill-bar:focus-within { border-color: #dc2626; }
        
        input[type="text"] { flex: 1; height: 38px; background: transparent; border: none; color: #111827; font-size: 15px; font-family: inherit; box-sizing: border-box; }
        input[type="text"]:focus { outline: none; }
        input[type="text"]::placeholder { color: #9ca3af; }
        
        .search-execute-btn { background: #dc2626; border: none; border-radius: 20px; padding: 10px 22px; font-size: 13px; font-weight: 700; color: #ffffff; cursor: pointer; flex-shrink: 0; text-transform: uppercase; letter-spacing: 0.5px; }
        .search-execute-btn:active { background: #b91c1c; }
    </style>
</head>
<body>
    <div id="app-screen">
        <div class="app-header">
            <div class="brand-logo">GistPulse</div>
            <div class="brand-sub">Live Campus News Aggregation & Short Gist Syndication</div>
        </div>
        
        <div class="publisher-card">
            <div class="publisher-title">GistPulse Newsroom</div>
            <div class="publisher-text"><strong>Lead Developer: Emmanuel Olorunjuwonlo</strong><br>Monitoring live academic news feeds, admissions data streams, and trending student updates.</div>
        </div>
        
        <div class="news-stream">
            {% if articles %}
                {% for item in articles %}
                <div class="news-card">
                    <div class="card-tag">Breaking News</div>
                    <div class="card-title">{{ item.title }}</div>
                    <div class="card-excerpt">{{ item.summary }}</div>
                    <a href="{{ item.link }}" target="_blank" class="action-link">Read Full Story &rarr;</a>
                </div>
                {% endfor %}
                
                <!-- Your name sits cleanly here at the end of the scroll stream, out of the way! -->
                <div class="static-footer-credit">Developed by Emmanuel Olorunjuwonlo</div>
            {% else %}
                <div class="no-results">No breaking headlines found matching your search keyword context filter.</div>
            {% endif %}
        </div>
        
        <div class="search-dock">
            <div class="search-pill-bar">
                <form method="POST" action="/" style="width:100%; display:flex; align-items:center; gap:8px; margin:0;">
                    <input type="text" name="search_filter" placeholder="Search school news (e.g. Miva, JAMB, Admission)...">
                    <button type="submit" class="search-execute-btn">Search</button>
                </form>
            </div>
        </div>
    </div>
</body>
</html>
"""

ADMIN_LAYOUT = """
<!DOCTYPE html>
<html>
<head>
    <title>GistPulse | Console</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { font-family: sans-serif; background: #ffffff; color: #111827; text-align: center; padding: 40px 20px; }
        .box { max-width: 400px; margin: auto; background: #f8fafc; border: 1px solid #e2e8f0; border-top: 4px solid #dc2626; padding: 28px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.02); }
        h3 { margin-top: 0; color: #111827; }
        .circle { width: 110px; height: 110px; border-radius: 50%; background: #ffffff; display: flex; align-items: center; justify-content: center; font-size: 36px; margin: 20px auto; border: 3px solid #dc2626; font-weight: bold; color: #dc2626; }
        input { width: 85%; padding: 12px; background: #ffffff; border: 2px solid #e5e7eb; color: #111827; margin-bottom: 12px; text-align: center; border-radius: 8px; font-size: 16px; }
        input:focus { border-color: #dc2626; outline: none; }
        button { background: #dc2626; color: #ffffff; border: none; padding: 12px 24px; border-radius: 8px; font-weight: bold; cursor: pointer; text-transform: uppercase; font-size: 13px; letter-spacing: 0.5px; }
    </style>
</head>
<body>
    <div class="box">
        <h3>GistPulse Co-Founder Console</h3>
        <p style="font-size:12px; color:#4b5563; margin-top:-5px; margin-bottom:20px;">Welcome, Emmanuel Olorunjuwonlo</p>
        {% if authenticated %}
            <div class="circle">{{ active_count }}</div>
            <p style="color:#4b5563; font-size:13px; line-height:1.5;">Unique device browser sessions logged inside server cache loop right now.</p>
        {% else %}
            <form method="POST" action="/admin">
                <input type="password" name="admin_password" placeholder="Admin Access Key" required><br>
                <button type="submit">Verify Identity</button>
            </form>
            {% if error %}<p style="color:#dc2626; font-size:12px; margin-top:10px; font-weight:600;">{{ error }}</p>{% endif %}
        {% endif %}
    </div>
</body>
</html>
"""
