from main import *

@client.event
async def on_ready():
    """
    Depending on the state of the machines:
        - Uses part of the free function again to check availability.
        - Send a discord notification when you laundry is ready to be removed.
    """
    available_machines, unavailable_machines = get_available()
    
    cron_job = CronTab(user=True)
    list_machines_min = list(cron_job.find_comment('{0}min'.format(minutes)))
    list_machines_dates = list(cron_job.find_comment(comment=re.compile(r'{}_\d+'.format("mal"))))
    if len(available_machines) != 0:
        clean()
        await client.get_channel(int(os.getenv("CHANNEL_ID"))).send("Here are the available machines (o˘◡˘o): " + str(available_machines))
        view=SelectView()
        await client.get_channel(int(os.getenv("CHANNEL_ID"))).send("""
        -----------------------------\nIn which machine did you put your laundry in?\nPlease select the machine AFTER dropping off your laundry
        """, view=view)
        await view.wait()
        
    elif len(list_machines_min) >= 1 or len(list_machines_dates) >= 1:
        if len(sys.argv) > 1:
            arg = re.compile(sys.argv[1])
            for job in cron_job:
                if arg.search(str(job)):
                    cron_job.remove(job)
            cron_job.write()
        if sys.argv[1] == "9999":
            await client.get_channel(int(os.getenv("CHANNEL_ID"))).send("🔴 Cycle over! Please go pick up your laundry \(⌒▽⌒) 🔴")
            exit()
        else:
            cron_job.remove_all(comment='{0}min'.format(minutes))
            cron_job.write()
        machines_msg_dates = busy_machines(unavailable_machines)
    atexit.unregister(clean)
    exit()

if __name__ == '__main__':
    atexit.register(clean)
    client.run(os.getenv("TOKEN"))
