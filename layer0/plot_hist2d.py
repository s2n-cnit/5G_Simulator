import numpy as np
import matplotlib.pyplot as plt

x = np.random.randn(50)
y = np.random.randn(50)

# b = np.

plt.hist2d(x,y, bins=100)

# plt.show()

plt.savefig("hist2d.pdf", bbox_inches='tight')