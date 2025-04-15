import json
import db_connector
import transportation
import utilities
import requests
import re
import time
from datetime import datetime
from bs4 import BeautifulSoup
import pandas as pd

cheapest_basket = None
meb_total = 0.0


def read_cell_as_float(file_path, cell_id):
    """
    Reads a specific cell from an Excel file and converts it to a float.

    Args:
        file_path (str): Path to the Excel file.
        cell_id (str): Cell ID (e.g., 'B2').

    Returns:
        float: The value of the cell converted to float, or None if conversion fails.
    """
    # Read the Excel file into a DataFrame
    df = pd.read_excel(file_path, engine='openpyxl')

    # Convert cell ID (e.g., 'B2') to row and column indices
    column = ord(cell_id[0].upper()) - ord('A')  # Convert column letter to index (0-based)
    row = int(cell_id[1:]) - 1  # Convert row number to index (0-based)

    try:
        # Retrieve the cell value
        cell_value = df.iat[row, column]
        # Convert the value to float
        return float(cell_value)
    except (ValueError, TypeError):
        # Handle cases where the value cannot be converted to float
        print(f"Value in cell {cell_id} cannot be converted to float.")
        return None
    except IndexError:
        # Handle cases where the cell is out of bounds
        print(f"Cell {cell_id} is out of bounds.")
        return None
    except Exception as e:
        # Handle any other exceptions
        print(f"An error occurred: {e}")
        return None


def get_beyaz_ekmek_price(url):
    # Send a request to fetch the content of the webpage
    response = requests.get(url)

    # Parse the content using BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find the table containing the price list
    table = soup.find('table', {'border': '1'})

    # Iterate through the rows of the table
    for row in table.find_all('tr'):
        cells = row.find_all('td')
        # Check if the first cell contains "BEYAZ EKMEK"
        if len(cells) > 0 and cells[0].text.strip() == 'BEYAZ EKMEK':
            # Extract the price and convert it to a float
            price_text = cells[2].text.strip()
            price_value = float(price_text.replace(' TL', '').replace(',', '.'))
            return price_value*30*5

    # If the price is not found, return None
    return None


# Get the bread price from Ankara Halk Ekmek website
def get_bread_price():
    # Define the headers for the request
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    try:
        # Send a GET request to fetch the HTML content of the page
        response = requests.get("https://ankarahalkekmek.com.tr/fiyat-listesi/", headers=headers)
        response.raise_for_status()  # Raise an exception for HTTP errors

        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find the table row containing "NORMAL EKMEK"
        rows = soup.find_all('tr')
        for row in rows:
            cols = row.find_all('td')
            if len(cols) > 1 and 'NORMAL EKMEK' in cols[1].text:
                price_str = cols[3].text.strip()
                price_float = float(price_str.replace(',', '.'))
                return price_float*30*5

    except requests.exceptions.RequestException as e:
        # Handle request errors
        print(f"Request error: {e}")
        return None


def read_page(meb_item):
    # Headers to mimic a request from a browser

    page_address = meb_item.url
    item_name = meb_item.item_name
    ratio = meb_item.ratio
    item_category = meb_item.item_category

    global meb_total
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    # Send a GET request to fetch the HTML content of the page
    response = requests.get(page_address, headers=headers)
    response.raise_for_status()  # Raise an exception for HTTP errors

    # Extract JSON data from the HTML content using regex
    html_content = response.text
    # print(html_content)
    json_match = re.search(r'{"@context":"https://schema.org","@type":"ItemList".*?]}</script>', html_content)
    #print(json_match)
    if json_match:
        json_data = json_match.group(0)
        end_index = json_data.find('</')
        extracted_part = json_data[:end_index]

        try:
            data = json.loads(extracted_part)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON data: {e}")
            data = None  # Or s    #print("Captured JSON Data:")

        item_list_elements = data.get('itemListElement', [])
        # Create an empty list to store the tuples
        items_data = []
    # Iterate through each item dictionary
        for item in item_list_elements:
            now = datetime.now()
            current_date = now.date()
            name = item['item']['name']
            low_price = item['item']['offers']['lowPrice']
            if item_category == "food":
                low_price = low_price * 5
            items_data.append((item_name, name, current_date, low_price))

        # Sort the list by the price (ascending order)
        sorted_items_data = sorted(items_data, key=lambda x: x[3])
        number_of_elements = len(sorted_items_data)
        temp_total = 0.0
        if number_of_elements >= 5:
            for i in range(5):
                temp_total += sorted_items_data[i][3]
            temp_total = temp_total / 5

        elif number_of_elements > 0:
            for i in range(number_of_elements):
                temp_total += sorted_items_data[i][3]
            temp_total = temp_total / 5

        cheapest_basket.append(sorted_items_data[0])
        db_connector.add_to_meb_hist(sorted_items_data[0], temp_total * ratio)
        meb_total += temp_total * ratio


