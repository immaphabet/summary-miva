import os
import base64
from flask import Flask, render_template_string, request
import google.generativeai as genai
import markdown

app = Flask(__name__)

API_KEY = os.environ.get("GEMINI_API_KEY")
genai.configure(api_key=API_KEY)
# CORRECT MODEL ID: Matches the exact syntax expected by your SDK version
model = genai.GenerativeModel('gemini-2.5-flash')

HTML_LAYOUT = """
<!DOCTYPE html>
<html>
<head>
    <title>CramPulse | AI Study Workspace</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 0; background: #000000; color: #ffffff; min-height: 100vh; display: flex; flex-direction: column; align-items: center; justify-content: flex-start; overflow-x: hidden; }
        #app-screen { width: 100%; max-width: 600px; padding: 20px; box-sizing: border-box; display: flex; flex-direction: column; min-height: 100vh; justify-content: space-between; }
        .workspace-body { flex: 1; display: flex; flex-direction: column; justify-content: center; padding-bottom: 140px; margin-top: 20px; width: 100%; }
        .gemini-greeting { font-size: 38px; font-weight: 400; line-height: 1.25; color: #ffffff; letter-spacing: -1px; margin-bottom: 35px; text-align: left; max-width: 95%; }
        .output-stream { width: 100%; display: flex; flex-direction: column; gap: 20px; }
        .summary-box { background: #11141b; border: 1px solid #1e293b; padding: 24px; border-radius: 20px; width: 100%; box-sizing: border-box; }
        .ai-markdown-bubble { color: #e2e8f0; font-size: 16px; line-height: 1.7; text-align: left; }
        .ai-markdown-bubble h1, .ai-markdown-bubble h2, .ai-markdown-bubble h3 { color: #38bdf8; margin-top: 16px; margin-bottom: 8px; font-weight: 600; }
        .ai-markdown-bubble h1 { font-size: 22px; border-bottom: 1px solid #1e293b; padding-bottom: 6px; }
        .ai-markdown-bubble h2 { font-size: 19px; }
        .ai-markdown-bubble h3 { font-size: 17px; }
        .ai-markdown-bubble p { margin: 0 0 12px 0; }
        .ai-markdown-bubble strong { color: #ffffff; font-weight: 600; }
        .ai-markdown-bubble ul, .ai-markdown-bubble ol { margin: 0 0 16px 0; padding-left: 20px; color: #cbd5e1; }
        .ai-markdown-bubble li { margin-bottom: 6px; }
        .ai-markdown-bubble code { background: #1e293b; padding: 2px 6px; border-radius: 4px; font-family: monospace; font-size: 14px; color: #f43f5e; }
        .bottom-dock { position: fixed; bottom: 0; left: 0; right: 0; background: linear-gradient(transparent, #000000 25%); padding: 20px 0; display: flex; flex-direction: column; align-items: center; z-index: 10; }
        .grok-disclosure-line { font-size: 12px; color: #475569; margin-bottom: 8px; text-align: center; font-weight: 500; }
        .console-pill { width: 92%; max-width: 600px; background: #11141b; border: 1px solid #1e293b; border-radius: 28px; padding: 8px 16px; box-sizing: border-box; display: flex; flex-direction: column; gap: 6px; }
        .input-text-group { display: flex; align-items: center; gap: 10px; width: 100%; }
        textarea { flex: 1; height: 44px; padding: 12px 4px 0 4px; border: none; background: transparent; color: #ffffff; resize: none; font-size: 15px; font-family: inherit; box-sizing: border-box; }
        textarea:focus { outline: none; }
        textarea::placeholder { color: #475569; }
        .action-send-btn { width: 40px; height: 40px; background: #38bdf8; border: none; border-radius: 50%; display: flex; align-items: center; justify-content: center; cursor: pointer; color: #000000; font-weight: bold; font-size: 16px; flex-shrink: 0; }
    </style>
</head>
<body>
    <div id="app-screen">
        <div class="workspace-body">
            <div class="gemini-greeting">I can help compress, study, review & more. What should we do?</div>
            <div class="output-stream">
                {% if summary %}
                <div class="summary-box">
                    <div class="ai-markdown-bubble">{{ summary|safe }}</div>
                </div>
                {% endif %}
            </div>
        </div>
        <div class="bottom-dock">
            <div class="grok-disclosure-line">Developed by Emmanuel Olorunjuwonlo</div>
            <div class="console-pill">
                <form method="POST" action="/" id="engine-form" style="margin:0; display:flex; flex-direction:column; gap:6px;">
                    <div class="input-text-group">
                        <textarea name="extra_prompt" id="user-input" placeholder="Ask CramPulse anything..." required></textarea>
                        <button type="submit" class="action-send-btn">&uarr;</button>
                    </div>
                </form>
            </div>
        </div>
    </div>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET": return render_template_string(HTML_LAYOUT, summary=None)
    summary = None
    extra_prompt = request.form.get("extra_prompt", "").strip()
    
    if extra_prompt:
        try:
            response = model.generate_content(contents=[extra_prompt])
            summary = markdown.markdown(response.text)
        except Exception as e:
            summary = f"⚠️ CramPulse Engine Error: {str(e)}"
            
    return render_template_string(HTML_LAYOUT, summary=summary)

if __name__ == '__main__':
    app.run(debug=True)
