#coding:utf-8
import datetime
from scapp import db
from scapp.config import logger

from scapp.models.performance.sc_assess_record import SC_assess_record 
from scapp.models.performance.sc_performance_list import SC_performance_list 
from scapp.models.performance.sc_examine_rise import SC_examine_rise
from scapp.models.performance.sc_manager_level_index import SC_manager_level_index 
from scapp.models import SC_Privilege
from scapp.models.performance.sc_parameter_configure import SC_parameter_configure
from scapp.models import SC_Loan_Apply
from scapp.models import SC_Approval_Decision
from scapp.models.performance.sc_loan_income_list import SC_loan_income_list 
from scapp.tools.convert_bank_data import Interface_bank_data
import json
from scapp.logic.cust_mgr.sc_payment import Payment
from scapp.tools.convert_bank_data import assist
from scapp.models.loan.sc_bank_loans_main import SC_Bank_Loans_Main
from scapp.config import WEBSERVICE_URL
import SOAPpy
class scriptload():
	#晋降级线程
	def rise(self):
		try:
			year = datetime.date.today().strftime('%Y')
			month = datetime.date.today().strftime('%m')
			if month==1:
				year = year-1
				month = 12
			else:
				month=int(month)-1
				if month<10:
					month = "0"+str(month)
			search_date = str(year)+"-"+str(month)
		   	sql = "select sc_user.id as id from sc_userrole,sc_role,sc_user where "
			sql +=" sc_userrole.role_id=sc_role.id and sc_role.role_level=2 and sc_user.id=sc_userrole.user_id"
			data = db.engine.execute(sql).fetchall()
			for i in range(len(data)):
				assess = SC_assess_record.query.filter_by(manager_id=data[i].id).first()
				if assess:
					if assess.assess_sum=='3':
						#获取客户经理上月业绩
						achieve = SC_performance_list.query.filter("manager_id="+str(data[i].id)+" and DATE_FORMAT(month, '%Y-%m')='"+search_date+"'").first()
						if float(assess.assess_arg)>90:	
							if achieve:		
								if not achieve.level_id==6:
									#获取当前层级考核业绩
									base_achieve = SC_manager_level_index.query.filter_by(level_id=int(achieve.level_id)).first()
									if float(achieve.count)>=float(base_achieve.count) and float(achieve.valid_sum)>=float(base_achieve.valid_sum) and float(achieve.balance_scale)>=float(base_achieve.balance_scale):
										SC_examine_rise(data[i].id,search_date,"1","1").add()
									else:
										if not achieve.level_id==1:
											#获取低一层级考核业绩
											level_id_new=int(achieve.level_id)-1
											base_achieve = SC_manager_level_index.query.filter_by(level_id=level_id_new).first()
											if float(achieve.count)<float(base_achieve.count) and float(achieve.valid_sum)<float(base_achieve.valid_sum) and float(achieve.balance_scale)<float(base_achieve.balance_scale):
												SC_examine_rise(data[i].id,search_date,"2","1").add()
						else:
							if achieve:
								if not achieve.level_id==1:
									if float(assess.assess_arg)<60:	
										SC_examine_rise(data[i].id,search_date,"2","1").add()
									else:
										#获取低一层级考核业绩
										base_achieve = SC_manager_level_index.query.filter_by(level_id=int(achieve.level_id)-1).first()
										if float(achieve.count)<float(base_achieve.count) and float(achieve.valid_sum)<float(base_achieve.valid_sum) and float(achieve.balance_scale)<float(base_achieve.balance_scale):
											SC_examine_rise(data[i].id,search_date,"2","1").add()
			# 事务提交
			db.session.commit()
		except:
			# 回滚
			db.session.rollback()
			logger.exception('exception')


	#每月初创建当月评估表
	def kpi(self):
		try:
			sql = "SELECT sc_user.id,sc_role.role_level FROM sc_userrole "
			sql += "INNER JOIN sc_role ON sc_userrole.role_id = sc_role.id "
			sql += "INNER JOIN sc_user ON sc_user.id = sc_userrole.user_id "
			sql += "where sc_role.role_level >= 2"
			users = db.session.execute(sql)
			now = datetime.datetime.now().date().strftime("%Y-%m-%d")

			for obj in users:
				if obj.role_level == 2:#客户经理
					insert_sql = "insert into sc_kpi_officer (user_id,assess_date) values ("+str(obj.id)+",'"+now+"')"
					db.session.execute(insert_sql)
				elif obj.role_level == 3:#运营岗
					insert_sql = "insert into sc_kpi_yunying (user_id,assess_date) values ("+str(obj.id)+",'"+now+"')"
					db.session.execute(insert_sql)

			# 事务提交
			db.session.commit()
		except:
			# 回滚
			db.session.rollback()
			logger.exception('exception')

	#创建上月余额规模
	def total(self):
		try:
			d1 = datetime.datetime.now()
			d3 = d1 - datetime.timedelta(hours=24)
			last_day = d3.strftime("%Y")+"-"+d3.strftime("%m")
			sql="select a.user_id as id from sc_userrole a,sc_role b where a.role_id=b.id and b.role_level=2"
			data = db.session.execute(sql)
			for obj in data:
				loan_sql = "select sum(a.loan_balance) as loanSum from sc_bank_loans_main a,sc_loan_apply b where a.loan_apply_id=b.id and loan_type = 1  dzZzand b.A_loan_officer="+str(obj.id)
				dataSum = db.session.execute(loan_sql).fetchall()
				#上月余额规模
				for i in dataSum:
					lastSum = i.loanSum
					update_sql="DATE_FORMAT(month, '%Y-%m')='"+last_day+"'"
					update_sql+=" and manager_id="+str(obj.id)
					performanc_list = SC_performance_list.query.filter(update_sql).first()
					if performanc_list:
						performanc_list.balance_scale=lastSum
			# 事务提交
			db.session.commit()
		except:
			# 回滚
			db.session.rollback()
			logger.exception('exception')

	#初始化当月业绩表
	def perform(self):
		try:	
			today = datetime.datetime.now().strftime('%Y')+"-"+datetime.datetime.now().strftime('%m')
			sql="select a.user_id as id from sc_userrole a,sc_role b where a.role_id=b.id and b.role_level=2"
			data = db.session.execute(sql)
			for obj in data:
				#获取层级
				level = SC_Privilege.query.filter_by(priviliege_master_id=obj.id,privilege_master="SC_User",
					priviliege_access="sc_account_manager_level").first()
				level_id=0
				if level:
					level_id = level.priviliege_access_value
				insert_sql="DATE_FORMAT(month, '%Y-%m')='"+today+"'"
				insert_sql+=" and manager_id="+str(obj.id)
				performanc_list = SC_performance_list.query.filter(insert_sql).first()
				if not performanc_list:
					SC_performance_list(datetime.datetime.now(),obj.id,0,0,0,0,level_id).add()
			db.session.commit()
		except:
			# 回滚
			db.session.rollback()
			logger.exception('exception')

	#统计每笔贷款所得笔数绩效
	def first(self):
		try:
			sql ="select a.* from sc_approval_decision a,sc_loan_apply b where a.loan_apply_id=b.id and b.process_status='601' and a.loan_apply_id not in (select loan_apply_id from sc_loan_income_list)"
			data = db.session.execute(sql)
			for obj in data:
				#获取放贷日期
				lending_date = obj.loan_date
				#计算绩效日期
				year = int(lending_date.strftime('%Y'))
				month = int(lending_date.strftime('%m'))
				if month==12:
				    year = year+1
				    month=1
				payment_date = datetime.date(year,month,1)
				#折算笔数
				inCount = self.amount(int(obj.amount))
				#查询层级
				loan_apply = SC_Loan_Apply.query.filter_by(id=obj.loan_apply_id).first()
				level = SC_Privilege.query.filter_by(priviliege_master_id=loan_apply.A_loan_officer,privilege_master="SC_User",priviliege_access="sc_account_manager_level").first()
				#查询所有绩效参数
				if level:
					parameter = SC_parameter_configure.query.filter_by(level_id=level.priviliege_access_value).first()
					#所得绩效
					if parameter:
						total = float(parameter.A1)*inCount
						yunying_total = total*0.1
						A_total = total*0.6
						B_total = total*0.3
						SC_loan_income_list(obj.loan_apply_id,loan_apply.yunying_loan_officer,yunying_total,loan_apply.A_loan_officer,
							A_total,loan_apply.B_loan_officer,B_total,payment_date,1).add()
		 	 # 事务提交
			db.session.commit()
		except:
			# 回滚
			db.session.rollback()
			logger.exception('exception')
	#折算笔数
	def amount(self,am):
	    if am<=50000:
	        return 0.7
	    elif am>50000 and am<=150000:
	        return 1
	    elif am>150000 and am<=300000:
	        return 1.5
	    elif am>300000 and am<=500000:
	        return 2
	    elif am>500000 and am<=1000000:
	        return 3
	    elif am>1000000 and am<=2000000:
	        return 3.5
	    elif am>2000000 and am<3000000:
	        return 4
	    elif am>3000000:
	        return 5


	#月初更新上月诚易贷放贷状态计算本月绩效
	def linePayment(self):
		try:
			#上月时间
			lst_fist = datetime.date(datetime.datetime.now().year,datetime.datetime.now().month-1,1)
			#当月时间
			to_fist = datetime.date(datetime.datetime.now().year,datetime.datetime.now().month,1)
			#上月时间
			last_month = lst_fist.strftime('%Y')+lst_fist.strftime('%m')
			sql ="select loan_apply_id,loan_total_amount from sc_bank_loans_main where DATE_FORMAT(t.loan_deliver_date, '%Y-%m')="+last_month+"'"
			data = db.session.execute(sql)
			for obj in data:
				#计算绩效日期
				payment_date = to_fist
				#折算笔数
				inCount = self.amount(int(obj.loan_total_amount))
				#查询层级
				loan_apply = SC_Loan_Apply.query.filter_by(id=obj.loan_apply_id).first()
				if loan_apply==1:
					level = SC_Privilege.query.filter_by(priviliege_master_id=loan_apply.A_loan_officer,privilege_master="SC_User",priviliege_access="sc_account_manager_level").first()
					#查询所有绩效参数
					if level:
						parameter = SC_parameter_configure.query.filter_by(level_id=level.priviliege_access_value).first()
						#所得绩效
						if parameter:
							total = float(parameter.A1)*inCount
							yunying_total = total*0.1
							A_total = total*0.6
							B_total = total*0.3
							SC_loan_income_list(obj.loan_apply_id,loan_apply.yunying_loan_officer,yunying_total,loan_apply.A_loan_officer,
								A_total,loan_apply.B_loan_officer,B_total,payment_date,1).add()
		 	 # 事务提交
			db.session.commit()
		except:
			# 回滚
			db.session.rollback()
			logger.exception('exception')
			

	# 月初更新易贷通模拟利润并计算绩效
	def yidaitong(self):
		try:
			#上一个月的第一天
			lst_fist = datetime.date(datetime.datetime.now().year,datetime.datetime.now().month-1,1)
			#上一个月的最后一天
		 	lst_last = datetime.date(datetime.datetime.now().year,datetime.datetime.now().month,1)-datetime.timedelta(1)
			#获取所有上月存在利润贷款
			lst = str(lst_fist) + " 00:00:00"
			last = str(lst_last) + " 23:59:59"
			sql = "loan_due_date > '" + lst + "'"
			sc_bank_loans_main= SC_Bank_Loans_Main.query.filter(sql).all()
			logger.info("=======模拟利润更新========")
			for obj in sc_bank_loans_main:
				sc_loan_apply = SC_Loan_Apply.query.filter_by(id=obj.loan_apply_id).first()
				logger.info(sc_loan_apply.loan_type)
				if sc_loan_apply:
					if sc_loan_apply.loan_type=='2':
						#接口--模拟利润
						server = SOAPpy.SOAPProxy(WEBSERVICE_URL) 
						dd = server.mnlr(obj.loan_account,lst_last.strftime("%Y%m%d"))
						logger.info("sc_loan_apply:"+str(sc_loan_apply.id))
						data = json.loads(dd)
						self.return_examp(obj.loan_apply_id,data[0]["BYMNLR"])
		except:
			logger.exception('exception')

	# 回调函数--获取模拟利润
	def return_examp(self,loan_apply_id,BYMNLR):			
		try:
			#参数配置表
			sc_parameter_configure = SC_parameter_configure.query.first()
			A_total = float(BYMNLR)*float(sc_parameter_configure.line_payment)/100
			#获取A岗人
			loan_apply = SC_Loan_Apply.query.filter_by(id=loan_apply_id).first()
			#计入下月绩效
			SC_loan_income_list(loan_apply_id,'','',loan_apply.A_loan_officer,A_total,'','',datetime.datetime.now(),2).add()
			# 事务提交
			db.session.commit()
		except:
			# 回滚
			db.session.rollback()
			logger.exception('exception')

	def paymentMonth(self):
		#获取所有人员名单
		sql="select a.id,b.role_level from sc_user a,sc_role b,sc_userrole c where a.id=c.user_id and c.role_id=b.id"
		data = db.session.execute(sql).fetchall()
		pay = Payment()
		#上月
		lst_fist = datetime.date(datetime.datetime.now().year,datetime.datetime.now().month-1,1)
		#客户经理工资计算
		for obj in data:
			if obj.role_level==2:
				pay.payroll(obj.id,lst_fist,80)
		#后台岗工资计算
		for obj in data:
			if obj.role_level==3:
				pay.backPayment(obj.id,lst_fist,80)