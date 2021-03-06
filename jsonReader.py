import pandas as pd
from getpass import getpass
from mysql.connector import connect, Error
from datetime import datetime
import matplotlib.pyplot as plt

#SQL setting up database
mydb = connect(host='localhost', user='root', password=getpass("Password: "), database='kiwireceipts')
print(mydb)

cursor = mydb.cursor()

#---------CREATION-OF-TABLES-SQL----------------------


createStoreTableQuery="""CREATE TABLE store (
    storeID INT AUTO_INCREMENT NOT NULL,
    storeName VARCHAR(50),
    PRIMARY KEY (storeID),
    UNIQUE KEY (storeName)
    )"""

createReceiptTableQuery="""CREATE TABLE receipt (
    receiptID INT NOT NULL AUTO_INCREMENT,
    receiptNum INT,
    date DATE,
    totalPrice FLOAT,
    storeID INT,
    PRIMARY KEY (receiptID),
    FOREIGN KEY (storeID) REFERENCES store(storeID)
)"""

createCategoryTableQuery="""CREATE TABLE category (
    categoryID INT NOT NULL AUTO_INCREMENT,
    categoryName VARCHAR(50),
    PRIMARY KEY (categoryID),
    UNIQUE KEY (categoryName)
)"""

createItemTableQuery="""CREATE TABLE item (
        itemID INT NOT NULL AUTO_INCREMENT,
        itemName VARCHAR(50),
        itemPrice FLOAT,
        receiptID INT,
        categoryID INT,
        PRIMARY KEY (itemID),
        FOREIGN KEY (receiptID) REFERENCES receipt (receiptID),
        FOREIGN KEY (categoryID) REFERENCES category (categoryID)
    )"""

#cursor.execute("SHOW TABLES")

#results = cursor.fetchall()


#--------------------pandas---------------------------

path = 'C:\\Users\\msomm\\OneDrive\\Documents\\ProgProjects\\KiwiReceiptJSONReader\\'
file = "transaksjoner_kiwi.json"
df = pd.read_json(path + file)
pd.set_option("max_rows", None)

#-----------------------------------------------------

def createTables():
    cursor.execute(createStoreTableQuery)
    cursor.execute(createReceiptTableQuery)
    cursor.execute(createCategoryTableQuery)
    cursor.execute(createItemTableQuery)

def getStoreInStoreTable(store):
    return f"SELECT * FROM store WHERE storeName LIKE '{store}'"

def addStoresToStoreTable():
    storesList = df.get("butikknavn")
    for storeVal in storesList:
        addStoreQuery = """
        INSERT IGNORE INTO store (storeName)
        VALUES ('%s')
        """ % (storeVal)
        cursor.execute(addStoreQuery)
        mydb.commit()

def formatDate(date): #format "DD.MM.YYYY" string to "DD,MM,YYYY" string
    words = date.split(".")
    return words[0]+','+words[1]+','+words[2]
# print(formatDate("22.01.2021"))

def addReceiptsToReceiptTable():
    for i in range(len(df)):

        receiptNum = df.get("kvitteringsnummer")[i]
        date = df.get("dato")[i]
        totalPrice = "%0.2f" % (df.get("totaltBelop")[i])
        storeName = df.get("butikknavn")[i]

        addReceiptQuery = f"""
        INSERT IGNORE INTO receipt (receiptNum, date, totalPrice, storeID)
        VALUES ({receiptNum}, (SELECT STR_TO_DATE("{date}",'%d.%m.%Y')), {totalPrice}, (SELECT storeID FROM store WHERE storeName LIKE '{storeName}')) 
        """
        cursor.execute(addReceiptQuery)
        mydb.commit()

