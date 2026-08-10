import os
import base64
from flask import Flask, render_template_string, request
import google.generativeai as genai

app = Flask(__name__)

# 🔑 Pull API key securely from Render environment variables
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
        /* Core Reset & Global Styles */
        body { 
            font-family: 'Segoe UI', Arial, sans-serif; 
            margin: 0; padding: 0; background: #0e1118; color: #e3e8f0; 
            min-height: 100vh; display: flex; flex-direction: column; 
            align-items: center; justify-content: flex-start; overflow-x: hidden; 
        }
        
        /* ⚪ Onboarding Introduction Screen Section */
        #intro-screen { 
            background: rgba(255, 255, 255, 0.96); max-width: 550px; width: 90%; 
            padding: 35px 25px; border-radius: 24px; box-shadow: 0 20px 40px rgba(15, 23, 42, 0.3); 
            text-align: center; box-sizing: border-box; margin: 40px auto; color: #0f172a;
        }
        .intro-title { color: #0284c7; font-size: 32px; margin-bottom: 15px; font-weight: 700; }
        .intro-bio { font-size: 14px; color: #475569; line-height: 1.6; margin-bottom: 20px; text-align: left; }
        
        /* ⚡ ANIMATION TARGETS: Default invisible state for hidden scroll rows */
        .reveal-left { opacity: 0; transform: translateX(-100px); transition: all 0.8s cubic-bezier(0.25, 1, 0.5, 1); }
        .reveal-right { opacity: 0; transform: translateX(100px); transition: all 0.8s cubic-bezier(0.25, 1, 0.5, 1); }
        
        /* 🎬 High-Tech Triggered State Classes injected by Intersection Observer */
        .reveal-left.active, .reveal-right.active { opacity: 1; transform: translateX(0); }

        /* Component Boxes */
        .features-box { text-align: left; background: rgba(248, 250, 252, 0.9); border: 1px solid #e2e8f0; padding: 15px 20px; border-radius: 12px; margin-bottom: 20px; }
        .features-title { font-size: 15px; font-weight: 700; color: #0284c7; margin-bottom: 10px; }
        .feature-item { font-size: 13px; color: #334155; margin-bottom: 8px; line-height: 1.5; display: flex; gap: 8px; }
        
        .agreement-card { background: #f1f5f9; padding: 15px; border-radius: 12px; margin-bottom: 25px; display: flex; text-align: left; gap: 12px; border: 1px solid #e2e8f0; }
        .agreement-card input { width: 20px; height: 20px; cursor: pointer; accent-color: #0284c7; }
        
        .primary-btn { width: 100%; padding: 16px; background: #0284c7; color: white; border: none; border-radius: 12px; font-size: 16px; font-weight: bold; cursor: pointer; transition: 0.2s; }
        .primary-btn:hover { background: #0369a1; }
        .primary-btn:disabled { background: #cbd5e1; cursor: not-allowed; }

        /* 🔵 Workspace Splitscreen Layout Panel Dashboard */
        #app-screen { width: 95%; max-width: 1100px; margin: 30px auto; display: none; box-sizing: border-box; }
        .dashboard-container { display: flex; flex-wrap: wrap; gap: 25px; width: 100%; }
        .panel { flex: 1; min-width: 300px; background: #1e293b; padding: 25px; border-radius: 20px; box-shadow: 0 8px 30px rgba(0,0,0,0.3); box-sizing: border-box; }
        
        h2, h3 { color: #38bdf8; margin-top: 0; }
        textarea { width: 100%; height: 120px; padding: 12px; border: 2px solid #334155; border-radius: 12px; font-size: 15px; background: #0f172a; color: white; box-sizing: border-box; resize: none; margin-bottom: 15px; }
        textarea:focus { border-color: #38bdf8; outline: none; }
        
        /* Native Multimodal Slideshow Viewer Box Layout */
        .slideshow-box { width: 100%; height: 250px; background: #0f172a; border: 2px dashed #334155; border-radius: 12px; display: flex; align-items: center; justify-content: center; overflow: hidden; margin: 15px 0; position: relative; }
        .slideshow-box img { max-width: 100%; max-height: 100%; object-fit: contain; }
        .slide-counter { position: absolute; bottom: 10px; right: 10px; background: rgba(0,0,0,0.7); padding: 4px 10px; border-radius: 12px; font-size: 12px; color: #38bdf8; }
        
        .control-row { display: flex; gap: 10px; margin-bottom: 15px; }
        .sub-btn { flex: 1; padding: 10px; background: #334155; border: none; color: white; border-radius: 8px; cursor: pointer; font-weight: bold; }
        .sub-btn:hover { background: #475569; }
        
        .result-text { line-height: 1.6; font-size: 15px; color: #e3e8f0; white-space: pre-wrap; }
    </style>
</head>
<body>

    <!-- ⚪ STAGE 1: DYNAMIC WELCOME CARD (SCROLL ANIMATION DEMO) -->
    <div id="intro-screen">
        <div class="intro-title">⚡ CramPulse Pro</div>
        
        <!-- Row 1: Slides in from the left on view -->
        <div class="intro-bio reveal-left">
            Welcome to your universal academic companion. This engine was engineered by <b>Emmanuel Olorunjuwonlo</b>, a dedicated Computer Science student, leveraging premium frontend scroll transitions to animate dashboards while utilizing multimodal AI core pipelines to ingest raw document slides from any university module.
        </div>
        
        <!-- Row 2: Slides in from the right on view -->
        <div class="features-box reveal-right">
            <div class="features-title">🛠️ Universal Core Capabilities:</div>
            <div class="feature-item"><span>✓</span> Drag & drop multiple lecture screenshots directly into the processing matrix pipeline.</div>
            <div class="feature-item"><span>✓</span> Automated scroll-triggered layouts rendering student parameters with high-tech animations.</div>
        </div>
        
        <!-- Row 3: Slides in from the left on view -->
        <div class="agreement-card reveal-left">
            <input type="checkbox" id="consent-check" onchange="toggleLaunchButton()">
            <label for="consent-check" style="font-size: 13px; color: #334155; font-weight: 500; cursor: pointer;">
                I agree to deploy this auxiliary study framework responsibly alongside my official university course materials.
            </label>
        </div>
        
        <button id="start-btn" class="primary-btn" disabled onclick="launchWorkspace()">Launch Workspace &rarr;</button>
    </div>

    <!-- 🔵 STAGE 2: HIGH-TECH WORKSPACE DASHBOARD -->
    <div id="app-screen">
        <center>
            <h2 style="font-size:32px; margin-bottom:5px;">⚡ CramPulse Workspace</h2>
            <div style="color:#94a3b8; margin-bottom:30px;">Universal Multi-Modal Slide Engine & Exam Prep Analyzer</div>
        </center>
        
        <div class="dashboard-container">
            <!-- Left Grid Panel: Controls and File Presentation Slideshow Component -->
            <div class="panel reveal-left">
                <h3>📂 Input Lecture Materials</h3>
                <form method="POST" enctype="multipart/form-data">
                    <label style="font-size:14px; color:#94a3b8; display:block; margin-bottom:8px;">Upload Slide Screenshots:</label>
                    <input type="file" name="slide_images" multiple accept="image/*" onchange="loadSlidesPreview(this)" required style="color:#94a3b8; margin-bottom:10px;">
                    
                    <div class="slideshow-box" id="display-frame">
                        <span style="color:#64748b;">No active slides loaded into engine memory</span>
                    </div>
                    
                    <div class="control-row">
                        <button type="button" class="sub-btn" onclick="shiftSlideIndex(-1)">&larr; Prev</button>
                        <button type="button" class="sub-btn" onclick="shiftSlideIndex(1)">Next &rarr;</button>
                    </div>
                    
                    <textarea name="extra_prompt" placeholder="Optional extra instructions (e.g., 'Focus heavily on the core formulas and vocabulary definitions')"></textarea>
                    <button type="submit" class="primary-btn">Analyze & Compress Materials</button>
                </form>
            </div>
            
            <!-- Right Grid Panel: Scrolling Real-time AI Output -->
            <div class="panel reveal-right">
                <h3>📝 Generated Exam Briefing</h3>
                <div style="background:#0f172a; padding:20px; border-radius:12px; min-height:350px; border-left:5px solid #38bdf8;">
                    <div class="result-text">{{ summary }}</div>
                </div>
            </div>
        </div>
    </div>

    <script>
        // 🏁 INTERSECTION OBSERVER: Triggers clean slide-in layout as elements scroll onto screen
        document.addEventListener("DOMContentLoaded", function() {
            const animationObserver = new IntersectionObserver((elements) => {
                elements.forEach(element => {
                    if (element.isIntersecting) {
                        element.target.classList.add("active");
                    }
                });
            }, { threshold: 0.15 });

            document.querySelectorAll('.reveal-left, .reveal-right').forEach(row => {
                animationObserver.observe(row);
            });

            var hasSummary = "{{ has_summary }}";
            if (hasSummary === "True") {
                launchWorkspace();
            }
        });

        // 🖼️ NATIVE SLIDESHOW VIEWER LOGIC
        var localSlidesCache = [];
        var activePointer = 0;

        function loadSlidesPreview(uploader) {
            localSlidesCache = [];
            activePointer = 0;
            if(uploader.files) {
                Array.from(uploader.files).forEach(file => {
                    const reader = new FileReader();
