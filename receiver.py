import board
import busio
from PIL import Image, ImageDraw, ImageFont, ImageOps
import digitalio
import io
import adafruit_ssd1306
import adafruit_rfm9x
import spidev
import time

import database as db

#SQL types
#NULL
#NUMERIC
#INTEGER
#REAL
#TEXT
#BLOB


date_dict = {"Timestamp":"INTEGER"}

spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
cs = digitalio.DigitalInOut(board.CE1)
reset = digitalio.DigitalInOut(board.D25)
lora = adafruit_rfm9x.RFM9x(spi, cs, reset, 915.0)
i2c = busio.I2C(board.SCL, board.SDA) 
display = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c)

def get_timestamp():
    return {"Timestamp" : int(time.time())}


def parse_create_hub_packet(data_str):
    
    data = {}
    properties = data_str.split(",")

    for prop in properties:
        prop_parts = prop.split(":")
        sensor_name = prop_parts[0]

        sensor_data_type = ""

        match prop_parts[1]:
            case "0":
                sensor_data_type = "BOOL"
            case "1":
                sensor_data_type = "INTEGER"
            case "2":
                sensor_data_type = "REAL"
            case "3":
                sensor_data_type = "TEXT"

        data[sensor_name] = sensor_data_type
        
    return data

def parse_push_data_packet(data_str):
    
    data = {}
    properties = data_str.split(",")

    for prop in properties:
        prop_parts = prop.split(":")
        sensor_name = prop_parts[0]
        sensor_data = prop_parts[1]

        data[sensor_name] = sensor_data
        
    return data


def parse_packet(packet, create_hub_callback, push_data_callback):
    packet_str = str(packet)[12:-2]
    #print("Parse: ", packet_str)
    packet_parts = packet_str.split(">")
    
    hub_name = packet_parts[0]
    command = packet_parts[1]
    properties = packet_parts[2]
    
    match command:
        case "CH":
            data = parse_create_hub_packet(properties)
            db._create_hub(hub_name, data)
            create_hub_callback(hub_name, data)
        case "PD": #format: Hub_Name>PD>SensorName:SensorData,SensorName:SensorData
            data = parse_push_data_packet(properties)
            timestamp = get_timestamp()

            db._push_sensor_data(hub_name, data, timestamp)
            push_data_callback(hub_name, data, timestamp["Timestamp"])

def start_lora_receiver(db_name, create_hub_callback, push_data_callback):
    db._open_db(db_name)
    print("--Start receiver--")
    counter = 0
    while True:
        packet = lora.receive()

        if packet is None:
            #print(counter, ": No packet")
            pass
        else:
            #try:
            parse_packet(packet, create_hub_callback, push_data_callback)
            #except:
            #    print("Failed to parse data: ", packet)

        counter += 1
