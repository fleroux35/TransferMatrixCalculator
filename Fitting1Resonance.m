# Author: Florian Le Roux
function [x] = Fitting1Resonance(AngleData, wLPdata, wUPdata, w1, lbO10, ubO10, lbneff, ubneff, lbE0, ubE0, p_init) 

% lb is the lowerbound definition on all paramers x

lb = [w1, lbO10, lbneff, lbE0];

% ub is the upperbound definition on all paramers x

ub = [w1, ubO10, ubneff, ubE0];

wLPdata = transpose(wLPdata);

wUPdata = transpose(wUPdata);

wdata = [wLPdata, wUPdata];

fittingFunction = @(x,AngleData)OneResonanceEngine(x,AngleData);

%At this point we define the tolerance of the fit, the max number of irations

options = optimoptions('lsqcurvefit');

options.StepTolerance = 1e-18;
options.FunctionTolerance = 1e-18;
options.MaxIterations = 1000;
options.MaxFunctionEvaluations = 1000;
options.OptimalityTolerance = 1e-18;

[x,resnorm,resid,exitflag,output,lambda,J]= lsqcurvefit(fittingFunction, p_init, AngleData, wdata, lb, ub, options);
 
%Confidence Inrvals on the Paramers

ci = nlparci(x,resid,'jacobian',J);

erroronwex = round(x(1) - ci(1),3);
erroronOmega = round(x(2) - ci(2),3);
erroronneff = round(x(3) - ci(3),3);
erroronE0 = round(x(4) - ci(4),4);

end


