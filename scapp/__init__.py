#!/usr/bin/env python
#coding=utf-8
import sys
import thread
reload(sys)  
sys.setdefaultencoding('utf8')
from config import unopath
sys.path.append(unopath)

from flask import Flask, render_template,flash
from flask.ext.login import LoginManager
from flask.ext.sqlalchemy import SQLAlchemy #建立单app -johnny
#import ibm_db_sa.ibm_db_sa

# 初始化
app = Flask(__name__)

# 读取配置文件
#app.config.from_object('scapp.config.DevConfig') # sqlite
app.config.from_object('scapp.config.ProConfig') # mysql

# 加载各模块url
# app.register_blueprint(login)
# app.register_blueprint(index)
#
# app.register_blueprint(information_khxxgl)
# app.register_blueprint(information_dkxxgl)
#
# app.register_blueprint(process)
#
# app.register_blueprint(system_ywcspz)
# app.register_blueprint(system_jkpz)
# app.register_blueprint(system_rzrj)
# app.register_blueprint(system_user)
# app.register_blueprint(system_sjzd)
# app.register_blueprint(system_jggl)
#
# app.register_blueprint(report_kh)
# app.register_blueprint(report_dkgjztfl)
# app.register_blueprint(report_xdgzlclb)
# app.register_blueprint(report_pcscbbcx)
# app.register_blueprint(report_zhgllbb)
# app.register_blueprint(report_line)
# app.register_blueprint(report_bar)
# app.register_blueprint(report_pie)
# --单APP不使用多APP注册 原regist_app方法已过时，应使用blueprint，为提升效率，使用单APP
# 初始化数据库
db = SQLAlchemy(app)

from scapp.tools.loading_work import timing

# flask-login---start
from scapp.models import SC_User

login_manager = LoginManager()
login_manager.init_app(app)
@login_manager.unauthorized_handler
def unauthorized():
    # 消息闪现
    flash('请重新登录','error')
    return render_template("login.html")

@login_manager.user_loader
def load_user(id):
    return SC_User.query.get(int(id))
# flask-login---end

# 404错误跳转
@app.errorhandler(404)
def page_not_found(error):
    return render_template('errors/404.html', error = error), 404
	
# 500错误跳转
@app.errorhandler(500)
def page_not_found(error):
    return render_template('errors/500.html', error = error), 500

#---------------------------------
#加载试图--johnny 放在最后防止循环引用
#---------------------------------
import views.index

import report.report_stock

import views.system.ywcspz
import views.system.jkpz
import views.system.rzrj
import views.system.user
import views.system.sjzd
import views.system.jggl
import views.system.mkgl

import views.information.khxxgl
import views.information.dkxxgl
import views.information.lfdj
import views.information.khfp

import views.process.dksq
import views.process.dksqsh
import views.process.dqdc
import views.process.dqdcWd_syb
import views.process.dqdcWd_zcfzb
import views.process.dqdcXed_zcfzb
import views.process.dqdcXed_jcjy
import views.process.dqdcXed_ysqkfx
import views.process.dqdcXed_xjlfx
import views.process.dqdcXed_dbdydcb
import views.process.dqdcXed_gdzcqd
import views.process.dqdcXed_kc
import views.process.dqdcXed_zkqd

import views.process.dksp
import views.process.dkfk
import views.process.fksh
import views.process.hkdj
import views.process.dhbg
import views.process.dhbgsh
import views.process.dhgl
import views.process.zcfl
import views.process.zcflsh

import views.report.kh
import views.report.dkgjztfl_1
import views.report.dkgjztfl_2
import views.report.dkgjztfl_3
import views.report.dkgjztfl_4
import views.report.dkgjztfl_5
import views.report.dkgjztfl_6
import views.report.dkgjztfl_7
import views.report.xdgzlclb
import views.report.pcscbbcx
import views.report.zhgllbb
import views.report.line
import views.report.bar
import views.report.pie

import views.credit_data.cash_flow
#import views.credit_data.sc_assets_acceptances
#import views.credit_data.sc_assets_cash
#import views.credit_data.sc_assets_deposit
#import views.credit_data.sc_assets_fixed_assets
#import views.credit_data.sc_assets_loan
#import views.credit_data.sc_assets_other_non_operate
#import views.credit_data.sc_assets_other_operate_assets
#import views.credit_data.sc_assets_payable
#import views.credit_data.sc_assets_receipts
#import views.credit_data.sc_assets_recervable
#import views.credit_data.sc_assets_stock
import views.credit_data.sc_cash_flow_assist

#import views.repayment.view_loan_disbursed#发放贷款统计视图
#import views.repayment.view_loan_overdue#逾期贷款统计视图
#import views.repayment.view_loan_refuse#拒绝贷款统计视图
#import views.repayment.view_loan_balance#贷款余额统计视图
#import views.repayment.view_loan_expected#预期贷款统计视图
#import views.repayment.view_loan_expire#到期终止贷款统计视图
import views.repayment.view_loan_repayment#贷款还款记录统计视图
import views.repayment.view_loan_change_record
import views.cust_mgr.view_sc_day_work #客户经理工时记录
import views.cust_mgr.view_kpi_ygpgkh #员工评估考核

import views.cust_mgr.performance.parameter_config
import views.cust_mgr.performance.business_error_list
import views.cust_mgr.performance.level
import views.cust_mgr.performance.payment
import views.cust_mgr.performance.margin
import views.cust_mgr.performance.line_payment
#---------------------------------
#ORM自动生成使用--johnny
#---------------------------------

from scapp.models import process
from scapp.models import information

from scapp.models.credit_data import sc_balance_sheet
from scapp.models.credit_data import sc_cash_flow,sc_cash_flow_assist
#from scapp.models.credit_data import sc_assets_acceptances,sc_assets_deposit,sc_assets_cash
#from scapp.models.credit_data import sc_assets_stock,sc_assets_receivable,sc_assets_payable,sc_assets_other_operate_assets
#from scapp.models.credit_data import sc_assets_loan,sc_assets_other_non_operate,sc_assets_fixed_assets,sc_assets_receipts
#from scapp.models.credit_data import sc_accounts_list
from scapp.models.credit_data import sc_fixed_assets_car,sc_fixed_assets_equipment,sc_fixed_assets_estate
from scapp.models.credit_data import sc_profit_loss
#from scapp.models.credit_data import sc_profit_month,sc_guarantee_mortgage,sc_gm_good,sc_gm_people
from scapp.models.credit_data import sc_stock,sc_cross_examination

from scapp.models.loan import sc_loan_balance #剩余贷款记录

from scapp.models.repayment import sc_change_record#贷后变更记录表
from scapp.models.repayment import sc_repayment #还款记录
from scapp.models.repayment import sc_repayment_plan #还款计划表
from scapp.models.repayment import sc_repayment_plan_detail #还款计划详细表
from scapp.models.repayment import sc_penalty_interest #罚息信息

from scapp.models.cust_mgr import sc_day_work #客户经理工时记录

time = timing()