# categories
categories = {
    "Vegetable": ["brokkoli", "paprika rød", "potet", "agurk",
 "asparges", "blomkål", "champignon", "salat", "erter", "gulrot",
  "hvitløk", "kikerter", "løk", "mais", "ruccula", "spinat",
   "squash", "tomater", "pastinakk"],

  "Dairy": ["cheese", "melk", "yoghurt", "jarlsberg", "norvegia", "rømme", "gudbrandsdalsost", "philadelphia"],

  "Fruit" : ["bananer", "druer", "eple", "jordbær", "pære", "sitron", "nektarin"], 

  "Meat" : ["kjøtt", "laks", "fisk", "hamburger"], 

  "Snack": ["cookies", "sjokolade", "saltstenger", "smågodt",
   "chips", "bixit", "lefsegodt", "mellombar", "smash", "after eight"],

   "Drink" : ["pepsi", "cider", "mylk"],

  "Bread" : ["brød", "hverdagsgrovt", "pizzabunn", "rundstykke", "baguette", "tortilla", "spaghetti", "penne"],

  "Baking" : ["margarin", "gjær", "sukker", "sirup", "hvetemel", "olje"],

  "Home" : ["colgate", "nivea", "serviett", "bakepapir", "jif", "palmolive"],

  "Grains/Nut" : ["frø", "mandler", "nøtter", "havregryn", "musli", "kornris"],

  "Condiment" : ["kaviar", "sauce", "saus", "syltetøy", "nugatti", "pesto", "salsa", "peanutbutter"]
  }

def getCategory(str):
    for c in categories:
        lenItemsPerCategory = len(categories[c])
        for itemIndex in range(lenItemsPerCategory):
            if categories[c][itemIndex] in str.lower():
                return c

def addItemToItemTable():
    for receipt in range(len(df)):
        receiptNum = int(df.get("kvitteringsnummer")[receipt])
        for item in df.get("varelinjer")[receipt]:
            itemName = item.get("varenavn")
            itemPrice = "%0.2f" % (float(item.get("vareBelop")) / float(item.get("vareAntallVekt")))
            addItemsQuery = f"""
            INSERT INTO item (itemName, itemPrice, receiptID, categoryID)
            VALUES (
                '{itemName}', 
                {itemPrice}, 
                (SELECT receiptID FROM receipt WHERE receiptNum = {receiptNum}),
                (SELECT categoryID FROM category WHERE categoryName LIKE '{getCategory(itemName)}')
            )"""
            cursor.execute(addItemsQuery)
            mydb.commit()

def updateCategoriesInItemTable():
    for receipt in range(len(df)):
        for item in df.get("varelinjer")[receipt]:
            itemName = item.get("varenavn")
            addItemsQuery = f"""
            UPDATE item
            SET categoryID = (SELECT categoryID FROM category WHERE categoryName LIKE '{getCategory(itemName)}')
            WHERE itemName LIKE '{itemName}'
            """
            cursor.execute(addItemsQuery)
            mydb.commit()

def addCategoriesToCategoryQuery():
    for c in categories:
        addCategoryQuery = f"""
        INSERT IGNORE INTO category (categoryName)
        VALUES ('{c}')
        """
        cursor.execute(addCategoryQuery)
        mydb.commit()
# createTables() #done
# addStoresToStoreTable() # done
# addReceiptsToReceiptTable() # done
# addCategoriesToCategoryQuery() # done
# addItemToItemTable() # done
# updateCategoriesInItemTable() # done

def plotByStoreNameAndCategory(storeName, category): #storeName ex: 'kiwi', 'meny', "" for all stores.. category ex: 'vegetable'
    testGraphQuery = f"""
    SELECT item.itemName, item.itemPrice, receipt.date
    FROM item 
    JOIN receipt ON item.receiptID = receipt.receiptID
    JOIN store ON receipt.storeID = store.storeID
    JOIN category ON item.categoryID = category.categoryID
    WHERE category.categoryName LIKE '{category}' AND store.storeName LIKE '%{storeName}%'
    ORDER BY item.itemName, receipt.date
    """
    cursor.execute(testGraphQuery)
    results = cursor.fetchall()
    items = {}
    #adding all items to dictionary with list of (price,date)
    for (itemName, price, date) in results:
        items.setdefault(itemName, []).append((price, date))
    #iterating through items -> putting prices and dates in list to then graph
    for item in items:
        prices = []
        dates = []
        for (price, date) in items.get(item):
            prices.append(price)
            dates.append(date)
        if(len(dates)>2):
            plt.plot(dates, prices, label=item)
    # plotting
    plt.title(f"Prices of {category} in {storeName}")
    plt.xlabel("Date")
    plt.ylabel("Price in NOK")
    plt.grid()
    plt.legend()
    plt.show()
    
plotByStoreNameAndCategory("", "vegetable")


#exceptions: 
# bringebær - 400g vs syltetøy, 
# paprika - spansk paprika vs paprika rød
# tomat - tomatketchup vs tomater vs tomatbønner
# cheese - tortilla chips cheese vs cheese