import os
import base64
from flask import Flask, render_template_string, request
import google.generativeai as genai
import markdown

app = Flask(__name__)

API_KEY = os.environ.get("GEMINI_API_KEY")
genai.configure(api_key=API_KEY)
# Securely hooks into Google's premier production flash model identifier
model = genai.GenerativeModel('gemini-1.5-flash')

HTML_LAYOUT = """
<!DOCTYPE html>
<html>
<head>
    <title>CramPulse | AI Study Workspace</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 0; background: #000000; color: #ffffff; min-height: 100vh; display: flex; flex-direction: column; align-items: center; justify-content: flex-start; overflow-x: hidden; -webkit-user-select: none; user-select: none; }
        #app-screen { width: 100%; max-width: 600px; padding: 20px; box-sizing: border-box; display: flex; flex-direction: column; min-height: 100vh; justify-content: space-between; position: relative; }
        .workspace-body { flex: 1; display: flex; flex-direction: column; justify-content: center; padding-bottom: 140px; margin-top: 20px; width: 100%; }
        .gemini-greeting { font-size: 38px; font-weight: 400; line-height: 1.25; color: #ffffff; letter-spacing: -1px; margin-bottom: 35px; text-align: left; max-width: 95%; }
        
        .output-stream { width: 100%; display: flex; flex-direction: column; gap: 16px; margin-bottom: 20px; }
        
        /* User Bubble Style with touch compatibility settings enabled */
        .user-message-bubble { background: #005c4b; color: #ffffff; padding: 14px 18px; border-radius: 18px 18px 4px 18px; align-self: flex-end; max-width: 85%; font-size: 15px; line-height: 1.5; word-wrap: break-word; text-align: left; box-shadow: 0 1px 2px rgba(0,0,0,0.3); margin-left: auto; position: relative; -webkit-tap-highlight-color: transparent; cursor: pointer; }
        
        /* AI Response Container Box */
        .summary-box { background: #11141b; border: 1px solid #1e293b; padding: 24px; border-radius: 18px 18px 18px 4px; width: 85%; box-sizing: border-box; align-self: flex-start; }
        .ai-markdown-bubble { color: #e2e8f0; font-size: 16px; line-height: 1.7; text-align: left; }
        .ai-markdown-bubble h1, .ai-markdown-bubble h2, .ai-markdown-bubble h3 { color: #38bdf8; margin-top: 16px; margin-bottom: 8px; font-weight: 600; }
        .ai-markdown-bubble p { margin: 0 0 12px 0; }
        .ai-markdown-bubble strong { color: #ffffff; font-weight: 600; }
        .ai-markdown-bubble ul, .ai-markdown-bubble ol { margin: 0 0 16px 0; padding-left: 20px; color: #cbd5e1; }
        .ai-markdown-bubble li { margin-bottom: 6px; }
        
        /* Floating Action Context Menu Menu Overlay (WhatsApp Layout Match) */
        .custom-context-menu { position: fixed; background: #1f2c34; border: 1px solid #2a3942; border-radius: 12px; padding: 6px 0; width: 140px; box-shadow: 0 4px 12px rgba(0,0,0,0.5); display: none; z-index: 100; }
        .context-menu-item { padding: 12px 16px; font-size: 14px; color: #e9edef; cursor: pointer; display: flex; align-items: center; font-weight: 500; }
        .context-menu-item:active { background: #101a20; }
        
        .bottom-dock { position: fixed; bottom: 0; left: 0; right: 0; background: linear-gradient(transparent, #000000 25%); padding: 20px 0; display: flex; flex-direction: column; align-items: center; z-index: 10; }
        .grok-disclosure-line { font-size: 12px; color: #475569; margin-bottom: 8px; text-align: center; font-weight: 500; }
        .console-pill { width: 92%; max-width: 600px; background: #11141b; border: 1px solid #1e293b; border-radius: 28px; padding: 8px 16px; box-sizing: border-box; display: flex; flex-direction: column; gap: 6px; }
        .input-text-group { display: flex; align-items: center; gap: 10px; width: 100%; }
        textarea { flex: 1; height: 44px; padding: 12px 4px 0 4px; border: none; background: transparent; color: #ffffff; resize: none; font-size: 15px; font-family: inherit; box-sizing: border-box; -webkit-user-select: text; user-select: text; }
        textarea:focus { outline: none; }
        textarea::placeholder { color: #475569; }
        .action-send-btn { width: 40px; height: 40px; background: #38bdf8; border: none; border-radius: 50%; display: flex; align-items: center; justify-content: center; cursor: pointer; color: #000000; flex-shrink: 0; padding-left: 4px; }
        .action-send-btn svg { fill: #000000; width: 18px; height: 18px; }
    </style>
</head>
<body>
    <div id="app-screen">
        <div class="workspace-body">
            <div class="gemini-greeting">I can help compress, study, review & more. What should we do?</div>
            
            <div class="output-stream">
                {% if user_question %}
                <div class="user-message-bubble" id="chat-bubble" ontouchstart="handleTouchStart(event)" ontouchend="handleTouchEnd(event)">{{ user_question }}</div>
                {% endif %}
                
                {% if summary %}
                <div class="summary-box" id="ai-response-box">
                    <div class="ai-markdown-bubble">{{ summary|safe }}</div>
                </div>
                {% endif %}
            </div>
        </div>
        
        <div class="custom-context-menu" id="popup-menu">
            <div class="context-menu-item" onclick="executeCopyAction()">Copy</div>
            <div class="context-menu-item" style="color: #38bdf8; border-top: 1px solid #2a3942;" onclick="executeEditAction()">Edit</div>
        </div>

        <div class="bottom-dock">
            <div class="grok-disclosure-line">Developed by Emmanuel Olorunjuwonlo</div>
            <div class="console-pill">
                <form method="POST" action="/" id="engine-form" style="margin:0; display:flex; flex-direction:column; gap:6px;">
                    <div class="input-text-group">
                        <textarea name="extra_prompt" id="user-input" placeholder="Ask CramPulse anything..." required></textarea>
                        <button type="submit" class="action-send-btn">
                            <svg viewBox="0 0 24 24">
                                <path d="M2,21L23,12L2,3V10L17,12L2,14V21Z" />
                            </svg>
                        </button>
                    </div>
                </form>
            </div>
        </div>
    </div>

    <script>
        let longPressTimer;
        const menu = document.getElementById("popup-menu");
        const bubble = document.getElementById("chat-bubble");

        function handleTouchStart(e) {
            longPressTimer = setTimeout(() => {
                triggerContextMenu(e);
            }, 500);
        }

        function handleTouchEnd() {
            clearTimeout(longPressTimer);
        }

        function triggerContextMenu(e) {
            e.preventDefault();
            const rect = bubble.getBoundingClientRect();
            menu.style.top = `${rect.top - 90}px`;
            menu.style.left = `${rect.right - 140}px`;
            menu.style.display = "block";
        }

        document.addEventListener("click", function(e) {
            if (e.target !== bubble && !menu.contains(e.target)) {
                menu.style.display = "none";
            }
        });

        function executeCopyAction() {
            const rawText = bubble.innerText;
            navigator.clipboard.writeText(rawText);
            menu.style.display = "none";
        }

        function executeEditAction() {
            const rawText = bubble.innerText;
            const textInput = document.getElementById("user-input");
            textInput.value = rawText;
            textInput.focus();
            menu.style.display = "none";
            bubble.style.display = "none";
            const aiResponse = document.getElementById("ai-response-box");
            if (aiResponse) aiResponse.style.display = "none";
        }
    </script>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET": return render_template_string(HTML_LAYOUT, summary=None, user_question=None)
    summary = None
    extra_prompt = request.form.get("extra_prompt", "").strip()
    
    if extra_prompt:
        try:
            response = model.generate_content(contents=[extra_prompt])
            summary = markdown.markdown(response.text)
        except Exception as e:
            summary = f"⚠️ CramPulse Engine Error: {str(e)}"
            
    return render_template_string(HTML_LAYOUT, summary=summary, user_question=extra_prompt)

if __name__ == '__main__':
    app.run(debug=True)
