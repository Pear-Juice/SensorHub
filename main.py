import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

import database as db
import receiver
import app

def test_db():
    #_write("2025-10-11T23:24:00Z")

    db._create_hub("Greenhouse", {"Temp":"REAL", "Humidity":"REAL", "Sunlight":"TEXT"})
    
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


def print_text_to_screen(text):
    # Create blank image for drawing
    image = Image.new("1", (display.width, display.height))
    draw = ImageDraw.Draw(image)

    # Load a TTF font
    font = ImageFont.load_default()  # built-in 8x8 font

    draw.text((0,0), text, font=font, fill=255)

    display.image(image)
    display.show()

def get_last_n(arr, n):
    
    if len(arr) == 0:
        return []

    count = min(n, len(arr))

    return arr[-count:]

def display_data():
    num_items = 1

    temperature = get_last_n(db._fetch_sensor_data("Greenhouse", "Temperature"), num_items)
    humidity = get_last_n(db._fetch_sensor_data("Greenhouse", "Humidity"), num_items)
    lux = get_last_n(db._fetch_sensor_data("Greenhouse", "Lux"), num_items)
    distance = get_last_n(db._fetch_sensor_data("Greenhouse", "Distance"), num_items)
    timestamp = get_last_n(db._fetch_sensor_data("Greenhouse", "Timestamp"), num_items)
    
    print(f"{timestamp} Temp: {temperature} Humidity: {humidity} Lux:{lux} Distance: {distance}")
    
    last_5 = get_last_n(db._fetch_sensor_data("Greenhouse", "Distance"), 5)

    plt.figure(figsize = (0.7,1))
    plt.plot(range(len(last_5)), last_5)
    plt.ylim(0,50)
    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=50)
    plt.close()
    buf.seek(0)

    img = Image.open(buf)
    img_resize = img.resize((display.width, display.height), Image.Resampling.LANCZOS)
    img_bw = ImageOps.invert(img_resize.convert("1"))

    display.image(img_bw)
    display.show()

def on_create_hub(hub_name, data):
    print(f"Create hub: {hub_name} {data}")

def on_push_data(hub_name, data, timestamp):
    print(f"{timestamp}: Push_data: {hub_name} {data}")

def main():
    receiver.start_lora_receiver("database", on_create_hub, on_push_data)

if __name__ == "__main__":
    main()

