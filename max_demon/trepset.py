import trep
from trep import tx, ty, tz, rx, ry, rz
from max_demon.constants import *
import numpy as np
import trep.discopt

def build_system(torque_force=False):
    sys = trep.System()
    frames = [
        ty('yc',name=CARTFRAME, mass=M,kinematic=True), [ 
            rx('theta', name="pendulumShoulder"), [
                tz(L, name=MASSFRAME, mass=M)]]]
    sys.import_frames(frames)
    trep.potentials.Gravity(sys, (0,0,-g))
    trep.forces.Damping(sys, B)
    if torque_force:
        trep.forces.ConfigForce(sys, 'theta', 'theta-force')
    return sys
######begin SAC Setup#######
def proj_func(x):
    x[0] = np.fmod(x[0]+np.pi, 2.0*np.pi)
    if(x[0] < 0):
        x[0] = x[0]+2.0*np.pi
    x[0] = x[0] - np.pi
#####end SAC SETUP##########
    

#####begin LQR setup########   
def build_LQR(mvisys, sys, X0):
    qBar = np.array([0., 0.0]) 
    Q = np.diag([200,0,0,0])  
    R = 0.3*np.eye(1) 
    # Create discrete system
    TVec = np.arange(0, TF+DT, DT)
    dsystem = trep.discopt.DSystem(mvisys, TVec)
    xB = dsystem.build_state(Q=qBar,p = np.zeros(sys.nQd)) 
    # Design linear feedback controller
    Qd = np.zeros((len(TVec), dsystem.system.nQ)) 
    thetaIndex = dsystem.system.get_config('theta').index 
    ycIndex = dsystem.system.get_config('yc').index
    for i,t in enumerate(TVec):
        Qd[i, thetaIndex] = qBar[0] 
        Qd[i, ycIndex] = qBar[1]
        (Xd, Ud) = dsystem.build_trajectory(Qd) 
    Qk = lambda k: Q 
    Rk = lambda k: R 
    KVec = dsystem.calc_feedback_controller(Xd, Ud, Qk, Rk) 
    KStabil = KVec[0] #use first value to approx infinite horzion controller gain
    dsystem.set(X0, np.array([0.]), 0)
    return (KStabil, dsystem,xB)
#######end LQR setup

######begin trajecotry optimization setup
def generate_desired_trajectory(system, t, amp=0.):
    qd = np.zeros((len(t), system.nQ))
    theta_index = system.get_config('theta').index
    for i,t in enumerate(t):
        qd[i, theta_index] = 0.
    return qd

def generate_initial_trajectory(system, t, theta=0.,y=0.,ptheta = 0.,dy=0.):
    qd = np.zeros((len(t), system.nQ))
    dqk = np.zeros((len(t),system.nQk))
    dqd = np.zeros((len(t),system.nQd))
    theta_index = system.get_config('theta').index
    y_index = system.get_config('yc').index
    for i,t in enumerate(t):
        qd[i, theta_index] = theta
        qd[i, y_index] = y
        dqd[i,0]=ptheta
        dqk[i,0]= dy
    return qd,dqd,dqk
######end trajectory opt setup###
