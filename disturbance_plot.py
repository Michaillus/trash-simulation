import pandas as pd
import matplotlib.pyplot as plt


if __name__ == "__main__":
    # Load csv
    df = pd.read_csv('logs//crowded_street.csv')

    # Filter rows where Robot is present (Robot present == 1)
    df_robot_present = df[df['Ticks with Robot present'] == 1]

    # Count the number of rows where 'Ticks with Close Robot' is 1 and where it is 0
    robot_contact_count = (df_robot_present['Robot Disturbance'] == 2).sum()
    robot_nearby_count = (df_robot_present['Robot Disturbance'] == 1).sum()
    robot_far_count = (df_robot_present['Robot Disturbance'] == 0).sum()

    # Prepare data for the pie chart
    labels = ['Robot within 1m\nof person', 'Robot within 2.5m\nof person', 'Robot further than 2.5m\nfrom any person']
    sizes = [robot_contact_count, robot_nearby_count, robot_far_count]
    colors = ['#ff9999','#66b3ff', '#99ff99']

    # Plot the pie chart
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=315, colors=colors)

    # Set aspect ratio to make the pie chart circular
    plt.axis('equal')

    # Title for the pie chart
    plt.title('Robot Disturbance in % (When Robot is Present)')

    # Show the plot
    plt.show()
