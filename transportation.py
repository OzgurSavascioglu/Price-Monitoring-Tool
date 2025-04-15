from bs4 import BeautifulSoup
import fitz
import PyPDF2
import requests
import re


def ankara_transport():
    # Define the headers for the request
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    # Send a GET request to fetch the HTML content of the page
    response = requests.get("https://www.ankarakart.com.tr/tarifeler", headers=headers)
    response.raise_for_status()  # Raise an exception for HTTP errors

    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find the specific table that contains the fare information
    table = soup.find('table', {'class': 'table table-striped table-bordered'})

    # Initialize variable to store the fare
    fare = None

    # Iterate through the rows of the table to find the relevant fare
    for row in table.find_all('tr'):
        columns = row.find_all('td')
        if columns and 'Ankara Kart Bir Biniş Ücreti' in columns[0].text:
            fare = columns[1].text.strip()
            fare = fare.replace(',', '.')
            break

    # Print the extracted fare
    if fare:
        # print("Ankara Kart Bir Biniş Ücreti:", fare)
        return float(fare)
    else:
        # print("Fare not found")
        return 0


def gaziantep_transport():
    # Define the headers for the request
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    # Send a GET request to fetch the HTML content of the page
    response = requests.get("https://gaziulas.com.tr/ucret-tarifesi", headers=headers)
    response.raise_for_status()  # Raise an exception for HTTP errors

    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find the specific table that contains the fare information
    table = soup.find('table', {'class': 'table table-striped fs-6'})

    # Initialize variable to store the fare
    fare = None

    # Iterate through the rows of the table to find the relevant fare
    for row in table.find_all('tr'):
        columns = row.find_all('td')
        if columns and 'Belediye (Şehir İçi)' in columns[0].text:
            fare = columns[1].text.strip()
            fare = fare.replace(',', '.')
            break

    # Print the extracted fare
    if fare:
        # print("Belediye (Şehir İçi):", fare)
        return float(fare)
    else:
        # print("Fare not found")
        return 0


def istanbul_transport():
    # Define the headers for the request
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    # Send a GET request to fetch the HTML content of the page
    response = requests.get("https://metro.istanbul/SeferDurumlari/BiletUcretleri", headers=headers)
    response.raise_for_status()  # Raise an exception for HTTP errors

    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')

    anonim_kart_section = soup.find('div', {'id': 'anonim-kart'})
    price_section = anonim_kart_section.find_next('ul', class_='price2')

    if price_section:
        tam_price = price_section.find('span', string='Tam:').find_next('span',
                                                                   class_='float-right').text.strip()
        tam_price_value = tam_price.split(' ')[0].replace(',', '.')

        # print("Anonim Kart Tam Price:", tam_price_value)
        return float(tam_price_value)
    else:
        # print("Anonim Kart price section not found.")
        return 0


def sanliurfa_transport():
    # Make a GET request to the API
    response = requests.get("https://pv2api3.teknarteknoloji.com/api/Transportation/Tariff")

    # Check if the request was successful (status code 200)
    response.raise_for_status()

    # Parse the JSON response
    data = response.json()

    # Initialize a variable to hold the fee
    fee = None

    # Iterate through the list of data items
    for item in data['data']:
        if item['name'] == "1-)ŞEHİR İÇİ MERKEZ VE TÜM İLÇE İÇİ TOPLU TAŞIMA FİYATLARI":
            fee = item['fee']
            break

    # Print the fee
    # print(f"The fee for '1-)ŞEHİR İÇİ MERKEZ VE TÜM İLÇE İÇİ TOPLU TAŞIMA FİYATLARI' is: {fee}")
    return float(fee)


# Function to extract numeric values from text using regular expressions
def extract_numeric_value(text, intIndex, decIndex):
    # Regular expression pattern to match numeric values
    pattern = r'\b\d+(?:\.\d+)?\b'  # Matches numbers with or without decimal points
    matches = re.findall(pattern, text)
    int_part = int(matches[intIndex])
    dec_part = (int(matches[decIndex]))/100
    if matches:
        return int_part+dec_part
    else:
        return None


# Step 2: Extract text from the PDF
def extract_text_from_pdf(pdf_path):
    document = fitz.open(pdf_path)
    text = ""
    for page_num in range(len(document)):
        page = document.load_page(page_num)
        text += page.get_text()
    return text


# Step 2: Extract text from the PDF using PyPDF2
def extract_text_from_pdf_v2(pdf_path):
    text = ""
    with open(pdf_path, 'rb') as f:
        pdf_reader = PyPDF2.PdfReader(f)
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            text += page.extract_text()
    return text


def hatay_transport():
    # Step 1: Download the PDF
    pdf_url = 'https://api.hatay.bel.tr/storage/gallery-media/December2022/NUygaO2bQj5CaSLG5jbH.pdf'
    response = requests.get(pdf_url)
    pdf_path = 'downloaded_file.pdf'
    with open(pdf_path, 'wb') as f:
        f.write(response.content)
    pdf_text = extract_text_from_pdf(pdf_path)
    my_number = extract_numeric_value(pdf_text, 4, 5)
    return float(my_number)


