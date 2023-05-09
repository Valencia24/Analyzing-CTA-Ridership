# Daniel Valencia
# Analyzing CTA2 L data using Python & SQL
#
# This program inputs commands from the user and outputs data from the
# CTA2 L daily ridership database. It begins by outputting basic stats
# retrieved from the database and allows for commands 1 - 9 to be inputted
# for more information or 'x' to exit the program. If any other input is
# read, the program will output an error message.

import sqlite3
import matplotlib.pyplot as plt


# print_stats
#
# Performs multiple queries to retrieve various statistics about the database
def print_stats(dbConn):
    dbCursor = dbConn.cursor()

    print("General stats:")

    # Query to retrieve total stations
    sql = "Select count(*) From Stations;"
    dbCursor.execute(sql)
    row = dbCursor.fetchone()
    print("  # of stations:", f"{row[0]:,}")

    # Query to retrieve total stops
    sql = "Select count(*) From Stops;"
    dbCursor.execute(sql)
    row = dbCursor.fetchone()
    print("  # of stops:", f"{row[0]:,}")

    # Query to retrieve total ride entries
    sql = "Select count(*) From Ridership;"
    dbCursor.execute(sql)
    row = dbCursor.fetchone()
    print("  # of ride entries:", f"{row[0]:,}")

    # Query to retrieve date range of the data
    sql = "Select min(date(Ride_Date)), max(date(Ride_Date)) From Ridership"
    dbCursor.execute(sql)
    date_rows = dbCursor.fetchall()
    print("  date range:", end=" ")
    for row in date_rows:
        print(row[0], "-", end=" ")
        print(row[1])

    # Query to retrieve total ridership
    sql = "Select sum(Num_Riders) From Ridership;"
    dbCursor.execute(sql)
    row = dbCursor.fetchone()
    total_riders = row[0]
    print("  Total ridership:", f"{row[0]:,}")

    # Query to retrieve total ridership on weekdays
    sql = "Select sum(Num_Riders) From Ridership Where Type_Of_Day = ?;"
    dbCursor.execute(sql, 'W')
    row = dbCursor.fetchone()
    percentage = (row[0] / total_riders) * 100
    print("  Weekday ridership:", f"{row[0]:,}", f"({percentage:.2f}%)")

    # Query to retrieve total ridership on saturdays
    sql = "Select sum(Num_Riders) From Ridership Where Type_Of_Day = ?;"
    dbCursor.execute(sql, 'A')
    row = dbCursor.fetchone()
    percentage = (row[0] / total_riders) * 100
    print("  Saturday ridership:", f"{row[0]:,}", f"({percentage:.2f}%)")

    # Query to retrieve total ridership on sundays/holidays
    sql = "Select sum(Num_Riders) From Ridership Where Type_Of_Day = ?;"
    dbCursor.execute(sql, 'U')
    row = dbCursor.fetchone()
    percentage = (row[0] / total_riders) * 100
    print("  Sunday/holiday ridership:", f"{row[0]:,}", f"({percentage:.2f}%)")


# total_riders
#
# Helper function
# Performs query that returns the total number of riders from all the stations combined
def total_riders(dbConn):
    dbCursor = dbConn.cursor()
    dbCursor.execute("Select sum(Num_Riders) From Ridership;")
    row = dbCursor.fetchone()
    total_riders = row[0]
    return total_riders


# command_one
#
# Performs query that retrieves station id and station name for all stations
# that match pattern inputted by user. If none are found, error message printed instead.
def command_one(dbConn):
    prompt = "Enter partial station name (wildcards _ and %): "
    user_input = input(prompt)
    sql = """Select Station_ID, Station_Name
    From Stations Where Station_Name like ?
    Group By Station_Name Order By Station_Name asc;"""

    dbCursor = dbConn.cursor()
    dbCursor.execute(sql, [user_input])
    stations = dbCursor.fetchall()

    # Check if no stations match user input
    if len(stations) == 0:
        print("**No stations found...")
        return

    for s in stations:
        stationid = s[0]
        stationname = s[1]
        print(stationid, ":", stationname)


