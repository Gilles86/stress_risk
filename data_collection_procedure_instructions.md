# stress_risk


# Session 1

* if no measurements before: 
  * Start the projector and eye-tracker 
  * Start the stimulus computer
* Put the forms ready **in the single subject room**.
* prepare button box configuration (green up --> yellow = index (choose pile 1), red = middle (choose pile 2))


## Prepare subject
 * Welcome the subject. Say your name and that you are the experimenter today. Explain that this is an experiment with 2 sessions. Whether they get invited for the second session depends on data quality. It's particularly important that they don't move in the scanner.
 * Bring them to the single subject room.
 * Ask them to fill in all the forms. If they have any questions come to you.
 * After they filled in all forms, check that they are eligible for the MRI scanner.
 * If all is OK, bring them to the changing room. 
 * Once they are changed, they can come to the single subject room again,

## Prepare task instructions script in single subject room

 * Put the instruction papers in the middle of the desk.
 * Open "Stress study isntructions"-shortcut. It should be on the Desktop. Otherwise, it can be found in `C:\Users\Public\Public Documents\stress_risk`.
 * Explain the subject to carefully read the instructions. After that they can perform the instruction task on the computer. "It should be pretty self-explanatory. Otherwise, don't hesitate to ask".
 * After they finish the instruction task, the subjects can be placed in the scanner room.
 
 ## Prepare task in scanner
 * Open "Track Screen 1" on the desktop
   * We use this program just to make sure the subject's eye is clearly visible. We *do not use it for calibration*.
 * Run the first Survey-scan.
 * During the survey you can already open the master script via the "Stress risk session 1"-shortcut on the desktop. 
   * It an also be found in `C:\Exp...\Maike\stress_risk`
 * Once the survey is done, *and you are sure that you don't have to move the subject*, start the eye tracker calibration by pressing `c`.
   ** Say the following to the subject: "*We are almost ready to start the first part of this session, but first we are going to calibrate the eye tracker. What I need you to do is slowly follow the dots on the screen with your eyes.*"
   ** Perform the calibration
 * Once the calibration is succesful, press `escape` to go to the main task.
 * Explain the subject what to do next: "We are now ready to start the first part of the session. We are going to do 4 runs of the task that you just practised. While you are doing the task, we are making anatomical scans, thus the scanner will be loud. It is very important that you don't move, in particular when you hear the scanner makings noises. After the 4th run, we will probably still be making some anatomical scans. During that time you can take a little break before the second part of the experiment begins. Just close your eyes if you want and try to relax. Press a button when you are ready to start"
 * Wait for the subject to start the task and then start the `T1w` and `FLAIR`-sequences.
 * After the anatomical scans are done press `q` to exit the first part of the session. Make sure your command window and your mouse are on the lower display.
 * You now get to see a psychometric graph of the behavior. Just close this graph to start the actual task.
 * Press `escape` to skip the eye tracking calibration (unless this is necessary for some reason).
 * Now tell the subject *"We are now ready to start the last part of the experiment. It consists of 6 more runs, so 30 minutes in total. Once you are ready to start, press a button."*.
 * Now you go over the 6 runs of the task. Just skip the eye tracking by pressing `escape` at the beginning of the task and `q` at the end of the task.
 * After closing the 6th run the 
 

 --> now the subject goes into the single-subject room, fills our the forms and then does the instruction on the computer
 
 
 ## Scanning


* check movement while fMRI:
  * start: doubleclick on `QA` (Matlab file)
  * push `start acquisition`
  * what to take care of: lower right panel `Volume deviation`


!!! after each scanning:
* copy new log files (behavioral data) to:'??/g_econ_department$/projects/2022/renkert_dehollander_aydogan_ruff_stressrisk/data/logs/'
* fill in the subject in the scanning overview table: https://docs.google.com/spreadsheets/d/133hnl9zbJ4RDN4olc57Q2fLO6ALtdK4T7De-kMySyug/edit#gid=0

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
 
