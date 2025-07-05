from flask import Flask, request, jsonify
from pymongo import MongoClient
from flask_cors import CORS
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
CORS(app)

client = MongoClient(os.getenv("MONGO_URI"))
db = client.github_webhooks
collection = db.events

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    event_type = request.headers.get('X-GitHub-Event')
    timestamp = datetime.utcnow()
    author = data['sender']['login']

    event = {
        "type": event_type,
        "author": author,
        "timestamp": timestamp.isoformat()
    }

    if event_type == "push":
        event["to_branch"] = data['ref'].split('/')[-1]

    elif event_type == "pull_request":
        event["from_branch"] = data['pull_request']['head']['ref']
        event["to_branch"] = data['pull_request']['base']['ref']

    elif event_type == "merge":
        event["from_branch"] = data['pull_request']['head']['ref']
        event["to_branch"] = data['pull_request']['base']['ref']

    collection.insert_one(event)
    return jsonify({"message": "Received"}), 200

@app.route('/events', methods=['GET'])
def get_events():
    data = list(collection.find({}, {"_id": 0}))
    return jsonify(data)

if __name__ == "__main__":
    app.run(port=5000)
