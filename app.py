from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import base64
import time


app = Flask(__name__)

# --- Initialize persistent ChromeDriver ---
options = webdriver.ChromeOptions()
options.add_argument("--headless")  # optional: run headless
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--window-size=1280,1024")

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=options
)
driver.maximize_window()

# ---------- Screenshot Endpoint ----------
@app.route("/screenshot")
def screenshot():
    png = driver.get_screenshot_as_png()
    b64 = base64.b64encode(png).decode('utf-8')
    return jsonify({"img": f"data:image/png;base64,{b64}"})

# ---------- Input typing ----------
@app.route("/input", methods=["POST"])
def input_text():
    data = request.json
    x, y, text = data["x"], data["y"], data["text"]
    element = driver.execute_script(
        "return document.elementFromPoint(arguments[0], arguments[1]);", x, y
    )
    if element:
        element.clear()
        element.send_keys(text)
        return jsonify({"status":"ok"})
    return jsonify({"status":"error", "message":"No element found at point"})

# ---------- Replay recorded actions ----------
@app.route("/replay", methods=["POST"])
def replay():
    data = request.json
    actions = data.get("actions", [])
    repeat = int(data.get("repeat", 1))
    ignore_idle = bool(data.get("ignore_idle", False))

    for _ in range(repeat):
        for action in actions:
            if action["type"] == "click":
                driver.execute_script(
                    "document.elementFromPoint(arguments[0], arguments[1]).click();",
                    action["x"], action["y"]
                )
            elif action["type"] == "input":
                el = driver.execute_script(
                    "return document.elementFromPoint(arguments[0], arguments[1]);",
                    action["x"], action["y"]
                )
                if el:
                    el.clear()
                    el.send_keys(action["text"])
            elif action["type"] == "wait" and not ignore_idle:
                time.sleep(action.get("seconds", 0))
    return jsonify({"status": f"Executed {repeat} times"})

# ---------- Optional DSL endpoint ----------
@app.route("/dsl", methods=["POST"])
def run_dsl():
    script = request.json.get("script", "")
    outputs = []
    for line in script.strip().splitlines():
        raw = line.strip()
        if not raw: 
            continue
        cmd = raw.lower()
        if cmd.startswith("open website"):
            url = raw.split("open website")[-1].strip().strip('"').strip("'")
            driver.get(url)
            outputs.append(f"Opened {url}")
        elif cmd.startswith("read screen then print"):
            outputs.append(driver.page_source)
        else:
            outputs.append(f"Unknown command: {raw}")
    return jsonify({"output": "\n".join(outputs)})

# ---------- Health check ----------
@app.route("/")
def index():
    return "Selenium backend is running."

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
