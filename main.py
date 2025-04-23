from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options

CHROME_OPTS = Options()
CHROME_OPTS.add_argument("--headless")
CHROME_OPTS.add_argument("--disable-gpu")
CHROME_OPTS.set_capability("pageLoadStrategy", "eager")

def main():
    airport = input("Input the airport code: ")
    driver = webdriver.Chrome(options=CHROME_OPTS)
    driver.set_page_load_timeout(10)

    try:
        driver.get(f"https://www.flightaware.com/live/airport/{airport}")
        source = driver.page_source
    except Exception as e:
        print("Timed out.")
        source = None

    src_html = BeautifulSoup(source, 'html5lib')

    try: 
        enroute_html = src_html.find('table', attrs={'data-type': 'enroute'}).find('tbody')
    except AttributeError: 
        print("Failed to retrieve data.")
        return
    
    flights_map = {}
    flights_list = []
    for flight_html in enroute_html.find_all('tr'):
        flight = (flight_html.find('td', class_= 'flight-ident')).a.text
        flights_map[flight] = flight_html
        flights_list.append(flight)
    
    print("Incoming Flight")
    print(f"{flights_list[0]}")
    print(f"Aircraft Type: {((flights_map[flights_list[0]].find_all('td'))[1]).a.text}")
    print(f"From: {(((flights_map[flights_list[0]].find_all('td'))[2]).find('span')).get('original-title')}")

if __name__ == "__main__":
    main()