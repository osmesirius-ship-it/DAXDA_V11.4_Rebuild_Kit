"""DAXDA V11.4 Web Server, REST API & Deterministic 3D Cinematic Renderer for Hostinger.

Compatible with Hostinger hPanel "Setup Python App" (Phusion Passenger / WSGI / Flask).
Provides:
  - Three.js WebGL 3D Geometric Double-Helix & Rotor Transformation Chamber Visualizer
  - 7-Stage Cinematic Sequence Controller ("Language Entering the Machine")
  - Holographic 3D Space-Crawl Delivery Receipt Renderer
  - REST API (/api/evaluate, /api/trace, /api/preflight, /api/health)
  - Unified JSON Trace Exporter for Video Generation Pipelines (Grok, Veo, Runway, Remotion)
"""
from __future__ import annotations
import os
import sys
import json
import time
import hashlib
from typing import Dict, Any

# Add current directory and parent rebuild kit to path for engine imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "DAXDA_V11.4_Rebuild_Kit"))

from daxda_engine_aglm_opt import DAXDAEngineAGLMOpt
from daxda_engine_v11_4 import DAXDAEngineV11_4

try:
    from daxda_engine_v11_4_2_candidate import DAXDAEngineV11_4_2_Candidate
    v11_4_2_engine = DAXDAEngineV11_4_2_Candidate()
except ImportError:
    v11_4_2_engine = None

aglm_engine = DAXDAEngineAGLMOpt()
v11_engine = DAXDAEngineV11_4()

try:
    from flask import Flask, request, jsonify, render_template_string
    USE_FLASK = True
