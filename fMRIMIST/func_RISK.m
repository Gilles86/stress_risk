function a = func_RISK(SUBID, iRUN, MAC)
sessionID = 2;
flags2pass = [sprintf('%02d', SUBID) ' ' num2str(sessionID) ' ' num2str(iRUN)];

cmd = [];
if MAC == 1
    cmd = ['source ~/.zshrc; '];
    cmd = [cmd 'conda activate stress_risk; '];
    cmd = [cmd 'cd ~/git/risk_experiment/experiment; '];
    cmd = [cmd 'python ~/git/risk_experiment/experiment/mapper.py 1 1 --overwrite; '];

else
    orig_path = pwd;
    cmd = [cmd 'cd C:\ExpFiles\Maike\stress_risk\experiment & '];
    %cd C:\Users\Econ_Experimenter\Documents\SNS\Gilles\stress_risk\experiment
    cmd = [cmd 'C:\ExpFiles\Maike\virtualenv\risk\Scripts\python.exe ' [ 'C:\ExpFiles\Maike\stress_risk\experiment\task.py ' flags2pass ' --settings 3t --overwrite ']];
    cd(orig_path);
end
a = system(cmd, '-echo');


end