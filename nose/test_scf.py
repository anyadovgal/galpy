############################TESTS ON POTENTIALS################################
from __future__ import print_function, division
import os
import sys
import numpy
import pynbody
from galpy import potential
from galpy.potential import SCFPotential
from galpy.util import bovy_coords
from galpy.orbit import Orbit
_TRAVIS= bool(os.getenv('TRAVIS'))

EPS = 1e-13 ## default epsilon

DEFAULT_R= numpy.array([0.5,1.,2.])
DEFAULT_Z= numpy.array([0.,.125,-.125,0.25,-0.25])
DEFAULT_PHI= numpy.array([0.,0.5,-0.5,1.,-1.,
                       numpy.pi,0.5+numpy.pi,
                       1.+numpy.pi])

 
## tests whether scf_compute_spherical computes the correct coefficients for a Hernquist Potential
def test_scf_compute_spherical_hernquist():
    Acos, Asin = potential.scf_compute_coeffs_spherical(sphericalHernquistDensity, 10)
    spherical_coeffsTest(Acos, Asin)
    assert numpy.fabs(Acos[0,0,0] - 1.) < EPS, "Acos(n=0,l=0,m=0) = 1 fails. Found to be Acos(n=0,l=0,m=0) = {0}".format(Acos[0,0,0])
    
## tests whether scf_compute_spherical computes the correct coefficients for Zeeuw's perfect Potential
def test_scf_compute_spherical_zeeuw():
    Acos, Asin = potential.scf_compute_coeffs_spherical(rho_Zeeuw, 10)
    spherical_coeffsTest(Acos, Asin)
    assert numpy.fabs(Acos[0,0,0] - 2*3./4) < EPS, "Acos(n=0,l=0,m=0) = 3/2 fails. Found to be Acos(n=0,l=0,m=0) = {0}".format(Acos[0,0,0])
    assert numpy.fabs(Acos[1,0,0] - 2*1./12) < EPS, "Acos(n=1,l=0,m=0) = 1/6 fails. Found to be Acos(n=0,l=0,m=0) = {0}".format(Acos[0,0,0])
    
## Tests whether scf density matches with Hernquist density
def test_densMatches_hernquist():
    h = potential.HernquistPotential()
    Acos, Asin = potential.scf_compute_coeffs_spherical(sphericalHernquistDensity,10)
    scf = SCFPotential()
    assertmsg = "Comparing the density of Hernquist Potential with SCF fails at R={0}, Z={1}, phi={2}"
    compareFunctions(h.dens,scf.dens, assertmsg) 
    
## Tests whether scf density matches with Hernquist density
def test_densMatches_hernquist():
    Acos, Asin = potential.scf_compute_coeffs_spherical(rho_Zeeuw,10)
    scf = SCFPotential(amp=1, Acos=Acos, Asin=Asin)
    assertmsg = "Comparing the density of Zeeuw's perfect ellipsoid with SCF fails at R={0}, Z={1}, phi={2}"
    compareFunctions(rho_Zeeuw,scf.dens, assertmsg) 

## Tests whether scf potential matches with Hernquist potential
def test_potentialMatches_hernquist():
    h = potential.HernquistPotential()
    Acos, Asin = potential.scf_compute_coeffs_spherical(sphericalHernquistDensity,10)
    scf = SCFPotential()
    assertmsg = "Comparing the potential of Hernquist Potential with SCF fails at R={0}, Z={1}, phi={2}"
    compareFunctions(h,scf, assertmsg)
  
  
## Tests whether scf Rforce matches with Hernquist Rforce
def test_RforceMatches_hernquist():
    h = potential.HernquistPotential()
    Acos, Asin = potential.scf_compute_coeffs_spherical(sphericalHernquistDensity,10)
    scf = SCFPotential()
    assertmsg = "Comparing the radial force of Hernquist Potential with SCF fails at R={0}, Z={1}, phi={2}"
    compareFunctions(h.Rforce,scf.Rforce, assertmsg)
    
## Tests whether scf zforce matches with Hernquist Rforce
def test_zforceMatches_hernquist():
    h = potential.HernquistPotential()
    Acos, Asin = potential.scf_compute_coeffs_spherical(sphericalHernquistDensity,10)
    scf = SCFPotential()
    assertmsg = "Comparing the vertical force of Hernquist Potential with SCF fails at R={0}, Z={1}, phi={2}"
    compareFunctions(h.zforce,scf.zforce, assertmsg)
    
    
## Tests whether scf phiforce matches with Hernquist Rforce
def test_phiforceMatches_hernquist():
    h = potential.HernquistPotential()
    Acos, Asin = potential.scf_compute_coeffs_spherical(sphericalHernquistDensity,10)
    scf = SCFPotential()
    assertmsg = "Comparing the azimuth force of Hernquist Potential with SCF fails at R={0}, Z={1}, phi={2}"
    compareFunctions(h.phiforce,scf.phiforce, assertmsg)

## Checks Energy conservation for the SCF Hernquist Potential    
def test_scfHernquist_energyConserved():
    Acos, Asin = potential.scf_compute_coeffs_spherical(sphericalHernquistDensity,10)
    scf = SCFPotential()
    times= numpy.linspace(0.,280.,1001)
    o= Orbit(vxvv=[1.,0.1,1.1,0.,0.1])
    o.integrate(times,scf,method='odeint')
    tEs= o.E(times)
    
    assert (numpy.std(tEs)/numpy.mean(tEs))**2. < EPS, "SCF Hernquist Conserved Energy fails."
  

##############GENERIC FUNCTIONS BELOW###############

## This is used to compare scf functions with its corresponding galpy function
def compareFunctions(galpyFunc, scfFunc, assertmsg, Rs=DEFAULT_R, Zs = DEFAULT_Z, phis = DEFAULT_PHI, eps=EPS):
    ##Assert msg must have 3 placeholders ({}) for Rs, Zs, and phis                      
    for ii in range(len(Rs)):
        for jj in range(len(Zs)):
            for kk in range(len(phis)):
                assert numpy.fabs(galpyFunc(Rs[ii],Zs[jj],phis[kk]) - scfFunc(Rs[ii],Zs[jj],phis[kk])) < eps, \
                assertmsg.format(Rs[ii],Zs[jj],phis[kk])

##General function that tests whether coefficients for a spherical density has the expected property
def spherical_coeffsTest(Acos, Asin):
    ## We expect Asin to be zero
    assert numpy.all(numpy.fabs(Asin) <EPS), "Conforming Asin = 0 fails"
    ## We expect that the only non-zero values occur at (n,l=0,m=0)
    assert numpy.all(numpy.fabs(Acos[:, 1:, :]) < EPS) and numpy.all(numpy.fabs(Acos[:,:,1:]) < EPS), "Non Zero value found at outside (n,l,m) = (n,0,0)" 
    
    
## Hernquist potential as a function of r
def sphericalHernquistDensity(r):
    h = potential.HernquistPotential()
    return h.dens(r,0,0)

def rho_Zeeuw(R, z=0., phi=0., a=1.):
    r, theta, phi = bovy_coords.cyl_to_spher(R,z, phi)
    return 3./(4*numpy.pi) * numpy.power((a + r),-4.) * a