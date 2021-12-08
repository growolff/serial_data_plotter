# -*- coding: utf-8 -*-

import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
mpl.rcParams['text.usetex'] = True


class TSActuator():
    '''
        L = 44 # mm
        A = 1.5 # radio 'pivote' A en m
        R = 0.175 # radio cuerda trenzada 0.35 mm diametro
    '''
    def __init__(self, L,R,A,B=0):
        self.L = L # initial (untwisted) distance between string pivots
        self.A = A # pivot rad
        self.B = B # pivot rad
        self.R = R # string rad

    def x(self,alpha):
        return np.sqrt(self.L*self.L-self.A*self.A)-np.sqrt((self.L*self.L)-pow(self.A+self.R*alpha,2))

    def dx(self,alpha):
        a = self.A-self.B
        b = a + self.R*alpha
        return np.sqrt(self.L*self.L + b*b) - np.sqrt(self.L*self.L + a*a)

    def max_alpha(self):
        aux = np.sqrt(np.pi*np.pi+4)
        return (np.pi*self.L - self.A*aux)/(self.R*aux)

    def max_x(self):
        aux = np.sqrt(np.pi*np.pi+4)
        return np.sqrt(self.L*self.L-self.A*self.A) - (2*self.L/aux)

    def RT(self,alpha):
        num = np.sqrt(pow(self.L,2)-pow(self.A+self.R*alpha,2))
        den = self.R*(self.A+self.R*alpha)
        return num/den



#idx_me = TSActuator(L=44,A=1.5,R=0.175)
idx_me = TSActuator(L=36,A=1.5,R=0.175)
idx_mf = TSActuator(L=36,A=1.5,R=0.175)

ac = TSActuator(L=44,A=1.5,B=1,R=0.175)
ac1 = TSActuator(L=36,A=1.5,B=1,R=0.175)

def main():
    a_max = 500
    a = np.linspace(0,a_max,50)
    af = a
    aux = ac.A - ac.B + ac.R*af
    aux2 = np.sqrt(ac.L*ac.L + (ac.A-ac.B)*(ac.A-ac.B))
    aux3 = np.sqrt(ac.L*ac.L + aux*aux)
    faf = np.sqrt(pow(ac.L - aux3 + 2*aux2 ,2) - ac.L*ac.L)
    ae = (faf + ac.B - ac.A)/ac.R

    print(ae)

    plotAFAE(af,ae)
    #plotDX(af,ae)
    #plotX(a)
    #plotRT(a)

def plotAFAE(a,b):
    fig, ax = plt.subplots()
    # ax.plot(a,(act.L - y),'m.--',linewidth=1,markersize=3,color='magenta')
    # ax.plot(a,(act1.L - y1),'bo--',linewidth=1,markersize=3,color='blue')
    ax.plot(a,b,'m.--',linewidth=1,markersize=3,color='magenta')
    #ax.plot(b,(ac.L-y1),'bo--',linewidth=1,markersize=3,color='blue')
    #ax.plot(a,(ac.L-y),'bo--',linewidth=1,markersize=3,color='blue')

    ax.grid()
    ax.set_title("Acortamiento de la cuerda trenzada")

    #ax.set_xlabel('\frac{\alpha}{2*\pi} [vueltas]')
    #ax.set_ylabel("Distancia x(r'$\alpha$') [mm]")
    ax.set_xlabel("Angulo de rotación del motor " + "alpha/2PI [vueltas]")
    ax.set_ylabel("Distancia x(alpha) [mm]")

    #fig.savefig("figure1.pdf")
    plt.show()

def plotDX(a,b):
    y = ac.dx(a)
    y1 = ac1.dx(b)

    fig, ax = plt.subplots()
    # ax.plot(a,(act.L - y),'m.--',linewidth=1,markersize=3,color='magenta')
    # ax.plot(a,(act1.L - y1),'bo--',linewidth=1,markersize=3,color='blue')
    ax.plot(a,(y),'m.--',linewidth=1,markersize=3,color='magenta')
    ax.plot(b,(ac.L-y1),'bo--',linewidth=1,markersize=3,color='blue')
    #ax.plot(a,(ac.L-y),'bo--',linewidth=1,markersize=3,color='blue')

    ax.grid()
    ax.set_title("Acortamiento de la cuerda trenzada")

    #ax.set_xlabel('\frac{\alpha}{2*\pi} [vueltas]')
    #ax.set_ylabel("Distancia x(r'$\alpha$') [mm]")
    ax.set_xlabel("Angulo de rotación del motor " + "alpha/2PI [vueltas]")
    ax.set_ylabel("Distancia x(alpha) [mm]")

    #fig.savefig("figure1.pdf")
    plt.show()

def plotX(a):

    y_me = idx_me.x(a)
    y_mf = idx_mf.x(a)

    fig, ax = plt.subplots()
    # ax.plot(a,(act.L - y),'m.--',linewidth=1,markersize=3,color='magenta')
    # ax.plot(a,(act1.L - y1),'bo--',linewidth=1,markersize=3,color='blue')
    ax.plot(a,(y_mf),'m.--',linewidth=1,markersize=3,color='magenta')
    ax.plot(a,(idx_me.L-y_mf),'bo--',linewidth=1,markersize=3,color='blue')

    max_x = idx_me.max_x()
    max_alpha = idx_me.max_alpha()

    print("max_alpha: " + str(max_alpha))
    print("max_x: " + str(max_x))


    ax.grid()
    ax.set_title("Acortamiento de la cuerda trenzada")

    #ax.set_xlabel('\frac{\alpha}{2*\pi} [vueltas]')
    #ax.set_ylabel("Distancia x(r'$\alpha$') [mm]")
    ax.set_xlabel("Angulo de rotación del motor" + "alpha/2PI [vueltas]")
    ax.set_ylabel("Distancia x(alpha) [mm]")

    #fig.savefig("figure1.pdf")
    plt.show()

def plotRT(a):
    y = act.RT(a)
    y1 = act1.RT(a)

    fig, ax = plt.subplots()
    # ax.plot(a,(act.L - y),'m.--',linewidth=1,markersize=3,color='magenta')
    # ax.plot(a,(act1.L - y1),'bo--',linewidth=1,markersize=3,color='blue')
    ax.plot(a,(y),'m.--',linewidth=1,markersize=3,color='magenta')
    ax.plot(a,(y1),'bo--',linewidth=1,markersize=3,color='blue')

    ax.grid()
    ax.set_title("Razón de transmisión")
    #ax.set_xlabel("Angulo de rotación del motor" + r'\alpha/2PI [vueltas]')
    #ax.set_xlabel('\frac{\alpha}{2*\pi} [vueltas]')
    ax.set_ylabel("Distancia x(alpha) [mm]")

    #fig.savefig("figure1.pdf")
    plt.show()


if __name__ == '__main__':
    main()
