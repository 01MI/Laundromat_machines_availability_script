# Laundromat machines availability script with cron jobs and a discord application 

## Context
Some laundromats allow you to retrieve machines status via their public gad.touchnpay.fr page.  

This script retrieve machines status via the API, if needed, creates cron jobs to periodically check the status and sends a discord notification when a machine is available.  
If a machine is available, a drop-down menu will be displayed. You can choose your machine after dropping of your laundry, then, a new cronjob will be created to notify you when to pick up your laundry.  
This script is useful during weekends, if like me, your residence has a laundromat with few machines and uses this application.

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

2. You will need to create a .env file with the following informations:
```
TOKEN = Discord bot token (Developper portal -> Applications -> Bot)
LAUNDROMAT_ID = Id after gad.touchnpay.fr/fr/public/material/
DELTA_ESTIMATE = Minutes to add to the machine time cycle.
CHANNEL_ID = Id of your discord channel (enable developer mode in advanced settings on your profile, right click on a channel, copy id)
MINUTES = Time to periodically check if the machines are still busy but their cycles is over.
TIMEOUT_MENU = Time to select your machine from the drop-down menu.
```

In my case, the time for a cycle given by the application is not accurate so I need to add ~10 min, so my DELTA_ESTIMATE = 10  
If a machine's cycle has ended but it's still not available, I want the cron job to check every 5minutes, so MINUTES = 5

## Usage

Launch the main script:
```bash
python3 main.py
```

* You can check all available commands with '!help'.

* To check the availability, use "!free":
If there is at least one available machine, the script will return the name of the machine and display a drop-down menu for you to select the machine you want to use, remove the cron jobs or stop the bot.  
   <table>
   <tr>
      <td valign="top"><img src="https://github.com/01MI/Laundromat_machines_availability_script/assets/151965188/baceeb66-7eba-4482-b47d-8b27861a6360" width="400"></td>
      <td valign="top"><img src="https://github.com/01MI/Laundromat_machines_availability_script/assets/151965188/781ee580-4396-4d37-aec4-3096c9923d01" width="400"></td>
   </tr>
   </table>

   If no machines are available, it will create cron jobs and send you the ends dates of the machines:
   1. If the machines have finished but are not availables, one cron job will be created and launched every X minutes (MINUTES var in the .env file).
   2. If the machines haven't finished, cron jobs will be created and launch on the estimate end date.  
   <table>
   <tr>
      <td valign="top"><img src="https://github.com/01MI/Laundromat_machines_availability_script/assets/151965188/fa2b82aa-a5aa-4058-9898-ec6bc85c7c76" width="400"></td>
      <td valign="top"><img src="https://github.com/01MI/Laundromat_machines_availability_script/assets/151965188/b4be204e-0829-4c28-bc06-cb0c99512b3a" width="400"></td>
   </tr>
   </table>

* If you only want to check the end dates of the machines without creating any cron jobs, use '!dates'  
  <img src="https://github.com/01MI/Laundromat_machines_availability_script/assets/151965188/8ad1c051-1d5f-4e4e-a9a1-b1e19e8e4e12" width="250">

* If you have already dropped of your laundry and want to select a machine, use '!machines' to display the drop-down menu:  
   <table>
   <tr>
      <td valign="top"><img src="https://github.com/01MI/Laundromat_machines_availability_script/assets/151965188/f7e6ba1b-329c-442f-a00a-d9f95eec7115" width="350"></td>
      <td valign="top"><img src="https://github.com/01MI/Laundromat_machines_availability_script/assets/151965188/7ab6d786-b57e-48da-b607-bae798ea3483" width="350"></td>
   </tr>
   </table>
  
* To remove all cron jobs, use '!remove_jobs'.  
  To stop the bot and remove all cron jobs, use "!stop_bot":  


You can check the cron jobs with the command:  
```bash
crontab -l
```

## To do





