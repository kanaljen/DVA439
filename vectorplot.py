from matplotlib import pyplot as plt
import time
import numpy as np


def plotAsVectors(x,y,query=[],labelx='',labely=''):
    """ Creates a plot with vectors in the range [0,1] from x and y,
        also optionally a query, and axes labels"""
    zero = np.zeros(len(x))
    plt.quiver(zero, zero, x, y, angles='xy', scale_units='xy', scale=1)
    for i in range(0, len(x)):
        xy = tuple([x[i], y[i]+0.03])
        plt.annotate('d {} ({:3},{:3})'.format(i, x[i], y[i]),
                     xy=xy, textcoords='data',
                     horizontalalignment='center',
                     fontsize=10)
    if len(query) == 2:
        plt.quiver(0, 0, query[0], query[1], angles='xy', scale_units='xy', scale=1)
        xy = tuple([query[0], query[1] + 0.03])
        plt.annotate('query ({:3},{:3})'.format(query[0], query[1]),
                     xy=xy, textcoords='data',
                     horizontalalignment='center',
                     fontsize=10)
    plt.xlabel = labelx
    plt.ylabel = labely
    plt.xlim(-0.1, 1.1)
    plt.ylim(-0.1, 1.1)
    plt.axhline(0, color='black',linestyle='dotted')
    plt.axvline(0, color='black',linestyle='dotted')
    # ISO 8601 format as name
    plt.savefig('{}.png'.format(time.strftime("vp_%Y%m%dT%H%M%S")))
