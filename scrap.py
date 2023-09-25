import requests
from bs4 import BeautifulSoup
import json
import numpy as np
import re

user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"

def flipkart_scrape(url):
    headers = {"User-Agent": user_agent}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, "html.parser")

    products = []

    flipkart_links = soup.find_all("a", class_="_1fQZEK")

    for i, product in enumerate(soup.find_all("div", class_="_4rR01T")):
        name = product.text.strip()
        price_elem = product.find_next("div", class_="_30jeq3 _1_WHN1")
        rating_elem = product.find_next("div", class_="_3LWZlK")
        image = product.find_next("img", class_="_396cs4")["src"]

        # Check if price and rating elements exist
        if price_elem and rating_elem:
            price = price_elem.text.strip()
            rating = rating_elem.text.strip()
        else:
            price = "N/A"
            rating = "N/A"

        # Clean and convert price to float
        price = re.sub('[^0-9.]', '', price)
        price = float(price) if price else 0.0

        # Clean and convert rating to float
        rating = re.sub('[^0-9.]', '', rating)
        rating = float(rating) if rating else 0.0

        products.append({
            "Name": name,
            "Price": price,
            "Review": rating,
            "ImageURL": image,
            "ProductURL": "https://www.flipkart.com" + flipkart_links[i]['href'] if i < len(flipkart_links) else None,
        })

    return products

def amazon_scrape(url):
    headers = {"User-Agent": user_agent}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, "html.parser")

    products = []

    amazon_links = soup.find_all("a", class_="a-link-normal s-no-outline")

    for i, product in enumerate(soup.find_all("div", class_="sg-col-20-of-24 s-result-item s-asin sg-col-0-of-12 sg-col-16-of-20 sg-col s-widget-spacing-small sg-col-12-of-16")):
        name_elem = product.find("span", class_="a-size-medium a-color-base a-text-normal")
        price_elem = product.find("span", class_="a-price-whole")
        rating_elem = product.find("span", class_="a-icon-alt")
        image_elem = product.find("img", class_="s-image")

        # Check if name, price, and rating elements exist
        if name_elem and price_elem and rating_elem:
            name = name_elem.text.strip()
            price = price_elem.text.strip()
            rating = rating_elem.text.strip()
        else:
            name = "N/A"
            price = "N/A"
            rating = "N/A"

        # Clean and convert price to float
        price = re.sub('[^0-9.]', '', price)
        price = float(price) if price else 0.0

        # Clean and convert rating to float
        rating = re.sub('[^0-9.]', '', rating)
        rating = float(rating) if rating else 0.0

        products.append({
            "Name": name,
            "Price": price,
            "Review": rating,
            "ImageURL": image_elem["src"] if image_elem else "",
            "ProductURL": "https://www.amazon.in" + amazon_links[i]['href'] if i < len(amazon_links) else None
        })

    return products

def normalize_data(data, key):
    values = [float(item[key]) for item in data]
    
    if not values:  # Check if the list is empty
        return [0] * len(data)
    
    min_val = min(values)
    max_val = max(values)

    if max_val == min_val:
        return [0] * len(data)

    normalized_values = [(val - min_val) / (max_val - min_val) for val in values]
    return normalized_values

def custom_sort_key(item):
    price_weight = 0.6
    review_weight = 0.4
    return (item["Normalized Price"] * price_weight) + (item["Normalized Review"] * review_weight)

def scrape_web(find_product):
    flipkart_url = f"https://www.flipkart.com/search?q={find_product}"
    flipkart_data = flipkart_scrape(flipkart_url)

    amazon_url = f"https://www.amazon.in/s?k={find_product}"
    amazon_data = amazon_scrape(amazon_url)

    merge_data = flipkart_data + amazon_data

    # Normalize Price and Review
    normalized_prices = normalize_data(merge_data, "Price")
    normalized_reviews = normalize_data(merge_data, "Review")

    for i, item in enumerate(merge_data):
        item["Normalized Price"] = normalized_prices[i]
        item["Normalized Review"] = normalized_reviews[i]

    # Sort the products based on the custom key in ascending order
    sorted_data = sorted(merge_data, key=custom_sort_key)

    # Save the sorted data to a JSON file
    with open("sorted_product_data.json", "w", encoding="utf-8") as json_file:
        json.dump(sorted_data, json_file, ensure_ascii=False, indent=4)

    print("Data written to 'sorted_product_data.json'")

if __name__ == "__main__":
    find_product = input("Enter the product you want to search for: ")
    scrape_web(find_product)
