# Laundromat machines availability script with cron jobs and a discord application 

Some laundromats allow you to retrieve machines status via their public gad.touchnpay.fr page.\
This script retrieve machines status via the API, if needed, creates cron jobs to periodically check the status and sends a discord notification when a machine is available.\
This script is useful during weekends, if like me, your residence has a laundromat with few machines and uses this application.

Example:\
![machines](https://github.com/01MI/Laundromat_machines_availability_script/assets/151965188/368e0e04-7f4e-4aa4-8950-2e013b079618)

## Prerequisites
1. You will need to install the librairies specified in requirements.txt

2. You will need to create a .env file with the following informations:
```
TOKEN = Discord bot token (Developper portal -> Applications -> Bot)
LAUNDROMAT_ID = the id after gad.touchnpay.fr/fr/public/material/
DELTA_ESTIMATE = minutes to add to the machine timer.
CHANNEL_ID = id of your discord channel (enable developer mode in advanced settings on your profile, right click on a channel, copy id)
MINUTES = will be used to set the cron job to periodically check when the machine has finished.
```

In my case, the time for a cycle given by the application is not accurate so I need to add ~10 min, so my DELTA_ESTIMATE = 10.\
After the machine has finished, I want the cron job to check every 5minutes, so MINUTES = 5

## Usage

Launch the main script:
```bash
python3 main.py
```
To check the availability, use "$free":
If there is at least one available machine, the script will return the name of the machine and exit.
![free_1](https://github.com/01MI/Laundromat_machines_availability_script/assets/151965188/b34b869c-9e9f-4cf3-bbbe-ca2a9e07f75f)

If no machines are available, it will create cron jobs:
1. If the machines have finished but are not availables, one cron job will be created and launched every X minutes (MINUTES var in the .env file).
2. If the machines haven't finished, cron jobs will be created and launch on the etablished date.
   ![free_2](https://github.com/01MI/Laundromat_machines_availability_script/assets/151965188/1013f055-32e3-4c46-bc1f-317ddc2455eb)

You can check the cron jobs with the command: 
```bash
crontab -l
```

To stop and remove all cron jobs, use "$stop":
![stop](https://github.com/01MI/Laundromat_machines_availability_script/assets/151965188/84e65f58-4cfc-401d-8c60-5e75183f1b90)

## To do



