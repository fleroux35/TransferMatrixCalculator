# Author: Florian Le Roux   
class FitInfo():
    
#this class prepares all the info necessary for fitting
    def __init__(self, fitOrderName, polarization, nbOfResonances, Resonances, lowerBounds, upperBounds, Emin, Emax, Zmin, Zmax, colormap):
                                              
        self.fitOrderName = fitOrderName
        self.polarization = polarization
        self.nbOfResonances = nbOfResonances
        self.Resonances = Resonances
        self.lowerBounds = lowerBounds
        self.upperBounds = upperBounds
        self.Emin = Emin
        self.Emax = Emax
        
        #for display purposes:
        
        self.Zmin = Zmin
        self.Zmax = Zmax
        self.colormap = colormap
