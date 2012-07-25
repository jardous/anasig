#!/usr/bin/python
# -*- coding: utf-8 -*-

##from scipy import eye, bmat, isscalar
from types import IntType, LongType, ComplexType, FloatType
from Numeric import transpose, array, reshape, zeros
from LinearAlgebra import inverse
from Matrix import Matrix as bmat


def eye(size, typecode='d'):
    ary = zeros((size, size), typecode)
    for i in range(size):
        ary[i][i] = 1
    return ary


def isscalar(e):
    if type(e) in (IntType, LongType, ComplexType, FloatType):
        return True
    return False


class KalmanFilter:
    """ Kalman filter """
    def __init__( self, A, B, C, D, Q, R, x0, P0 ):
        """ initialize the Kalman filter object with given parameter
            A  - state transition matrix (NxN)
            B  - control input matrix (Nxp)
            C  - output matrix (qxN)
            D  - feedforward matrix (pxq)
            Q  - process covariance
            R  - observation noise covariance
            x0 - initial state estimate
            P0 - initial error covariance estimate
        """
        self.A = bmat( array(A, typecode='d') ) # NxN
        if self.A.shape[0] != self.A.shape[1]: # A must be NxN
            raise 'matrix A hat to be NxN'
        N = self.A.shape[0]
        self.B = bmat( array(B, typecode='d') ) # Nxp
        p = self.B.shape[1]
        if self.B.shape != (N, p):
            raise 'matrix B has to be Nxp'
        self.C = bmat( array(C, typecode='d') ) # qxN
        q = self.C.shape[0]
        if self.C.shape != (q, N):
            raise 'matrix C has to be qxN'
        self.D = bmat( array(D, typecode='d') ) # pxq
        if self.D.shape != (q, p):
            raise 'matrix C has to be qxp'

        self.states  = N  # N
        self.inputs  = p  # p
        self.outputs = q  # q

        # covariance matrixes
        # Q must be NxN
        if isscalar(Q):
            self.Q = bmat( eye(self.states, typecode='d') * Q )
        else:
            self.Q = bmat( array(Q, typecode='d') )

        if self.Q.shape != (N, N):
            raise 'matrix Q has to be NxN'
        # R must be qxq
        if isscalar(R):
            self.R = bmat( eye(self.outputs, typecode='d') * R )
        else:
            self.R = bmat( array(R, typecode='d') )

        if self.R.shape != (q, q):
            raise 'matrix R has to be qxq'

        # initial values
        self.x0 = bmat( array(x0, typecode='d') )       # Nxp
        if self.x0.shape != (N, p):
            raise 'vector x0 has to be Nxp'
        if isscalar(P0): # create matrix from scalar
            P0 = eye(N)*P0
        self.P0 = bmat( array(P0, typecode='d') )       # NxN
        if self.P0.shape != (N, N):
            raise 'vector P0 has to be NxN'

    def process(self, yv, u=None):
        # make column matrixes from vectors
        if u!=None:
            if len(u.shape) == 1:
                u = reshape( u, (u.shape[0], 1) )
        if len(yv.shape) == 1:
            yv = reshape( yv, (yv.shape[0], 1) )

        # data length
        LEN = yv.shape[0]
        
        x, P = self.x0, self.P0
        # output vectors
        y_est_out = zeros((LEN, self.outputs), typecode='d')
        x_out = zeros((LEN, self.states), typecode='d')
        P_out = []
        K_out = zeros((LEN, self.states), typecode='d')
        xa = transpose(x.array)
        x_out[0] = xa[0]
        P_out.append( P )
        ##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        ## loop through the entire data:
        ## Kalman filter algorithm core
        for i in range(0, LEN):
            # fetch values
            if u == None:
                uval = bmat(array([[0]]))
            else:
                uval = bmat(array([u[i,:]]))

            yvval = bmat(array([yv[i,:]]))

            y_est_out[i], x, K, P  = self.tick( yvval, uval, x, P )
            # make arrays from Matrixes
            xo = transpose(x.array)
            Po = P.array
            Ko = transpose(K.array)
            #x_out.append( x )
            x_out[i] = xo[0]
            #K_out.append( K )
            K_out[i] = Ko[0]#K[0,0]
            P_out.append( Po )
        ##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        return (y_est_out, x_out, K_out, P_out)

    def tick( self, yv_k, u_k, x, P ):
        """algorithm core - represents one cycle"""
        # estimate (time update)
        x_est = self.A*x + self.B*u_k
        #print "APAT:", (self.A*P*transpose(self.A)).array
        #print "Q", self.Q.array
        P_est = self.A*P*transpose(self.A) + self.Q
        #print "P_est", P_est.array

        # correction (measurement update)
        K = P_est*transpose(self.C) * inverse( self.C*P_est*transpose(self.C) + self.R )
        x = x_est + K*( transpose(yv_k) - self.C*x_est - self.D*u_k )
        P = (eye(self.states) - K*self.C) * P_est

        y_est = self.C*x + self.D*u_k

        return (y_est[0,0], x, K, P)