# command_two
#
# Performs SQL query that joins two tables to retrieve the total ridership at each
# station. This information is printed along with the % based on total ridership of all the stations combined.
def command_two(dbConn):
    print("** ridership all stations **")
    sql = """Select Station_Name, sum(Num_Riders)
    From Stations Left Join Ridership on
    Stations.Station_ID = Ridership.Station_ID
    Group By Station_Name Order By Station_Name asc;"""

    dbCursor = dbConn.cursor()
    dbCursor.execute(sql)
    stations = dbCursor.fetchall()

    for s in stations:
        stationname = s[0]
        ridership = s[1]
        percentage = (ridership / total_riders(dbConn)) * 100
        print(stationname, ":", f"{ridership:,}", f"({percentage:.2f}%)")


# command_three
#
# Performs SQL query that joins two tables to retrieve the top 10 busiest
# stations. The station name, total riders and the % based on
# total ridership of all the stations combined is printed.
def command_three(dbConn):
    print("** top-10 stations **")
    sql = """Select Station_Name, sum(Num_Riders)
    From Stations Inner Join Ridership on
    Stations.Station_ID = Ridership.Station_ID
    Group By Station_Name Order By sum(Num_Riders)
    desc Limit 10;"""

    dbCursor = dbConn.cursor()
    dbCursor.execute(sql)
    stations = dbCursor.fetchall()

    for s in stations:
        stationname = s[0]
        ridership = s[1]
        percentage = (ridership / total_riders(dbConn)) * 100
        print(stationname, ":", f"{ridership:,}", f"({percentage:.2f}%)")


# command_four
#
# Performs SQL query that joins two tables to retrieve the least 10 busiest
# stations. The station name, total riders and the % based on
# total ridership of all the stations combined is printed.
def command_four(dbConn):
    print("** least-10 stations **")
    sql = """Select Station_Name, sum(Num_Riders)
    From Stations Inner Join Ridership on
    Stations.Station_ID = Ridership.Station_ID
    Group By Station_Name Order By sum(Num_Riders)
    asc Limit 10;"""

    dbCursor = dbConn.cursor()
    dbCursor.execute(sql)
    stations = dbCursor.fetchall()

    for s in stations:
        stationname = s[0]
        ridership = s[1]
        percentage = (ridership / total_riders(dbConn)) * 100
        print(stationname, ":", f"{ridership:,}", f"({percentage:.2f}%)")


# command_five
#
# Performs SQL query that joins three tables to retrieve stop details based on the
# line color that matches the user's input. The stop name,
# direction, and accessibility is printed if a match is found.
def command_five(dbConn):
    prompt = "Enter a line color (e.g. Red or Yellow): "
    user_input = input(prompt)

    sql = """Select Stop_Name, Direction, ADA From
    Stops Inner Join StopDetails on Stops.Stop_ID = 
    StopDetails.Stop_ID Inner Join Lines on StopDetails.Line_ID = Lines.Line_ID Where Color like ?
    Order By Stop_Name asc;"""

    dbCursor = dbConn.cursor()
    dbCursor.execute(sql, [user_input])
    stops = dbCursor.fetchall()

    # Check if user input matches line color
    if len(stops) == 0:
        print("**No such line...")
        return

    for s in stops:
        stopname = s[0]
        direction = s[1]
        ada = s[2]

        if ada == 0:
            str_ada = "no"
        elif ada == 1:
            str_ada = "yes"

        print(stopname, ":",
            "direction = {}".format(direction),
            "(accessible? {})".format(str_ada))


# command_six
#
# Performs SQL query that retrieves total ridership by month. If necessary,
# plot is printed out as well.
def command_six(dbConn):
    print("** ridership by month **")
    sql = """Select strftime('%m', Ride_Date) as Month,
    sum(Num_Riders) From Ridership Where Month >= '01'
    And Month <= '12' Group By Month Order By Month asc;"""

    dbCursor = dbConn.cursor()
    dbCursor.execute(sql)
    rows = dbCursor.fetchall()

    for r in rows:
        month = r[0]
        riders = r[1]
        print(month, ":", f"{riders:,}")

    # Plot only printed when user inputs 'y'
    print()
    prompt = "Plot? (y/n) "
    user_input = input(prompt)
    if user_input == "y":
        plt.close('all')
        x = []
        y = []
        for r in rows:
            month = r[0]
            x.append(month)
            y.append(r[1])
        plt.xlabel("month")
        plt.ylabel("number of riders (x*10^8)")
        plt.title("monthly ridership")
        plt.plot(x, y)
        plt.show()
    else:
        return

