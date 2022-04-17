import numpy as np


def get_temperature(file: str,
                    A: float,
                    D: float,
                    epsilon = 0.965,
                    data = False):

    AU = 1.496E8
    if not data:
        trajectory = np.genfromtxt(file, delimiter=",", skip_footer=63)

    else:
        trajectory = file

    trajectory = np.hstack((trajectory[:, :1], np.linalg.norm(trajectory[:, 2:], axis=1).reshape(
        np.size(trajectory[:, 0]), -1)))

    trajectory[:, 0] = trajectory[:, 0] - np.roll(trajectory[:, 0], 1)
    trajectory[0, 0] = 0

    S = 4 * np.pi * (D / 2) ** 2
    crosssec = np.pi * (D / 2) ** 2

    epsilon = epsilon
    A = A
    S_0 = 1.361E3
    sigma = 5.6704E-8
    eta = 0.756

    T_eqm = ((S_0 * (1 - A) * crosssec) / (sigma * epsilon * S * (trajectory[:, 1] / AU) ** 2)) ** (1 / 4)
    T_stm = ((S_0 * (1 - A) * crosssec) / (eta * sigma * epsilon * S * (trajectory[:, 1] / AU) ** 2)) ** (1 / 4)
    T_frm = ((S_0 * (1 - A) * crosssec) / (np.pi * sigma * epsilon * S * (trajectory[:, 1] / AU) ** 2)) ** (1 / 4)

    trajectory = np.hstack((trajectory, T_eqm.reshape(np.size(trajectory[:, 0]), -1)))
    trajectory = np.hstack((trajectory, T_stm.reshape(np.size(trajectory[:, 0]), -1)))
    trajectory = np.hstack((trajectory, T_frm.reshape(np.size(trajectory[:, 0]), -1)))

    return trajectory

if __name__ == "__main__":

    file = r"../Data/1566_Icarus.csv"

    trajectory = get_temperature(file, A = 0.51, D = 1E3)

    #print(trajectory)
    print(trajectory[:, 2:][:, 2])
    print(trajectory[:, 4:])



