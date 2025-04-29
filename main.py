from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

CHROME_OPTS = Options()
CHROME_OPTS.add_argument("--headless")
CHROME_OPTS.add_argument("--disable-gpu")
CHROME_OPTS.set_capability("pageLoadStrategy", "eager")

def getICAO(airport: str) -> str:
    driver = webdriver.Chrome(options=CHROME_OPTS)
    driver.set_page_load_timeout(10)
    
    try:
        driver.get(f"https://en.wikipedia.org/wiki/{airport}")
        source = driver.page_source
    except Exception as e:
        print("Timed out.")
        source = None
        return ""
    
    src_html = BeautifulSoup(source, 'html5lib')
    driver.close()
    icao = ((src_html.find_all('span', class_='nowrap'))[1]).find('span', class_='nickname').text
    return icao

def getPOI(icao):
    driver = webdriver.Chrome(options=CHROME_OPTS)
    driver.set_page_load_timeout(10)
    
    try:
        driver.get(f"https://runway.airportdb.io/airport/{icao}")
        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.p-8")))
        source = driver.page_source
    except Exception as e:
        print("Timed out.")
        source = None
        return
    
    src_html = BeautifulSoup(source, 'html5lib')
    driver.close()
    runways = src_html.find_all('div', class_='p-8')
    lp = [] # possible landing points
    tp = [] # possible takeoff points
    for runway_html in runways:
        runway_num = (runway_html.find('div', class_="px-3 py-1 border border-gray-500 text-lg rounded-md font-bold")).text
        wind_type = (runway_html.find('div', class_='ml-5')).text
        if wind_type == "Headwind":
            lp.append(runway_num)
        elif wind_type == "Tailwind":
            tp.append(runway_num)
    print("Arriving planes will fly over runway(s):", end="   ")
    printItems(lp)
    print("Departing planes will fly over runway(s):", end="   ")
    printItems(tp)

def getArrivals(airport):
    driver = webdriver.Chrome(options=CHROME_OPTS)
    driver.set_page_load_timeout(10)

    try:
        driver.get(f"https://www.flightaware.com/live/airport/{airport}")
        source = driver.page_source
    except Exception as e:
        print("Timed out.")
        source = None
        return

    src_html = BeautifulSoup(source, 'html5lib')
    driver.close()

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

def printItems(list):
    for item in list:
        print(item, end="   ")
    print("")

def main():
    while True:
        airport = input("Input the airport code: ")
        action = input("Choose function (0 to exit): ")
        match action:
            case '0':
                print("Exiting...")
                return
            case '1':
                getICAO(airport)
            case '2':
                icao = getICAO(airport)
                getPOI(icao)
            case '3':
                getArrivals(airport)
            case _:
                print("No command found.")

if __name__ == "__main__":
    main()