# import libraries
from selenium import webdriver
import time
import pandas as pd
import re
from datetime import date
import datetime
from selenium.webdriver.firefox.options import Options
import locale


#Input Configuration
urlpage = 'https://shopee.co.id/flash_sale'
locale.setlocale(locale.LC_ALL, 'en_US')
tanggal = datetime.datetime
print(date.today())
SCROLL_PAUSE_TIME = 0.5
optionss = Options()
optionss.headless = True
autoScheduler = True
startTimeHr = 12
startTimeMin = 57
initialTimer = True
skipTimer = False
repeat = True
AutoTime = True

chrome_options = webdriver.ChromeOptions()
chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--no-sandbox")
driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), chrome_options=chrome_options)

#AutoScheduler on Progress
if AutoTime == True:
    driver = webdriver.Chrome(options=optionss)
    driver.get(urlpage)
    time.sleep(3)
    sessionPointer = driver.find_elements_by_xpath("//*[@class='flash-sale-session__display-hour']")
    session = []
    for sessionTime in sessionPointer:
        sessionText = sessionTime.text
        session.append(sessionText)
    fsStartTime = []
    fsStartTime = session[0]
    fsStartTime = fsStartTime[:2] + '.' + fsStartTime[3:]
    fsEndTime = session[1]
    fsEndTime = fsEndTime[:2] + '.' + fsEndTime[3:]
    nextSessionStart = session[1]
    if int(nextSessionStart[:2]) == 0:
        startTimeHr = 23
    elif int(nextSessionStart[3:]) != 0:
        startTimeHr = int(nextSessionStart[:2])
    else:
        startTimeHr = int(nextSessionStart[:2]) - 1
    
    if int(nextSessionStart[3:]) == 0:
        startTimeMin = 57
    else:
        startTimeMin = int(nextSessionStart[3:]) - 1
    driver.quit()
else:
    test=[]