except ImportError:
    USE_FLASK = False

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DAXDA V11.4 Engine | Deterministic 3D Geometric Gateway</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
    <style>
        :root {
            --bg-dark: #070a12;
            --bg-card: rgba(15, 23, 42, 0.75);
            --bg-card-border: rgba(255, 255, 255, 0.08);
            --accent-cyan: #00f2fe;
            --accent-purple: #7f00ff;
            --accent-green: #00e676;
            --accent-amber: #ffab00;
            --accent-red: #ff1744;
            --text-main: #f0f4f8;
            --text-muted: #8a99ad;
            --font-main: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            --font-mono: 'JetBrains Mono', monospace;
        }

        * { box-sizing: border-box; margin: 0; padding: 0; }

        body {
            background-color: var(--bg-dark);
            background-image: 
                radial-gradient(circle at 15% 15%, rgba(0, 242, 254, 0.06) 0%, transparent 40%),
                radial-gradient(circle at 85% 85%, rgba(127, 0, 255, 0.06) 0%, transparent 40%);
            color: var(--text-main);
            font-family: var(--font-main);
            min-height: 100vh;
            padding: 1.5rem;
        }

        .container { max-width: 1360px; margin: 0 auto; }

        header {
            display: flex; justify-content: space-between; align-items: center;
            padding-bottom: 1.25rem; margin-bottom: 1.5rem;
            border-bottom: 1px solid var(--bg-card-border);
        }

        .logo-group { display: flex; align-items: center; gap: 0.75rem; }

        .logo-badge {
            width: 44px; height: 44px;
            background: linear-gradient(135deg, var(--accent-cyan), var(--accent-purple));
            border-radius: 12px; display: flex; align-items: center; justify-content: center;
            font-weight: 800; font-size: 1.25rem; color: #fff;
            box-shadow: 0 0 24px rgba(0, 242, 254, 0.35);
        }

        .title-group h1 {
            font-size: 1.4rem; font-weight: 800; letter-spacing: -0.02em;
            background: linear-gradient(90deg, #ffffff, var(--accent-cyan));
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        }

        .title-group p { font-size: 0.8rem; color: var(--text-muted); }

        .status-pill {
            display: inline-flex; align-items: center; gap: 0.5rem;
            background: rgba(0, 230, 118, 0.1); border: 1px solid rgba(0, 230, 118, 0.3);
            color: var(--accent-green); padding: 0.35rem 0.85rem; border-radius: 20px;
            font-size: 0.8rem; font-weight: 600;
        }

        .status-dot {
            width: 8px; height: 8px; border-radius: 50%;
            background-color: var(--accent-green); box-shadow: 0 0 8px var(--accent-green);
        }

        .grid { display: grid; grid-template-columns: 380px 1fr; gap: 1.5rem; }
        @media (max-width: 1024px) { .grid { grid-template-columns: 1fr; } }

        .card {
            background: var(--bg-card); backdrop-filter: blur(16px);
            border: 1px solid var(--bg-card-border); border-radius: 16px;
            padding: 1.25rem; box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
        }

        .card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; }
        .card-title { font-size: 1rem; font-weight: 600; color: var(--text-main); }

        .form-group { margin-bottom: 1rem; }
        label { display: block; font-size: 0.8rem; font-weight: 500; color: var(--text-muted); margin-bottom: 0.4rem; }

        textarea, select {
            width: 100%; background: rgba(9, 13, 22, 0.85);
            border: 1px solid var(--bg-card-border); border-radius: 10px;
            padding: 0.75rem 0.9rem; color: var(--text-main); font-family: var(--font-main);
            font-size: 0.9rem; transition: all 0.2s ease;
        }

        textarea:focus, select:focus { outline: none; border-color: var(--accent-cyan); box-shadow: 0 0 12px rgba(0, 242, 254, 0.25); }
        textarea { min-height: 100px; resize: vertical; }

        .btn-group { display: flex; gap: 0.75rem; flex-wrap: wrap; }

        button {
            background: linear-gradient(135deg, var(--accent-cyan), #00a8ff);
            color: #000; font-weight: 700; border: none; border-radius: 10px;
            padding: 0.75rem 1.25rem; cursor: pointer; font-size: 0.85rem;
            transition: all 0.2s ease; box-shadow: 0 4px 15px rgba(0, 242, 254, 0.25);
        }

        button:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(0, 242, 254, 0.4); }
        button.btn-secondary { background: rgba(255, 255, 255, 0.05); color: var(--text-main); border: 1px solid var(--bg-card-border); box-shadow: none; }
        button.btn-secondary:hover { background: rgba(255, 255, 255, 0.1); }

        /* 3D Visualizer Canvas Section */
        .visualizer-container {
            position: relative; width: 100%; height: 460px;
            background: radial-gradient(circle at center, #0d1424 0%, #050811 100%);
            border-radius: 14px; overflow: hidden; border: 1px solid var(--bg-card-border);
        }

        #canvas3d { width: 100%; height: 100%; display: block; }

        .canvas-overlay {
            position: absolute; top: 1rem; left: 1rem; pointer-events: none;
            display: flex; flex-direction: column; gap: 0.25rem;
        }

        .canvas-badge {
            background: rgba(9, 13, 22, 0.75); backdrop-filter: blur(8px);
            border: 1px solid var(--bg-card-border); padding: 0.35rem 0.75rem;
            border-radius: 8px; font-family: var(--font-mono); font-size: 0.75rem; color: var(--accent-cyan);
        }

        .stage-controller {
            position: absolute; bottom: 1rem; left: 1rem; right: 1rem;
            background: rgba(9, 13, 22, 0.8); backdrop-filter: blur(12px);
            border: 1px solid var(--bg-card-border); border-radius: 10px;
            padding: 0.6rem 1rem; display: flex; justify-content: space-between; align-items: center;
        }

        .stage-title { font-size: 0.8rem; font-weight: 600; color: var(--text-main); font-family: var(--font-mono); }

        .badge-disposition {
            padding: 0.35rem 0.85rem; border-radius: 8px; font-weight: 700;
            font-size: 0.85rem; letter-spacing: 0.05em; text-transform: uppercase;
        }

        .disposition-RELEASE { background: rgba(0, 230, 118, 0.15); color: var(--accent-green); border: 1px solid rgba(0, 230, 118, 0.4); }
        .disposition-WARN { background: rgba(255, 171, 0, 0.15); color: var(--accent-amber); border: 1px solid rgba(255, 171, 0, 0.4); }
        .disposition-BLOCK { background: rgba(255, 23, 68, 0.15); color: var(--accent-red); border: 1px solid rgba(255, 23, 68, 0.4); }

        pre {
            background: rgba(5, 8, 17, 0.95); border: 1px solid var(--bg-card-border);
            border-radius: 10px; padding: 1rem; font-family: var(--font-mono);
            font-size: 0.8rem; color: var(--accent-cyan); overflow-x: auto; max-height: 220px;
        }

        footer {
            margin-top: 2rem; text-align: center; font-size: 0.8rem; color: var(--text-muted);
            border-top: 1px solid var(--bg-card-border); padding-top: 1.25rem;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div class="logo-group">
                <div class="logo-badge">Cl</div>
                <div class="title-group">
                    <h1>DAXDA Deterministic 3D Gateway</h1>
                    <p>Clifford Algebra Cl(4,1) / Cl(7,0) Cinematic Rendering Compiler</p>
                </div>
            </div>
            <div class="status-pill">
                <div class="status-dot"></div>
                <span>Hostinger Production Node</span>
            </div>
        </header>

        <div class="grid">
            <!-- Left Controls Panel -->
            <div class="card">
                <div class="card-header">
                    <div class="card-title">Execution Controls</div>
                </div>

                <div class="form-group">
                    <label for="engineSelect">Select Reasoner Protocol</label>
                    <select id="engineSelect">
                        <option value="AGLM-OPT">AGLM-OPT (Frozen Baseline V11.4 Engine)</option>
                        <option value="V11.4.2-CANDIDATE">V11.4.2-CANDIDATE (Typed Dependency Engine)</option>
                        <option value="V11.4">V11.4 Standard Engine</option>
                    </select>
                </div>

                <div class="form-group">
                    <label for="inputText">Input Query / Prompt Text</label>
                    <textarea id="inputText" placeholder="Enter query text to evaluate through Clifford geometric transport...">Do not allow unauthorized access.</textarea>
                </div>

                <div class="btn-group">
                    <button id="evalBtn" onclick="evaluatePrompt()">Run Geometric Compiler</button>
                    <button class="btn-secondary" onclick="replayCinematic()">Replay 3D Sequence</button>
                    <button class="btn-secondary" onclick="exportJSONTrace()">Export JSON Trace</button>
                </div>

                <div style="margin-top: 1.25rem;">
                    <div class="card-title" style="font-size: 0.85rem; margin-bottom: 0.5rem;">Blade Color Legend</div>
                    <div style="font-size: 0.75rem; display: grid; grid-template-columns: 1fr 1fr; gap: 0.4rem; color: var(--text-muted); font-family: var(--font-mono);">
                        <div><span style="color: #00f2fe;">●</span> e1: Safety/Trust</div>
                        <div><span style="color: #ffffff;">●</span> e2: Factual</div>
                        <div><span style="color: #7f00ff;">●</span> e3: Negation</div>
                        <div><span style="color: #ffab00;">●</span> e4: Condition</div>
                        <div><span style="color: #ff1744;">●</span> e15: Adversarial</div>
                        <div><span style="color: #8a99ad;">●</span> UNKNOWN: Phase</div>
                    </div>
                </div>
            </div>

            <!-- Right 3D Visualizer Panel -->
            <div class="card">
                <div class="card-header">
                    <div class="card-title">3D Clifford Double-Helix & Transformation Chamber</div>
                    <div id="dispBadge" class="badge-disposition disposition-RELEASE">READY</div>
                </div>

                <div class="visualizer-container">
                    <canvas id="canvas3d"></canvas>
                    
                    <div class="canvas-overlay">
                        <div id="overlayEngine" class="canvas-badge">ENGINE: AGLM-OPT</div>
                        <div id="overlayAlgebra" class="canvas-badge">ALGEBRA: Cl(4,1) (32 Blades)</div>
                        <div id="overlayHash" class="canvas-badge">HASH: e824...e2faf</div>
                    </div>

                    <div class="stage-controller">
                        <div id="stageText" class="stage-title">STAGE: IDLE (Awaiting Input)</div>
                        <div id="coherenceLabel" style="font-family: var(--font-mono); font-size: 0.8rem; color: var(--accent-cyan);">S(M): 1.000</div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Lower Section: Cryptographic Receipt JSON -->
        <div class="card" style="margin-top: 1.5rem;">
            <div class="card-header">
                <div class="card-title">Cryptographic Execution & Video Trace Receipt (SHA256 Signed)</div>
            </div>
            <pre id="jsonReceipt">// Visual trace JSON output will be rendered here...</pre>
        </div>

        <footer>
            <p>DAXDA V11.4 Deterministic Cinematic Compiler &bull; Hostinger Web Node &bull; Cl(4,1) / Cl(7,0) Geometric Algebra</p>
        </footer>
    </div>

    <script>
        let scene, camera, renderer, controls;
        let helixGroup, bladeSpheres = [], particleSystem, gatePlane;
        let lastResult = null;

        function init3D() {
            const container = document.querySelector('.visualizer-container');
            const canvas = document.getElementById('canvas3d');

            scene = new THREE.Scene();
            scene.fog = new THREE.FogExp2(0x050811, 0.03);

            camera = new THREE.PerspectiveCamera(45, container.clientWidth / container.clientHeight, 0.1, 1000);
            camera.position.set(0, 0, 18);

            renderer = new THREE.WebGLRenderer({ canvas: canvas, antialias: true, alpha: true });
            renderer.setSize(container.clientWidth, container.clientHeight);
            renderer.setPixelRatio(window.devicePixelRatio);

            controls = new THREE.OrbitControls(camera, renderer.domElement);
            controls.enableDamping = true;
            controls.dampingFactor = 0.05;

            // Ambient & Point Lights
            const ambLight = new THREE.AmbientLight(0xffffff, 0.6);
            scene.add(ambLight);

            const pointLight = new THREE.PointLight(0x00f2fe, 1.5, 50);
            pointLight.position.set(5, 10, 10);
            scene.add(pointLight);

            // Create Group for Clifford Double Helix
            helixGroup = new THREE.Group();
            scene.add(helixGroup);

            // Construct 3D Double Helix Geometry
            const bladeColors = [0x00f2fe, 0xffffff, 0x7f00ff, 0xffab00, 0xff1744];
            for (let i = 0; i < 24; i++) {
                const t = (i / 24) * Math.PI * 4;
                const radius = 3.5;
                
                // Strand A
                const x1 = Math.cos(t) * radius;
                const y1 = (i - 12) * 0.4;
                const z1 = Math.sin(t) * radius;
                
                const geom1 = new THREE.SphereGeometry(0.25, 16, 16);
                const mat1 = new THREE.MeshPhongMaterial({ color: bladeColors[i % 5], emissive: bladeColors[i % 5], emissiveIntensity: 0.5 });
                const sphere1 = new THREE.Mesh(geom1, mat1);
                sphere1.position.set(x1, y1, z1);
                helixGroup.add(sphere1);
                bladeSpheres.push(sphere1);

                // Strand B
                const x2 = Math.cos(t + Math.PI) * radius;
                const y2 = (i - 12) * 0.4;
                const z2 = Math.sin(t + Math.PI) * radius;

                const geom2 = new THREE.SphereGeometry(0.2, 16, 16);
                const mat2 = new THREE.MeshPhongMaterial({ color: 0x7f00ff, emissive: 0x7f00ff, emissiveIntensity: 0.4 });
                const sphere2 = new THREE.Mesh(geom2, mat2);
                sphere2.position.set(x2, y2, z2);
                helixGroup.add(sphere2);
            }

            // Gate Intersect Ring Plane
            const ringGeom = new THREE.RingGeometry(4, 4.3, 32);
            const ringMat = new THREE.MeshBasicMaterial({ color: 0x00f2fe, side: THREE.DoubleSide, transparent: true, opacity: 0.3 });
            gatePlane = new THREE.Mesh(ringGeom, ringMat);
            gatePlane.rotation.x = Math.PI / 2;
            scene.add(gatePlane);

            window.addEventListener('resize', onWindowResize);
            animate();
        }

        function animate() {
            requestAnimationFrame(animate);
            if (helixGroup) {
                helixGroup.rotation.y += 0.008;
            }
            controls.update();
            renderer.render(scene, camera);
        }

        function onWindowResize() {
            const container = document.querySelector('.visualizer-container');
            camera.aspect = container.clientWidth / container.clientHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(container.clientWidth, container.clientHeight);
        }

        async function evaluatePrompt() {
            const text = document.getElementById('inputText').value;
            const engine = document.getElementById('engineSelect').value;

            if (!text.trim()) { alert('Please enter text.'); return; }

            document.getElementById('stageText').innerText = 'STAGE 1: THE UTTERANCE';
            
            try {
                const res = await fetch('/api/evaluate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ input_text: text, engine: engine })
                });
                const data = await res.json();
                lastResult = data;
                renderVisualTrace(data);
            } catch (err) {
                alert('Evaluation error: ' + err.message);
            }
        }

        function renderVisualTrace(data) {
            // Update Overlay Info
            document.getElementById('overlayEngine').innerText = 'ENGINE: ' + (data.version || 'V11.4');
            document.getElementById('overlayAlgebra').innerText = 'ALGEBRA: ' + (data.algebra_signature || 'Cl(4,1) 32 Blades');
            document.getElementById('overlayHash').innerText = 'HASH: ' + (data.receipt_sha256 ? data.receipt_sha256.slice(0, 12) + '...' : 'N/A');

            // Update Disposition Badge
            const badge = document.getElementById('dispBadge');
            badge.innerText = data.disposition || 'RELEASE';
            badge.className = 'badge-disposition disposition-' + (data.disposition || 'RELEASE');

            document.getElementById('coherenceLabel').innerText = 'S(M): ' + (data.feedback ? data.feedback.final_coherence.toFixed(4) : '1.000');

            // Animate Gate Plane Color based on Disposition
            if (data.disposition === 'RELEASE') {
                gatePlane.material.color.setHex(0x00f2fe);
            } else if (data.disposition === 'BLOCK') {
                gatePlane.material.color.setHex(0xff1744);
            } else {
                gatePlane.material.color.setHex(0xffab00);
            }

            // Cinematic Stage Progression Sequence
            const stages = [
                'STAGE 1: THE UTTERANCE',
                'STAGE 2: SEMANTIC DISASSEMBLY',
                'STAGE 3: GEOMETRIC INCARNATION',
                'STAGE 4: DOUBLE HELIX ORBIT',
                'STAGE 5: ROTOR TRANSPORT CHAMBER',
                'STAGE 6: GATE INTERSECT (' + (data.disposition || 'RELEASE') + ')',
                'STAGE 7: HOLOGRAPHIC DELIVERY RECEIPT'
            ];

            let step = 0;
            const interval = setInterval(() => {
                if (step < stages.length) {
                    document.getElementById('stageText').innerText = stages[step];
                    helixGroup.rotation.y += 0.2;
                    step++;
                } else {
                    clearInterval(interval);
                }
            }, 600);

            // Render Trace JSON Receipt
            document.getElementById('jsonReceipt').innerText = JSON.stringify(data, null, 2);
        }

        function replayCinematic() {
            if (lastResult) renderVisualTrace(lastResult);
        }

        function exportJSONTrace() {
            if (!lastResult) { alert('Run evaluation first.'); return; }
            const blob = new Blob([JSON.stringify(lastResult, null, 2)], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url; a.download = 'daxda_visual_trace_' + Date.now() + '.json';
            a.click();
        }

        window.onload = init3D;
    </script>
</body>
</html>
"""

if USE_FLASK:
    app = Flask(__name__)

    @app.route('/')
    def index():
        return render_template_string(HTML_TEMPLATE)

    @app.route('/api/evaluate', methods=['POST'])
    def api_evaluate():
        data = request.get_json(force=True) or {}
        text = data.get('input_text', '')
        engine_type = data.get('engine', 'AGLM-OPT')
        case_id = data.get('case_id', f'REQ-{int(time.time())}')

        record = {"case_id": case_id, "input_text": text}
        if engine_type == 'V11.4.2-CANDIDATE' and v11_4_2_engine is not None:
            result = v11_4_2_engine.evaluate(record)
        elif engine_type == 'V11.4':
            result = v11_engine.evaluate(record)
        else:
            result = aglm_engine.evaluate(record)

        return jsonify(result)

    @app.route('/api/trace', methods=['POST'])
    def api_trace():
        data = request.get_json(force=True) or {}
        text = data.get('input_text', '')
        res = aglm_engine.evaluate({"case_id": "TRACE", "input_text": text})
        
        # Standardized Visual Trace JSON object for external renderers (Grok, Veo, Runway, Remotion)
        trace_json = {
            "input": text,
            "engine": res.get("version", "AGLM-1.0.0"),
            "algebra": "Cl(4,1)",
            "blades": res.get("semantic_profile", {}),
            "coherence": res.get("feedback", {}).get("final_coherence", 1.0),
            "disposition": res.get("disposition", "RELEASE"),
            "trace_hash": res.get("receipt_sha256", ""),
            "timestamp_utc": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
        }
        return jsonify(trace_json)

    @app.route('/api/preflight', methods=['GET'])
    def api_preflight():
        preflight_file = os.path.join(os.path.dirname(__file__), 'preflight_outputs.jsonl')
        cases = []
        if os.path.exists(preflight_file):
            with open(preflight_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        cases.append(json.loads(line.strip()))

        results = [aglm_engine.evaluate(c) for c in cases]
        return jsonify({
            "status": "COMPLETED",
            "count": len(results),
            "protocol": "DAXDA-AGLM-OPT",
            "results": results
        })

    @app.route('/api/health', methods=['GET'])
    def api_health():
        return jsonify({
            "status": "HEALTHY",
            "engine": "DAXDA V11.4 Deterministic Cinematic Compiler",
            "protocol": "AGLM-1.0.0",
            "timestamp": time.time()
        })

else:
    def application(environ, start_response):
        path = environ.get('PATH_INFO', '/')
        method = environ.get('REQUEST_METHOD', 'GET')

        if path == '/' and method == 'GET':
            start_response('200 OK', [('Content-Type', 'text/html; charset=utf-8')])
            return [HTML_TEMPLATE.encode('utf-8')]

        elif path == '/api/health' and method == 'GET':
            body = json.dumps({"status": "HEALTHY", "engine": "DAXDA V11.4 Cinematic Compiler"}).encode('utf-8')
            start_response('200 OK', [('Content-Type', 'application/json'), ('Content-Length', str(len(body)))])
            return [body]

        elif path == '/api/evaluate' and method == 'POST':
            try:
                length = int(environ.get('CONTENT_LENGTH', '0'))
                body_bytes = environ['wsgi.input'].read(length)
                data = json.loads(body_bytes.decode('utf-8'))
                record = {"case_id": data.get('case_id', 'REQ'), "input_text": data.get('input_text', '')}
                res = aglm_engine.evaluate(record)
                resp_bytes = json.dumps(res).encode('utf-8')
                start_response('200 OK', [('Content-Type', 'application/json'), ('Content-Length', str(len(resp_bytes)))])
                return [resp_bytes]
            except Exception as e:
                resp_bytes = json.dumps({"error": str(e)}).encode('utf-8')
                start_response('400 Bad Request', [('Content-Type', 'application/json')])
                return [resp_bytes]

        start_response('404 Not Found', [('Content-Type', 'text/plain')])
        return [b'404 Not Found']

if __name__ == '__main__':
    if USE_FLASK:
        port = int(os.environ.get('PORT', 5000))
        print(f"Starting DAXDA 3D Gateway Web Server on port {port}...")
        app.run(host='0.0.0.0', port=port, debug=True)
    else:
        from wsgiref.simple_server import make_server
        print("Starting WSGI fallback server on port 5000...")
        httpd = make_server('0.0.0.0', 5000, application)
        httpd.serve_forever()
