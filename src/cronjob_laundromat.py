from main import *
import sys

@client.event
async def on_ready():
    """
    Depending on machines availability, either send them or delete the current cron job and uses busy_machine function again.
    """
    #await client.get_channel(int(os.getenv("CHANNEL_ID"))).send("Checking") #debug
    available_machines, unavailable_machines = get_available()
    if len(available_machines) != 0: 
        await client.get_channel(int(os.getenv("CHANNEL_ID"))).send(available_machines)
    else:
        #await client.get_channel(int(os.getenv("CHANNEL_ID"))).send("Still no machines available (╥﹏╥)") #debug
        cron_job = CronTab(user=True)
        if len(sys.argv) > 1:
            arg = re.compile(sys.argv[1])
            for job in cron_job:
                if arg.search(str(job)):
                    cron_job.remove(job)
            cron_job.write()
        else:
            cron_job.remove_all(comment='{0}min'.format(minutes))
            cron_job.write()
        busy_machines(unavailable_machines)
    exit()

if __name__ == '__main__':
    client.run(os.getenv("TOKEN"))