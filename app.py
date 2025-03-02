import os
import razorpay
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from dotenv import load_dotenv
import os

print("RAZORPAY_KEY_ID:", os.getenv("RAZORPAY_KEY_ID"))
print("RAZORPAY_KEY_SECRET:", os.getenv("RAZORPAY_KEY_SECRET"))


# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Google Sheet ID
SHEET_ID = "1MttQVsu1pbc1G4s-Qo8zrfTdF4-UCmsnchXeVv-bs2U"
students=[]
colleges=[]

def fetch_public_sheet(sheet_name):
    """Fetch data from a public Google Sheet."""
    try:
        url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:json&sheet={sheet_name}"
        response = requests.get(url)
        raw_data = response.text

        # Extract JSON part from response (Google wraps it in additional text)
        json_data = raw_data[raw_data.index("{"):-2]

        import json
        parsed_data = json.loads(json_data)

        # Extract table values
        rows = parsed_data["table"]["rows"]
        headers = [col["label"] for col in parsed_data["table"]["cols"]]

        # Convert rows to JSON objects
        records = [
            {headers[i]: (cell["v"] if "v" in cell else "") for i, cell in enumerate(row["c"])}
            for row in rows
        ]
        # Sort by "Points" column in descending order (convert to int for sorting)
        records.sort(key=lambda x: int(x.get("points", 0)), reverse=True)

        return records

    except Exception as e:
        return {"error": str(e)}

@app.route('/leaderboard', methods=['GET'])
def get_leaderboard():
    """Fetch and return leaderboard data."""
    students = fetch_public_sheet("Sheet1")  # Student Data
    colleges = fetch_public_sheet("Sheet2")  # College Data
    print("student:",students)
    print("colleges:",colleges)

    return jsonify({"students": students, "colleges": colleges})

# Initialize Razorpay Client
razorpay_client = razorpay.Client(auth=(os.getenv("RAZORPAY_KEY_ID"), os.getenv("RAZORPAY_KEY_SECRET")))

@app.route('/create-order', methods=['POST'])
def create_order():
    try:
        data = request.json
        amount = data.get("amount", 1) 
        currency = data.get("currency", "INR")

        # Create order
        order = razorpay_client.order.create({
            "amount": amount * 100,  # Razorpay expects amount in paise
            "currency": currency,
            "payment_capture": 1  # Auto capture payment
        })

        return jsonify(order)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv("PORT", 5000)), debug=True)
