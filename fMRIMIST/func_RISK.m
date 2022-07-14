function a = func_RISK(SUBID,sessionID, iRUN, MAC)

flags2pass = [num2str(SUBID) ' ' num2str(sessionID) ' ' num2str(iRUN)];

cmd = [];
if MAC == 1
    cmd = ['source ~/.zshrc; '];
    cmd = [cmd 'conda activate stress_risk; '];
    cmd = [cmd 'cd ~/git/risk_experiment/experiment; '];
    cmd = [cmd 'python ~/git/risk_experiment/experiment/mapper.py 1 1 --overwrite; '];

else
    orig_path = pwd;
    cmd = [cmd 'cd ' orig_path '\risk_task & '];
    %cd C:\Users\Econ_Experimenter\Documents\SNS\Gilles\stress_risk\experiment
    cmd = [cmd [ orig_path '\virtualenv\risk\Scripts\python.exe '] [ orig_path '\risk_task\task.py ' flags2pass ' --settings 3t --overwrite ']];
    cd(orig_path);
end
a = system(cmd, '-echo');


end