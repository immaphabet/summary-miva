import os
import base64
from flask import Flask, render_template_string, request
import google.generativeai as genai

app = Flask(__name__)

# 🔑 Secured API pipeline structure
API_KEY = os.environ.get("GEMINI_API_KEY", "AQ.Ab8RN6LzjBRO6-riXiNGS2amPS7")
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-2.5-flash')

HTML_LAYOUT = """
<!DOCTYPE html>
<html>
<head>
    <title>CramPulse | Universal AI Study Briefings</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { font-family: 'Segoe UI', sans-serif; margin: 0; padding: 0; background: #0e1118; color: #e3e8f0; min-height: 100vh; display: flex; flex-direction: column; align-items: center; justify-content: flex-start; overflow-x: hidden; }
        #intro-screen { background: #fff; max-width: 500px; width: 90%; padding: 30px 20px; border-radius: 24px; box-shadow: 0 20px 40px rgba(0,0,0,0.3); text-align: center; margin: 40px auto; color: #0f172a; }
        .intro-title { color: #0284c7; font-size: 30px; margin-bottom: 15px; font-weight: 700; }
        .intro-bio { font-size: 14px; color: #475569; line-height: 1.6; margin-bottom: 20px; text-align: left; }
        .reveal-left { opacity: 0; transform: translateX(-50px); transition: all 0.6s ease-out; }
        .reveal-right { opacity: 0; transform: translateX(50px); transition: all 0.6s ease-out; }
        .reveal-left.active, .reveal-right.active { opacity: 1; transform: translateX(0); }
        .features-box { text-align: left; background: #f8fafc; border: 1px solid #e2e8f0; padding: 15px; border-radius: 12px; margin-bottom: 20px; }
        .agreement-card { background: #f1f5f9; padding: 15px; border-radius: 12px; margin-bottom: 25px; display: flex; text-align: left; gap: 12px; }
        .primary-btn { width: 100%; padding: 16px; background: #0284c7; color: white; border: none; border-radius: 12px; font-size: 16px; font-weight: bold; cursor: pointer; }
        .primary-btn:disabled { background: #cbd5e1; cursor: not-allowed; }
        #app-screen { width: 95%; max-width: 1000px; margin: 30px auto; display: none; }
        .dashboard-container { display: flex; flex-wrap: wrap; gap: 20px; width: 100%; }
        .panel { flex: 1; min-width: 300px; background: #1e293b; padding: 20px; border-radius: 20px; box-shadow: 0 8px 30px rgba(0,0,0,0.3); box-sizing: border-box; }
        textarea { width: 100%; height: 100px; padding: 12px; border: 2px solid #334155; border-radius: 12px; background: #0f172a; color: white; resize: none; margin-bottom: 15px; box-sizing: border-box; }
        .slideshow-box { width: 100%; height: 220px; background: #0f172a; border: 2px dashed #334155; border-radius: 12px; display: flex; align-items: center; justify-content: center; overflow: hidden; margin: 15px 0; position: relative; }
        .slideshow-box img { max-width: 100%; max-height: 100%; object-fit: contain; }
        .slide-counter { position: absolute; bottom: 10px; right: 10px; background: rgba(0,0,0,0.8); padding: 4px 10px; border-radius: 12px; font-size: 12px; color: #38bdf8; }
        .control-row { display: flex; gap: 10px; margin-bottom: 15px; }
        .sub-btn { flex: 1; padding: 10px; background: #334155; border: none; color: white; border-radius: 8px; cursor: pointer; }
        .result-text { line-height: 1.6; font-size: 15px; white-space: pre-wrap; }
    </style>
</head>
<body>

    <div id="intro-screen">
        <div class="intro-title">⚡ CramPulse Pro</div>
        <div class="intro-bio reveal-left">
            Welcome to your universal academic companion. This engine was engineered by <b>Emmanuel Olorunjuwonlo</b>, a dedicated Computer Science student, leveraging smooth scroll transitions to animate your workspace dashboards while utilizing multimodal AI core pipelines to ingest raw document slides natively.
        </div>
        <div class="features-box reveal-right">
            <div style="font-weight:700; color:#0284c7; margin-bottom:8px;">🛠️ Universal Capabilities:</div>
            <div style="font-size:13px; color:#334155; margin-bottom:5px;">✓ Drag & drop multiple lecture screenshots directly into the processor.</div>
            <div style="font-size:13px; color:#334155;">✓ Automated scroll-triggered layouts rendering clear text transitions.</div>
        </div>
        <div class="agreement-card reveal-left">
            <input type="checkbox" id="consent-check" onchange="toggleLaunchButton()">
            <label for="consent-check" style="font-size: 13px; color: #334155; font-weight: 500; cursor: pointer;">
                I agree to use these generated briefings responsibly alongside my official university course materials.
            </label>
        </div>
        <button id="start-btn" class="primary-btn" disabled onclick="launchWorkspace()">Launch Workspace &rarr;</button>
    </div>

    <div id="app-screen">
        <center>
            <h2 style="color:#38bdf8; margin-top:0;">⚡ CramPulse Workspace</h2>
            <div style="color:#94a3b8; margin-bottom:25px;">Universal Multi-Modal Slide Engine & Exam Prep Analyzer</div>
        </center>
        <div class="dashboard-container">
            <div class="panel reveal-left">
                <h3>📂 Input Lecture Materials</h3>
                <form method="POST" enctype="multipart/form-data">
                    <input type="file" name="slide_images" multiple accept="image/*" onchange="loadSlidesPreview(this)" required style="color:#94a3b8; margin-bottom:10px;">
                    <div class="slideshow-box" id="display-frame"><span style="color:#64748b;">No active slides loaded</span></div>
                    <div class="control-row">
                        <button type="button" class="sub-btn" onclick="shiftSlideIndex(-1)">&larr; Prev</button>
                        <button type="button" class="sub-btn" onclick="shiftSlideIndex(1)">Next &rarr;</button>
                    </div>
                    <textarea name="extra_prompt" placeholder="Optional instructions (e.g., 'Focus heavily on formulas')"></textarea>
                    <button type="submit" class="primary-btn">Analyze & Compress Materials</button>
                </form>
            </div>
            <div class="panel reveal-right">
                <h3>📝 Generated Exam Briefing</h3>
                <div style="background:#0f172a; padding:20px; border-radius:12px; min-height:300px; border-left:5px solid #38bdf8;">
                    <div class="result-text">{{ summary }}</div>
                </div>
            </div>
        </div>
    </div>

    <script>
        document.addEventListener("DOMContentLoaded", function() {
            const animationObserver = new IntersectionObserver((elements) => {
                elements.forEach(el => { if (el.isIntersecting) el.target.classList.add("active"); });
            }, { threshold: 0.1 });
            document.querySelectorAll('.reveal-left, .reveal-right').forEach(row => animationObserver.observe(row));
            if ("{{ has_summary }}" === "True") launchWorkspace();
        });

        var localSlidesCache = []; var activePointer = 0;
        function loadSlidesPreview(uploader) {
            localSlidesCache = []; activePointer = 0;
            if(uploader.files) {
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
            frame.innerHTML = `<img src="${localSlidesCache[activePointer]}"><div class="slide-counter">Slide ${activePointer + 1} of ${localSlidesCache.length}</div>`;
        }
        function shiftSlideIndex(direction) {
            if (localSlidesCache.length === 0) return;
            activePointer = (activePointer + direction + localSlidesCache.length) % localSlidesCache.length;
            refreshViewerDOM();
        }
        function toggleLaunchButton() { document.getElementById("start-btn").disabled = !document.getElementById("consent-check").checked; }
        function launchWorkspace() { document.getElementById("intro-screen").style.display = "none"; document.getElementById("app-screen").style.display = "block"; }
    </script>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    summary = "Your interactive exam briefing will compile here instantly after analyzing the uploaded files."
    has_summary = "False"
    if request.method == "POST":
        slide_files = request.files.getlist("slide_images")
        extra_prompt = request.form.get("extra_prompt", "")
        gemini_payload = []
        for file in slide_files:
            if file and file.filename != '':
                gemini_payload.append({
                    "mime_type": file.content_type,
                    "data": base64.b64encode(file.read()).decode("utf-8")
                })
        if gemini_payload:
            try:
                base_instruction = "Analyze these university lecture slides and extract a comprehensive, crisp exam-prep study briefing highlighting core vocabulary definitions and key details."
                if extra_prompt:
                    base_instruction += f" Additional Note: {extra_prompt}"
                gemini_payload.append(base_instruction)
                response = model.generate_content(gemini_payload)
                summary = response.text
                has_summary = "True"
            except Exception as e:
                summary = f"API Error: {str(e)}"
                has_summary = "True"
    return render_template_string(HTML_LAYOUT, summary=summary, has_summary=has_summary)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
