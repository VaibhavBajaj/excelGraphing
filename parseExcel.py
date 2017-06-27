import csv
import mysql.connector
from constants import config
from constants import TABLE_TEMPLATE
from constants import PAYLOAD_TEMPLATE
from secretConstants import EXCEL_PATH
from mysql.connector import errorcode
from datetime import datetime


def create_table(dataDict):
    try:
        print("Creating table {}: ".format(dataDict['Subdomain']), end='')
        cursor.execute(TABLE_TEMPLATE.format(dataDict['Subdomain']))
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
            print("already exists.")
        else:
            print(err.msg)
    else:
        print("OK")

# Opening mysql connection
try:
    # Uses config from constants to make connection
    connection = mysql.connector.connect(**config)
except mysql.connector.Error as err:
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        print("Something is wrong with user name or password :/")
    elif err.errno == errorcode.ER_BAD_DB_ERROR:
        print("Database does not exist :(")
    else:
        print(err)
else:
    # Yipee! We connected
    cursor = connection.cursor()

    # Opening csv table to feed data
    with open(EXCEL_PATH, 'r') as weeklyInsight:
        reader = csv.DictReader(weeklyInsight)
        for dataDict in reader:
            # Creates table if not previously existing
            create_table(dataDict)

            # Changing date to %m/%d/%Y format
            to_date = dataDict['To'][:5] + "20" + dataDict['To'][5:]
            validity = False if dataDict['Disabled Today'] is 'Yes' else True
            payload_data = (
                datetime.strptime(to_date, '%m/%d/%Y'),
                dataDict['CustomerName'],
                dataDict['InternalUsers'],
                validity
            )
            cursor.execute(PAYLOAD_TEMPLATE.format(dataDict['Subdomain']), payload_data)
    connection.close()
