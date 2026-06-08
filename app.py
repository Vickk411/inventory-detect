from flask import Flask, request, jsonify, render_template
from supabase import create_client
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
def calculate_stock(distance):

    # Full
    if distance <= 4:
        percentage = 100
        status = "FULL"

    # Medium zone (4cm to 6cm)
    elif 4 < distance < 6:

        percentage = ((6 - distance) / (6 - 4)) * 100

        if percentage >= 70:
            status = "FULL"
        elif percentage >= 30:
            status = "MEDIUM"
        else:
            status = "LOW"

    # Empty
    else:
        percentage = 0
        status = "EMPTY"

    return round(percentage, 2), status

@app.route('/coffee', methods=['POST'])
def coffee():

    data = request.json

    distance = float(data['distance'])

    percentage, status = calculate_stock(distance)

    supabase.table("coffee_stock").insert({
        "distance": distance,
        "percentage": percentage,
        "status": status
    }).execute()

    return jsonify({
        "distance": distance,
        "percentage": percentage,
        "status": status
    })


@app.route('/')
def dashboard():

    result = (
        supabase
        .table("coffee_stock")
        .select("*")
        .order("created_at", desc=True)
        .limit(1)
        .execute()
    )

    if not result.data:
        return "No Data Available"

    coffee = result.data[0]

    return render_template(
        "dashboard.html",
        distance=coffee["distance"],
        percentage=coffee["percentage"],
        status=coffee["status"],
        created_at=coffee["created_at"]
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)