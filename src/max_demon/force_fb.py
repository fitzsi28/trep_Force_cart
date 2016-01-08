import numpy as np
from max_demon.constants import *

def sat_func(v):
    f = -15./(1.+np.exp(-1.0*(v-MAXVEL))) + 15./(1.+np.exp(1.0*(v+MAXVEL)))
    return f

def sat_u(ustar):
    if ustar>MAXSTEP: 
        ustar=MAXSTEP
    elif ustar<-MAXSTEP:
        ustar=-MAXSTEP
    return ustar

def wall_func(wall,prevq):
    f=np.array([0.,Kp*(wall-prevq[0])+Kd*(prevq[1]-prevq[0]),0.])
    return f