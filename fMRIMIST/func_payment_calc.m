function func_payment_calc(SUBID,sessionID)

flags2pass = [sprintf('%02d', SUBID) ' ' num2str(sessionID) ];

cmd = [];
orig_path = pwd;
cmd = [cmd 'cd C:\ExpFiles\Maike\stress_risk\experiment & '];
%cd C:\Users\Econ_Experimenter\Documents\SNS\Gilles\stress_risk\experiment
cmd = [cmd 'C:\ExpFiles\Maike\virtualenv\risk\Scripts\python.exe ' [ 'C:\ExpFiles\Maike\stress_risk\experiment\payout.py ' flags2pass ' --settings 3t ']];
cd(orig_path);


a = system(cmd, '-echo');




end