import csv
from distutils.core import run_setup
import operator
from re import A
import requests
import datetime
from classes import Position
from classes import Asteroid
import stupid
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from thermal_model import get_temperature
from pathlib import Path
location = str(Path(__file__).parent.absolute())


all_path = location + "/all.csv"
pha_path  = location + "/pha.csv"
pha_100_path  = location + "/pha_100.csv"
earth_path = location + "/earth.txt"

# asteroids = []
# file = open(pha_100_path)
# csvreader = csv.reader(file)
# header = next(csvreader)
# rows = []
# index = 0
# for row in csvreader:
#     asteroid = {}
#     for field in range(len(row)):
#         asteroid[header[field]] = row[field]
#     asteroids.append(asteroid)
#     index += 1
# file.close()


# startDate = '2023-01-01'
# stopDate = '2030-01-01'

# index = 0
# for asteroid in asteroids:
#     asteroidName = asteroid["full_name"].split('(')[0].strip("    ")
#     number = asteroidName.split(" ")[0]
#     number = "2" + ("0" * (7 - len(number) - 1)) + number
#     url = "https://ssd.jpl.nasa.gov/api/horizons.api?format=json&COMMAND='DES={name}'&OBJ_DATA='NO'&MAKE_EPHEM='YES'&EPHEM_TYPE='VECTOR'&CENTER='500@0'&START_TIME='{start}'&STOP_TIME='{stop}'&STEP_SIZE='1d'&QUANTITIES='1'&CSV_FORMAT='YES'".format(
#         name = number,
#         start = startDate,
#         stop = stopDate
#     )
#     r = requests.get(url)

#     table = r.json()["result"]
#     table = table.split('SOE\n')[1].split('\n')
#     write_path = "/Users/timsmit/Documents/TU/Master/Jaar 1/PS II/Project/ephemerides_sentry/" + asteroidName + '.csv'
#     with open(write_path, 'w') as f:
#         writer = csv.writer(f)
#         for row in table:
#             row = row.split(',')[0:5]
#             writer.writerow(row)
#     index+=1
#     if index % 10 == 0:
#         print(index/len(asteroids)*100, "%")
# test2 = 1

startDate = '2023-01-01'
stopDate = '2030-01-01'


# DOWNLOAD ALL SENTRY ASTEROIDS
url = "https://ssd-api.jpl.nasa.gov/sentry.api"
r = requests.get(url)
list = r.json()

n = 1395

asteroids = []

# DOWNLOAD EPHEMERIDES FOR ALL SENTRY ASTEROIDS
# SAVE EPHEMERIDES TO A CSV FOR EACH ASTEROID
index = 0
for asteroid in list['data']:
    asteroidName = asteroid['fullname']
    url = "https://ssd.jpl.nasa.gov/api/horizons.api?format=json&COMMAND='DES={name}'&OBJ_DATA='NO'&MAKE_EPHEM='YES'&EPHEM_TYPE='VECTOR'&CENTER='500@0'&START_TIME='{start}'&STOP_TIME='{stop}'&STEP_SIZE='1d'&QUANTITIES='1'&CSV_FORMAT='YES'".format(
            name = asteroid['des'],
            start = startDate,
            stop = stopDate
        )
    r = requests.get(url)
    table = r.json()["result"]
    if "No matches found" in table: continue
    table = table.split('SOE\n')[1].split('\n')
    ephemeris = []
    write_path =  location + "/ephemerides_sentry/" + asteroidName + '.csv'
    with open(write_path, 'w') as f:
        writer = csv.writer(f)
        for row in table:
            if row == "$$EOE" : break
            row = row.split(',')[0:5]
            date = row[1].strip(' ').split(' ')[1]
            date = datetime.datetime(int(date.split('-')[0]), stupid.string_to_month(date.split('-')[1]), int(date.split('-')[2]))
            position = Position(date, float(row[2]), float(row[3]), float(row[4]))
            ephemeris.append(position)
            writer.writerow(row)
    asteroid_obj = Asteroid(asteroidName, asteroid['diameter'], asteroid['h'], 0.154, float(asteroid['ps_max']), float(asteroid['ps_cum']), ephemeris)
    asteroids.append(asteroid_obj)
    index += 1
    print("Downloading and saving ephemeris:", index/n*100, '%')

sorted_asteroids = sorted(asteroids, key= operator.attrgetter("palermo_max"), reverse=True)