#TIMER
kill = False
while kill == False:
    if skipTimer == False and initialTimer == True:
        print("Next Session Will start at: " + str(startTimeHr) + ":" + str(startTimeMin))
        while True:
            time.sleep(0.5)
            now = datetime.datetime.now()
            current_time = now.strftime("%H:%M:%S")  
            if (int(now.strftime("%H")) == startTimeHr) and (int(now.strftime("%M")) == startTimeMin):
                break
    else:
        print("Starting...")
    # Selenium
    print("Loading Selenium...")
    driver = webdriver.Firefox(options=optionss)
    print("Opening " + urlpage + "...")
    driver.get(urlpage)
    time.sleep(5)
    pageHeight = []
    pageHeight.clear()
    pageHeight.append(500)
    pageHeight.append(500)
    pageHeight.append(500)
    pageHeight.append(500)
    pageHeight.append(500)
    pageHeight.append(500)
    print("Scrolling...")
    while True:
        # Get scroll height
        pageHeight.append(driver.execute_script("return document.body.scrollHeight"))
        # Scroll down to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight-500)")
        # Wait to load page
        time.sleep(SCROLL_PAUSE_TIME)  
        if pageHeight[-1] == pageHeight[-6]:
            break

    print("Scroll Complete, page height " + str(pageHeight[-1]))

    #TIMER
    
    #FS Live & sold out class pointer
    captureTime = datetime.datetime.now()
    captureDate = date.today()
    fsLiveProducts = driver.find_elements_by_xpath("//*[@class='flash-sale-item-card flash-sale-item-card--landing-page flash-sale-item-card--ID']")
    fsSoldOut = driver.find_elements_by_xpath("//*[@class='flash-sale-item-card flash-sale-item-card--landing-page flash-sale-item-card--ID flash-sale-item-card--sold-out']")
    sessionPointer = driver.find_elements_by_xpath("//*[@class='flash-sale-session__display-hour']")
    session = []
    for sessionTime in sessionPointer:
        sessionText = sessionTime.text
        session.append(sessionText)

    fsStartTime = []
    fsStartTime = session[0]
    fsStartTime = fsStartTime[:2] + '.' + fsStartTime[3:]
    fsEndTime = session[1]
    fsEndTime = fsEndTime[:2] + '.' + fsEndTime[3:]
    nextSessionStart = session[2]

    #Next Session Timer
    if int(nextSessionStart[:2]) == 0:
        startTimeHr = 23
    elif int(nextSessionStart[3:]) != 0:
        startTimeHr = int(nextSessionStart[:2])
    else:
        startTimeHr = int(nextSessionStart[:2]) - 1
    
    if int(nextSessionStart[3:]) == 0:
        startTimeMin = 57
    else:
        startTimeMin = int(nextSessionStart[3:]) - 1
    print("Capturing flash sale for: " + str(fsStartTime) + " - " + str(fsEndTime) + " session")
    print('Number of results', len(fsLiveProducts))
    print('Number of Sold Out', len(fsSoldOut))

    print("Creating data...")
    # create empty array to store data
    data = []
    data.clear()
    i = 0
    options = Options()
    options.headless = True
    #get data for fs product that still LIVE (stock not empty)
    #if you see this, this is form of frustation. 
    print("Capturing LIVE products...")
    for result in fsLiveProducts:
        body = result.text
        splitted = body.split('\n',)
        product_name = splitted[0]
        #normal price
        normalPrice = int(re.sub(r"\D", "", splitted[1]))
        #selling price
        sellingPrice = int(re.sub(r"\D", "", splitted[2]))
        #sold at the moment
        if splitted[3] == "SEGERA HABIS":
            orders = 0
        else:
            orders = int(re.sub(r"\D", "", splitted[3]))
        #GMV
        GMV = int(orders) * int(sellingPrice)
        #Adjustment
        adjustment1 = ( float(normalPrice) - float(sellingPrice) ) * float(orders)
        adjustment = int(format(adjustment1, '.0f'))
        #Discount 
        discountPercentage1 = -((float(sellingPrice) - float(normalPrice)) / float(normalPrice)) * 100
        discountPercentage = int(format(discountPercentage1, '.0f'))
        #link
        link = result.find_element_by_tag_name('a')
        product_link = link.get_attribute("href")
        # append dict to array
        i = i + 1
        data.append({"Position" : int(i) , "SKU Name" : product_name, "Normal Price" : int(normalPrice), "Selling Price" : int(sellingPrice), "Discount (Percentage, per SKU)" : int(discountPercentage), "Total Order Item" : int(orders), "GMV" : int(GMV), "Total Adjustment (total discount given)" : int(adjustment), "link" : product_link, "FS Date": captureDate, "FS Start Session Time" : str(fsStartTime), "FS End Session Time" : str(fsEndTime), "This data is captured on: " : captureTime, "Status" : "LIVE"})
        

    print("LIVE product captured!")
    print("Capturing Sold Out data...")
    #get data for OOS product, as shopee keep it on different class
    for result in fsSoldOut:
        body = result.text
        splitted = body.split('\n',)
        product_name = splitted[0]
        #normal price
        normalPrice = int(re.sub(r"\D", "", splitted[1]))
        #selling price
        sellingPrice = int(re.sub(r"\D", "", splitted[2]))
        #sold at the moment
        orders1 = splitted[3]
        orders2=orders1.split()
        orders = re.sub(r"\D", "", orders2[0])
        #GMV
        GMV = int(orders) * int(sellingPrice)
        #Adjustment
        adjustment1 = ( float(normalPrice) - float(sellingPrice) ) * float(orders)
        adjustment = format(adjustment1, '.0f')
        #Discount 
        discountPercentage1 = -((float(sellingPrice) - float(normalPrice)) / float(normalPrice)) * 100
        discountPercentage = format(discountPercentage1, '.0f')
        #link
        link = result.find_element_by_tag_name('a')
        product_link = link.get_attribute("href")
        # append dict to array
        i = i + 1
        data.append({"Position" : int(i), "SKU Name" : product_name, "Normal Price" : int(normalPrice), "Selling Price" : int(sellingPrice), "Discount (Percentage, per SKU)" : int   (discountPercentage), "Total Order Item" : int(orders), "GMV" : int(GMV), "Total Adjustment (total discount given)" : int(adjustment), "link" : product_link, "FS Date": captureDate, "FS Start Session Time" : str(fsStartTime), "FS End Session Time" : str(fsEndTime), "This data is captured on: " : captureTime, "Status" : "SOLD OUT"})
    print("Sold Out data captured!")
        

    df = pd.DataFrame(data)
    print("Data Stored on DB")
    print("GMV = " + locale.format_string("%d", df['GMV'].sum(), grouping=True))
    print("Orders = " + locale.format_string("%d", df['Total Order Item'].sum(), grouping=True))
    print("AOV = " + locale.format_string("%d", df['GMV'].sum() / df['Total Order Item'].sum(), grouping=True))

    #export df to csv
    nameFormat = "Shopee " + str(date.today()) + ". " + str(fsStartTime) + " - " + str(fsEndTime) + ".xlsx"
    df.to_excel(nameFormat)
    print("Data stored on: " + nameFormat)
    totalItems = len(fsLiveProducts) + len(fsSoldOut)
    print(session[2])
    driver.quit()
    #Appending to master data
    print("Appending to Master Data...")
    MasterDB = pd.read_excel(r'Master DB Shopee FS.xlsx', index_col = 0)
    dfM = pd.DataFrame(MasterDB)
    dfMf = dfM.append(df, ignore_index=True)
    dfMf.to_excel('Master DB Shopee FS.xlsx')
    print("Master data appended, Total Data captured: " + str(len(dfMf)))
    if repeat == True:
        kill = False
    else:
        break