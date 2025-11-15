import sqlite3
import pandas as pd
import regex as re

conn = None  # Creates a new database file if it doesn’t exist
cursor = None

date_dict = {"Timestamp":"INTEGER"}

def _open_db(db_name):
    global conn
    conn = sqlite3.connect(f"{db_name}.db")
    global cursor
    cursor = conn.cursor()

def _commit_db():
    conn.commit()

def _close_db():
    conn.close()

def validate_expression(expr):
    return bool(expr) and bool(re.fullmatch(r"[a-zA-Z0-9_]+", expr))

def validate_table_name(table_name):
    if not validate_expression(table_name):
        print(f"Given table '{table_name}' name is not valid")
        return False

    return True

def validate_sensor_list(sensors):
    print("Validate ", sensors)
    for sensor in sensors:
        if not validate_expression(sensor):
            print(f"Invalid sensor name '{sensor}'")
            return False
    for sensor_type in sensors.values():
        if sensor_type == "":
            pass
    return True

def validate_sensor_data(sensor_data):
    return sensor_data

def array_to_property_list(arr):
    return f"({', '.join(arr)})"

def get_placeholder_list(count: int) -> str:
    return f"({', '.join(['?'] * count)})"

def dict_to_property_list(dict):
    property_list = []
    for item in dict:
        property_list += [f"{item} {dict[item]}"]

    return array_to_property_list(property_list)
        
def array_to_string(arr):
    return f"{', '.join(arr)}"

## Creates a new table set up to handle inputs from an array of sensors
## hub_name: String, Name of the hub to be created
## sensors: Array[String], List of sensors
def _create_hub(hub_name, sensors):
    if not validate_table_name(hub_name) or not validate_sensor_list(sensors): 
        return

    print("Create new hub: ", hub_name, " with sensors: ", sensors | date_dict)

    sensor_property_list = dict_to_property_list(sensors | date_dict)
    
    cursor.execute(f"SELECT count(*) FROM sqlite_master WHERE type='table' AND name=?", (hub_name,))
    if cursor.fetchone()[0] == 0:
        cursor.execute(f"CREATE TABLE IF NOT EXISTS {hub_name}{sensor_property_list}")
    else:
        print(f"Hub {hub_name} already exists")

def _fetch_sensor_data(hub_name, sensor_name):
    #print(f"Fetch {sensor_name} from {hub_name}")
    cursor.execute(f"SELECT {sensor_name} FROM {hub_name}")

    rows = cursor.fetchall()
    return [row[0] for row in rows]


def _push_sensor_data(hub_name, sensor_data, timestamp):
    inputs = sensor_data | timestamp

    columns = array_to_property_list(inputs.keys())
    values = array_to_property_list(list(map(str, inputs.values())))

    for column in columns:
        pass

    try:
        #print(f"Push data: {columns} into {hub_name}")
        cursor.execute(f"INSERT INTO {hub_name} {columns} VALUES {values}")
    except:
        print(f"Failed to push to hub '{hub_name}', invalid data: {sensor_data}")

def _get_pandas_hub(hub_name):
    df
    try:
        df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
        return df
    except:
        print(f"Failed to retrieve pandas dataframe from {hub_name}")
        return NULL

def print_table(table_name):
    print(f"---{table_name}---")
    df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
    print(df)
    print("------")

