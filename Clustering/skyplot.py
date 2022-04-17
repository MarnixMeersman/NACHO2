import numpy as np
import pandas as pd
from Preprocessing.asteroidStuff import x_earths, y_earths, z_earths, x_asteroids, y_asteroids, z_asteroids
import plotly.express as px
df = pd.read_csv("../Data/full_data.csv", sep=",")


pos = pd.DataFrame({'X Earth': x_earths, 'Y Earth': y_earths, 'Z Earth': z_earths,
        'X Asteroid': x_asteroids, 'Y Asteroid': y_asteroids, 'Z Asteroid': z_asteroids})

Qs = []
for i in range(len(pos)):
    P = [pos.at[i, 'X Asteroid'] - pos.at[i, 'X Earth'],
         pos.at[i, 'Y Asteroid'] - pos.at[i, 'Y Earth'],
         pos.at[i, 'Z Asteroid'] - pos.at[i, 'Z Earth']]
    d = np.sqrt(P[0]**2 + P[1]**2 + P[2]**2)
    Q = P/d
    Qs.append(Q)

Qs = np.array(Qs)
proj = pd.DataFrame({'x': Qs[:, 0], 'y': Qs[:, 1], 'z': Qs[:, 2]})


df = pd.concat([df, proj], axis= 1)
df.to_csv('full_data.csv')



fig = px.scatter_3d(df, x='x', y='y', z='z', color='Name')
fig.show()