def get_pharmacy_retail_price(url):
    # Send a GET request to the webpage
    response = requests.get(url)

    # Parse the HTML content
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find the table containing the price information
    table = soup.find('div', class_='ilacgenel').find('table')

    # Iterate through the rows of the table to find the specific price
    for row in table.find_all('tr'):
        columns = row.find_all('td')
        for i, column in enumerate(columns):
            if 'Eczane Perakende Satış Fiyatı ( KDV Dahil )' in column.text:
                price_text = columns[i + 1].text.strip()
                # Extract the numeric value from the price string
                price_value = float(price_text.replace(' TL', '').replace(',', '.'))
                return price_value

    return None


def get_doctor_fee(url):
    # Fetch the HTML content from the given URL
    response = requests.get(url)

    if response.status_code != 200:
        raise Exception(f"Failed to retrieve content from {url}. Status code: {response.status_code}")

    html_content = response.text

    # Parse the HTML content
    soup = BeautifulSoup(html_content, 'html.parser')

    # Find the relevant list item
    items = soup.find_all('li')
    for item in items:
        if "Üniversite hastanelerine bağlı üçüncü basamak sağlık hizmeti sunucularında" in item.text:
            # Extract the numeric value using regular expression

            str_temp = item.text[96:]
            str_temp = str_temp[:str_temp.find(' ')]
            price_value = float(str_temp.replace(',', '.'))
            return price_value*3

    return None


def med_reader(med_item):
    medicine_total = 0.0

    if med_item.alt_exists == 1:
        med_price = get_pharmacy_retail_price(med_item.med_link)
        alter_price = get_pharmacy_retail_price(med_item.alter_link)
        if med_price > alter_price:
            medicine_total = med_price - alter_price

    # Example usage
    url = "https://www.sgk.gov.tr/Content/Post/1c403747-5401-410e-9a1f-041d705333d3/Muayene-Katilim-Payi-2022-05-14-09-42-31"
    doctor_fee = get_doctor_fee(url)

    return medicine_total+doctor_fee


# Defining main function
def main():
    meb_list = db_connector.connect_db()
    medicine_list = db_connector.connect_medicine()
    global meb_total
    medic_total = 0.0
    global cheapest_basket
    cheapest_basket = []

    # Loop through the list of URLs and read each page
    for item in medicine_list:
        price = med_reader(item)
        if price > 0:
            medic_total += price

    medic_price = (medic_total / 5) * 3
    now = datetime.now()
    current_date = now.date()

    if medic_price is not None:
        db_connector.add_to_meb_manual("Specialist doctor visit Visits and medicine", current_date, medic_price)
        meb_total += medic_price
    else:
        print("Could not retrieve the medic_price.")

    # Loop through the list of URLs and read each page
    for meb_item in meb_list:
        if meb_item.ratio > 0:
            # print(meb_item.url)
            read_page(meb_item)

    transportation_cost = transportation.calculate_transportation_cost()
    if transportation_cost is not None:
        db_connector.add_to_meb_manual("Transport", current_date, transportation_cost)
        meb_total += transportation_cost
    else:
        print("Could not retrieve the transportation_cost.")

    # electricity price
    electricity_cost = utilities.electricity_cost()
    if electricity_cost is not None:
        db_connector.add_to_meb_manual("Electricity", current_date, electricity_cost)
        meb_total += electricity_cost
    else:
        print("Could not retrieve the electricity_cost.")

    # tube gas price
    tubegas_price = utilities.get_tupgaz_price()
    if tubegas_price is not None:
        db_connector.add_to_meb_manual("Tube gas canister", current_date, tubegas_price)
        meb_total += tubegas_price
    else:
        print("Could not retrieve the tubegas_price.")

    # water price
    water_prices = utilities.get_water_prices()
    if water_prices:
        db_connector.add_to_meb_manual("Water Supply", current_date, water_prices)
        meb_total += water_prices
    else:
        print("Could not retrieve the water_prices.")

    # bread_price = get_bread_price()
    # if bread_price:
        #print(f"The current price is: {bread_price}")
        # meb_total += bread_price
    # else:
        # print("Failed to retrieve the bread_price.")


    # URL of the webpage to be scraped
    url = 'http://www.eskisehirhalkekmek.com/fiyat-listesi'

    # Call the function and print the result
    bread_price = get_beyaz_ekmek_price(url)
    if bread_price is not None:
        db_connector.add_to_meb_manual("Bread", current_date, bread_price)
        meb_total += bread_price
    else:
        print("BEYAZ EKMEK price not found.")

    # extract rent price
    # URL of the webpage to be scraped
    path = r'C:\Users\SAVASCIO\UNHCR\UNHCR Türkiye Inter-Agency and IM Team - Information Management\01. Türkiye\24. CBI\Market Price Tracker\Rent_Data.xlsx'
    rent_average = read_cell_as_float(path, "I10")
    db_connector.add_to_meb_manual("Rent", current_date, rent_average)
    meb_total += rent_average

    # add meb_total to the database
    db_connector.add_total(meb_total)


# Using the special variable
# __name__
if __name__ == "__main__":
    main()

