import csv
import mysql.connector
from constants import config
from constants import TABLE_TEMPLATE
from constants import COMMANDS
from secretConstants import EXCEL_PATH
from mysql.connector import errorcode
from datetime import datetime


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
    cursor = connection.cursor(buffered = True)

    # Opening csv table to feed data
    with open(EXCEL_PATH, 'r') as weeklyInsight:
        # List of dictionaries with data returned
        dictCollection = csv.DictReader(weeklyInsight)
        # Creates table if not previously existing
        create_table()

        for dictElement in dictCollection:
            # Changing date to %m/%d/%Y format
            to_date = dictElement['To'][:5] + "20" + dictElement['To'][5:]
            to_date = datetime.strptime(to_date, '%m/%d/%Y')
            metadata_payload = (
                datetime.strftime(to_date, '%Y-%m-%d'),
                dictElement['InternalUsers'],
                dictElement['Subdomain']
            )

            # Check existence of metadata in Table Metadata
            cursor.execute(COMMANDS['Check_Entry_Existence_Metadata']
                           .format(dictElement['Subdomain'], datetime.strftime(to_date, '%Y-%m-%d')))

            # When debugging, do not print fetchone().
            # If called more than once after cursor.execute(), its value becomes None.
            if cursor.fetchone()[0] == 0:
                # Metadata doesn't already exist in database
                # Insert metadata into table Metadata
                try:
                    cursor.execute(COMMANDS['Insert_Metadata'], metadata_payload)
                except mysql.connector.Error as err:
                    print("Error in inserting metadata: {0}".format(err.msg))

            # Check existence of directory in Table Directory
            cursor.execute(COMMANDS['Check_Entry_Existence_Directory']
                           .format(dictElement['Subdomain']))

            # Checking company contract validity.
            valid = 0 if dictElement['Disabled Today'] == 'Yes' else 1

            if cursor.fetchone()[0] == 0:
                directory_payload = (
                    dictElement['CustomerName'],
                    dictElement['Subdomain'],
                    valid
                )
                try:
                    cursor.execute(COMMANDS['Insert_Directory'], directory_payload)
                except mysql.connector.Error as err:
                    print("Error in inserting directory: {0}".format(err.msg))
            else:
                # Subdomain directory already exists
                if valid == 0:
                    # If subdomain directory exists and validity has become False
                    # (only happens once), update validity of existing directory to False
                    cursor.execute(COMMANDS['Update_Validity_Directory']
                                   .format(dictElement['Subdomain']))

    # Committing data added
    connection.commit()

    cursor.close()
    connection.close()
