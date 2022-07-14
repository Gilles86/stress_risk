function func_payment_calc(SUBID,sessionID)

flags2pass = [num2str(SUBID) ' ' num2str(sessionID) ];

cmd = [];
orig_path = pwd;
cmd = [cmd 'cd ' orig_path '\risk_task & '];
%cd C:\Users\Econ_Experimenter\Documents\SNS\Gilles\stress_risk\experiment
cmd = [cmd [ orig_path '\virtualenv\risk\Scripts\python.exe '] [ orig_path '\risk_task\payout.py ' flags2pass ' --settings 3t ']];
cd(orig_path);


a = system(cmd, '-echo');




end