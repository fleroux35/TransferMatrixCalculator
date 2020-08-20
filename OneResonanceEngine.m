function [ polaritonEnergies ] = OneResonanceEngine(x,AngleData) %x is the quadruplet [wex,O0,neff,E0]

if size(AngleData,1) == 1

	AngleData = transpose(AngleData);
	
numberAngles = size(AngleData,1);

polaritonEnergies = zeros(numberAngles,2);

wex = x(1);
O0 = x(2);
neff = x(3);
E0 = x(4);

wcavAll = photonDispersionModel(neff,AngleData,E0);

for i = 1 : numberAngles

wcav = wcavAll(i);

%LP branch

polaritonEnergies(i,1) = (O0^2/2 - ((O0^2 + wcav^2 - 2*wcav*wex + wex^2)*(O0^2 + wcav^2 + 2*wcav*wex + wex^2))^(1/2)/2 + wcav^2/2 + wex^2/2)^(1/2);

%UP branch

polaritonEnergies(i,2) = (O0^2/2 + ((O0^2 + wcav^2 - 2*wcav*wex + wex^2)*(O0^2 + wcav^2 + 2*wcav*wex + wex^2))^(1/2)/2 + wcav^2/2 + wex^2/2)^(1/2);
 
end


end

