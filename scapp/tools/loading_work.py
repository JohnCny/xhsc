#coding:utf-8
from apscheduler.scheduler import Scheduler
from scapp.views.cust_mgr.autoload.load import scriptload
from daily_work import daily_work
from monthly_work import monthly_work
from scapp.config import logger
import datetime


class timing():
    def __init__(self):
        sched = Scheduler()
        sched.daemonic = False
        script = scriptload()
        monthly = monthly_work()
        daily = daily_work()
        sched.add_cron_job(script.rise, month='1,4,7,10', day='10', hour='1',minute='1')
        # sched.add_cron_job(script.kpi, month='1-12', day='1', hour='1',minute='1')  #每月1号凌晨2点创建当月评估表
        sched.add_cron_job(script.total, month='1-12', day='1', hour='2',minute='1')  #每月1号凌晨2点创建上月余额规模
        sched.add_cron_job(script.perform, month='1-12', day='1', hour='3',minute='1')  #每月1号凌晨3点初始化当月业绩表
        # sched.add_cron_job(script.first, month='1-12', day='1', hour='5',minute='1')  #计算历史贷款笔数分成
        sched.add_cron_job(monthly.run,month='1-12',day='1',hour='4',minute='1') #计算上月利润贡献
        sched.add_cron_job(daily.run,month='1-12',day='1',hour='1',minute='1')#有效管数、逾期更新、未结算贷款、还款更新 
        sched.add_cron_job(script.linePayment, month='1-12',day='1',hour='2',minute='1')#月初更新诚易贷并计算绩效
        sched.add_cron_job(script.yidaitong, month='1-12',day='1',hour='5',minute='1')#月初更新易贷通模拟利润并计算绩效
        # sched.add_cron_job(script.yidaitong, max_runs=1)
        sched.add_cron_job(script.paymentMonth, month='1-12',day='2',hour='5',minute='1')#月初计算上月工资
        
        sched.start()