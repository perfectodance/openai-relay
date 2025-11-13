from flask import Flask, request, jsonify
import os, subprocess, requests

app = Flask(__name__)

OPENAI_URL = "https://api.openai.com/v1/chat/completions"
RELAY_SECRET = os.getenv("DISTAFF_RELAY_SECRET", "distaff123secret")
EXEC_KEY = os.getenv("DISTAFF_EXEC_KEY", "distaff_exec_456")


@app.route("/", methods=["GET"])
def home():
    return "Relay online with exec endpoint"


@app.route("/v1/chat/completions", methods=["POST"])
def relay():
    if request.headers.get("Authorization") != f"Bearer {RELAY_SECRET}":
        return jsonify({"error": "unauthorized"}), 401

    try:
        r = requests.post(
            OPENAI_URL,
            json=request.json,
            headers={
                "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY', '')}",
                "Content-Type": "application/json",
            },
            timeout=120,
        )
        return (r.text, r.status_code, r.headers.items())
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/relay/exec", methods=["POST"])
def exec_cmd():
    if request.headers.get("X-Exec-Key") != EXEC_KEY:
        return jsonify({"error": "unauthorized"}), 401

    data = request.json or {}
    cmd = data.get("cmd")
    if not cmd:
        return jsonify({"error": "no cmd"}), 400

    try:
        out = subprocess.check_output(
            cmd, shell=True, stderr=subprocess.STDOUT, timeout=60, text=True
        )
        return jsonify({"ok": True, "output": out})
    except subprocess.CalledProcessError as e:
        return jsonify({"ok": False, "output": e.output, "code": e.returncode})
    except Exception as e:
        return jsonify({"ok": False, "output": str(e)})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
