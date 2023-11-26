import discord
import os
import requests
import json
from dotenv import load_dotenv
import datetime
from crontab import CronTab
from zoneinfo import ZoneInfo
import logging
import atexit
import re
from discord.ext import commands

BASEDIR = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(BASEDIR, '.env'))

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

URL = "https://api.touchnpay.fr/public/"

minutes = os.getenv("MINUTES")

def get_available():
    """
    Parses the JSON file and returns the list of available and unavailable machines

    Returns:
        tuple of lists: available_machines, unavailable_machines
    """
    available_machines = []
    unavailable_machines = []

    response = requests.get(URL + os.getenv("LAUNDROMAT_ID"))
    if response.status_code == 200:
        json_data = json.loads(response.text)
        if type(json_data) == list:
            for machine in json_data:
                if "machine_state" in machine and "machine_type" in machine:
                    if machine['machine_state'] == '0' and machine['machine_type'] != 'sec': #remove the second part if you also want dryers included
                        available_machines.append(machine['machine_name'])
                    elif machine['machine_state'] == '1' and machine['machine_type'] != 'sec': #remove the second part if you also want dryers included
                        unavailable_machines.append(machine)
                else:
                    logging.error("There is a problem with parameter machine_state or machine_type, the program stops.")
                    exit()
            return available_machines, unavailable_machines
        else:
            logging.error("The type of json_data is not a list, the program stops.")
            exit()
    else:
        logging.error("An error occured while loading the page, the program stops.")
        exit()  
    

def busy_machines(unavailable_machines):
    """
    According to the states of the machines, create and delete cron jobs

    Parameters:
        unavailable_machines (list): machines currently unavailable
    """
    current_directory = os.getcwd()
    count = 0

    for machine in unavailable_machines:
        if "duration_estimate" in machine and "started_at" in machine:
            machine_id = machine['machine_type']+ "_" + machine['machine_nbr']
            cron_job = CronTab(user=True)
            list_machines_min = list(cron_job.find_comment('{0}min'.format(minutes)))
            list_machines_dates = list(cron_job.find_comment(re.compile(r'{}'.format(machine_id))))
            

            duration_estimate = machine['duration_estimate'] + int(os.getenv("DELTA_ESTIMATE"))
            started_at = datetime.datetime.strptime(machine["started_at"], '%Y-%m-%dT%H:%M:%S.%fZ').replace(tzinfo=datetime.timezone.utc).astimezone()

            finish_date = (started_at + datetime.timedelta(minutes=duration_estimate))
            finish_date = finish_date.replace(second = 0, microsecond = 0)

            current_time = datetime.datetime.now().replace(second = 0, microsecond = 0)
            delta = finish_date - current_time.astimezone()
            finish_date = finish_date.strftime('%Y-%m-%d %H:%M:%S.%f')
            job_already_set = list(cron_job.find_time(finish_date[14:16], finish_date[11:13], None, None, None))

            if len(job_already_set) != 0:
                pass
            elif delta > datetime.timedelta(0):
                if len(list_machines_dates) >= 1:
                    cron_job.remove_all(comment=re.compile(r'{}'.format(machine_id)))
                    cron_job.write()
                arg = finish_date[11:13]+finish_date[14:16]
                job = cron_job.new(command="python3 {0}/cronjob_laundromat.py {1} # {2}".format(current_directory, arg, machine_id))
                job.setall("%i %s * * *"% (int(finish_date[14:16]), finish_date[11:13]))
                cron_job.write()
                count += 1

            elif len(list_machines_min) == 0:
                job = cron_job.new(command="python3 {0}/cronjob_laundromat.py # {1}min".format(current_directory, minutes))
                job.setall("*/{0} * * * *".format(minutes))
                cron_job.write()

        else:
            logging.error("There is a problem with the parameter duration_estimate or started_at, the program stops.")
            exit()

    if count == len(unavailable_machines) and len(list_machines_min) >= 1:
        cron_job = CronTab(user=True)
        cron_job.remove_all(comment='{0}min'.format(minutes))
        cron_job.write()



def clean():
    """
    Remove all cron jobs
    """
    cron_job = CronTab(user=True)
    cron_job.remove_all(comment='{0}min'.format(minutes))
    cron_job.remove_all(comment=re.compile(r'{}_\d+'.format("mal")))
    cron_job.write()


@client.event
async def on_ready():
    logging.warning(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    """
    Control commands of the Discord bot.
    Depending on machines availability, either send them or uses busy_machine function.
    """
    print(message.content)
    if message.author == client.user:
        return
    if message.content.startswith('$free'):
        available_machines, unavailable_machines = get_available()
        if len(available_machines) != 0:
            await message.channel.send("Here are the machines available (o˘◡˘o): " + str(available_machines))
        else:
            await message.channel.send("There are no machines available. I'm creating the cron jobs ヽ(￣～￣ )/")
            busy_machines(unavailable_machines)
    if message.content.startswith('$stop'):
        await message.channel.send("Removing the cron jobs and disconnecting \(￣▽￣)/ ")
        exit()


if __name__ == '__main__':
        atexit.register(clean)
        client.run(os.getenv("TOKEN"))