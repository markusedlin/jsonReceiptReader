import pandas as pd

path = 'C:\\Users\\msomm\\OneDrive\\Documents\\ProgProjects\\KiwiReceiptJSONReader\\'
file = "transaksjoner_kiwi.json"
df = pd.read_json(path + file)
pd.set_option("max_rows", None)

#type in date of shopping trip -> returns shopping trip
def getOneShoppingTrip(date):
    dates = df.get("dato")
    for i in range(len(dates)):
        if dates[i] == date:
            return df.get("varelinjer")[i]
            
def getOneElementFromShoppingTrip(date, elem):
    if (len(getOneShoppingTrip(date)) >= elem and 0 <= elem):
        return getOneShoppingTrip(date)[elem]


#pypi.org
# not working    df.lookup('1', 'varelinjer')

df
df.columns
df.get('dato')

for date in df.get("dato"):
    for vare in getOneShoppingTrip(date):
        print(f"Price per unit/kilo of {vare['varenavn']} on {date}: " + str(round((float(vare["vareBelop"]) / float(vare['vareAntallVekt'])),2) ) )
