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
import sys
import time
from discord.ext import commands 

BASEDIR = os.path.dirname(__file__)
load_dotenv(os.path.join(BASEDIR, '.env'))

intents = discord.Intents.default()
intents.message_content = True
client = commands.Bot(command_prefix="!", intents=intents, help_command=commands.DefaultHelpCommand())

URL = "https://api.touchnpay.fr/public/"

minutes = os.getenv("MINUTES")
timeout_menu = os.getenv("TIMEOUT_MENU")
list_machines = []

def get_available():
    """
    Parses the JSON data and returns the list of available and unavailable machines

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
                    if machine['machine_state'] == '0' and machine['machine_type'] != 'sec': #remove second part if you also want dryers
                        available_machines.append(machine["machine_name"])
                    elif machine['machine_state'] == '1' and machine['machine_type'] != 'sec': #remove second part if you also want dryers
                        unavailable_machines.append(machine)
                else:
                    logging.error("There is a problem with the parameter machine_state or machine_type, the program stops.")
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
    Returns:
        machines_msg_dates (list): end dates of the machines
    """
    count = 0
    machines_msg_dates = []

    for machine in unavailable_machines:
        if "duration_estimate" in machine and "started_at" in machine:
            machine_id = machine['machine_type']+ "_" + machine['machine_nbr']
            cron_job = CronTab(user=True)
            list_machines_min = list(cron_job.find_comment('{0}min'.format(minutes)))
            list_machines_dates = list(cron_job.find_comment(re.compile(r'{}'.format(machine_id))))
            
            duration_estimate = machine['duration_estimate'] + int(os.getenv("DELTA_ESTIMATE"))
            started_at = datetime.datetime.strptime(machine["started_at"], '%Y-%m-%dT%H:%M:%S.%fZ').replace(tzinfo=datetime.timezone.utc).astimezone()

            end_date = (started_at + datetime.timedelta(minutes=duration_estimate))
            end_date = end_date.replace(second = 0, microsecond = 0)

            current_time = datetime.datetime.now().replace(second = 0, microsecond = 0)
            delta = end_date - current_time.astimezone()
            end_date = end_date.strftime('%Y-%m-%d %H:%M:%S.%f')
            job_already_set = list(cron_job.find_time(end_date[14:16], end_date[11:13], None, None, None))

            if len(job_already_set) != 0:
                pass
            elif delta > datetime.timedelta(0):
                if len(list_machines_dates) >= 1:
                    cron_job.remove_all(comment=re.compile(r'{}'.format(machine_id)))
                    cron_job.write()
                arg = end_date[11:13]+end_date[14:16] if machine["special_val"] != "selected" else "9999"
                job = cron_job.new(command="python3 {0}/cronjob_laundromat.py {1} # {2}".format(BASEDIR, arg, machine_id))
                job.setall("%i %s * * *"% (int(end_date[14:16]), end_date[11:13]))
                cron_job.write()
                count += 1
                machines_msg_dates.append(machine['machine_name'] + " ends at " + end_date[11:13] + ":" + end_date[14:16])
 
            elif len(list_machines_min) == 0:
                job = cron_job.new(command="python3 {0}/cronjob_laundromat.py # {1}min".format(BASEDIR, minutes))
                job.setall("*/{0} * * * *".format(minutes))
                cron_job.write()
                machines_msg_dates.append(machine['machine_name'] + "'s cycle ended but the machine is still busy ")
            else:
                machines_msg_dates.append(machine['machine_name'] + "'s cycle ended but the machine is still busy ")
        else:
            logging.error("There is a problem with the parameter duration_estimate or started_at, the program stops.")
            exit()

    if count == len(unavailable_machines) and len(list_machines_min) >= 1:
        cron_job = CronTab(user=True)
        cron_job.remove_all(comment='{0}min'.format(minutes))
        cron_job.write()
    atexit.unregister(clean)
    return machines_msg_dates



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


