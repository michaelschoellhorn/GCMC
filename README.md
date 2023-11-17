# GCMC
Code to perform a grand canonical monte carlo simulation of a system of hard rods in 2D. This simulation was created as a university course assignment. Therefore it should not be viewed as a ready-to-use code but as a showcase of the methods and the physics involved. 

## Features
Monte Carlo Insertion and Deletion with physically motivated probability

Multiprocessing capabilities for faster simulation execution

Reliance on numpy build-in functions and data structures for faster execution

## Physics
This code simulates a 2D system of hard rods on a grid with periodic boundary conditions. The goal was to show the emergence of separate phases when the activity of the system is increased. The activity in this context is a physically derived quantity which is proportional to the insertion probability of a rod. We hope to show that the system is isotropic for low activity values and ordered with distinct vertically/horizontally dominated phases for high values. To get meaningful data the system is only evaluated in thermal equilibrium.

## Code
The main simulation code is written in gcmc.py. Execute it first. Expect reasonably long runtimes dependant on the CPU you are using.
The simulation starts with an empty grid. For each pseudo timestep we then either insert or delete a vertical or horizontal rod of lenght L. 
The deletion or insertion is only accepted if:
1. There is space in case of the addition &
2. The corresponding insertion/deletion probability is greater than some randomly generated float in range [0, 1]

Otherwise nothing happens.

Since we start with an empty grid we need to thermalise the system first. This means we need to run the above scheme for Ntherm pseudo timesteps to make certain that the system is in thermal equilibrium. 
After this we take snapshots of the system in regular intervals to evaluate the quantities we're interested in.

To visualize the system, plotting.py can be executed after commenting in the functions you are interested in.

## Example Results
In the directory example_results one can find the results of the simulation. Endkongifuration is a snapshot of the system for different activities at the last timestep. Here you can see the rod configuration and the different phases. The N_thermal's show the thermalisation runs for different activities. Seta shows the phase transition by looking at the order parameter |S| against the packing density.
