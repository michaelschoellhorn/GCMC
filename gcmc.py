import numpy as np
from random import random, randint
import time
import concurrent.futures


def multiprocess(list_of_z, list_of_N_max, list_of_N_therm, list_of_delta_N, M, L):
    '''
    Executes multiple simulations at once by running them in parallel.\n
    Parameters
    -----------------
    list_of_z(list(float)): list of activities(float) z to be calculated\n
    list_of_N_max(list(int)): list of number of steps for how long should be iterated\n
    list_of_N_therm(list(int)): list of number of thermalization steps(int) made before measurement is started.\n
    list_of_delta_N(list(int)): list of number of steps between measurement\n
    For further documentation regarding the parameters look at the simulation function.
    '''
    start = time.perf_counter()

    # executes the different simulations on different processes to minimize time needed for multiple simulations
    with concurrent.futures.ProcessPoolExecutor() as executor:
        results = executor.map(simulation, list_of_N_max,
                               list_of_z, list_of_N_therm, list_of_delta_N, M, L)

    print(f'Runtime: {time.perf_counter()-start} s')
    return results


def simulation(N_measure, z, N_therm=1, delta_N=1000, M=64, L=8):
    '''
    Simulation function for the given 2D rods system
    ----------------------------------------
    For determining N_therm, just use with the dafault settings and plot N/N+/N-\n
    Parameters:
    ---------------------------------------
    N_measure(int): number of measurement steps\n
    z(float): activity\n
    N_therm(int): number of thermalisation steps\n
    delta_N(int): number of steps without between logging of observables\n
    M(int): gridlength, default is 64\n
    L(int): Length of rods, default is 8
    '''

    # initialization
    grid = np.zeros((M, M))
    pos = []
    # pos contains elements of the form [x, y, direction]
    # direction is 1 for horizontal and 0 for vertical
    Nplus = 0
    Nminus = 0
    Nplus_list = []
    Nminus_list = []

    starttime = time.perf_counter()

    # thermalization loop
    for i in range(N_therm):
        grid, pos, Nplus, Nminus = gcmc_step(grid, pos, Nplus, Nminus, z, M, L)
    print(f'Thermalisation finished for z = {z}')

    # measurement loop
    for i in range(N_measure):
        grid, pos, Nplus, Nminus = gcmc_step(grid, pos, Nplus, Nminus, z, M, L)

        # log data
        if i % delta_N == 0:
            Nplus_list, Nminus_list = log_observables(
                Nplus, Nminus, Nplus_list, Nminus_list)

            # progress feedback:
            # parallelization leads to multiple print statements, therfore we only monitor progress for the slowest z
            if i % int(N_measure/10) == 0 and z == 0.05:
                print(f'z={z}: {i/N_measure*100} % ', end='\r', flush=True)

    print('\n{} Loop Runtime:   {} s'.format(z, time.perf_counter()-starttime))

    # data pre-processing:
    N_plus_array = np.array(Nplus_list)
    N_minus_array = np.array(Nminus_list)
    return z, grid, pos, N_plus_array, N_minus_array


def log_observables(Nplus, Nminus, Nplus_list, Nminus_list):
    Nplus_list.append(Nplus)
    Nminus_list.append(Nminus)
    return Nplus_list, Nminus_list


def gcmc_step(grid, pos, Nplus, Nminus, z, M, L):
    '''
    performs the grand canonical monte carlo step, by either possibly inserting or deleting a particle
    '''

    # insertion/deletion branch
    if random() < 0.5:
        grid, pos, Nplus, Nminus = insert(grid, pos, Nplus, Nminus, z, M, L)
    else:
        grid, pos, Nplus, Nminus = delete(grid, pos, Nplus, Nminus, z, M, L)
    return grid, pos, Nplus, Nminus


def delete(grid, pos, Nplus, Nminus, z, M, L):
    '''
    Deletes a random particle out of the lattice if there is one and the dices fall right
    '''
    N = Nplus + Nminus
    if random() < (N / (2 * M ** 2) / z):  # catches automatically case N=0

        # choose a random particle
        i = randint(0, N - 1)
        chosen_particle = pos[i]
        x_pos = chosen_particle[0]
        y_pos = chosen_particle[1]
        direction = chosen_particle[2]

        # delete particle from occupation grid
        if direction == 1:  # particle horizontal
            if x_pos + L > M - 1:  # particle goes over the right border
                grid[y_pos, x_pos:M] = 0
                grid[y_pos, 0:(x_pos + L) % M] = 0
                #print('horizontally outside deleted')
            else:  # particle is completely inside boundries
                grid[y_pos, x_pos:x_pos + L] = 0
                #print('horizontally inside deleted')
            Nplus -= 1

        if direction == 0:  # particle vertical
            if y_pos + L > M - 1:
                grid[y_pos:M, x_pos] = 0
                grid[0:(y_pos + L) % M, x_pos] = 0
                #print('vertically outside deleted')
            else:
                grid[y_pos:y_pos + L, x_pos] = 0
                #print('vertically inside deleted')
            Nminus -= 1

        # delete column(chosen particle) out of pos(list of particles)
        del pos[i]

        return grid, pos, Nplus, Nminus
    return grid, pos, Nplus, Nminus


