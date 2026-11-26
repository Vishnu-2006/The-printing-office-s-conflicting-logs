from flask import Blueprint, jsonify, render_template, request
from .merger import merge_departments, InputError
from .db import save_result, get_history

bp = Blueprint("main", __name__)

@bp.get("/")
def index():
    return render_template("index.html")

@bp.get("/api/health")
def health():
    return jsonify({"status": "ok", "service": "Printing Office Consolidator"})

@bp.post("/api/merge")
def merge():
    payload = request.get_json(silent=True)
    try:
        result = merge_departments(payload)
        result["history_id"] = save_result(result)
        return jsonify(result)
    except InputError as exc:
        return jsonify({"error": str(exc)}), 400
    except Exception:
        return jsonify({"error": "Unexpected server error while merging queues."}), 500

@bp.get("/api/history")
def history():
    return jsonify({"history": get_history()})
