from flask import Flask, request, jsonify
import uuid
import datetime
from utils.file_manager import load_json, save_json
from utils.s3_handler import upload_to_s3

app = Flask(__name__)
DATA_FILE = 'storage/requests.json'

@app.route('/request', methods=['POST'])
def create_request():
    data = request.form.to_dict()
    file = request.files.get('document')
    file_url = upload_to_s3(file, f"{uuid.uuid4()}_{file.filename}") if file else None

    request_data = {
        "id": str(uuid.uuid4()),
        "student_name": data.get("student_name"),
        "type": data.get("type"),
        "details": data.get("details"),
        "status": "open",
        "created_at": str(datetime.datetime.now()),
        "file_url": file_url
    }

    requests = load_json(DATA_FILE)
    requests.append(request_data)
    save_json(DATA_FILE, requests)
    return jsonify(request_data), 201

@app.route('/requests', methods=['GET'])
def get_requests():
    return jsonify(load_json(DATA_FILE)), 200

@app.route('/request/<req_id>', methods=['PATCH'])
def update_request(req_id):
    data = request.json
    requests = load_json(DATA_FILE)
    for req in requests:
        if req['id'] == req_id:
            req['status'] = data.get('status', req['status'])
            if data.get("note"):
                req['note'] = data["note"]
            break
    else:
        return jsonify({"error": "Request not found"}), 404

    save_json(DATA_FILE, requests)
    return jsonify(req), 200

@app.route('/dashboard', methods=['GET'])
def dashboard():
    requests = load_json(DATA_FILE)
    summary = {
        "open": sum(1 for r in requests if r["status"] == "open"),
        "in_progress": sum(1 for r in requests if r["status"] == "in_progress"),
        "closed": sum(1 for r in requests if r["status"] == "closed"),
        "total": len(requests)
    }
    return jsonify(summary), 200

@app.route('/report', methods=['GET'])
def report():
    start = request.args.get('start')
    end = request.args.get('end')
    detailed = request.args.get('detailed', 'false').lower() == 'true'

    requests = load_json(DATA_FILE)
    filtered = [
        r for r in requests
        if start <= r["created_at"][:10] <= end
    ]

    if not detailed:
        summary = {}
        for r in filtered:
            summary[r['status']] = summary.get(r['status'], 0) + 1
        return jsonify(summary)
    else:
        return jsonify(filtered)

if __name__ == '__main__':
    app.run(debug=True)
