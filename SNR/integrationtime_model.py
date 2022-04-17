import numpy as np
import pandas as pd
import os
from Thermal.thermal_model import get_temperature
import plotly.express as px

h = 6.62607004e-34  # Planck's constant
c = 299792458  # m/s
SNR = 10
wavelength_min = 8
wavelength_max = 12
avg_lamda = (wavelength_min + wavelength_max) / 2
f = 1.6
mirror_diameter = 0.5


def albedo(D, H):
    return (1329 / D) * 10 ** (-0.2 * H)


def lamda_E_lamda(lamda, T, epsilon):
    # emit 10-20 micron region
    c1, c2 = 3.7418 * 10 ** 8, 14388

    return epsilon * ((c1 / lamda ** 4) * (1 / ((np.exp(c2 / (lamda * T))) - 1)))


def S(D, diameter, R, T, epsilon, time):  # atmospheric stuff and instrument stuff all neglected.

    temp1 = (D ** 2) * time * (4 * np.pi * (diameter / 2) ** 2)
    temp2 = 4 * h * c * R ** 2

    c1 = 3.7418 * 10 ** 8
    c2 = 14388

    return (temp1 / temp2) * avg_lamda * epsilon * (
                (c1 / avg_lamda ** 4) * (1 / ((np.exp(c2 / (avg_lamda * T))) - 1)))  # temp3[0]


def B(D, time, f):
    det_area = 1.7689e-4  # From Cheops 13.3mm x 13.3mm

    return 0.3 * (np.pi / (4 * h * c)) * ((D ** 2) / (f ** 2)) * avg_lamda * (det_area) * time


def albedos(dataframe):
    albedo_lst = []
    for i in range(dataframe.shape[0]):
        bedo = albedo(dataframe.at[i, "diameter"], dataframe.at[i, "H"])
        albedo_lst.append(bedo)
    return albedo_lst


def format_csv(filename):
    cols = ['no', 'date', 't_eqm', 't_stm', 't_frm']
    df_thermal = pd.read_csv(filename, names=cols)

    df_thermal = df_thermal.loc[: df_thermal[(df_thermal['no'] == '$$EOE')].index[0], :]
    df_thermal = df_thermal.drop(df_thermal.index[-1:])
    df_thermal['date'] = df_thermal['date'].str.slice(start=5, stop=17)
    df_thermal['date'] = pd.to_datetime(df_thermal.date)
    df_thermal['date'] = df_thermal['date'].dt.strftime('%Y-%b-%d')

    return df_thermal


df = pd.read_csv('../Data/data.csv', sep=",")
albedos = albedos(df)
df = df.assign(albedo_computed=albedos)

# Re format date of dataframe to match thermal modal date
df['date_closest'] = pd.to_datetime(df.date_closest)
df['date_closest'] = df['date_closest'].dt.strftime('%Y-%b-%d')

'''
# df_thermal = format_csv('1566_Icarus.csv')
# print(df_thermal)

# df_merged = df.merge(df_thermal, left_on='date_closest', right_on='date')[df_thermal.columns]
# q = df_thermal.index[df['myvar'] == 'specific_name']
# print(df_merged.iloc[0])


# print(df_thermal.query('1 == "2029-Dec-28"'))

# df_merged = df.merge(df_thermal, left_on='date_closest', right_on=1)[df.columns]
# print(df_merged)'''

SNR_lst = []
T_lst = []
for i, filename in zip(range(df.shape[0]), os.listdir('../Ephemerides')):
    file = os.path.join('../Ephemerides', filename)
    df_thermal = format_csv(file)
    j = df_thermal.index[df_thermal['date'] == df.at[i, "date_closest"]].item()
    A = df.at[i, "albedo_computed"]

    D = mirror_diameter
    diameter = df.at[i, "diameter"] * 1000
    R = df.at[i, "closest distance"] * 1000
    epsilon = 0.965

    T = get_temperature(file, A, diameter, epsilon)[:, 2:][j - 1, 2]
    t = integration_time

    Signal = 0.3 * S(D, diameter, R, T, epsilon, t)  # 0.3 is quantum efficiency
    Background = B(D, t, f)
    Noise = np.sqrt(Background + Signal)
    SNR = Signal / Noise
    SNR_lst.append(SNR)
    T_lst.append(T)

df = df.assign(SNR=SNR_lst)
df = df.assign(Temp=T_lst)

pd.set_option('display.max_columns', None)
print(df)

fig = px.scatter(df, x="SNR", y="date_closest",
                 size="diameter", color="Temp",
                 hover_name="Name", size_max=35)
fig.show()