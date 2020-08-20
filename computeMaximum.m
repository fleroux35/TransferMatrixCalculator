# Author: Florian Le Roux
function [maxEnergy1, maxEnergy2] = computeMaximum(energies, curveName, midIndex)

curve = importdata(curveName)

if midIndex > 0
    
    tempcurve = abs(energies - midIndex)
    midValue = min(tempcurve)
    midPos = find(tempcurve == midValue)

else
    
    midValue = 0
    
end

if midPos > 0

    max1 = max(curve(1:midPos));
    
    max2 = max(curve(midPos:end));
    
    maxEnergy1Value = find(curve(1:midPos) == max1);
    
    maxEnergy2Value = find(curve(midPos:end) == max2);
    
    maxEnergy1 = energies(maxEnergy1Value);
    
    maxEnergy2 = energies(midPos + maxEnergy2Value);
    
else
    
    find(curve == midValue);

    max1 = max(curve);
    
    maxEnergy1Value = find(curve == max1);
            
    maxEnergy1 = energies(maxEnergy1Value);
    
    maxEnergy2 = 0; 

end

end