# command_seven
#
# Performs SQL query that retrieves total ridership by year. If necessary,
# plot is printed out as well.
def command_seven(dbConn):
    print("** ridership by year **")
    sql = """Select strftime('%Y', Ride_Date) as Year,
    sum(Num_Riders) From Ridership Where Year >= '2001' And
    Year <= '2021' Group By Year Order By Year asc;"""

    dbCursor = dbConn.cursor()
    dbCursor.execute(sql)
    rows = dbCursor.fetchall()

    for r in rows:
        year = r[0]
        riders = r[1]
        print(year, ":", f"{riders:,}")

    # Plot only printed when user inputs 'y'
    print()
    prompt = "Plot? (y/n) "
    user_input = input(prompt)
    if user_input == "y":
        plt.close('all')
        x = []
        y = []
        for r in rows:
            year = r[0]
            x.append(year[2:])
            y.append(r[1])
        plt.xlabel("year")
        plt.ylabel("number of riders (x*10^8)")
        plt.title("yearly ridership")
        plt.plot(x, y)
        plt.show()
    else:
        return


# check_num_stations
#
# Checks how many stations were returned by a sql query
def check_num_stations(stations):
    is_error = False

    if len(stations) == 0:
        print("**No station found...")
        is_error = True
    elif len(stations) > 1:
        print("**Multiple stations found...")
        is_error = True

    return is_error

# retrieve_name_id
#
# Performs sql query that retrieves station name and id based on
# name passed in. returns station list
def retrieve_name_id(dbConn, name):
    sql = """Select Station_ID, Station_Name
    From Stations Where Station_Name like ?
    Group By Station_Name;"""

    dbCursor = dbConn.cursor()
    dbCursor.execute(sql, [name])
    stations = dbCursor.fetchall()

    return stations


# retrieve_date_riders
#
# Performs sql query that retrieves date and daily num of riders
# for specific year and station based on year and station name
# passed in. returns list of dates and riders
def retrieve_date_riders(dbConn, name, year):
    sql = """Select date(Ride_Date), Num_Riders
    From Ridership Inner Join Stations On
    Ridership.Station_ID = Stations.Station_ID
    Where Station_Name like ? and
    strftime('%Y', Ride_Date) like ? Order By
    Ride_Date asc;"""

    dbCursor = dbConn.cursor()
    dbCursor.execute(sql, [name, year])
    rows = dbCursor.fetchall()

    return rows

# print_first_last_five
#
# Prints the first and last 5 rows of a list passed in
def print_first_last_five(rows):
    for row in rows[:5]:
        day = row[0]
        riders = row[1]
        print(day, riders)

    for row in rows[-5:]:
        day = row[0]
        riders = row[1]
        print(day, riders)


# retrieve_name
#
# Performs sql query to retrieve the station name based on
# user input passed in. Returns the station name
def retrieve_name(dbConn, name):
    sql = """Select Station_Name From Stations
    Where Station_Name like ?"""

    dbCursor = dbConn.cursor()
    dbCursor.execute(sql, [name])
    row = dbCursor.fetchone()
    station = row[0]

    return station

