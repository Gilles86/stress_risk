C:\ExpFiles\Maike\virtualenv\risk\Scripts\activate.ps1

cd C:\ExpFiles\Maike\stress_risk\experiment

$subject = Read-Host -Prompt 'Subject number'

python payout.py $subject 1 --settings 3t