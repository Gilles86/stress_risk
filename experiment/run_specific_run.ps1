C:\ExpFiles\Maike\virtualenv\risk\Scripts\activate.ps1

cd C:\ExpFiles\Maike\stress_risk\experiment

$subject = Read-Host -Prompt 'Subject number'
$run = Read-Host -Prompt 'Run'

echo $subject
echo $run

python .\task.py $subject 1 $run --settings 3t
