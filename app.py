from flask import Flask, render_template, request, redirect, url_for
import os
import json
from scrap import scrape_web  # Import your scraping script

app = Flask(__name__)

# Define a route to scrape and display product data
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        find_product = request.form["find_product"]
        scrape_web(find_product)  # Call your scraping function

    # Load the sorted product data from the JSON file
    with open("sorted_product_data.json", "r", encoding="utf-8") as json_file:
        data = json.load(json_file)
      
    return render_template("index.html", products=data)

if __name__ == "__main__":
    app.run(debug=True)