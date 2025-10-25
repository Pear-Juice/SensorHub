import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

import database as db

#SQL types
#NULL
#NUMERIC
#INTEGER
#REAL
#TEXT
#BLOB



date_dict = {"Year":"INTEGER", "Month":"INTEGER", "Day":"INTEGER", "Hour":"INTEGER", "Minute":"INTEGER", "Second":"INTEGER"}

def main():
    #_write("2025-10-11T23:24:00Z")

    db._new_hub("Greenhouse", {"Temp":"REAL", "Humidity":"REAL", "Sunlight":"TEXT"})
    
    #"2025-10-11T23:24:00Z"
    db._push_sensor_data("Greenhouse", {"Temp" : 1.0, "Humidity" : 5.0, "Day" : 1})
    db._push_sensor_data("Greenhouse", {"Temp" : 4.0, "Humidity" : 7.0, "Day" : 2})
    db._push_sensor_data("Greenhouse", {"Temp" : 10.0, "Humidity" : 7.0, "Day" : 3})
    db._push_sensor_data("Greenhouse", {"Temp" : 3.0, "Humidity" : 3.0, "Day" : 4})
    db.print_table("Greenhouse")

    temp = db._fetch_sensor_data("Greenhouse", "Temp")
    day = db._fetch_sensor_data("Greenhouse", "Day")

    #conn.commit()
    db._close_db()

    fig, ax = plt.subplots()
    ax.plot(day, temp)
    plt.show()

    #_fetch_sensor("Greenhouse", "Humidity")


if __name__ == "__main__":
    main()

