import csv
import os
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
        date = date[:6] + "20" + date[6:]
        return datetime.strptime(date, "%m/%d/%Y")


# Extracting field from dictionary. In some cases, excel-extracted dictionary does not contain field.
def extract_element(dictElement, field, file, missingFieldReported):
    if missingFieldReported[field] is True:
        return False
    try:
        return dictElement[field]
    except KeyError:
        print("Field not found in file: " + field)
        print(file)
        # Field missing has been logged. No need to log again.
        missingFieldReported[field] = True
        # Skip file if false.
        return 0

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
    for file in os.listdir(EXCEL_PATH):
        if file.endswith(".csv"):
            with open(EXCEL_PATH + file, 'r') as weeklyInsight:

                # List of dictionaries with data returned
                dictCollection = csv.DictReader(weeklyInsight)

                # A dict to keep track of whether a missing field was already reported or not
                missingFieldReported = {
                    'To': False,
                    'Subdomain': False,
                    'CustomerName': False,
                    'InternalUsers': False,
                    'Disabled Today': False,
                    'InternalIncidents': False,
                    'ExternalIncidents': False,
                    'AuthoringActivity': False,
                    'TotalActiveNodes': False
                }

                for dictElement in dictCollection:

                    # Fields required
                    toDate = extract_element(dictElement, 'To', file, missingFieldReported)
                    subdomain = extract_element(dictElement, 'Subdomain', file, missingFieldReported)
                    customerName = extract_element(dictElement, 'CustomerName', file, missingFieldReported)

                    # If any of the required fields is returned False, break out of this file.
                    if not (toDate and subdomain and customerName):
                        break

                    # Optional fields
                    internalUsers = extract_element(dictElement, 'InternalUsers', file, missingFieldReported)
                    disabledToday = extract_element(dictElement, 'Disabled Today', file, missingFieldReported)
                    internalIncidents = extract_element(dictElement, 'InternalIncidents', file, missingFieldReported)
                    externalIncidents = extract_element(dictElement, 'ExternalIncidents', file, missingFieldReported)
                    authoringActivity = extract_element(dictElement, 'AuthoringActivity', file, missingFieldReported)
                    totalActiveNodes = extract_element(dictElement, 'TotalActiveNodes', file, missingFieldReported)

                    # If optional fields aren't found, default Value --> 0
                    # For clarity, disabledToday will be 0 if not found. This won't change functionality.

                    # Changing date to %Y-%m-%d format
                    toDate = parse_date(toDate)
                    # Form of metadata:
                    # (ToDate, Subdomain, InternalUsers, InternalIncidents,
                    # ExternalIncidents, AuthoringActivity, TotalActiveNodes)
                    metadataPayload = (
                        datetime.strftime(toDate, '%Y-%m-%d'),
                        subdomain,
                        internalUsers,
                        internalIncidents,
                        externalIncidents,
                        authoringActivity,
                        totalActiveNodes
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
                            cursor.execute(COMMANDS['Insert_Metadata'], metadataPayload)
                        except mysql.connector.Error as err:
                            print("Error in inserting directory: {0}\n {1} \n {2}"
                                  .format(err.msg, customerName, file))

                    # Reset validity to true for only those companies in most recent excel doc.
                    cursor.execute(COMMANDS['Reset_Validity'], multi=True)
                    # Check company contract validity in most recent excel doc.
                    valid = 0 if disabledToday == 'Yes' else 1

                    # Check existence of directory in Table Directory
                    cursor.execute(COMMANDS['Check_Entry_Existence_Directory']
                                   .format(subdomain))

                    # When debugging, do not print fetchone().
                    # If called more than once after cursor.execute(), its value becomes None.
                    if cursor.fetchone()[0] == 0:
                        # Value is 0, so directory doesn't exist. Create it.
                        directoryPayload = (
                            customerName,
                            subdomain,
                            valid
                        )
                        try:
                            cursor.execute(COMMANDS['Insert_Directory'], directoryPayload)
                        except mysql.connector.Error as err:
                            print("Error in inserting directory: {0}\n{1}\n{2}"
                                  .format(err.msg, customerName, file))
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
