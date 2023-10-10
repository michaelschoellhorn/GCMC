import numpy as np
from matplotlib import pyplot as plt
from matplotlib import colors

plt.rcParams['axes.axisbelow'] = True
list_of_z = [0.05, 0.125, 0.25, 0.56, 0.86, 1.1, 1.15, 1.5]


def load_data(z):
    N_plus, N_minus = np.loadtxt(f'obs_{z}.csv', dtype=int)
    #pos = np.loadtxt(f'pos_{z}.csv', dtype=int)
    return N_plus, N_minus  # , pos


# thermalization plots
def therm(list_of_z=[0.05, 0.125, 0.25, 0.56, 0.86, 1.1, 1.15, 1.5]):
    for z in list_of_z:
        N_plus, N_minus = load_data(z)
        N = N_plus + N_minus
        S = (N_plus - N_minus)/(N+1e-16)
        x = np.linspace(0, 5e7, len(N_plus))
        plt.figure.figsize = (18/2.54, 10/2.54)
        plt.plot(x, N, label='$N$', linewidth=0.7)
        plt.plot(x, N_minus, label='$N\_$', linewidth=0.7)
        plt.plot(x, N_plus, label='$N_+$', linewidth=0.7)
        plt.legend(loc='upper right')
        plt.title(f'Thermalisierungslauf $z={z}$')
        plt.xlabel('Schrittanzahl')
        plt.ylabel('Stäbchenanzahl')
        plt.grid(zorder=-1)
        #plt.savefig(f'N_{zvar}.png', dpi=400)
        plt.show()
        plt.close()
    return 0

# histogram plots


def histogram():
    N_plus = []
    N_minus = []
    N = []
    S = []
    varnames = ['Stäbchenanzahl $N_+$', 'Stäbchenanzahl $N\_$',
                'Stäbchenanzahl $N$', 'Ordnungsparameter $S$']

    # load/process data
    for z in [0.25, 0.56, 0.86, 1.1]:
        x, y = load_data(str(z))
        N_plus.append(x)
        N_minus.append(y)
        N.append(x+y)
        S.append((x-y)/(x+y))
    data = np.array([N_plus, N_minus, N, S])

    # plot histograms in 2x2 subplots grouped by N+/-, N and S
    for i in range(4):
        fig, axs = plt.subplots(
            2, 2, sharex=True, sharey=True, constrained_layout=True)
        fig.set_size_inches(17/2.54, 15/2.54)
        if i < 3:  # N,N+/- (int observables)
            # +/- 0.5 avoids that the int->float conversion of N+ leads to bins without/double the count, since the value is no longer close to the binedge
            axs[0, 0].hist(data[i, 0], bins=np.arange(
                np.amin(data[i, 0])-0.5, np.amax(data[i, 0])+0.5))
            axs[0, 1].hist(data[i, 1], bins=np.arange(
                np.amin(data[i, 1])-0.5, np.amax(data[i, 1])+0.5))  # rt
            axs[1, 0].hist(data[i, 2], bins=np.arange(
                np.amin(data[i, 2])-0.5, np.amax(data[i, 2])+0.5))  # lb
            axs[1, 1].hist(data[i, 3], bins=np.arange(
                np.amin(data[i, 3])-0.5, np.amax(data[i, 3])+0.5))  # rb

        else:  # S (float observables)
            axs[0, 0].hist(
                data[i, 0], bins=np.linspace(-1.003, 1.005, 96))  # lt
            axs[0, 1].hist(
                data[i, 1], bins=np.linspace(-1.003, 1.005, 101))  # rt
            axs[1, 0].hist(
                data[i, 2], bins=np.linspace(-1.003, 1.005, 101))  # lb
            axs[1, 1].hist(
                data[i, 3], bins=np.linspace(-1.0021, 1.0051, 86))  # rb

        # styling
        fig.suptitle('Histogramme von ' + varnames[i])
        axs[0, 0].set_title('$z=0.25$')
        axs[0, 0].set_ylabel('Counts')
        axs[0, 1].set_title('$z=0.56$')
        axs[1, 0].set_ylabel('Counts')
        axs[1, 0].set_title('$z=0.86$')
        axs[1, 1].set_title('$z=1.1$')
        axs[1, 1].set_xlabel(varnames[i])
        axs[1, 0].set_xlabel(varnames[i])
        axs[1, 0].grid(True)
        axs[0, 1].grid(True)
        axs[0, 0].grid(True)
        axs[1, 1].grid(True)

        plt.savefig(f'Histogram_{i}.png', dpi=600)
        # plt.show()
        plt.close(fig)
    return 0


