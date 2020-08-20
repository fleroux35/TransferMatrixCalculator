function [x, ci] = Fitting2Resonance(AngleData, wLPdata, wMPdata, wUPdata, w1, w2, lbO10, ubO10, lbO20, ubO20, lbneff, ubneff, lbE0, ubE0, p_init)

% w1 and w2 are to be entered in eV
% lower and upper bounds on O1, O2 are to be entered in eV
% lower and upper bounds on neff are dimensionless
% lower and upper bounds on E0 are to be entered in eV

options = optimoptions('lsqcurvefit');

options.StepTolerance = 1e-16;
options.FunctionTolerance = 1e-16;
options.MaxIterations = 400;
options.MaxFunctionEvaluations = 1000;
options.OptimalityTolerance = 1e-16;

% lb is the lowerbound definition on all parameters x

lb = [w1, w2, lbO10, lbO20, lbneff, lbE0];

% ub is the upperbound definition on all parameters x

ub = [w1, w2, ubO10, ubO20, ubneff, ubE0];

fittingFunction = @(x,AngleData)TwoResonanceEngine(x,AngleData)

wLPdata = transpose(wLPdata);
wMPdata = transpose(wMPdata);
wUPdata = transpose(wUPdata);

wdata = [wLPdata,wMPdata,wUPdata];

[x,resnorm,resid,exitflag,output,lambda,J] = lsqcurvefit(fittingFunction, p_init, AngleData, wdata, lb, ub, options);

%Confidence Intervals on the Parameters

ci = nlparci(x,resid,'jacobian',J);

end