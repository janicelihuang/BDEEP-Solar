import csv
import time

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import WebDriverException
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import UnexpectedAlertPresentException
from selenium.common.exceptions import NoAlertPresentException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from multiprocessing import Pool
from multiprocessing import Process

def wait_and_get(driver, cond):
    try:
        elem = WebDriverWait(driver, 60).until(cond)
        return elem
    except NoSuchElementException:
        return None
    except UnexpectedAlertPresentException:
        return None
    except WebDriverException:
        return None

def load_webpage(url):
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    options.add_argument('--disable-gpu')
    options.add_argument('no-sandbox')

    try:
        driver = webdriver.Chrome(chrome_options=options)
        driver.get(url)
        if driver.title.find("Home") != -1:
            return driver
        else:
            return None
    except WebDriverException:
        return None

def get_sunnumber(driver, address):
    cond = EC.presence_of_element_located((By.NAME, "ngcaddress"))
    elem = wait_and_get(driver, cond)
    if elem == None:
        return ("No Results")
    try:
        elem.clear()
        elem.send_keys(address)
        driver.execute_script("window.confirm = function(){return true;}");
        elem.send_keys(Keys.RETURN)
    except UnexpectedAlertPresentException:
        return ("NA")

    cond = EC.presence_of_element_located((By.CSS_SELECTOR, "button.btn"))
    elem = wait_and_get(driver, cond)
    if elem == None:
        return ("Exception")
    elem.send_keys(Keys.RETURN)
    if driver.title.find("Not Found") != -1:
        return ("NA")
    if driver.title.find("Your SunNumber") == -1:
        return ("NA")
    if driver.current_url.find("incoverage=0") != -1:
        return ("NA")

    cond = EC.presence_of_element_located((By.CSS_SELECTOR, "li.num"))
    elem = wait_and_get(driver, cond)
    if elem == None:
        return ("No Results")
    return elem.text

def f(x):
    start_time = time.time()
    inputfile = x[0]
    outputfile = x[1]
    processid = x[2]

    with open(inputfile, 'r') as csvinput:
        with open(outputfile, 'ab') as csvoutput:
    	    reader = csv.DictReader(csvinput)
    	    fieldnames = reader.fieldnames
    	    fieldnames.append("SunNumber")
            writer = csv.DictWriter(csvoutput, fieldnames)
            for row in reader:
                driver = load_webpage("http://www.sunnumber.com")
                if driver != None:
                    address = row['PropertyFullStreetAddress'] + " " + row['PropertyCity'] + " " + row['State'] + " " + row["PropertyZip"]
                    sun_number = get_sunnumber(driver, address)
                    row['SunNumber'] = sun_number
                    print (processid, ": Retrieved Sun Number: ", time.time()-start_time)
                    writer.writerow(row)
                    try:
                        if driver != None:
                            driver.close()
                    except WebDriverException:
                        pass
                else:
                    row['SunNumber'] = 'error'
                    writer.writerow(row)
    return


if __name__ == '__main__':
    p = Pool(processes=7)
    p1 = ("CTHedonics_unique_00.csv","CTHedonics_updated_00.csv", 1)
    p2 = ("CTHedonics_unique_01.csv","CTHedonics_updated_01.csv", 2)
    p3 = ("CTHedonics_unique_02.csv","CTHedonics_updated_02.csv", 3)
    p4 = ("CTHedonics_unique_03.csv","CTHedonics_updated_03.csv", 4)
    p5 = ("CTHedonics_unique_04.csv","CTHedonics_updated_04.csv", 5)
    p6 = ("CTHedonics_unique_05.csv", "CTHedonics_updated_05.csv", 6)
    p7 = ("CTHedonics_unique_06.csv", "CTHedonics_updated_06.csv", 7)
    p.map(f, [p1,p2,p3,p4,p5,p6,p7])