class Select(discord.ui.Select):
    """
    Drop-down menu to select the available machine.
    Depending of the choice:
        - remove cron jobs
        - restart the free function
        - uses the busy_function to create the cron job of the selected machine
    """
    def __init__(self):
        options = []
        available_machines, unavailable_machines = get_available()
            
        for machine in unavailable_machines:
            options.append(discord.SelectOption(label=machine["machine_name"], emoji="🔴"))
        for machine in available_machines:
            options.append(discord.SelectOption(label=machine, emoji="🟢"))
        options.extend([discord.SelectOption(label="None, remove the cron jobs",emoji="🟡"),discord.SelectOption(label="None, restart the availability function",emoji="🟡")])
        super().__init__(placeholder="Select an option",max_values=1,min_values=1,options=options)

    async def callback(self, interaction: discord.Interaction):
        if self.values[0] == "None, remove the cron jobs":
            clean()
            await interaction.response.send_message("Cleaned!")
        elif self.values[0] == "None, restart the availability function":
            await interaction.response.send_message("!free")
            ctx = await client.get_context(interaction.message)
            clean()
            await free(ctx)

        else:
            available_machines, unavailable_machines = get_available()
            machine_selected = self.values[0][11:12]
            for machine in unavailable_machines:
                if "machine_nbr" in machine and machine["machine_nbr"] == str(machine_selected):
                    machine["special_val"] = "selected"
                    machine_msg_date = busy_machines([machine])
                    atexit.unregister(clean)
                    await interaction.response.edit_message(content="✨ Machine selected! " + machine_msg_date[0] + " ✨")

class SelectView(discord.ui.View):
    def __init__(self, *, timeout = int(timeout_menu)):
        super().__init__(timeout=timeout)
        self.add_item(Select())

@client.command()
async def free(ctx):
    """
    Control command of the Discord bot.
    Depending on machines availability, either send them along with the drop-down menu or uses busy_machines function.
    """
    cron_job = CronTab(user=True)
    list_machines_min = list(cron_job.find_comment('{0}min'.format(minutes)))
    list_machines_dates = list(cron_job.find_comment(comment=re.compile(r'{}_\d+'.format("mal"))))

    available_machines, unavailable_machines = get_available()
    if len(available_machines) != 0:
        clean()
        await client.get_channel(int(os.getenv("CHANNEL_ID"))).send("Here are the available machines (o˘◡˘o): " + str(available_machines))
        await machines(ctx)
        
    elif len(list_machines_min) >= 1 or len(list_machines_dates) >= 1:
        if len(sys.argv) > 1:
            arg = re.compile(sys.argv[1])
            for job in cron_job:
                if arg.search(str(job)):
                    cron_job.remove(job)
            cron_job.write()
        else:
            cron_job.remove_all(comment='{0}min'.format(minutes))
            cron_job.write()
        machines_msg_dates = busy_machines(unavailable_machines)
        for machine_msg in machines_msg_dates:
            await client.get_channel(int(os.getenv("CHANNEL_ID"))).send(machine_msg)

    else:
        await client.get_channel(int(os.getenv("CHANNEL_ID"))).send("There are no machines available. I'm creating the cron jobs ヽ(￣～￣ )/")
        machines_msg_dates = busy_machines(unavailable_machines)
        for machine_msg in machines_msg_dates:
            await client.get_channel(int(os.getenv("CHANNEL_ID"))).send(machine_msg)

@client.command() 
async def machines(ctx):
    """
    Control command of the Discord bot.
    Send the drop-down menu to select a machine.
    """
    clean()
    view=SelectView()
    await client.get_channel(int(os.getenv("CHANNEL_ID"))).send("""
    -----------------------------\nIn which machine did you put your laundry in?\nPlease select the machine AFTER dropping off your laundry
    """, view=view)
    await view.wait()

@client.command()
async def dates(ctx):
    """
    Control command of the Discord bot.
    Give the end dates of the machines without creating cron jobs
    """
    available_machines, unavailable_machines = get_available()
    machines_msg_dates = busy_machines(unavailable_machines)
    clean()
    for machine_msg in machines_msg_dates:
        await client.get_channel(int(os.getenv("CHANNEL_ID"))).send(machine_msg)


@client.command() 
async def stop_bot(ctx):
    """
    Control command of the Discord bot.
    Remove all cron jobs and disconnect the bot.
    """
    await ctx.send("Removing the laundromat cron jobs and disconnecting \(￣▽￣)/ ")
    clean()
    exit()

@client.command()
async def remove_jobs(ctx):
    """
    Control command of the Discord bot.
    Remove all cron jobs.
    """
    await ctx.send("Removing the laundromat cron jobs \(￣▽￣)/ ")
    clean()

if __name__ == '__main__':
    atexit.register(clean)
    client.run(os.getenv("TOKEN"))