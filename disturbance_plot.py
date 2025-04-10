import pandas as pd
import matplotlib.pyplot as plt


if __name__ == "__main__":
    # Load csv
    df = pd.read_csv('logs//low_traffic_street.csv') # Enter csv path of your choice

    # Filter rows where Robot is present (Robot present == 1)
    df_robot_present = df[df['Ticks with Robot present'] == 1]

    # Count the number of rows where 'Ticks with Close Robot' is 1 and where it is 0
    robot_contact_count = (df_robot_present['Robot Disturbance'] == 2).sum()
    robot_nearby_count = (df_robot_present['Robot Disturbance'] == 1).sum()
    robot_far_count = (df_robot_present['Robot Disturbance'] == 0).sum()

    # Prepare data for the pie chart
    labels = ['Contact (< 1m)', 'Close (< 2.5m)', 'Distant (>= 2.5m)']
    
    sizes = [robot_contact_count, robot_nearby_count, robot_far_count]
    colors = ['#ff9999','#66b3ff', '#99ff99']


    # Plot the pie chart
    plt.pie(sizes, autopct='%1.1f%%', startangle=180, colors=colors, labels=labels, radius=0.1)
    # plt.pie(sizes, autopct='', startangle=180, colors=colors, labels=labels, radius=0.1)
    # Set aspect ratio to make the pie chart circular
    plt.axis('equal')

    # Title for the pie chart
    plt.title('Robot Disturbance')

    # Show the plot
    plt.show()
