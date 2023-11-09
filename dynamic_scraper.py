#### This program scrapes naukri.com's page and gives our result as a 
#### list of all the job_profiles which are currently present there. 
  
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import csv 

fields = ['reference_number', 'color_and_brick', 'quantity', 'set_number'] 

def get_piece_info_for_set(set_number):

    pieces = []
    print(set_number)
    #url of the page we want to scrape
    url = "https://www.bricklink.com/v2/catalog/catalogitem.page?S=" + str(set_number) + "#T=I"
    
    # initiating the webdriver. Parameter includes the path of the webdriver.
    driver = webdriver.Chrome('./chromedriver.exe') 
    driver.get(url) 
  
    # this is just to ensure that the page is loaded
    time.sleep(0.05) 

    html = driver.page_source

    #Click the accept all cookies button
    python_button = driver.find_elements_by_xpath('//*[@id="js-btn-save"]/button[2]')[0]
    python_button.click()

    time.sleep(0.05)
    
    # this renders the JS code and stores all
    # of the information in static HTML code.
    
    # Now, we could simply apply bs4 to html variable
    soup = BeautifulSoup(html, "html.parser")
    all_rows = soup.find_all('tr', {'class' : 'pciinvItemRow'})
    for row in all_rows:
        reference_number, quantity, color_and_brick = 0, 0, 0
        count = 0
        for data in row:
            count += 1
            if count == 6:
                quantity = data.text
            if count == 8:
                reference_number = data.text
            if count == 10:
                color_and_brick = data.text
        pieces.append([reference_number, color_and_brick, quantity, str(set_number)])
        # pieces.append({"quantity_number":quantity_count,"reference_number":reference_number,"color_and_brick":color_and_brick,"set":set_number})
    if(len(pieces) == 0):
        return []
    # name of csv file 
    filename = "set_data/" + str(set_number) + ".csv"

    # writing to csv file 
    with open(filename, 'w', encoding="utf-8") as csvfile: 
        # creating a csv writer object 
        csvwriter = csv.writer(csvfile) 
            
        # writing the fields 
        csvwriter.writerow(fields) 
            
        # writing the data rows 
        csvwriter.writerows(pieces)

    driver.close() # closing the webdriver
    return pieces

LIST_OF_SETS = [4735,7113,8089,8036,620,7201,6211,527,6059,7899,6265,4501,7103,6949,6267,7245,7235,8632,4727,3825,4488,4916,8401,6886,6846,4733,7903,7890,6046,6210,6205,6246,7412,7255,7655,1793,7003,4762,6357,7622,8810,7624,4492,7251,10186,10144,7200,6044,7771,7654,6245,4338,7899,4494,4712,8119,7133,8038,7626,8630,6265,4502,7261,7620,4702,7256,7070,6211,4490,7682,6206,7000,4477,6209,7621,4488,6207,4415,6193,6239,7250,7659,8662,10186,4850,4475,7263,7252,4480,6983,6190,7258,8666,7251,4766,6698,6256,4417,7002,6258,6155,1723,4491,4500]
new_sets = [75249,76392,75277,21006,75258,7171,75267,75254,75269,75280,75290]
# list_of_pieces = []

# for lego_set in new_sets:
#     list_of_pieces.append(get_piece_info_for_set(lego_set))
# get_piece_info_for_set()
