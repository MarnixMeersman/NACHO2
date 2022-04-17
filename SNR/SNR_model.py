import numpy as np
import pandas as pd
import os
from Thermal.thermal_model import get_temperature
import plotly.express as px

h = 6.62607004e-34  # Planck's constant
c = 299792458  # m/s
integration_time = 30*60
wavelength_min = 8
wavelength_max = 12
avg_lamda = (wavelength_min + wavelength_max)/2
f = 1.6
mirror_diameter = 0.5



def lamda_E_lamda(lamda, T, epsilon):
    
    # emit 10-20 micron region
    c1, c2 = 3.7418*10**8, 14388

    return epsilon * (   (c1/lamda**4) * (1/((np.exp(c2/(lamda*T)))-1))   )

def S(D, diameter, R, T, epsilon, time):  # atmospheric stuff and instrument stuff all neglected.
    
    temp1 = (D**2)*time*(4*np.pi*(diameter/2)**2)
    temp2 = 4*h*c*R**2
    
    c1 = 3.7418*10**8
    c2 = 14388

    return (temp1/temp2) * avg_lamda* epsilon * (   (c1/avg_lamda**4) * (1/((np.exp(c2/(avg_lamda*T)))-1))   ) # temp3[0]

def B(D, time, f):

    det_area = 1.7689e-4  # From Cheops 13.3mm x 13.3mm

    return 0.3*(np.pi/(4*h*c))*((D**2)/(f**2)) * avg_lamda*(det_area)*time

def get_albedos(dataframe):
    albedo_lst = []
    for i in range(dataframe.shape[0]):
        D = dataframe.at[i, "diameter"]
        H = dataframe.at[i, "H"]
        bedo = (1329 / D) * 10 ** (-0.2 * H)
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



# df = pd.read_csv('data_old.csv', sep=",")
# albedos = get_albedos(df)
# df = df.assign(albedo_computed = albedos)
#
# # Re format date of dataframe to match thermal modal date
# df['date_closest'] = pd.to_datetime(df.date_closest)
# df['date_closest'] = df['date_closest'].dt.strftime('%Y-%b-%d')


# df_thermal = format_csv('1566_Icarus.csv')
# print(df_thermal)

#df_merged = df.merge(df_thermal, left_on='date_closest', right_on='date')[df_thermal.columns]
# q = df_thermal.index[df['myvar'] == 'specific_name']
# print(df_merged.iloc[0])



# print(df_thermal.query('1 == "2029-Dec-28"'))

# df_merged = df.merge(df_thermal, left_on='date_closest', right_on=1)[df.columns]
# print(df_merged)
S_lst = []
SNR_lst = []
T_lst = []
filenames = ['1566 Icarus.csv', '1620 Geographos.csv', '1862 Apollo.csv', '1981 Midas.csv', '2101 Adonis.csv', '2102 Tantalus.csv', '2201 Oljato.csv', '2340 Hathor.csv', '3122 Florence.csv', '3200 Phaethon.csv', '3361 Orpheus.csv', '3362 Khufu.csv', '3671 Dionysus.csv', '3757 Anagolay.csv', '4015 Wilson-Harrington.csv', '4034 Vishnu.csv', '4179 Toutatis.csv', '4183 Cuno.csv', '4486 Mithra.csv', '4660 Nereus.csv', '4769 Castalia.csv', '5604.csv', '6489 Golevka.csv', '7335.csv', '7341.csv', '7482.csv', '7822.csv', '8014.csv', '8566.csv', '9856.csv', '10115.csv', '11500 Tomaiyowit.csv', '12538.csv', '12923 Zephyr.csv', '13651.csv', '14827 Hypnos.csv', '25143 Itokawa.csv', '29075.csv', '33342.csv', '35107.csv', '35396.csv', '39572.csv', '41429.csv', '52760.csv', '52768.csv', '53319.csv', '53789.csv', '65679.csv', '65803 Didymos.csv', '66391 Moshup.csv', '68216.csv', '68346.csv', '68548.csv', '68950.csv', '85182.csv', '85713.csv', '85774.csv', '85989.csv', '85990.csv', '86039.csv', '86819.csv', '88254.csv', '89830.csv', '89959.csv', '90075.csv', '90403.csv', '90416.csv', '99248.csv', '99942 Apophis.csv', '101955 Bennu.csv', '103067.csv', '111253.csv', '138127.csv', '140158.csv', '140288.csv', '141432.csv', '143624.csv', '152671.csv', '152754.csv', '152978.csv', '153201.csv', '153591.csv', '153814.csv', '154276.csv', '159857.csv', '161989 Cacus.csv', '162000.csv', '162116.csv', '162510.csv', '162567.csv', '162998.csv', '163132.csv', '163243.csv', '163348.csv', '163818.csv', '163899.csv', '164121.csv', '164207.csv', '168318.csv', '175706.csv', '185851.csv', '187040.csv', '194268.csv', '206378.csv', '207945.csv', '215588.csv', '217628 Lugh.csv', '221980.csv', '226554.csv', '230549.csv', '231937.csv', '234145.csv', '235756.csv', '242450.csv', '242643.csv', '243566.csv', '244977.csv', '250620.csv', '250680.csv', '250706.csv', '252399.csv', '263976.csv', '264357.csv', '265196.csv', '267221.csv', '267337.csv', '269690.csv', '277570.csv', '294739.csv', '297274.csv', '297300.csv', '297418.csv', '301844.csv', '303450.csv', '304330.csv', '307493.csv', '308635.csv', '310560.csv', '312070.csv', '333578.csv', '341843.csv', '349068.csv', '357022.csv', '357024.csv', '360191.csv', '363024.csv', '363027.csv', '363505.csv', '363599.csv', '363831.csv', '365071.csv', '365424.csv', '366774.csv', '367248.csv', '369264.csv', '371660.csv', '373135.csv', '377732.csv', '381906.csv', '385186.csv', '385343.csv', '386454.csv', '386847.csv', '387505.csv', '387746.csv', '389694.csv', '390725.csv', '391211.csv', '395207.csv', '398188 Agni.csv', '409836.csv', '410778.csv', '411165.csv', '414286.csv', '414287.csv', '416801.csv', '417634.csv', '418094.csv', '419472.csv', '419624.csv', '419880.csv', '422686.csv', '422699.csv', '423321.csv', '433953.csv', '434096.csv', '434633.csv', '436329.csv', '436671.csv', '441987.csv', '442037.csv', '443806.csv', '443880.csv', '444193.csv', '445305.csv', '451124.csv', '453707.csv', '454094.csv', '454100.csv', '455299.csv', '458436.csv', '459683.csv', '462238.csv', '468468.csv', '468727.csv', '469445.csv', '471241.csv', '477519.csv', '480936.csv', '483508.csv', '484402.csv', '488789.csv', '490581.csv', '496816.csv', '496817.csv', '499582.csv', '503941.csv', '504800.csv', '505657.csv', '506074.csv', '510055.csv', '511008.csv', '511684.csv', '523589.csv', '523664.csv', '523775.csv', '523816.csv', '529668.csv', '529753.csv', '533722.csv', '538212.csv']