# command_eight
#
# Performs SQL query that retrieves daily ridership for the first and last 5 days of
# a specific year for two user inputted stations. The resulting data can be plotted if desired.
def command_eight(dbConn):
    # User prompt for year
    print()
    year_prompt = "Year to compare against? "
    user_year = input(year_prompt)
    print()

    # User prompt for first station
    stat_one = "Enter station 1 (wildcards _ and %): "
    user_stat_one = input(stat_one)

    # Query to grab first station name and ID based on user input
    first_stations = retrieve_name_id(dbConn, user_stat_one)

    # Check if 0 or more than 1 stations were found
    if check_num_stations(first_stations):
        return

    # User prompt for second station
    print()
    stat_two = "Enter station 2 (wildcards _ and %): "
    user_stat_two = input(stat_two)

    # Query to grab second station name and ID based on user input
    second_stations = retrieve_name_id(dbConn, user_stat_two)

    # Check if 0 or more than 1 stations were found
    if check_num_stations(second_stations):
        return

    # Query for first station's daily stats
    for s in first_stations:
        stationid = s[0]
        stationname = s[1]
        print("Station 1:", stationid, stationname)

    # Print first and last 5 days
    date_rows = retrieve_date_riders(dbConn, user_stat_one, user_year)
    print_first_last_five(date_rows)

    # Query for second station's daily stats
    for s in second_stations:
        stationid = s[0]
        stationname = s[1]
        print("Station 2:", stationid, stationname)

    # Print first and last 5 days
    date_two_rows = retrieve_date_riders(dbConn, user_stat_two, user_year)
    print_first_last_five(date_two_rows)

    # Plot only when user inputs 'y'
    print()
    plot_prompt = "Plot? (y/n) "
    plot_input = input(plot_prompt)
    if plot_input == "y":
        plt.close('all')
        x = []
        y1 = []
        y2 = []
        day = 1
        count_one = 0
        count_two = 0

        # Get number of riders per day for each station
        for d in date_rows:
            y1.append(d[1])
            count_one += 1

        for d in date_two_rows:
            y2.append(d[1])
            count_two += 1

        # Get days for x-axis based on whichever year has more days
        total_days = max(count_one, count_two)
        while day <= total_days:
            x.append(day)
            day += 1

        # Get names for legend
        stat_one = retrieve_name(dbConn, user_stat_one)
        stat_two = retrieve_name(dbConn, user_stat_two)

        plt.xlabel("day")
        plt.ylabel("number of riders")
        plt.title("riders each day of " + user_year)
        plt.plot(x, y1)
        plt.plot(x, y2)
        plt.legend([stat_one, stat_two])
        plt.show()
    else:
        return


# command_nine
#
# Performs SQL query that joins 4 tables together to retrieve station names belonging
# to a line color matching the user's input. Plot is printed out if necessary.
def command_nine(dbConn):
    prompt = "Enter a line color (e.g. Red or Yellow): "
    user_input = input(prompt)

    sql = """Select Distinct Stations.Station_Name, Stops.Latitude,
    Stops.Longitude From Stations Inner Join Stops on 
    Stations.Station_ID = Stops.Station_ID Inner Join StopDetails on
    Stops.Stop_ID = StopDetails.Stop_ID Inner Join Lines
    on StopDetails.Line_ID = Lines.Line_ID Where Color like ?
    Order By Station_Name asc;"""

    dbCursor = dbConn.cursor()
    dbCursor.execute(sql, [user_input])
    stations = dbCursor.fetchall()

    # Check if line color matches input
    if len(stations) == 0:
        print("**No such line...")
        return
    else:
        for s in stations:
            stationname = s[0]
            lat = s[1]
            lon = s[2]
            print(stationname, ":", "({}, {})".format(lat, lon))

    # Plot only printed when user inputs 'y'
    print()
    plot_prompt = "Plot? (y/n) "
    plot_input = input(plot_prompt)
    if plot_input == "y":
        plt.close('all')
        x = []
        y = []
        for s in stations:
            lat = s[1]
            lon = s[2]
            x.append(lon)
            y.append(lat)
        image = plt.imread("chicago.png")
        xydims = [-87.9277, -87.5569, 41.7012, 42.0868]
        plt.imshow(image, extent=xydims)
        plt.title(user_input + " line")
        if user_input.lower() == "purple-express":
            user_input = "Purple"
        plt.plot(x, y, "o", c=user_input)

        for s in stations:
            stationname = s[0]
            lat = s[1]
            lon = s[2]
            plt.annotate(stationname, (lon, lat))

        plt.xlim([-87.9277, -87.5569])
        plt.ylim([41.7012, 42.0868])
        plt.show()
    else:
        return


# main
print('** Welcome to CTA L analysis app **')
print()

dbConn = sqlite3.connect('CTA2_L_daily_ridership.db')

print_stats(dbConn)
print()
prompt = "Please enter a command (1-9, x to exit): "
command = input(prompt)

# Command Prompts
while command != "x":
    if command == "1":
        print()
        command_one(dbConn)
        print()
    elif command == "2":
        command_two(dbConn)
        print()
    elif command == "3":
        command_three(dbConn)
        print()
    elif command == "4":
        command_four(dbConn)
        print()
    elif command == "5":
        print()
        command_five(dbConn)
        print()
    elif command == "6":
        command_six(dbConn)
        print()
    elif command == "7":
        command_seven(dbConn)
        print()
    elif command == "8":
        command_eight(dbConn)
        print()
    elif command == "9":
        print()
        command_nine(dbConn)
        print()
    else:
        print("**Error, unknown command, try again...")
        print()
    command = input(prompt)

#
# done
#
