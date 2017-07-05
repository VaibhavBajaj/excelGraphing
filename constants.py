from secretConstants import DB_NAME
from secretConstants import PASSWORD

USERNAME = 'root'
HOST_CONFIG = '127.0.0.1'

TABLE_TEMPLATE = dict()
TABLE_TEMPLATE['Directory'] = (
    "CREATE TABLE Directory ("
    "  CustomerName VARCHAR(100) NOT NULL,"
    "  Subdomain VARCHAR(120) NOT NULL,"
    "  Valid BOOLEAN NOT NULL,"
    "  PRIMARY KEY (Subdomain)"
    ");"
)
TABLE_TEMPLATE['Metadata'] = (
    "CREATE TABLE Metadata ("
    "  Id INTEGER(11) NOT NULL AUTO_INCREMENT,"
    "  ToDate DATE NOT NULL,"      # Please see that "To_Date" is different from the excel field "To"
    "  InternalUsers INTEGER(11) NOT NULL,"
    "  Subdomain VARCHAR(120) NOT NULL,"
    "  PRIMARY KEY (Id)"
    ");"
)

COMMANDS = dict()

# COMMAND list to push data to MySQL database.
# Check entry existence
COMMANDS['Check_Entry_Existence_Directory'] = (
    "SELECT EXISTS("
    "SELECT * "
    "FROM Directory "
    "WHERE Subdomain = \"{0}\""
    ");"
)
COMMANDS['Check_Entry_Existence_Metadata'] = (
    "SELECT EXISTS("
    "SELECT * "
    "FROM Metadata "
    "WHERE Subdomain = \"{0}\" AND ToDate = \"{1}\""
    ");"
)

# Insert entry
COMMANDS['Insert_Directory'] = (
    "INSERT INTO Directory "
    "(CustomerName, Subdomain, Valid) "
    "VALUES (%s, %s, %s)"
)
COMMANDS['Insert_Metadata'] = (
    "INSERT INTO Metadata "
    "(ToDate, InternalUsers, Subdomain) "
    "VALUES (%s, %s, %s)"
)

# Update certain field in entry
COMMANDS['Update_Validity_Directory'] = (
    "UPDATE Directory "
    "SET Valid = 0 "
    "WHERE Subdomain = \"{0}\""
)


# Command list to pull data from MySQL database
# Searches an entry by subdomain returning customerName, toDate, internalUsers, validity
COMMANDS['Search_By_Subdomain'] = (
    "SELECT Directory.CustomerName, Metadata.ToDate, Metadata.InternalUsers, Directory.Valid "
    "FROM Directory "
    "JOIN Metadata "
    "ON Directory.Subdomain = Metadata.Subdomain "
    "WHERE Directory.Subdomain = \"{0}\" "
    "ORDER BY Metadata.ToDate ASC"
)

# Extracts all valid users present in most recent excel document
COMMANDS['Search_Recent_Valid_Users'] = (
    "SELECT Directory.CustomerName, Directory.Subdomain, Metadata.InternalUsers "
    "FROM Directory "
    "JOIN Metadata "
    "ON Directory.Subdomain = Metadata.Subdomain "
    "WHERE Directory.Valid = 1 "
    "AND Metadata.ToDate = (SELECT MAX(ToDate) FROM Metadata) "
    "ORDER BY Metadata.InternalUsers DESC;"
)

config = {
    'user': USERNAME,
    'password': PASSWORD,
    'host': HOST_CONFIG,
    'database': DB_NAME
}