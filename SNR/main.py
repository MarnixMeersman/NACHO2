import os
import numpy as np
import pandas as pd
from Thermal.thermal_model import get_temperature
from Preprocessing.asteroidStuff import filenames
from SNR_model import S, B




def get_albedos(dataframe):
    albedo_lst = []
    for i in range(dataframe.shape[0]):
        D = dataframe.at[i, "diameter"]
        H = dataframe.at[i, "H"]
        bedo = (1329 / D) * 10 ** (-0.2 * H)
        albedo_lst.append(bedo)
    return albedo_lst


# Constants
epsilon = 0.965
h = 6.62607004e-34  # Planck's constant
c = 299792458  # m/s
integration_time = 30*60
wavelength_min = 8
wavelength_max = 12
avg_lamda = (wavelength_min + wavelength_max)/2
f = 1.6
mirror_diameter = 0.5

# Import dataframe
df = pd.read_csv("../Data/data.csv", sep=",")

# Computed albedos
albedos = get_albedos(df)
df = df.assign(albedo_computed = albedos)
df.info()
# Execute thermal model on all csv files and append to dataframe
temperatures = []

i = 0
for filename in filenames:
    file = os.path.join('../Ephemerides', filename)
    T = get_temperature(file, df.at[i, "albedo_computed"], df.at[i, "diameter"] * 1000, epsilon)[:, 2:][:, 2]
    T = np.append(T, T[-1])

    temperatures.append(T)
    i += len(T)+1

temperatures = np.array(temperatures).flatten()
df = df.assign(temperature = temperatures)

SNR_lst, S_lst, N_lst = [], [], []
for i in range(len(df)):
    A = df.at[i, "albedo_computed"]

    D = mirror_diameter
    diameter = df.at[i, "diameter"] * 1000
    R = df.at[i, "distance"] * 1000
    epsilon = epsilon

    T = df.at[i, 'temperature']
    t = integration_time

    Signal = 0.3 * S(D, diameter, R, T, epsilon, t)  # 0.3 is quantum efficiency
    Background = B(D, t, f)
    Noise = np.sqrt(Background + Signal)
    SNR = Signal / Noise
    SNR_lst.append(SNR)
    S_lst.append(Signal)
    N_lst.append(Noise)

df = df.assign(Signal_Power_Watts = [i/integration_time for i in S_lst])
df = df.assign(Noise_Power_Watts = [i/integration_time for i in N_lst])
df = df.assign(SNR = SNR_lst)
df = df.assign(SNR_dB = [10*np.log(i) for i in SNR_lst])
# df = df.assign(x_e = np.array(y_earths).flatten(), z_e=np.array(z_earths).flatten(),
#                x_a= np.array(x_asteroids).flatten(),y_a= np.array(y_asteroids).flatten(),
#                z_a= np.array(z_asteroids).flatten())




print(df)
# df.to_csv('full_data.csv')

