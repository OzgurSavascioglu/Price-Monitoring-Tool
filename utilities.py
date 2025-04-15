from bs4 import BeautifulSoup
import requests


def electricity_cost():
    # Fetch the webpage content
    url = 'https://enerjiajansi.com.tr/elektrik-birim-fiyatlari/'
    response = requests.get(url)
    webpage_content = response.text

    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(webpage_content, 'html.parser')

    # Find the table containing the prices
    table = soup.find('figure', class_='wp-block-table').find('table')

    # Extract rows from the table
    rows = table.find_all('tr')

    # Initialize a dictionary to store the prices
    prices = {}
    monthly_cost = 0.0
    # Loop through the rows to find the relevant prices
    for row in rows:
        cells = row.find_all('td')
        if len(cells) > 0:
            mesken_tipi = cells[0].text.strip()
            final_price = cells[5].text.strip()

            if mesken_tipi == "Konut (240 kWh tüketime kadar)":
                prices['Konut (240 kWh tüketime kadar)'] = float(final_price.replace(',', '.'))
                monthly_cost += float(final_price.replace(',', '.')) * 208.333
            elif mesken_tipi == "Konut (240 kWh tüketimden sonra)":
                prices['Konut (240 kWh tüketimden sonra)'] = float(final_price.replace(',', '.'))
                monthly_cost += float(final_price.replace(',', '.')) * 0

    return monthly_cost


def get_tupgaz_price():
    # Define the headers for the request
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    try:
        # Send a GET request to fetch the HTML content of the page
        response = requests.get("https://www.ergaz.com.tr/otogaz-ve-tup-fiyatlari", headers=headers)  # Replace URL_OF_THE_PAGE with the actual URL
        response.raise_for_status()  # Raise an exception for HTTP errors

        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find the table containing the relevant data
        table = soup.find('div', {'id': 'list-home-1517'}).find('table')
        rows = table.find_all('tr')

        # Get the price from the second row, fourth column (index 3)
        price_str = rows[1].find_all('td')[4].text.strip()

        # Replace comma with dot and convert to float
        price_float = float(price_str.replace(',', '.'))
        return price_float

    except requests.exceptions.RequestException as e:
        # Handle request errors
        print(f"Request error: {e}")
        return None


def get_water_prices():
    # Define the headers for the request
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    try:
        # Send a GET request to fetch the HTML content of the page
        response = requests.get("https://www.aski.gov.tr/tr/ucretler.aspx", headers=headers, verify=False)  # Replace URL_OF_THE_PAGE with the actual URL
        response.raise_for_status()  # Raise an exception for HTTP errors

        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find the table containing the relevant data
        table = soup.find('table', {'class': 'table table-responsive-lg table-bordered table-sm mb-3'})
        rows = table.find_all('tr')

        # Initialize a dictionary to store the prices
        toplam_price_float = 0
        first_iteration = 1

        # Iterate over the rows to find the relevant data
        for row in rows:
            cols = row.find_all('td')
            if len(cols) > 0:
                abonetype = cols[0].text.strip()
                if abonetype in ["0-15 m³"]:
                    toplam_price_str = cols[3].text.strip()
                    # Replace comma with dot and convert to float
                    toplam_price_float += float(toplam_price_str.replace(',', '.'))*1.5

                elif abonetype in ["16-30 m³"]:
                    toplam_price_str = cols[3].text.strip()
                    # Replace comma with dot and convert to float
                    if first_iteration == 1:
                        toplam_price_float += float(toplam_price_str.replace(',', '.'))*0
                        first_iteration = 0

        return toplam_price_float

    except requests.exceptions.RequestException as e:
        # Handle request errors
        print(f"Request error: {e}")
        return None