from flask import Flask, render_template, request, redirect, url_for, jsonify
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
from decimal import Decimal
import os

app = Flask(__name__)

# Path to CSV file and image folder
CSV_FILE = "../../Library/CloudStorage/OneDrive-VytautoDidžiojouniversitetas/lsmu/waso-PV/renovation_expenses.csv"
CHART_FOLDER = "static/charts"
os.makedirs(CHART_FOLDER, exist_ok=True)


# Load the CSV data into a pandas DataFrame
def load_data():
    return pd.read_csv(CSV_FILE) if os.path.exists(CSV_FILE) else pd.DataFrame(
        columns=["Date", "Item/Service", "Category (Shop)", "Cost", "Notes"])


# Save the DataFrame to CSV
def save_data(df):
    df.to_csv(CSV_FILE, index=False)


# Route for the main page
@app.route("/")
def index():
    df = load_data()
    return render_template("index.html", data=df.to_dict(orient="records"))


# Route for adding a new expense
@app.route("/add", methods=["POST"])
def add_expense():
    date = request.form["Date"]
    item = request.form["Item/Service"]
    category = request.form["Category (Shop)"]
    cost = Decimal(request.form["Cost"])
    notes = request.form["Notes"]

    df = load_data()
    new_row = {"Date": date, "Item/Service": item, "Category (Shop)": category, "Cost": cost, "Notes": notes}
    df = df.append(new_row, ignore_index=True)
    save_data(df)

    return redirect(url_for("index"))


# Route for removing an expense
@app.route("/remove", methods=["POST"])
def remove_expense():
    index = int(request.form["index"])
    df = load_data()
    df = df.drop(index)
    save_data(df)

    return redirect(url_for("index"))


# Route for generating the bar chart
@app.route("/bar_chart")
def bar_chart():
    df = load_data()
    grouped = df.groupby("Category (Shop)")["Cost"].sum()

    # Create bar chart
    plt.figure(figsize=(10, 6))
    grouped.plot(kind="bar", color="skyblue", edgecolor="black")
    plt.title("Total Costs by Category (Shop)", fontsize=14)
    plt.xlabel("Category (Shop)", fontsize=12)
    plt.ylabel("Total Cost", fontsize=12)
    plt.xticks(rotation=45)
    plt.grid(axis="y", linestyle="--", alpha=0.7)

    # Save the chart
    chart_path = os.path.join(CHART_FOLDER, "category_costs_bar_chart.png")
    plt.tight_layout()
    plt.savefig(chart_path)
    plt.close()

    return jsonify({"chart_path": chart_path})


# Route for generating the pie chart
@app.route("/pie_chart")
def pie_chart():
    df = load_data()
    grouped = df.groupby("Category (Shop)")["Cost"].sum()

    # Create pie chart
    plt.figure(figsize=(8, 8))
    grouped.plot(kind="pie", autopct="%1.1f%%", startangle=140, colors=["#ff9999", "#66b3ff", "#99ff99"])
    plt.title("Cost Distribution by Category (Shop)", fontsize=14)
    plt.ylabel("")  # Remove y-axis label

    # Save the chart
    chart_path = os.path.join(CHART_FOLDER, "category_costs_pie_chart.png")
    plt.tight_layout()
    plt.savefig(chart_path)
    plt.close()

    return jsonify({"chart_path": chart_path})


if __name__ == "__main__":
    app.run(debug=True)
