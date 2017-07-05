import mysql.connector
import re
from mysql.connector import errorcode
from flask import Flask
from flask import render_template
from constants import config
from constants import COMMANDS
from datetime import datetime

app = Flask(__name__)


@app.route("/", methods=['GET'])
def default():
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
        cursor.execute(COMMANDS['Search_Recent_Valid_Users'])
        dataList = []
        for data in cursor.fetchall():
            temp = re.match('https://([-\w]+).yonyx.com/y/login/', data[1])
            targetDomain = temp.group(1)
            dataList.append([data[0], data[1], data[2], targetDomain])
            print(dataList)

        return render_template(
            'usersTable.html',
            dataList=dataList
        )


# Displays graph of user with subdomainPart in subdomain.
# Here Subdomain --> https://sample.yonyx.com/y/login/ has subdomainPart --> sample
@app.route("/<subdomainPart>", methods=['GET'])
def graph(subdomainPart):
    subdomain = "https://" + subdomainPart + ".yonyx.com/y/login/"

    customerName = 'Unknown'
    internalUsers = []
    valid = "Invalid"

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
        cursor.execute(COMMANDS['Search_By_Subdomain'].format(subdomain))
        for data in cursor.fetchall():
            customerName = data[0]
            internalUsers.append([datetime.strftime(data[1], '%m/%d/%Y'), data[2]])
            valid = "Valid" if data[3] == 1 else "Invalid"

        return render_template(
            'graphData.html',
            customerName=customerName,
            subdomain=subdomain,
            internalUsers=internalUsers,
            valid=valid
        )

if __name__ == "__main__":
    app.run(port=8080, debug=True)
