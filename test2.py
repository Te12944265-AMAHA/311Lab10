import numpy as np 

t = [[1,2,3],[1,2],[1]]
print(t)


a = np.array([[1,2,3],[4,5,6]])
b = np.vstack((a, a, a))
b[1] = np.array([0,0,0])
print(b)
print(False==-0)

hh = [[1,2,3],[4,5,6]]
print(np.flip(hh, 1))
hh2 = [[0 for c in range(3)] for r in range(2)]

hh2 = [[hh[i][j] if j == 1 else 6 for j in range(3)] for i in range(2)]
print(hh2)

lol = [(1,2),(3,4),(5,6)]
lol = np.array(lol)
print(lol)
ll = np.flip(lol, 1)
print(ll)
ll[:,0]=ll[:,0]*10
print(ll)
print(lol)

p = np.arange(-np.pi, np.pi+0.01, 1/2*np.pi)
print(p)
p = np.degrees(p)
print(p)
p = np.radians(np.array(hh))
print(p)

