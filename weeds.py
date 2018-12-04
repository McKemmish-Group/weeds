#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 11 17:02:10 2018

@author: z5190046
"""

import numpy as np
import matplotlib.pyplot as plt 
import pandas as pd
import seaborn as sns
from scipy import stats

def weeds(data1, intensity_cutoff, no_bins, scale):
    
    g_ns_dict = {'31P16O':2, '31P32S':2, '14N32S':3, '32S1H':2, '45Sc1H':16, '27Al16O': 6, '27Al18O': 6 , '26Al16O': 6}
    
    name1 = data1.split('_') 
    
    molecule = name1[1].split('/')[0]
#    print(molecule)

    
    if molecule in g_ns_dict:
        g_ns = (g_ns_dict[molecule])
    else: print('Molecule g_ns not in dictionary')
    
    data1_statestrans = {}
    join_statestrans(data1, data1_statestrans, g_ns)
   
    name = data1.split('K')
    csv_filename = name[0] + 'K.csv'
    
    write_csv(data1_statestrans, csv_filename)
    
    df = pd.read_csv(csv_filename)

    x = []
    y = []
#    print(df['Intensity'].max())
    for i in range(no_bins):
    #    print(i)
        cutoff = df['Intensity'].min()*(10**(i/(no_bins/15)))
        x.append(cutoff)
    #    print(cutoff)
        if scale == 'yes':
            y.append(df['Transition_ID'][df.Intensity >= cutoff].count()/len(df)) 
        else: 
            y.append(df['Transition_ID'][df.Intensity >= cutoff].count())
        
#    print(x,y)
    
    plt.plot(x,y, '-', label = molecule) #+ " " + name1[-1])
    plt.xlabel('Intensity cutoff')
#    plt.xlim(10**(-15),10**(-31))
    plt.ylabel('number of transitions')
    plt.title('weeds ' + name1[-2] + ' with a max rotational number of ' + name1[-3] + '.5')
    plt.xscale('log')
#    plt.yscale('log')

    return True


# function to join the states and trans file from DUO output and calculate the intensitives of all the transitions - output as a dictionary with teh transition as the key
# taskes input of the file name without extention, dictionary name, and the nuclear statistical weight factor for that molecule (g_ns)
def join_statestrans(data, statestrans, g_ns):
    
    import math
    
    statesdict = {}
    states = data + '.states'
    x = open(states, 'r')
    
    f = x.readline()
    #while loop to read through states file and split each line on the spaces 
    # store in a dictionary with the key as the ID and the whole line as a list as the value 
    # ID, states energy in cm^-1, state degeneracy , Total angular momentum J, Total parity, rotationless parity, state label, vibrational quantum number, projection of the electronic angular momentum, projection of the electronic spin, projection of the total angular momentum
    while f:
        g = f.split()
        #print(g)
        statesdict[int(g[0])] = g[:]
        f = x.readline()
    x.close()
    
    #T = 100 #K - set manually 
    #grab the temperature from the data file name 
    names = data.split('_')
    temp = names[-2].split('K') 
    T = float(temp[0])
    #constants 
    c2 = 1.43877736 #cm K from CODATA
    c = 29979245800.00 #cm/s
       
    #calculating Partition funciton - split equation up to make more clear for calculation 
    # Q(T) = g_ns \Sigma_i (2J_i + 1)exp(-c_2 * \bar{E_i} / T), c_2 = h c/k_B, \bar{E_i} = E_i/hc (in cm^-1 taken from .states file)
    q_T = 0
    for key in statesdict:
        first = (2 * float(statesdict[key][3])) + 1
        second = math.exp((-c2 * float(statesdict[key][1]))/T)
        q_T += first*second 
    Q_T = g_ns * q_T
    
#    print(len(statesdict))
#    print(len(statesdict[1]))
#    print(statesdict[1])
#    print(Q_T)
    
    #open trans file to add Einstien A and frequency (\bar{\nu}) (cm^-1) and calculate intensity (unitless?)
    trans = data + '.trans'
    x = open(trans, 'r')
    f = x.readline()
    g = f.split()
    
    #
    while f: 
        g = f.split()
#        print (g)
        #calculate the intensity of the transition - broken up into three steps
        #I = g_ns (2J_f + 1) A_fi / (8 pi c \bar{\nu}^2) exp(-c_2 * \bar{E_i} / T) (1 - exp(-c_2 * \bar{\nu_if} / T))/ Q_T
        one = g_ns * (2 * float(statesdict[int(g[0])][3]) + 1) * float(g[2]) /(8 * math.pi * c * (float(g[3]))**2)
        two = math.exp((-c2 * float(statesdict[int(g[1])][1]))/T)
        three = (1 - math.exp((-c2 * float(g[3]))/T))
        intensity = one * (two * three)/Q_T
        #create dictionary - key is transition as state_ID - state_ID
        if len(statesdict[1]) == 12:
            statestrans[statesdict[int(g[0])][0] + " - " + statesdict[int(g[1])][0]] = [float(statesdict[int(g[0])][1]),int(statesdict[int(g[0])][2]), float(statesdict[int(g[0])][3]), statesdict[int(g[0])][4],  statesdict[int(g[0])][5], statesdict[int(g[0])][6] + statesdict[int(g[0])][7] ,int(statesdict[int(g[0])][8]) ,int(statesdict[int(g[0])][9]), float(statesdict[int(g[0])][10]), float(statesdict[int(g[0])][11]), float(statesdict[int(g[1])][1]),int(statesdict[int(g[1])][2]), float(statesdict[int(g[1])][3]), statesdict[int(g[1])][4],  statesdict[int(g[1])][5], statesdict[int(g[1])][6] + statesdict[int(g[1])][7] ,int(statesdict[int(g[1])][8]), int(statesdict[int(g[1])][9]), float(statesdict[int(g[1])][10]), float(statesdict[int(g[1])][11]), float(g[2]), float(g[3]), intensity]
        elif len(statesdict[1]) == 11:
            statestrans[statesdict[int(g[0])][0] + " - " + statesdict[int(g[1])][0]] = [float(statesdict[int(g[0])][1]),int(statesdict[int(g[0])][2]), float(statesdict[int(g[0])][3]), statesdict[int(g[0])][4],  statesdict[int(g[0])][5], statesdict[int(g[0])][6] ,int(statesdict[int(g[0])][7]) ,int(statesdict[int(g[0])][8]), float(statesdict[int(g[0])][9]), float(statesdict[int(g[0])][10]), float(statesdict[int(g[1])][1]),int(statesdict[int(g[1])][2]), float(statesdict[int(g[1])][3]), statesdict[int(g[1])][4],  statesdict[int(g[1])][5], statesdict[int(g[1])][6] ,int(statesdict[int(g[1])][7]), int(statesdict[int(g[1])][8]), float(statesdict[int(g[1])][9]), float(statesdict[int(g[1])][10]), float(g[2]), float(g[3]), intensity]

        # value for each key is a list of all the information from the states file for each states then, Einstien A, frequency (\bar{\nu}) (cm^-1), intensity 
#        statestrans[statesdict[int(g[0])][0] + " - " + statesdict[int(g[1])][0]] = [float(statesdict[int(g[0])][1]),int(statesdict[int(g[0])][2]), float(statesdict[int(g[0])][3]), statesdict[int(g[0])][4],  statesdict[int(g[0])][5], statesdict[int(g[0])][6] + statesdict[int(g[0])][7] ,int(statesdict[int(g[0])][8]) ,int(statesdict[int(g[0])][9]), float(statesdict[int(g[0])][10]), float(statesdict[int(g[0])][11]), float(statesdict[int(g[1])][1]),int(statesdict[int(g[1])][2]), float(statesdict[int(g[1])][3]), statesdict[int(g[1])][4],  statesdict[int(g[1])][5], statesdict[int(g[1])][6] + statesdict[int(g[1])][7] ,int(statesdict[int(g[1])][8]), int(statesdict[int(g[1])][9]), float(statesdict[int(g[1])][10]), float(statesdict[int(g[1])][11]), float(g[2]), float(g[3]), intensity]
        f = x.readline()

    x.close()
    
    return statestrans





#function to write dictionary out to a csv file to use with pandas package 
def write_csv(original_mass, filename):
    #open file and set coloumn headings 
    y = open(filename, 'w')
    y.write("Transition_ID,") 
    y.write("Upper_energy,")
    y.write("Upper_degen,")
    y.write("Upper_J," )
    y.write("Upper_Tparity,")
    y.write("Upper_Rparity,")
    y.write("Upper_state,")
    y.write("Upper_v,")
    y.write("Upper_Lambda,")
    y.write("Upper_Sigma,")
    y.write("Upper_Omega,")
    y.write("Lower_energy,")
    y.write("Lower_degen,")
    y.write("Lower_J," )
    y.write("Lower_Tparity,")
    y.write("Lower_Rparity,")
    y.write("Lower_state,")
    y.write("Lower_v,")
    y.write("Lower_Lambda,")
    y.write("Lower_Sigma,")
    y.write("Lower_Omega,")
    y.write("Einstien_A,")
    y.write("Intensity,")
    y.write("wavenumber\n")

    #loop over keys in dictionary and write to file, keeping track of what is a string, float, or in scientific notation
    for key in original_mass:
        
        y.write(key + ",") 
        y.write("%6f," % original_mass[key][0])
        y.write("%.1f," % original_mass[key][1])
        y.write("%.1f," % original_mass[key][2])
        y.write(str(original_mass[key][3])+ ",")
        y.write(str(original_mass[key][4])+ ",")
        y.write(str(original_mass[key][5])+ ",")
        y.write("%.1f," % original_mass[key][6])
        y.write("%.1f," % original_mass[key][7])
        y.write("%.1f," % original_mass[key][8])
        y.write("%.1f," % original_mass[key][9])
        y.write("%.6f," % original_mass[key][10])
        y.write("%.1f," % original_mass[key][11])
        y.write("%.1f," % original_mass[key][12])
        y.write(str(original_mass[key][13])+ ",")
        y.write(str(original_mass[key][14])+ ",")
        y.write(str(original_mass[key][15])+ ",")
        y.write("%.1f," % original_mass[key][16])
        y.write("%.1f," % original_mass[key][17])
        y.write("%.1f," % original_mass[key][18])
        y.write("%.1f," % original_mass[key][19])
        y.write("%.6e," % original_mass[key][20])
        y.write("%.6e," % original_mass[key][22])
        y.write("%.6e\n" % original_mass[key][21])

    y.close()
    

molecules = ['14N32S', '32S1H', '31P16O_CURVES', '31P32S_CURVES', '45Sc1H', '27Al16O', '27Al18O', '26Al16O']

for i in range(len(molecules)):
    filename = 'Data_' + molecules[i] + '/' + molecules[i] + '_J10_100K_e-0'
    weeds(filename, 0, 1000, 'no')


plt.legend()
plt.show()



    
    
    

            