def visualize(list_of_z=[0.05, 0.56, 0.86, 1.15]):
    # load data
    grid = []
    for z in list_of_z:
        grid.append(np.loadtxt(f'grid_{z}.csv'))

    # plot data as heatmaps
    cmap = colors.ListedColormap(['white', 'red', 'blue'])
    fig, axs = plt.subplots(2, 2, constrained_layout=True)
    fig.set_size_inches(17/2.54, 17/2.54)
    axs[0, 0].imshow(grid[0], cmap=cmap)
    axs[0, 1].imshow(grid[1], cmap=cmap)
    axs[1, 0].imshow(grid[2], cmap=cmap)
    axs[1, 1].imshow(grid[3], cmap=cmap)

    # styling
    fig.suptitle('Endkonfigurationen ausgewählter Aktivitäten')
    axs[0, 0].set_title(f'$z={list_of_z[0]}$')
    axs[0, 1].set_title(f'$z={list_of_z[1]}$')
    axs[1, 0].set_title(f'$z={list_of_z[2]}$')
    axs[1, 1].set_title(f'$z={list_of_z[3]}$')
    plt.savefig('Endkonfig.png', dpi=1000)
    plt.show()
    plt.close()


def S_eta(list_of_z=[0.05, 0.125, 0.25, 0.56, 0.86, 1.1, 1.15, 1.5]):
    # load data and calculate quantities
    list_S_mean = []
    list_eta_mean = []
    list_Serror = []
    list_etaerror = []
    for z in list_of_z:
        N_plus, N_minus = load_data(z)
        N = N_plus + N_minus
        S = (N_plus - N_minus)/(N+1e-16)
        S_abs = abs(S)
        eta = 8*N/64**2
        S_mean, eta_mean, Serror, etaerror = mean_error(S_abs, eta, 5)
        list_S_mean.append(S_mean)
        list_eta_mean.append(eta_mean)
        list_Serror.append(Serror)
        list_etaerror.append(etaerror)

    # make/save plot
    plt.figure.figsize = (17/2.54, 10/2.54)
    plt.errorbar(list_eta_mean, list_S_mean, xerr=list_etaerror,
                 yerr=list_Serror, fmt='.', capsize=2, linewidth=0.5)
    plt.xlabel('Packungsdichte $<\eta>$')
    plt.ylabel('Absolutwert Ordnung $<|S|>$')
    plt.title('')
    plt.savefig('Seta.png', dpi=1000)
    plt.show()
    plt.close()
    return 0


def mean_error(data1, data2, k):
    sigma1 = data1.std()
    sigma1 = sigma1/(len(data1)/1000)**0.5
    sigma2 = data2.std()
    sigma2 = sigma2/(len(data2)/1000)**0.5
    return data1.mean(), data2.mean(), k*sigma1, k*sigma2


def title_picture(z):
    grid = np.loadtxt(f'grid_{z}.csv')
    cmap = colors.ListedColormap(['white', 'red', 'blue'])
    fig, ax = plt.subplots()
    fig.set_size_inches(17/2.54, 17/2.54)
    ax.imshow(grid, cmap=cmap)
    ax.set_title(f'$z={z}$')
    plt.savefig('Title.png', dpi=1000)
    plt.close()


# therm()
# histogram()
# visualize()
# S_eta()
# title_picture(0.56)