# STORE LIST OF ALL ASTEROID NAMES SO THEY CAN BE USED IN FUTURE CROSS_CHECKING
write_path =  location + "/" + 'names_all' + '.csv'
with open(write_path, 'w') as f:
    writer = csv.writer(f)
    for asteroid in sorted_asteroids:
        writer.writerow(asteroid.name)

# STORE LIST OF TOP 50 MOST DANGEROUS ASTEROID NAMES SO THEY CAN BE USED IN FUTURE CROSS_CHECKING
write_path =  location + "/" + 'names_50' + '.csv'
with open(write_path, 'w') as f:
    writer = csv.writer(f)
    for asteroid in sorted_asteroids[0:50]:
        writer.writerow(asteroid.name)

# STORE LIST OF TOP 500 MOST DANGEROUS ASTEROID NAMES SO THEY CAN BE USED IN FUTURE CROSS_CHECKING
write_path =  location + "/" + 'names_500' + '.csv'
with open(write_path, 'w') as f:
    writer = csv.writer(f)
    for asteroid in sorted_asteroids[0:500]:
        writer.writerow(asteroid.name)

startDate = datetime.datetime(int(startDate.split('-')[0]), int(startDate.split('-')[1]), int(startDate.split('-')[2])) 
stopDate = datetime.datetime(int(stopDate.split('-')[0]), int(stopDate.split('-')[1]), int(stopDate.split('-')[2]))

# GET EARTH EPHEMERIS
earth = [[], [], [], []]
file = open(earth_path)
csvreader = csv.reader(file)
for row in csvreader:
    date = row[1].strip(' ').split(' ')[1]
    date = datetime.datetime(int(date.split('-')[0]), stupid.string_to_month(date.split('-')[1]), int(date.split('-')[2]))
    if date < startDate or date > stopDate: continue
    earth[0].append(date)
    earth[1].append(float(row[2])) 
    earth[2].append(float(row[3])) 
    earth[3].append(float(row[4])) 
file.close()

# COMPUTE AND SAVE DISTANCES FOR ALL DATES
write_path = location + "/data.csv"
with open(write_path, 'w') as f:
    writer = csv.writer(f)
    header = ["Name", "diameter", "H", "albedo", "date", "distance", "top_50"]
    writer.writerow(header)
    asteroid_index = 0
    for asteroid in sorted_asteroids:
        index = 0
        for asteroid_position in asteroid.ephemeris:
            earth_position = np.array(earth)[:, index]
            if not asteroid_position.date == earth_position[0]: raise Exception("Dates don't match")

            difference = np.array([asteroid_position.x , asteroid_position.y, asteroid_position.z]) - np.array([earth_position[1], earth_position[2],earth_position[3]])
            distance = np.linalg.norm(difference)
            if index < 50: top_50 = "True"
            else: top_50 = "False"
            writer.writerow([asteroid.name, asteroid.diameter, asteroid.H, asteroid.albedo, asteroid_position.date.strftime("%d/%m/%Y"), distance, top_50])

            index += 1
        asteroid_index += 1
        print("Computing and saving distances:", asteroid_index/n*100, '%')

for asteroid in asteroids:
    asteroidName = asteroid["full_name"].split('(')[0].strip("    ")
    number = asteroidName.split(" ")[0]
    # number = "2" + ("0" * (7 - len(number) - 1)) + number
    url = "https://ssd-api.jpl.nasa.gov/sentry.api?des={number}".format(
        number = asteroidName
    )
    r = requests.get(url)

    table = r.json()
    table = table.split('SOE\n')[1].split('\n')
    write_path = "/Users/timsmit/Documents/TU/Master/Jaar 1/PS II/Project/ephemerides/" + asteroidName + '.csv'
    with open(write_path, 'w') as f:
        writer = csv.writer(f)
        for row in table:
            row = row.split(',')[0:5]
            writer.writerow(row)
    index+=1
    if index % 10 == 0:
        print(index/len(asteroids)*100, "%")
test2 = 1






