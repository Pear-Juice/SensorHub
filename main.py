import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

import board
import busio
from PIL import Image, ImageDraw, ImageFont, ImageOps
import digitalio
import io
import adafruit_ssd1306
import adafruit_rfm9x
import spidev
import datetime

import database as db



#SQL types
#NULL
#NUMERIC
#INTEGER
#REAL
#TEXT
#BLOB


date_dict = {"Year":"INTEGER", "Month":"INTEGER", "Day":"INTEGER", "Hour":"INTEGER", "Minute":"INTEGER", "Second":"INTEGER"}

spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
cs = digitalio.DigitalInOut(board.CE1)
reset = digitalio.DigitalInOut(board.D25)
lora = adafruit_rfm9x.RFM9x(spi, cs, reset, 915.0)
i2c = busio.I2C(board.SCL, board.SDA) 
display = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c)


def test_db():
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
    hour = get_last_n(db._fetch_sensor_data("Greenhouse", "Hour"), num_items)
    minute = get_last_n(db._fetch_sensor_data("Greenhouse", "Minute"), num_items)
    second = get_last_n(db._fetch_sensor_data("Greenhouse", "Second"), num_items)
    
    print(f"{hour}:{minute}:{second} Temp: {temperature} Humidity: {humidity} Lux:{lux} Distance: {distance}")
    
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


def parse_timestamp(timestamp):
    return {"Year" : timestamp.year, "Month" : timestamp.month, "Day" : timestamp.day, "Hour" : timestamp.hour, "Minute" : timestamp.minute, "Second" : timestamp.second}

def parse_push_data_packet(data_str):
    
    data = {}
    properties = data_str.split(",")

    for prop in properties:
        prop_parts = prop.split(":")
        sensor_name = prop_parts[0]
        sensor_data = prop_parts[1]

        data[sensor_name] = sensor_data
        
    return data


def parse_packet(packet, timestamp):
    packet_str = str(packet)[12:-3]
    #print("Parse: ", packet_str)
    packet_parts = packet_str.split(">")
    

    hub_name = packet_parts[0]
    command = packet_parts[1]
    properties = packet_parts[2]


    match command:
        case "PD": #format: Hub_Name>PD>SensorName:SensorData,SensorName:SensorData
            data = parse_push_data_packet(properties)
            db._push_sensor_data(hub_name, data, timestamp)


def start_lora_receiver():
    print("--Start receiver--")
    counter = 0
    while True:
        packet = lora.receive()
        timestamp = parse_timestamp(datetime.datetime.utcnow())

        if packet is None:
            #print(counter, ": No packet")
            pass
        else:
            try:
                parse_packet(packet, timestamp)
            except:
                print("Failed to parse data: ", packet)

            try:
                display_data()
            except:
                print("Failed to print data")

        counter += 1

def main():
    db._new_hub("Greenhouse", {"Temperature":"INTEGER", "Humidity":"REAL", "Lux":"INTEGER", "Distance":"REAL"})

    start_lora_receiver()

if __name__ == "__main__":
    main()

