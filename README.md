# Laundromat machines availability script with cron jobs and a discord application 

## Context
Some laundromats allow you to retrieve the status of machines via their public gad.touchnpay.fr page.\
This script is useful on weekends, especially if, like me, your residence has a laundromat with few machines and uses this web application.

This script retrieves machines statuses through the API and, if needed, creates cron jobs to periodically check the status and send a discord notification when a machine is available.\ 
If a machine is available, a drop-down menu will be displayed. You can choose your machine after dropping off your laundry, then a new cronjob will be created to notify you when to pick up your laundry.  


Example of the different states of a machine:  
<table>
   <tr>
      <td valign="middle"><img src="https://github.com/01MI/Laundromat_machines_availability_script/assets/151965188/d2b0c17a-3e67-4525-96c5-12667d607039" width="250"></td>
      <td valign="top"><img src="https://github.com/01MI/Laundromat_machines_availability_script/assets/151965188/7ea0abff-65e3-4a13-a5ce-54638a13928f" width="250"></td>
      <td valign="top"><img src="https://github.com/01MI/Laundromat_machines_availability_script/assets/151965188/de40fd5d-d0ab-426c-a78d-2c664d598a3a" width="250"></td>
   </tr>
</table>

## Prerequisites
1. You will need to install the dependencies specified in requirements.txt
```
pip3 install -r requirements.txt
```

3. You will need to create a .env file with the following information:
```
TOKEN = Discord bot token (Developper portal -> Applications -> Bot)
LAUNDROMAT_ID = Id after gad.touchnpay.fr/fr/public/material/
DELTA_ESTIMATE = Time in minutes to add to the machine time cycle.
CHANNEL_ID = Id of your discord channel (enable developer mode in advanced settings on your profile, right click on a channel, copy id)
MINUTES = Time in minutes to periodically check if the machines are still busy but their cycles is over.
TIMEOUT_MENU = Time in seconds to select your machine from the drop-down menu.
```

In my case, the time for a cycle given by the application is not accurate so I need to add ~10 min, so my DELTA_ESTIMATE = 10  
If a machine's cycle has ended but it's still not available, I want the cron job to check every 5minutes, so MINUTES = 5

## Usage

Launch the main script:
```bash
python3 src/main.py
```

* You can check all available commands with '!help'.

* To check the availability, use "!free":
If there is at least one available machine, the script will return the name of the machine and display a drop-down menu for you to select the machine you want to use, remove the cron jobs or stop the bot.  
   <table>
   <tr>
      <td valign="top"><img src="https://github.com/01MI/Laundromat_machines_availability_script/assets/151965188/96c7c6bc-cb65-4941-bc48-31333573b08f" width="400"></td>
      <td valign="top"><img src="https://github.com/01MI/Laundromat_machines_availability_script/assets/151965188/d42fcd32-efcf-4fc6-8d39-52f5bcd5a0eb" width="400"></td>
   </tr>
   </table>

   If no machines are available, it will create cron jobs and send you the ends dates of the machines:
   1. If the machines have finished but are not available, one cron job will be created and launched every X minutes (MINUTES var in the .env file).
   2. If the machines haven't finished, cron jobs will be created and launch on the estimate end date.  
   <table>
   <tr>
      <td valign="top"><img src="https://github.com/01MI/Laundromat_machines_availability_script/assets/151965188/dc25711b-c5d1-407e-9511-8709270126e6" width="400"></td>
      <td valign="top"><img src="https://github.com/01MI/Laundromat_machines_availability_script/assets/151965188/b4be204e-0829-4c28-bc06-cb0c99512b3a" width="400"></td>
   </tr>
   </table>
   
* If you only want to check the end dates of the machines without creating any cron jobs, use '!dates':
  <img src="https://github.com/01MI/Laundromat_machines_availability_script/assets/151965188/8ad1c051-1d5f-4e4e-a9a1-b1e19e8e4e12" width="250">

* If you have already dropped off your laundry and want to select a machine, use '!machines' to display the drop-down menu:  
   <table>
   <tr>
      <td valign="top"><img src="https://github.com/01MI/Laundromat_machines_availability_script/assets/151965188/f7e6ba1b-329c-442f-a00a-d9f95eec7115" width="350"></td>
      <td valign="top"><img src="https://github.com/01MI/Laundromat_machines_availability_script/assets/151965188/7ab6d786-b57e-48da-b607-bae798ea3483" width="350"></td>
   </tr>
   </table>
  
* To remove all cron jobs, use '!remove_jobs'.  
  To stop the bot and remove all cron jobs, use "!stop_bot":