asteroid_ephemerides = []
filenames = []
for asteroid in asteroids:
    asteroidName = asteroid["full_name"].split('(')[0].strip("    ")
    read_path = location + "/ephemerides/" + asteroidName + '.csv'
    name = asteroidName + '.csv'
    filenames.append(name)
    file = open(read_path)
    temps = get_temperature(read_path, 0.51, 1E3)
    csvreader = csv.reader(file)
    ephemeride = {"name": asteroidName, "eph":[[],[], [], []]}
    for row in csvreader:
        if row[0] == "$$EOE" : break
        date = row[1].strip(' ').split(' ')[1]
        date = datetime.datetime(int(date.split('-')[0]), stupid.string_to_month(date.split('-')[1]), int(date.split('-')[2]))
        if date < startDate or date > stopDate: continue
        ephemeride["eph"][0].append(date) 
        ephemeride["eph"][1].append(float(row[2])) 
        ephemeride["eph"][2].append(float(row[3])) 
        ephemeride["eph"][3].append(float(row[4])) 
    asteroid_ephemerides.append(ephemeride)

    # break
file.close()


index = 0
observations = []
write_path = location + "/data.csv"
with open(write_path, 'w') as f:
    writer = csv.writer(f)
    header = ["Name", "diameter", "H", "albedo", "date", "distance"]
    writer.writerow(header)
    for asteroid in asteroid_ephemerides:
        difference = np.zeros((len(asteroid['eph'][1]), 3))
        difference[:, 0] = np.array(asteroid['eph'][1]) - np.array(earth[0])
        difference[:, 1] = np.array(asteroid['eph'][2]) - np.array(earth[1])
        difference[:, 2] = np.array(asteroid['eph'][3]) - np.array(earth[2])
        difference = np.vstack((
            np.array(asteroid['eph'][1]) - np.array(earth[0]),
            np.array(asteroid['eph'][2]) - np.array(earth[1]),
            np.array(asteroid['eph'][3]) - np.array(earth[2]))
            )
        difference = np.linalg.norm(difference, axis = 0)
        index_min = min(range(len(difference)), key=difference.__getitem__)
        distance = difference[index_min]
        date = asteroid['eph'][0][index_min]
        asteroid_position = [asteroid['eph'][1][index_min], asteroid['eph'][2][index_min], asteroid['eph'][3][index_min]]
        earth_position = [earth[0][index_min], earth[1][index_min], earth[2][index_min]]
        observation = {"date": date, "distance": distance, "asteroid_position": asteroid_position, "earth_position": earth_position}
        observations.append(observation)

        asteroid_data = asteroids[index]
        # asteroid_data.append([date, distance])
        for i in range(len(difference)):
            distance = difference[i]
            date = asteroid['eph'][0][i]
            writer.writerow([["full_name"], asteroid_data["diameter"], asteroid_data["H"], asteroid_data["albedo"], date, distance])
        index += 1



# fig = plt.figure()
# plt.style.use('dark_background')
# ax = fig.add_subplot(111, projection='3d')
# u, v = np.mgrid[0:2*np.pi:20j, 0:np.pi:10j]
#
# r_sun = 696340
# x_sun = r_sun * np.cos(u)*np.sin(v)
# y_sun = r_sun * np.sin(u)*np.sin(v)
# z_sun = r_sun * np.cos(v)
# ax.plot_surface(x_sun, y_sun, z_sun, color="r")
# r_earth = 6378
# r_asteroid = 1000
# for observation in observations:
#     x_earth = r_earth * np.cos(u)*np.sin(v) + observation["earth_position"][0]
#     y_earth = r_earth * np.sin(u)*np.sin(v) + observation["earth_position"][1]
#     z_earth = r_earth * np.cos(v) + observation["earth_position"][2]
#     ax.plot_surface(x_earth, y_earth, z_earth, color="blue")
#
#     x_asteroid = r_asteroid * np.cos(u)*np.sin(v) + observation["asteroid_position"][0]
#     y_asteroid = r_asteroid * np.sin(u)*np.sin(v) + observation["asteroid_position"][1]
#     z_asteroid = r_asteroid * np.cos(v) + observation["asteroid_position"][2]
#     ax.plot_surface(x_asteroid, y_asteroid, z_asteroid, color="white")
#
#     ax.plot(
#         [observation["earth_position"][0], observation["asteroid_position"][0]],
#         [observation["earth_position"][1], observation["asteroid_position"][1]],
#         [observation["earth_position"][2], observation["asteroid_position"][2]], color="green")
#     # ax.set_xlim([-2E8, 2E8])
#     # ax.set_ylim([-2E8, 2E8])
#     # ax.set_zlim([-2E8, 2E8])
# # plt.axis("scaled")
# ax.set_xlabel("x")
# ax.set_ylabel("y")
# ax.set_zlabel("z")
# plt.show()