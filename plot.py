from matplotlib import pyplot as plt
import matplotlib.cm as cm
import numpy as np

#fig = plt.figure()
#fig.add_subplot(111)

A = -0.75, -0.25, 0, 0.25, 0.5, 0.75, 1.0
B = 0.73, 0.97, 1.0, 0.97, 0.88, 0.73, 0.54
colors = cm.rainbow(np.linspace(0, 1, len(A)))
zero = np.zeros(len(A))

plt.quiver(zero, zero, A, B, angles='xy', scale_units='xy', scale=1,color = colors)
for i in range(0,len(A)):
    xy = tuple([A[i],B[i]])
    plt.annotate('line {} ({:3},{:3})'.format(i,A[i],B[i]),
                xy=xy, textcoords='data',
                 horizontalalignment='center',
                 fontsize=8)
plt.xlabel('population')
plt.ylabel('sweden')
plt.xlim(0, 1.2)
plt.ylim(0, 1.2)

plt.savefig('plots.png')
plt.show()