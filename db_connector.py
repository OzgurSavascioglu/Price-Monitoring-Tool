import mysql.connector
import time
from datetime import datetime

# Database configuration
db_config = {
    'user': 'root',
    'password': 'YOUR_PASSWORD',
    'host': 'localhost',
    'database': 'pricemonitoring'
}


class BasketItem:
    def __init__(self, url, item_name, ratio, item_category):
        self.url = url
        self.item_name = item_name
        self.ratio = ratio
        self.item_category = item_category


class MedicineItem:
    def __init__(self, medicine_name, alt_exists, medicine_alternative, med_link, alter_link):
        self.medicine_name = medicine_name
        self.alt_exists = alt_exists
        self.medicine_alternative = medicine_alternative
        self.med_link = med_link
        self.alter_link = alter_link


def connect_db():
    # Query to fetch the URLs
    # query = "SELECT url FROM Basket_Details"
    query = "SELECT url, item_name, ratio, item_category FROM Basket_Details"

    # Connect to the database
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()

    # Execute the query
    cursor.execute(query)

    # Fetch all the results
    results = cursor.fetchall()

    # Initialize the URL list with the base URL
    base_url = None
    url_list = [base_url]

    # Add the URLs from the database to the list
    for row in results:
        item = BasketItem(row[0], row[1], row[2], row[3])
        url_list.append(item)
        # item_list.append(row[1])

    # Close the cursor and connection
    cursor.close()
    connection.close()

    # Removing the first element
    if url_list:
        url_list.pop(0)

    return url_list


def connect_medicine():
    # Query to fetch the URLs
    # query = "SELECT url FROM Basket_Details"
    query = "SELECT medicine_name, alt_exists, medicine_alternative, med_link, alter_link FROM medicines"

    # Connect to the database
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()

    # Execute the query
    cursor.execute(query)

    # Fetch all the results
    results = cursor.fetchall()

    # Initialize the URL list with the base URL
    base_url = None
    url_list = [base_url]

    # Add the URLs from the database to the list
    for row in results:
        item = MedicineItem(row[0], row[1], row[2], row[3], row[4])
        url_list.append(item)

    # Close the cursor and connection
    cursor.close()
    connection.close()

    # Removing the first element
    if url_list:
        url_list.pop(0)

    return url_list


def add_to_meb_hist(item, average_lower):
    # Query to fetch the URLs
    query = "INSERT INTO Meb_Historical(item_name, item_brand, cur_date, price) VALUES (%s, %s, %s, %s)"

    # Connect to the database
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    # Execute the query with dynamic values
    cursor.execute(query, (item[0], item[1], item[2], average_lower))

    # Commit the changes
    connection.commit()

    # Close the connection
    cursor.close()
    connection.close()


def add_to_meb_manual(item_name, cur_date, price):
    # Query to fetch the URLs
    query = "INSERT INTO Meb_Historical(item_name, cur_date, price) VALUES (%s, %s, %s)"

    # Connect to the database
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    # Execute the query with dynamic values
    cursor.execute(query, (item_name, cur_date, price))

    # Commit the changes
    connection.commit()

    # Close the connection
    cursor.close()
    connection.close()


def calculate_total():
    now = datetime.now()
    current_date = now.date()
    # Query to fetch the URLs
    query = "SELECT SUM(price) FROM Meb_Historical WHERE Cur_Date =  %s"

    # Connect to the database
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    # Execute the query with dynamic values
    cursor.execute(query, (current_date,))

    # Fetch the result
    result = cursor.fetchone()

    # Check if the result is not None
    if result and result[0] is not None:
        sum_price = result[0]
        print(f"The sum of prices for {current_date} is: {sum_price}")
    else:
        print(f"No data found for {current_date}")

    # Close the connection
    cursor.close()
    connection.close()
    return sum_price


def add_total(meb_total):
    now = datetime.now()
    current_date = now.date()
    # sum_price = calculate_total()
    # Query to fetch the URLs
    query = "INSERT INTO Basket_Total(basket_name, cur_date, price) VALUES (%s, %s, %s)"

    # Connect to the database
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    # Execute the query with dynamic values
    cursor.execute(query, ("meb", current_date, meb_total))

    # Commit the changes
    connection.commit()

    # Close the connection
    cursor.close()
    connection.close()


def get_ratio(item_name):
    # Query to fetch the URLs
    query = "SELECT ratio FROM basket_details WHERE basket_name = %s AND item_name = %s"
    ratio = None
    # Connect to the database
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    # Execute the query with dynamic values
    cursor.execute(query, ("meb", item_name))

    # Fetch the result
    result = cursor.fetchone()

    # Check if the result is not None
    if result and result[0] is not None:
        ratio = result[0]
    else:
        print("No data found")

    # Close the connection
    cursor.close()
    connection.close()
    return ratio
