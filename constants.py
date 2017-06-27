from secretConstants import PASSWORD

USERNAME = 'root'
HOST_CONFIG = '127.0.0.1'
DB_NAME = 'yonyx_project'

TABLE_TEMPLATE = (
    "  CREATE TABLE {0} ("
    "'To' DATE NOT NULL,"
    "'CustomerName' VARCHAR(40) NOT NULL,"
    "'InternalUsers' INT(11) NOT NULL,"
    "'Valid' BOOLEAN NOT NULL"
    ") ENGINE=InnoDB"
)

PAYLOAD_TEMPLATE = (
    "INSERT INTO {0}"
    "(to_date, customer_name, internal_users, validity)"
    "VALUES (%s, %s, %s, %s)"
)

config = {
    'user': USERNAME,
    'password': PASSWORD,
    'host': HOST_CONFIG,
    'database': DB_NAME
}