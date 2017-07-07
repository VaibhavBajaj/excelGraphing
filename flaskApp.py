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
            subdomainPart = temp.group(1)

            # For clarity, I am giving names to data array numbers
            customerName = data[0]
            subdomain = data[1]
            internalUsers = data[2]
            internalUserLink = 'http://127.0.0.1:8080/' + subdomainPart + '/InternalUsers/'
            # data[3] = Internal incidents, data[4] = External Incidents
            totalIncidents = data[3] + data[4]
            totalIncidentsLink = 'http://127.0.0.1:8080/' + subdomainPart + '/TotalIncidents/'
            authoringActivity = data[5]
            authoringActivityLink = 'http://127.0.0.1:8080/' + subdomainPart + '/AuthoringActivity/'
            totalActiveNodes = data[6]
            totalActiveNodesLink = 'http://127.0.0.1:8080/' + subdomainPart + '/TotalActiveNodes/'
            dataList.append([
                customerName,
                subdomain,
                internalUsers,
                internalUserLink,
                totalIncidents,
                totalIncidentsLink,
                authoringActivity,
                authoringActivityLink,
                totalActiveNodes,
                totalActiveNodesLink
            ])

        return render_template(
            'usersTable.html',
            dataList=dataList
        )


# Displays graph of user with subdomainPart in subdomain.
# Here Subdomain --> https://sample.yonyx.com/y/login/ has subdomainPart --> sample
@app.route("/<subdomainPart>/<field>/", methods=['GET'])
def graph(subdomainPart, field):
    subdomain = "https://" + subdomainPart + ".yonyx.com/y/login/"

    customerName = 'Unknown'
    dataList = []
    secondaryDataList = []
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
        if (field != 'TotalIncidents'):
            cursor.execute(COMMANDS['Search_By_Subdomain'].format(subdomain, field))
            for data in cursor.fetchall():
                customerName = data[0]
                dataList.append([datetime.strftime(data[1], '%m/%d/%Y'), data[2]])
                valid = "Valid" if data[3] == 1 else "Invalid"
        else:
            cursor.execute(COMMANDS['Search_By_Subdomain'].format(subdomain, 'InternalIncidents'))
            for data in cursor.fetchall():
                customerName = data[0]
                dataList.append([datetime.strftime(data[1], '%m/%d/%Y'), data[2]])
                valid = "Valid" if data[3] == 1 else "Invalid"
            cursor.execute(COMMANDS['Search_By_Subdomain'].format(subdomain, 'ExternalIncidents'))
            for data in cursor.fetchall():
                secondaryDataList.append(data[2])

            for i in range(len(secondaryDataList)):
                dataList[i][1] += secondaryDataList[i]

        return render_template(
            'graphData.html',
            customerName=customerName,
            subdomain=subdomain,
            field=field,
            dataList=dataList,
            valid=valid
        )

if __name__ == "__main__":
    app.run(port=8080, debug=True)
