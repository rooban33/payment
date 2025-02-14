import os
import razorpay
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os

print("RAZORPAY_KEY_ID:", os.getenv("RAZORPAY_KEY_ID"))
print("RAZORPAY_KEY_SECRET:", os.getenv("RAZORPAY_KEY_SECRET"))


# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Initialize Razorpay Client
razorpay_client = razorpay.Client(auth=(os.getenv("RAZORPAY_KEY_ID"), os.getenv("RAZORPAY_KEY_SECRET")))

@app.route('/create-order', methods=['POST'])
def create_order():
    try:
        data = request.json
        amount = data.get("amount", 1)  # Default to 500 INR
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