def test():
    #import numpy
    import pylab
    import random

    n_iter = 50
    #xorig = -0.23 # truth value (typo in example at top of p. 13 calls this z)
    # generate gaussian noise
    #z = [xorig]*n_iter
    #for i in range(len(z)):
    #    z[i] = random.gauss(xorig, 0.1) # observations (normal about x, sigma=0.1)
    #z = [0.840188,  0.394383,  0.783099]
    z = [0.840188  ,0.394383  ,0.783099]#  ,0.79844  ,0.911647  ,0.197551  ,0.335223  ,0.76823  ,0.277775  ,0.55397  ,0.477397  ,0.628871  ,0.364784  ,0.513401  ,0.95223  ,0.916195]
    z = array(z)

    Q = 1.#1e-5 # process variance
    R = 1.#0.1**2 # estimate of measurement variance, change to see effect

    # intial guesses
    x0 = 0.0
    P0 = 1.0

    kf = KalmanFilter([[1]], [[0]], [[1]], [[0]], Q, R, x0, P0)
    yest, x, K, P = kf.process(z)

    #print str(yest)
    #print str(x)
    print str(P)
    return


    yest = reshape( yest, (1, yest.shape[0]) ) [0].tolist()
    x = reshape( x, (1, x.shape[0]) ) [0].tolist()
    z = z.tolist()
    pylab.figure()
    pylab.plot(z,'k+', label='noisy measurements')
    #pylab.plot([xorig]*n_iter, 'r-',label='truth value')
    pylab.plot(yest,'b-', label='a posteriori estimate', linewidth=2)
    pylab.legend()
    pylab.savefig('kalmtest_web.png')

    import sys
    sys.exit(0)



    from matplotlib.pylab import *

    n = 128
    Q = 1.
    R = 1.

    w = load('w.txt')
    v = load('v.txt')
    yv = load('yv.txt')
    u = load('u.txt')
    ureq = load('ureq.txt')

    A, B, C, D = [[-6.,-25.], [1.,0.]], [[1.],[0.]], [[0., 1.]], [[0.]]
    #A, B, C, D = [[0.,0.], [0.,.]], [[1.],[0.]], [[0., 1.]], [[0.]]
    #A, B, C, D = [[1.]], [[1.]], [[1.]], [[0.]]

    yreal = yv

    kf = KalmanFilter(A, B, C, D, Q, R, [[0.], [0.]], eye(2))
    yest, x, K, P = kf.process(yv)#, u)

    rc('lines', linewidth=1.2)
    plot   ( range(n), yest, range(n), u, range(n), ureq, range(n), yreal,)
    legend ((       'yest',         'u',         'ureq',          'yreal'))
    #show()
    savefig('kalmtest.png')

if __name__ == "__main__":
    test()
