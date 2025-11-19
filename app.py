from tkinter import *
import tkinter as tk
from tkinter import ttk

import datetime
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import database as db


update_delay = 1000
data_time_start = 180
data_time_end = 0

root = Tk()
root.title("Sensor Hub")
frm = ttk.Frame(root, padding=10)

plots = {}

def read_sensor(hub, sensor, start_offset, end_offset):
    curr_t = datetime.datetime.now().timestamp()
    return db._fetch_sensor_data(hub,sensor, curr_t - start_offset, curr_t - end_offset)


def plot_func(hub_idx, hub, sensor_idx, sensor, canvas, ax):
    sensor_data = read_sensor(hub, sensor, data_time_start, data_time_end)        

    ax.clear()
    ax.plot(range(0,len(sensor_data)), sensor_data)
    ax.set_title(f"{hub} : {sensor}")

    canvas.draw()
    
    #root.after(update_delay, lambda: plot_func(hub_idx, hub, sensor_idx, sensor, canvas, ax))

def process_hub_data():
    for hub_idx, hub in enumerate(db._get_hubs()):
        for sensor_idx, sensor in enumerate(db._get_sensors(hub)[:-1]):
            fig = Figure(figsize=(3,2), dpi=50)
            ax = fig.add_subplot()

            canvas = FigureCanvasTkAgg(fig, master=root)
            canvas_widget = canvas.get_tk_widget()
            canvas_widget.grid(row=hub_idx, column=sensor_idx, sticky="nsew")

            plots[hub + sensor] = (hub_idx, hub, sensor_idx, sensor, canvas, ax)

def update():
    for plot in plots.values():
        plot_func(plot[0], plot[1], plot[2], plot[3], plot[4], plot[5])

    root.after(update_delay, update)

def main():
    db._open_db("database")

    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)
    
    process_hub_data()
    update()

    root.mainloop()


if __name__ == "__main__":
    main()
