function [ wcav ] = photonDispersionModel(neff, AngleData, w0)

%Formulas can be found in 'Polariton trap in microcavities with metallic
%mirrors 'Litinskaya and Agranovich 2012.

%wcavTMS is the first TM mode symmetric supported by the structure
%wcavTES is the first TE mode symmetric supported by the structure

numberAngles = size(AngleData,1);
wcav = zeros(numberAngles,1);

for i = 1 : numberAngles

wcav(i) = w0*(1-(sin((2*pi)*AngleData(i)/360)^2/(neff^2)))^(-(1/2));

end


end