def adana_transport():
    # Step 1: Download the PDF
    pdf_url = 'https://www.adana.bel.tr/panel/uploads/duyuru_v/dosya/toplu-tasima-araclari-ucret-tarifesi.pdf'
    response = requests.get(pdf_url, verify=False)
    response.raise_for_status()  # Raise an exception for HTTP errors

    pdf_path = 'downloaded_file2.pdf'
    with open(pdf_path, 'wb') as f:
        f.write(response.content)

    # Step 2: Extract text from the PDF using PyPDF2
    pdf_text = extract_text_from_pdf_v2(pdf_path)

    # Step 3: Extract numeric value from the text
    my_number = extract_numeric_value(pdf_text, 5, 6)
    return float(my_number)


def mersin_transport():
    # Define the headers for the request
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    # Send a GET request to fetch the HTML content of the page
    response = requests.get("https://ulasim.mersin.bel.tr/ulasimucretleri.php", headers=headers, verify=False)
    response.raise_for_status()  # Raise an exception for HTTP errors

    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find the div with class "btn ulasim_buton" and onclick attribute "tam();"
    tam_div = soup.find('div', {'class': 'btn ulasim_buton', 'onclick': 'tam();'})

    if tam_div:
        # Find the font element containing the price
        price_font = tam_div.find('font', style='font-weight:bold;')

        if price_font:
            # Extract the text of the font element and remove any unnecessary characters
            tam_price_text = price_font.text.strip()

            # Extract the numeric value from the text
            tam_price_value = tam_price_text.split(' ')[0].replace(',', '.')

            # print("Anonim Kart Tam Price:", tam_price_value)
            return float(tam_price_value)
        else:
            # print("Anonim Kart Tam price font not found.")
            return 0
    else:
        # print("Anonim Kart button not found.")
        return 0


def bursa_transport():
    # Define the headers for the request
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    # Send a GET request to fetch the HTML content of the page
    response = requests.get("https://www.burulas.com.tr/fiyat-tarifeleri/", headers=headers)
    response.raise_for_status()  # Raise an exception for HTTP errors

    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')

    # Locate the table containing fare information
    # table = soup.find("table")

    # Find the cell with data-cell-id="B9"
    uzun_hat_cell = soup.find("td", {"data-cell-id": "C9"})

    # Extract the price from the corresponding cell
    if uzun_hat_cell:
        uzun_hat_price = uzun_hat_cell.get_text().strip().replace('₺', '').strip()
        uzun_hat_price = uzun_hat_price.replace(',', '.')
        return float(uzun_hat_price)
    else:
        return 0


def konya_transport():
    # Define the headers for the request
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    # Send a GET request to fetch the HTML content of the page
    response = requests.get("https://konyakart.konya.bel.tr/sayfa/konyakart-hakkinda-genel-bilgiler", headers=headers)
    response.raise_for_status()  # Raise an exception for HTTP errors

    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')

    # Search for the price in the provided HTML structure
    tam_konyakart_price = None
    for li in soup.find_all('li'):
        if 'tam KONYAKART ile' in li.get_text():
            text = li.get_text()
            # Extract the price using split and strip
            price_text = text.split('tam KONYAKART ile')[1].split(',')[0].strip()
            tam_konyakart_price = ''.join(filter(str.isdigit, price_text))
            break

    return float(tam_konyakart_price)


def izmir_transport():
    # Define the headers for the request
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    try:
        # Send a GET request to fetch the HTML content of the page
        response = requests.get("https://www.izmirimkart.com.tr/tarife-ve-ucretlendirme", headers=headers, verify=False)
        response.raise_for_status()  # Raise an exception for HTTP errors

        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find the table row that contains the text "İzmirim Kart İlk Binişi"
        price_row = soup.find("td", text="İzmirim Kart İlk Binişi").parent

        # Extract the price from the second cell in the row
        price_cell = price_row.find_all("td")[1]
        price = price_cell.text.strip()
        tam_price_value = price.split(' ')[0].replace(',', '.')

        # print(f"İzmirim Kart İlk Binişi Tam (TL) price: {tam_price_value}")
        return float(tam_price_value)

    except requests.exceptions.RequestException as e:
        # print(f"Request error: {e}")
        return 0


def calculate_transportation_cost():
    cost = istanbul_transport() * 0.219851493
    cost += gaziantep_transport() * 0.178168775
    cost += sanliurfa_transport() * 0.113082945
    cost += hatay_transport() * 0.106527472
    cost += adana_transport() * 0.090423359
    cost += mersin_transport() * 0.083581245
    cost += bursa_transport() * 0.071112343
    cost += konya_transport() * 0.050472088
    cost += izmir_transport() * 0.04951068
    cost += 15 * 0.04951068 # ankara_transport()
    return cost * 32
