# -*- coding: utf-8 -*-
"""
Created on Thu Sep 08 15:39:44 2016

@author: admin_lab
"""


import numpy as np
import warnings
import os
import mpl_toolkits.mplot3d
import matplotlib.pyplot as pp

np.set_printoptions(precision=4)

warnings.simplefilter(action = "ignore", category = FutureWarning)




def sinewave(frequency=1.0, offset=0, samples=1000.0):
    samples=samples/frequency
    t = np.linspace(0,2*np.pi,samples)
    y = np.sin(t+offset*np.pi/180)[:,None]
    return y

#    #if caio.get_ao_range_for_channel() == 0: ao_range=10.0
#    #only 10V ao_range possible for our device             
#    ao_range=10.0
#    actual_s = self.sampling_count
#    fs = self.fs
#    actual_volt = ao_range * actual_s/fs

def constant(amplitude=0.0):
    return amplitude*np.ones((1, 1))

def writebuffer(x=None, y=None, z=None):             
    empty   = np.zeros((1,1))
    a       = type(empty)
    rows    = np.shape(empty)[0] 
    
    if x is None: x = empty
    if y is None: y = empty
    if z is None: z = empty
    
    v= x, y, z    

    
    
    #check if x,y,z are arrays        
    if any([type(i) != a for i in v]):
       print 'writebuffer(x,y,z): Input arguments must be arrays of same length'
       return 'Error'
        
    # no argument >> return only zeros
    if all([np.array_equal(i, empty) for i in v]): 
        return np.hstack((empty,empty,empty))
    else:
    #use rows from non-empty argument
        for i in v:
            if not (np.array_equal(i, empty)): 
                rows = np.shape(i)[0]
    #and append zeros if no argument is given
        for i in v:         
            if (np.array_equal(i, empty)):             
                i.resize((rows,1), refcheck=False)

    
    if (np.shape(x) != np.shape(y)) or (np.shape(y) != np.shape(z)) or (np.shape(z) != np.shape(x)):
        print 'writebuffer(): Shape of the input arrays differ:'     
        return 'Error'
    else:
        return np.hstack((x,y,z))


def direction(axis, mode, amp=1.0, freq=1.0, samp=1000.0, calibration=[0.01,0.01,0.01]):
                
    #use list with calibration factors [x,y,z]
    x_cal = calibration[0]
    y_cal = calibration[1]
    z_cal = calibration[2]


    #calculate sine signals
    if (mode =='rotate'):    
        a = amp*sinewave(frequency=freq, offset=0, samples=samp)    
        b = amp*sinewave(frequency=freq, offset=90, samples=samp)
        b_neg = amp*sinewave(frequency=freq, offset=270, samples=samp)

    #return signals
    if (axis == 'x'):
        if (mode == 'constant'): 
            return writebuffer(x=constant(x_cal*amp))
        elif (mode == 'rotate'):
            return writebuffer(y=y_cal*a,z=z_cal*b)
    if (axis == '-x'):
        if (mode == 'constant'): 
            return writebuffer(x=constant(x_cal*(-1)*amp))
        elif (mode == 'rotate'):
            return writebuffer(y=y_cal*a,z=z_cal*b_neg)
            
    if (axis == 'y'):
        if (mode == 'constant'): 
            return writebuffer(y=constant(y_cal*amp))
        elif (mode == 'rotate'):
            return writebuffer(x=x_cal*a,z=z_cal*b)
    if (axis == '-y'):
        if (mode == 'constant'): 
            return writebuffer(y=constant(y_cal*(-1)*amp))
        elif (mode == 'rotate'):
            return writebuffer(x=x_cal*a,z=z_cal*b_neg)
            
    if (axis == 'z'):
        if (mode == 'constant'): 
            return writebuffer(z=constant(z_cal*amp))
        elif (mode == 'rotate'):
            return writebuffer(x=x_cal*a, y=y_cal*b)
    if (axis == '-z'):
        if (mode == 'constant'): 
            return writebuffer(z=constant(z_cal*(-1)*amp))
        elif (mode == 'rotate'):
            return writebuffer(x=x_cal*a,y=y_cal*b_neg) 
              
    else:
        print 'direction(): Input wrong, use string as axis and mode'
        return writebuffer(constant(0))
        
    
def list_f_ext(directory, extension):
    out=[]
    for f in os.listdir(directory):
        if f.endswith('.' + extension):
            out.append(f)
    return out


