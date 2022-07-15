# stress_risk


## Run task instructions script in single subject room

* Start the stimulus computer
* Open `Windows PowerShell` by pushing the start button and type `powershell`
* Activate the virtual environment:
  * Go to the virtualenv directory: `cd .\Documents\Gilles\virtualenv\Scripts`
  * Activate the environment: `.\activate` (the `.\` is important!)
  * Go to the experiment folder `cd C:\USers\Econ_Experiment\Documents\Gilles\risk_experiment\experiment`
* Run the instruction script: `python instruct.py --settings macbook`
* Create random trials for the calibration script: `python make_calibration_settings.py <subject number>`
* Run the calibration script: `python calibrate.py <subject n> 1 1 --settings macbook`
* The output of the calibration script will be in 
`C:\USers\Econ_Experiment\Documents\Gilles\risk_experiment\experiment\logs\sub-<subject n>\ses-1\sub-<subject n>_ses-1_task-calibration_run-1_events.tsv` (*single subject computer*)
* Copy this file to *the scanner computer* via the network into `C:\USers\Econ_Experiment\Documents\Maike_Renkert\2022StressRisk\fMRIMIST\risk_task\logs\sub-<subject n>\ses-1\sub-<subject n>_ses-1_task-calibration_run-1_events.tsv` (*scanner computer*)

# Calibrate trials on stimulus computer
* Now open powershell on the *scanner computer* 
  * Open `Windows PowerShell` by pushing the start button and type `powershell`
  * Go to the right directory: `cd .\Documents\SNS\Gilles\virtualenv\risk\Scripts`
  * Activate the environment: `.\activate` (the `.\` is important!)
  * Go to the experiment folder `cd C:\USers\Econ_Experiment\Documents\Maike_Renkert\2022StressRisk\fMRIMIST\risk_task\`
* Use the calibration script to make a settings file for the task: `python make_trial_design.py <subject n> 1 1`.
* Now you can run the actual task with `task.py <subject n> <sessino> <run> --settings 3t`.

*Note 1: you can find all these commands again by pressing `ctrl + r`. Then start typing the command and you will find it in the shell history. \
Then just press `enter` to execute it. This takes way less time than actually typing everything out.*

*Note 2: For now we use the code for the tms project. We should at some point refine the instructions to the particularities of this experiment.*
