#Compound beam overview plots of QA

from __future__ import print_function

__author__="E.A.K. Adams"

"""
Functions for producing compound beam plots
showing an overview of data QA
"""

from astropy.io import ascii
from matplotlib.patches import Circle
from matplotlib.collections import PatchCollection
import matplotlib.pyplot as plt
import numpy as np

def make_cb_plot(filename,column,goodrange=None,
                 boolean=False,cboffsets='cb_offsets.txt'):
    """
    Take a csv file and produce the plots
    Provide the column name to plot
    Optionally provide a range of good values that 
    will have beams plotted in green
    Or set boolean=True to plot colors based on a boolean value
    Lack of data in plotted in grey
    Default is to plot as red
    Color scheme should be updated to 
    take into account colorblindness
    """
    #read the csv file
    table = ascii.read(filename,format='csv')
    print(table.colnames)
    #check that column name exists:
    if column in table.colnames:
        pass
    else:
        #select a column, assume first column is beams
        print(('Warning! Column name {0} not found.'
               ' Using third column of csv, {1} as default.'.format(column,
                                                                     table.colnames[2])))
        column = table.colnames[2]
    #make an array to hold colors:
    colors = np.full(40,'r')
    #find empty beams
    #'exist' column is read as strings
    nanind = np.where(table['exist'] == 'False')[0]
    colors[nanind] = 'k'
    #find "good" values
    if goodrange != None:
        if len(goodrange) == 2:
            #first turn good data into floats:
            goodind = np.where(np.logical_and(table[column]>=goodrange[0],
                                              table[column]<=goodrange[1]))[0]
            #goodind = np.where(table[column]>=goodrange[0])[0]
            print(goodind)
            colors[goodind] = 'green'
    if boolean == True:
        #assume column array is true/false
        #find trues and make green
        goodind = np.where(table[column] == 'True')[0]
        colors[goodind] = 'green'
    #get the beams
    cbpos = ascii.read(cboffsets)
    #open figure
    fig,ax = plt.subplots(figsize=(8,8))
    ax.axis([1.75,-1.75,-1.75,1.75]) #RA axis runs backwards
    #set up beams
    beams = []
    r = 0.2 #beam size
    for i,(x1,y1) in enumerate(zip(cbpos['ra'],cbpos['dec'])):
        if i == 0:
            #offset beam 0
            x1 = 1.5
            y1 = -1.5
        #set circle
        circle = Circle((x1,y1),r,color=colors[i],alpha=0.4)
        fig.gca().add_artist(circle)
        #beams.append(circle)
        #write text with value
        ax.text(x1,y1,('CB{0:02}\n'
                       '{2}').format(table['beam'][i],column,
                                           str(table[column][i])),
                horizontalalignment='center',
                verticalalignment='center')
    #p=PatchCollection(beams, alpha=0.4)
    #ax.add_collection(p)
    ax.set_xlabel('RA offset, deg')
    ax.set_ylabel('Dec offset, deg')
    ax.set_title('{}'.format(column))
    plt.savefig('cb_overview_{}.png'.format(column))