def insert(grid, pos, Nplus, Nminus, z, M, L):
    '''
    Insert a particle in the lattice at a random position/direction, if there's space and the dices fall right
    '''
    # calculate alpha
    alpha_ins = 2*M**2/(Nplus + Nminus + 1)*z

    # choose random position
    x_pos = randint(0, M-1)
    y_pos = randint(0, M-1)
    new_position = (x_pos, y_pos)

    # choose direction
    if random() > 0.5:

        # horizontal
        if not check_collision(grid, new_position, 1, M, L):

            if random() < alpha_ins:
                # insertion successful
                if x_pos + L > M - 1:
                    # particle goes over the right border
                    grid[y_pos, x_pos:M] = 1
                    grid[y_pos, 0:(x_pos + L) % M] = 1
                    #print('horizontally outside inserted')

                else:
                    # particle is completely inside boundries
                    grid[y_pos, x_pos:x_pos + L] = 1
                    #print('horizontally inside inserted')

                # add inserted particle to list
                pos.append([new_position[0], new_position[1], 1])
                Nplus += 1

            # else:
                #print('not inserted')

    else:
        # vertical
        if not check_collision(grid, new_position, 0, M, L):

            if random() < alpha_ins:
                # insertion successful
                if y_pos + L > M - 1:
                    # set to two to simplyfy visualisation, the collision check works with count_nonzero so there is no difference between 1/2
                    grid[y_pos:M, x_pos] = 2
                    grid[0:(y_pos + L) % M, x_pos] = 2
                    #print('vertically outside inserted')

                else:
                    grid[y_pos:y_pos + L, x_pos] = 2
                    #print('vertically inside inserted')

                # add inserted particle to list
                pos.append([new_position[0], new_position[1], 0])
                Nminus += 1

            # else:
                #print('not inserted')

    return grid, pos, Nplus, Nminus


def check_collision(grid, new_position, new_direction, M, L):
    ''' 
    Checks if there is a collision for a given position&direction\n
    returns True, if there is an collision\n
    returns False, if there is no collision
    '''

    x_pos = new_position[0]
    y_pos = new_position[1]

    if new_direction == 1:
        # particle horizontal
        if x_pos + L > M - 1:  # particle goes over the right border
            #print('horizontally outside')
            return np.count_nonzero(grid[y_pos, x_pos:M]) + np.count_nonzero(grid[y_pos, 0:(x_pos + L) % M]) >= 1
        else:  # particle is completely inside boundries
            #print('horizontally inside')
            return np.count_nonzero(grid[y_pos, x_pos:x_pos + L]) >= 1

    if new_direction == 0:
        # particle vertical
        if y_pos + L > M - 1:
            #print('vertically outside')
            return np.count_nonzero(grid[y_pos:M, x_pos]) + np.count_nonzero(grid[0:(y_pos + L) % M, x_pos]) >= 1
        else:
            #print('vertically inside')
            return np.count_nonzero(grid[y_pos:y_pos + L, x_pos]) >= 1


if __name__ == '__main__':  

    # -----------------------------------
    # parameters to change:
    list_of_z = [0.05, 0.125, 0.25, 0.56, 0.86, 1.1, 1.15, 1.5] #activities to run the system
    list_of_N_max = [int(4e9)]*8 # number of steps to run the simulation
    list_of_N_therm = [2000000, 2000000, 5000000,
                       5000000, 6000000, 14000000, 20000000, 20000000] # number of thermalization steps(Steps to reach thermal equlibrium)
    list_of_delta_N = [int(1e4)]*8 # number of steps the systems quantities are logged
    M = [64]*8 #size of computational domain
    L = [8]*8 #rodlength
    # ------------------------------------

    results = multiprocess(list_of_z, list_of_N_max,
                           list_of_N_therm, list_of_delta_N, M, L)

    # save data for further processing
    for result in results:
        z, grid, pos, N_plus, N_minus = result
        np.savetxt(f'grid_{z}.csv', grid)
        np.savetxt(f'pos_{z}.csv', pos)
        np.savetxt(f'obs_{z}.csv', (N_plus, N_minus))