def spherical_points(npoints, ndim=3):
    # create random points on unit sphere
    vec = np.random.randn(ndim, npoints)
    vec /= np.linalg.norm(vec, axis=0)
    return vec.T

def golden_spiral(num_pts=100):
    # Derived from the golden spiral method from
    # https://stackoverflow.com/questions/9600801/evenly-distributing-n-points-on-a-sphere
    # -----------
    # IMPORTANT: theta and phi are swapped sometimes
    # +++++++ NOW IN PHYSICAL/ISO COORDINATES ++++++++++
    # -----------

    # subtract two points from the trajectory to manually insert theta/phi = (0,0) in the end
    # num_pts -= 2
    #create indices
    indices = np.arange(0, num_pts, dtype=float) + 0.5
    #create theta and phi
    theta = np.arccos(1 - 2*indices/num_pts) #from 0 ti Pi
    phi = np.mod((1 + 5**0.5) * indices, 2*np.pi) #from 0 to 2Pi

    #calculate x,y,z
    x = np.cos(phi) * np.sin(theta)
    y = np.sin(phi) * np.sin(theta)
    z = np.cos(theta)

    #create a trajectory with connecting "nearest" neighbor point
    vec = np.vstack((x, y, z)).T.round(15)
    v1= vec[1::2]   #rows with odd indices
    v2 = vec[::2]   #rows with even indices
    backandforth = np.vstack((v1, v2[::-1])) #stack v2 in reversed order to avoid jumping

    #get theta phi
    thetaphi =  np.vstack((theta, phi)).T.round(15)
    tp1= thetaphi[1::2]   #rows with odd indices
    tp2 = thetaphi[::2]   #rows with even indices
    thetaphi = np.vstack((tp1, tp2[::-1])) #stack v2 in reversed order to avoid jumping

    # #manually add theta=phi=0 and theta=180, phi=0 --> (x, y, z)==(0,0,1) or (0,0,-1)
    # thetaphi = np.insert(thetaphi, 0, [0,0], 0)
    # backandforth = np.insert(backandforth, 0, [0,0,1], 0)
    # halfidx=(num_pts/2)
    # thetaphi = np.insert(thetaphi, halfidx, [0,np.pi] ,0)
    # backandforth = np.insert(backandforth, halfidx, [0,0,-1], 0)

    # #this would be a vector with a trajectory going bck and forth
    # field = vec.repeat(2, axis=0)
    # field[::2] = [0, 0, 0]
    # #-- plot trajectory 1 and two --
    # pp.figure().add_subplot(111, projection='3d').plot(v1[:,0], v1[:,1], v1[:,2], 'o-')
    # pp.figure().add_subplot(111, projection='3d').plot(v2[:,0], v2[:,1], v2[:,2], 'o-')
    # #----------- plot scatter-line of full trajectory and field vector ---------
    # pp.figure().add_subplot(111, projection='3d').plot(backandforth[:, 0], backandforth[:, 1], backandforth[:, 2], 'o-')
    # pp.title('trajectory for n=%d points' % (num_pts))
    # pp.figure().add_subplot(111, projection='3d').plot(field[:, 0], field[:, 1], field[:, 2], 'r-')
    # pp.title('orientation of field vector')
    # pp.show()
    #
    # np.savetxt("C:\Users\sachs\testraw_N" + str(num_pts) + ".csv", np.hstack((thetaphi, backandforth)), delimiter=",")

    return backandforth


def traj_on_sphere(npoints):
    #not evenly distirbuted!
    pts = np.zeros((npoints,3))

    theta = np.deg2rad(np.linspace(0,180,npoints/2)) #half sphere would be 0-90deg
    phi = np.deg2rad(np.linspace(0,360,npoints/2))

    cnt=0
    for the_tmp in theta:
        for phi_tmp in phi:
            x = np.sin(theta) * np.cos(phi)
            y = np.sin(theta) * np.sin(phi)
            z = np.cos(theta)

            pts[cnt, :] = np.hstack((x,y,z))
            cnt+=1
    return pts

def circleXY(n_points):
    x=sinewave(frequency=1.0, offset=0, samples=n_points)
    y=sinewave(frequency=1.0, offset=90, samples=n_points)
    z=np.zeros((n_points,1))
    ptsXYZ=np.hstack((x,y, z))
    return ptsXYZ
