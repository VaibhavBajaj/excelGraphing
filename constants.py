from secretConstants import PASSWORD
from secretConstants import DB_NAME

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
COMMANDS['Update_Validity_Directory'] = (
    "UPDATE Directory "
    "SET Valid = 0 "
    "WHERE Subdomain = \"{0}\""
)


config = {
    'user': USERNAME,
    'password': PASSWORD,
    'host': HOST_CONFIG,
    'database': DB_NAME
}