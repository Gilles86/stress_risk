#$subject=$args[0]o


C:\ExpFiles\Maike\virtualenv\risk\Scripts\activate.ps1

cd C:\ExpFiles\Maike\stress_risk\experiment

$subject = Read-Host -Prompt 'Subject number'

echo $subject

python make_calibration_settings.py $subject

python calibrate.py $subject 1 1 --settings 3t

python make_trial_design.py $subject 1 1

for ($i=1; $i -lt 7; $i++){
     python .\task.py $subject 1 $i --settings 3t
     echo $1
}

python payout.py $subject 1 --settings 3t