for i, filename in zip(range(df.shape[0]), filenames):
    file = os.path.join('../Ephemerides/', filename)
    df_thermal = format_csv(file)
    j = df_thermal.index[df_thermal['date'] == df.at[i, 'date_closest']].item()
    A = df.at[i, "albedo_computed"]
    print("check if filename and asteroid name correspond: ", filename, df.at[i, "Name"])

    D = mirror_diameter
    diameter = df.at[i, "diameter"] * 1000
    R = df.at[i, "closest distance"] * 1000
    epsilon = 0.965

    T = get_temperature(file, A, diameter, epsilon)[:, 2:][j-1, 2]
    t = integration_time

    Signal = 0.3*S(D, diameter, R, T, epsilon, t)  # 0.3 is quantum efficiency
    Background = B(D, t, f)
    Noise = np.sqrt(Background + Signal)
    SNR = Signal/Noise
    SNR_lst.append(SNR)
    T_lst.append(T)
    S_lst.append(Signal)

S_power = [i/integration_time for i in S_lst]
SNR_dB  = [10*np.log(snr) for snr in SNR_lst]
df = df.assign(SNR = SNR_lst)
df = df.assign(Temp = T_lst)
df = df.assign(Signal_power_W = S_power)
df = df.assign(SNR_dB = SNR_dB)



pd.set_option('display.max_columns', None)
print(df)

fig = px.scatter(df, x="SNR", y="Signal_power_W",
                 size="diameter", color="Temp",
                 hover_name="Name", size_max=35, title="Signal to Noise per asteroid with 0.5 [m] diameter mirror and IR sensor spectrum of 8-12 [micron]")
# fig.update_yaxes(type="log")
fig.update_xaxes(type="log")
#fig.show()
fig.write_html("snr_signalpower_closest_range.html")


fig = px.scatter(df, x="SNR", y="closest distance",
                 size="diameter", color="Temp",
                 hover_name="Name", size_max=35, title="Signal to Noise per asteroid with 0.5 [m] diameter mirror and IR sensor spectrum of 8-12 [micron]")
# fig.update_yaxes(type="log")
fig.update_xaxes(type="log")
#fig.show()

fig.write_html("snr_albedo_closest_range.html")

fig = px.scatter(df, x="date_closest", y="SNR",
                 size="diameter", color="Temp",
                 hover_name="Name", size_max=35, title="Signal to Noise per asteroid with 0.5 [m] diameter mirror and IR sensor spectrum of 8-12 [micron]")
fig.update_yaxes(type="log")
#fig.update_xaxes(type="log")
#fig.show()

fig.write_html("snr_date_closest_range.html")