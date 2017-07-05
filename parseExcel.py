import csv
from datetime import datetime

import mysql.connector
from mysql.connector import errorcode

from constants import COMMANDS
from constants import TABLE_TEMPLATE
from constants import config
from secretConstants import EXCEL_PATH


def create_table():
    for name, cmd in TABLE_TEMPLATE.items():
        try:
                print("Creating table {0}: ".format(name))
                cursor.execute(cmd)
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                print("already exists.")
            else:
                print(err.msg)
        else:
            print("OK")


# Date is in two formats
def parse_date(date):
    try:
        return datetime.strptime(date, "%m-%d-%Y")
    except ValueError:
        date = date[:5] + "20" + date[5:]
        return datetime.strptime(date, "%m/%d/%Y")


# Extracting field from dictionary. In some cases, excel-extracted dictionary does not contain field.
def extract_element(dictElement, field, fileNo):
    try:
        return dictElement[field]
    except KeyError:
        print("Could not find field: " + field)
        print(EXCEL_PATH.format(fileNo))
        # Skip file if false.
        return False

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
    print("MySQL connection successful.")
    cursor = connection.cursor(buffered=True)
    # Creates table if not previously existing
    create_table()

    # Opening csv table to feed data
    for num in range(1,53):
        with open(EXCEL_PATH.format(num), 'r') as weeklyInsight:
            # List of dictionaries with data returned
            dictCollection = csv.DictReader(weeklyInsight)

            for dictElement in dictCollection:
                # Fields needed
                toDate = extract_element(dictElement, 'To', num)
                internalUsers = extract_element(dictElement, 'InternalUsers', num)
                subdomain = extract_element(dictElement, 'Subdomain', num)
                customerName = extract_element(dictElement, 'CustomerName', num)
                disabledToday = extract_element(dictElement, 'Disabled Today', num)

                # If any of the fields is returned False, break out of this file.
                if not (toDate and internalUsers and subdomain and customerName):
                    break

                if (customerName == 'Excelacom'):
                    print (EXCEL_PATH.format(num))

                # Changing date to %Y-%m-%d format
                toDate = parse_date(toDate)
                metadata_payload = (
                    datetime.strftime(toDate, '%Y-%m-%d'),
                    internalUsers,
                    subdomain
                )

                # Check existence of metadata in Table Metadata
                cursor.execute(COMMANDS['Check_Entry_Existence_Metadata']
                               .format(subdomain, datetime.strftime(toDate, '%Y-%m-%d')))

                # When debugging, do not print fetchone().
                # If called more than once after cursor.execute(), its value becomes None.
                if cursor.fetchone()[0] == 0:
                    # Metadata doesn't already exist in database
                    # Insert metadata into table Metadata
                    try:
                        cursor.execute(COMMANDS['Insert_Metadata'], metadata_payload)
                    except mysql.connector.Error as err:
                        print("Error in inserting metadata: {0}".format(err.msg))
                        print(customerName)
                        print(EXCEL_PATH.format(num))

                # Check existence of directory in Table Directory
                cursor.execute(COMMANDS['Check_Entry_Existence_Directory']
                               .format(subdomain))

                # Checking company contract validity.
                valid = 0 if disabledToday == 'Yes' else 1

                if cursor.fetchone()[0] == 0:
                    directory_payload = (
                        customerName,
                        subdomain,
                        valid
                    )
                    try:
                        cursor.execute(COMMANDS['Insert_Directory'], directory_payload)
                    except mysql.connector.Error as err:
                        print("Error in inserting directory: {0}".format(err.msg))
                        print(customerName)
                        print(EXCEL_PATH.format(num))
                else:
                    # Subdomain directory already exists
                    if valid == 0:
                        # If subdomain directory exists and validity has become False
                        # (only happens once), update validity of existing directory to False
                        cursor.execute(COMMANDS['Update_Validity_Directory']
                                       .format(subdomain))

    # Committing data added
    connection.commit()

    # Destroying cursors
    cursor.close()
    connection.close()
