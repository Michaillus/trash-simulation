import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta


if __name__ == "__main__":
    # Load csv
    df = pd.read_csv('logs//low_traffic_street.csv') # Enter csv path of your choice


    # Filter data for every 600th step (every minute)
    df_minute = df[df['Step'] % 600 == 0]

    # Start time is 6:00 AM (6:00 AM is the reference point)
    start_time = datetime.strptime('06:00 AM', '%I:%M %p')

    # Convert minutes to time format by adding to the start time
    df_minute['Time'] = df_minute['Step'] / 600
    df_minute['Time'] = df_minute['Time'].apply(lambda x: start_time + timedelta(minutes=x))

    df_minute["Amount of trash on street (No Robot)"] = df_minute["Total trash produced"]

    plt.plot(df_minute['Time'], df_minute["Amount of trash on street"], label="With Robot")
    plt.plot(df_minute['Time'], df_minute["Amount of trash on street (No Robot)"], label="Without Robot")
    # Format the x-axis to show time in HH:MM AM/PM format
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%I:%M %p'))
    plt.gca().xaxis.set_major_locator(mdates.HourLocator(interval=4))  # Show ticks every hour

    plt.legend()
    plt.ylabel('Units of Trash')
    plt.title('Amount of Trash on Low Traffic Street')
    plt.grid(True)
    plt.show()