# stress_risk


# Session 1

* if no measurements before: 
  * Start the projector and eye-tracker 
  * Start the stimulus computer
* Put the forms ready.
* prepare button box configuration

## prepare task instructions script in single subject room

* Open `Windows PowerShell` by pushing the start button and type `powershell` and press enter.
* Activate the virtual environment:
   * go to folder by: `cd Documents\Gilles\virtualenv\Scripts\`
   * activate environment from there: `.\activate`
* Go to the experiment folder `cd C:\Users\Econ_Experiment\Documents\Maike_Renkert\2022StressRisk\fMRIMIST\risk_task\`
* Run the **instruction script**: `python instruct.py --settings macbook` (--> welcome screen comes up)

 --> now the subject goes into the single-subject room, fills our the forms and then does the instruction on the computer
 
## calibration
### set up calibration on *stimulus computer*
* on the *stimulus computer* :
  * Open `Windows PowerShell` by pushing the start button and type `powershell`
  * Go to the right directory: `cd .\Documents\SNS\Gilles\virtualenv\risk\Scripts`
  * Activate the environment: `.\activate` (the `.\` is important!)
  * run:  `python .\make_calibration_settings.py <subject number>`

### run calibration while anatomical scans
* subject is now in the scanner, MRI scan sequence is ready. 
* ?!? run `calibration.py` 

## risk-experiment
* prepare experiment settings
  * Go to the experiment folder cd `C:\Users\Econ_Experimenter\Documents\SNS\Gilles\tms_risk\experiment`
  * Use the calibration script to make a settings file for the task: `python make_trial_design.py <subject n> 1 1`.
* Now you can run the actual task with `task.py <subject n> <session> <run> --settings 3t`.
  * the script basically runs itself. Just:
    * Use q to exit the script after the last volume has been colleceted
    * Press escape when you see the calibration screen to exit the calibration phase and start the next run (unless you want to recalibrate, but during TMS you never want this).
    
After the last (6th) run, immediately run python payout.py <subject> <session> --settings 3t to show the subject how much money they made on this session. This should also be noted down on the 1st sheeft of the Google spreadsheet document.


* check movement while fMRI:
  * start: doubleclick on `QA` (Matlab file)
  * push `start acquisition`
  * what to take care of: lower right panel `Volume deviation`

# Session 2
* prepare scanner screen
  * open webcam (camera feedback; res.=1024x576; press 'start'; press on arrow box to make boarder disappear)
  * adjust position of webcam windwow: right boarder at left part of trolly, upper boarder at scanner cross
  * open background-grey-box (upper screen)

* experiment script
  * open Matlab, make sure you are in the right folder `C:\Users\Econ_Experiment\Documents\Maike_Renkert\2022StressRisk\fMRIMIST`
  * check `Risk_settings.m` (e.g. speedupfactor = 1 !!!) --> close again
  * start by typing `Risk_task_Wrapper(<sub ID>)`  
    * type in subject characterisitics
    * for condition: 0 = control, 1 = stress(MIST)
  * useful keys:
     * S = start
     * 
 
# additional 
  * basic scanning settings can also be checked on: Transfer-Computer --> `SNS-Lab/Documents/Allerlei_Nuetzliches/Studienparameter_2022.docx`
 
 *Note 1: you can find all these commands again in PowerShell by pressing `ctrl + r` and then start typing the command and you will find it in the shell history. 
Then just press `enter` to execute it. This takes way less time than actually typing everything out.*

*Note 2: For now we use the code for the tms project. We should at some point refine the instructions to the particularities of this experiment.*
* Create random trials for the calibration script: `python make_calibration_settings.py <subject number>`
* Run the **calibration task**: `python calibrate.py <subject n> 1 1 --settings macbook`
* We run this task during the
* The output of the calibration script will be in 
`C:\Users\Econ_Experiment\Documents\Gilles\tms_risk\experiment\logs\sub-<subject n>\ses-1\sub-<subject n>_ses-1_task-calibration_run-1_events.tsv` (*single subject computer*)
 
