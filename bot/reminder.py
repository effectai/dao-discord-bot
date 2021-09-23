
import arrow
from modules.eos import get_config, get_cycle
from apscheduler.events import EVENT_JOB_ERROR
from bot.admin import Admin
import logging
from settings.defaults import CHANNEL_IDS
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from discord.ext import commands


logger = logging.getLogger(__name__)

class Reminder(commands.Cog):
    """Reminder messages"""

    def __init__(self, bot, db):
        self.bot = bot
        self.db = db
        self.scheduler = AsyncIOScheduler()

    async def notify_vote_duration(self):        
        now = arrow.utcnow()
        config = get_config()
        cycle = get_cycle(config['current_cycle'])
        started_at = arrow.get(cycle['start_time'])

        vote_duration = arrow.get(started_at.timestamp() + config['cycle_voting_duration_sec'])
        vote_duration_str = vote_duration.humanize(now, granularity=["day", "hour", "minute"])
        vote_duration_dt = vote_duration.format("D MMMM YYYY HH:mm:ss ZZZ")


        for channel_id in CHANNEL_IDS:
            channel = self.bot.get_channel(CHANNEL_IDS[channel_id])

            await channel.send(f"The current vote duration is almost over! **VOTE** while you still can on https://dao.effect.network/proposals\nThe vote duration ends at {vote_duration_dt} (**{vote_duration_str}**)")

    async def notify_dao_call(self):

        for channel_id in CHANNEL_IDS:
            channel = self.bot.get_channel(CHANNEL_IDS[channel_id])
            
            await channel.send(f":warning:The weekly DAO CALL is starting:bangbang: Join us in the voice channel:warning:")

    @commands.command(hidden=True)
    async def reschedule(self, ctx, trigger='cron | date', job_id="job_id", *args):
        """Reschedule reminders to a different time."""
        func = None
    
        if not Admin._sender_is_effect_member(ctx):
            return 
        
        job = self.scheduler.get_job(job_id=job_id)

        if not job:
            if job_id == "dao_call_notify": func = self.notify_dao_call
            elif job_id == "dao_vote_notify": func = self.notify_vote_duration

        try:
            if trigger == 'cron':
                day_of_week, hour, minute = args

                # for the reschedule_job you need first 3 chars of the weekdays.
                if len(day_of_week) <= 3: return 
                elif len(day_of_week) > 3: day_of_week = day_of_week[0:3]

                # create job when there is no job, else reschedule.
                if not job:
                    self.scheduler.add_job(func, trigger='cron', day_of_week=day_of_week, hour=hour, minute=minute, id="dao_call_notify")
                    return await ctx.send(f"Job did not exist, created new one: **{job_id}**")
                
                else:
                    self.scheduler.reschedule_job(job_id, trigger='cron', day_of_week=day_of_week, hour=hour, minute=minute)


            elif trigger == 'date':
                run_date, = args
            
                if not job:
                    self.scheduler.add_job(func=func, trigger='date', run_date=run_date, id="dao_vote_notify")
                    return await ctx.send(f"Job did not exist, created new one: **{job_id}**")
                else:
                    self.scheduler.reschedule_job(job_id, trigger='date', run_date=run_date)

        except EVENT_JOB_ERROR:
            return await ctx.send("something went wrong with rescheduling...")
        
        return await ctx.send("changed schedule for {0}.".format(job_id))

    @commands.Cog.listener()
    async def on_ready(self):

        config = get_config()
        cycle = get_cycle(config['current_cycle'])

        started_at = arrow.get(cycle['start_time'])
        vote_duration = arrow.get(started_at.timestamp() + config['cycle_voting_duration_sec'])
        # set vote duration 2 days earlier.
        vote_duration = vote_duration.shift(days=-2)
        
        #starting the scheduler
        self.scheduler.start()

        # DAO call notification on discord.
        self.scheduler.add_job(self.notify_dao_call, trigger='cron', day_of_week='wed', hour=17, minute=0, id="dao_call_notify")
        self.scheduler.add_job(self.notify_vote_duration, 'date', run_date=vote_duration.datetime, id="dao_vote_notify")
