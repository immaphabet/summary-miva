import os
import base64
from flask import Flask, render_template_string, request
import google.generativeai as genai

app = Flask(__name__)

API_KEY = os.environ.get("GEMINI_API_KEY")
genai.configure(api_key=API_KEY)
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
        .ai-markdown-bubble { color: #e2e8f0; font-size: 16px; line-height: 1.7; text-align: left; white-space: pre-wrap; word-wrap: break-word; }
        .slide-bubble { width: 100%; height: 240px; background: #11141b; border: 1px solid #1e293b; border-radius: 20px; display: flex; align-items: center; justify-content: center; overflow: hidden; position: relative; margin-bottom: 11px; }
        .slide-bubble img { max-width: 100%; max-height: 100%; object-fit: contain; }
        .counter-pill { position: absolute; top: 12px; right: 12px; background: rgba(0,0,0,0.85); padding: 4px 12px; border-radius: 20px; font-size: 11px; color: #38bdf8; font-weight: 600; }
        .slider-row { display: flex; gap: 10px; margin-bottom: 25px; }
        .nav-btn { flex: 1; padding: 12px; background: #11141b; border: 1px solid #1e293b; color: #e2e8f0; border-radius: 12px; cursor: pointer; font-size: 13px; font-weight: 600; }
        .bottom-dock { position: fixed; bottom: 0; left: 0; right: 0; background: linear-gradient(transparent, #000000 25%); padding: 20px 0; display: flex; flex-direction: column; align-items: center; }
        .grok-disclosure-line { font-size: 12px; color: #475569; margin-bottom: 8px; text-align: center; font-weight: 500; }
        .console-pill { width: 92%; max-width: 600px; background: #11141b; border: 1px solid #1e293b; border-radius: 28px; padding: 8px 16px; box-sizing: border-box; display: flex; flex-direction: column; gap: 6px; }
        .file-upload-row { display: flex; align-items: center; justify-content: flex-start; padding: 4px 0; border-bottom: 1px solid #1e293b; margin-bottom: 4px; }
        .file-upload-row input[type="file"] { font-size: 12px; color: #64748b; width: 100%; }
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
                <div id="deck-preview-bubble" style="display:none; width: 100%;">
                    <div class="slide-bubble" id="display-frame"><span style="color:#475569;">Assembling material elements...</span></div>
                    <div class="slider-row">
                        <button type="button" class="nav-btn" onclick="shiftSlideIndex(-1)">&larr; Prev Slide</button>
                        <button type="button" class="nav-btn" onclick="shiftSlideIndex(1)">Next Slide &rarr;</button>
                    </div>
                </div>
                <div class="ai-markdown-bubble" id="response-block">{{ summary }}</div>
            </div>
        </div>
        <div class="bottom-dock">
            <div class="grok-disclosure-line">Developed by Emmanuel Olorunjuwonlo</div>
            <div class="console-pill">
                <form method="POST" enctype="multipart/form-data" id="engine-form" style="margin:0; display:flex; flex-direction:column; gap:6px;">
                    <div class="file-upload-row"><input type="file" name="slide_images" multiple accept="image/*" onchange="loadSlidesPreview(this)" required></div>
                    <div class="input-text-group">
                        <textarea name="extra_prompt" id="user-input" placeholder="Ask CramPulse anything..." required></textarea>
                        <button type="submit" class="action-send-btn" onclick="indicateLoadingState()">&uarr;</button>
                    </div>
                </form>
            </div>
        </div>
    </div>
    <script>
        var localSlidesCache = []; var activePointer = 0;
        function loadSlidesPreview(uploader) {
            localSlidesCache = []; activePointer = 0;
            if(uploader.files && uploader.files.length > 0) {
                document.getElementById("deck-preview-bubble").style.display = "block";
                Array.from(uploader.files).forEach(file => {
                    const reader = new FileReader();
                    reader.onload = (e) => { localSlidesCache.push(e.target.result); refreshViewerDOM(); };
                    reader.readAsDataURL(file);
                });
            }
        }
        function refreshViewerDOM() {
            const frame = document.getElementById("display-frame");
            if (localSlidesCache.length === 0) return;
            frame.innerHTML = `<img src="${localSlidesCache[activePointer]}"><div class="counter-pill">Slide ${activePointer + 1} of ${localSlidesCache.length}</div>`;
        }
        function shiftSlideIndex(direction) {
            if (localSlidesCache.length === 0) return;
            activePointer = (activePointer + direction + localSlidesCache.length) % localSlidesCache.length;
            refreshViewerDOM();
        }
        function indicateLoadingState() {
            const textareaValue = document.getElementById("user-input").value;
            const fileInput = document.querySelector('input[type="file"]').files;
            if(textareaValue && fileInput.length > 0) {
                document.getElementById("response-block").innerHTML = "✨ CramPulse is analyzing your slide materials... compiling your custom briefing study notes now.";
            }
        }
    </script>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    summary = "Hello! Upload your lecture slide files or note screenshots inside the bottom command pill bar, append an action prompt command, and execute to initialize operations."
    if request.method == "POST":
        slide_files = request.files.getlist("slide_images")
        extra_prompt = request.form.get("extra_prompt", "")
        gemini_payload = []
        for file in slide_files:
            if file and file.filename != '':
                file_data = base64.b64encode(file.read()).decode("utf-8")
                gemini_payload.append({"mime_type": file.content_type, "data": file_data})
        if gemini_payload:
            base_instruction = "Analyze these university lecture slides and extract a comprehensive, crisp exam-prep study briefing highlighting core vocabulary definitions and key details."
            if extra_prompt:
                base_instruction += f" Additional Note: {extra_prompt}"
            gemini_payload.append(base_instruction)
            response = model.generate_content(gemini_payload)
            summary = response.text
    return render_template_string(HTML_LAYOUT, summary=summary)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
