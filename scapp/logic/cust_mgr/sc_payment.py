#coding:utf-8
from flask.ext.login import login_user, logout_user, current_user, login_required,flash

from scapp.models.performance.sc_payment_list import SC_payment_list 
from scapp.models.performance.sc_business_error_list import SC_business_error_list 
from scapp.models.performance.sc_parameter_configure import SC_parameter_configure 
from scapp.models.performance.sc_risk_margin_list import SC_risk_margin_list 
from scapp.models.performance.sc_risk_margin import SC_risk_margin
from scapp.models.cust_mgr.sc_sta_mlm import SC_Sta_Mlm 
from scapp import db
from scapp.config import logger
from scapp.config import PER_PAGE
from scapp.models import SC_User,SC_UserRole
from scapp.models import SC_Privilege
from scapp.models.performance.sc_performance_list import SC_performance_list 
from decimal import *


class Payment():
	#获得工资单
	def getPaymentByPerson(self,page,request,user_id):
		beg_time = request.form['beg_time'] + " 00:00:00"
		end_time = request.form['end_time'] + " 23:59:59"
		sql = "payment_time between '"+beg_time+"' and '"+end_time+"'"
		sql += " and manager_id="+str(user_id)
		data = SC_payment_list.query.filter(sql).order_by("payment_time asc").paginate(page, per_page = PER_PAGE)
		return data
	def getPaymentByQuery(self,page,request):
		beg_time = request.form['beg_time'] + " 00:00:00"
		end_time = request.form['end_time'] + " 23:59:59"
		user_id = request.form['user_id']
		sql = "payment_time between '"+beg_time+"' and '"+end_time+"'"
		if user_id:
			sql += " and manager_id="+user_id
		data = SC_payment_list.query.filter(sql).order_by("payment_time asc").paginate(page, per_page = PER_PAGE)
		return data

	#客户经理岗薪酬计算
	def payroll(self,user_id,date,score):
		today = date.strftime('%Y')+"-"+date.strftime('%m')
		try:
	    	#客户经理工资计算
			role = SC_UserRole.query.filter_by(user_id=user_id).first().role
			role_level = role.role_level #取得用户权限等级
	        #客户经理
			if role_level==2:
	            #查询所处层级
				data = SC_Privilege.query.filter_by(priviliege_master_id=user_id,privilege_master="SC_User",priviliege_access
	                ="sc_account_manager_level").first()
				level_id = data.priviliege_access_value
				#查询基本工资
				parameter = SC_parameter_configure.query.filter_by(level_id=level_id).first()
				base_payment = parameter.base_payment
				#查询上月绩效
				sql = "SELECT sum(sum1) as total FROM (( SELECT sum(singel_performance) AS sum1"
				sql +=" FROM sc_loan_income_list WHERE DATE_FORMAT(create_time, '%%Y-%%m') = '"+today+"' and manager_id="+str(user_id)+") "
				sql +=" UNION (SELECT sum(singel_performance_A) AS sum1 FROM sc_loan_income_list WHERE"
				sql +=" DATE_FORMAT(create_time, '%%Y-%%m') = '"+today+"' and manager_id_A="+str(user_id)+")" 
				sql +=" UNION (SELECT sum(singel_performance_B) AS sum1 FROM sc_loan_income_list WHERE"
				sql +=" DATE_FORMAT(create_time, '%%Y-%%m') = '"+today+"' and manager_id_B="+str(user_id)+")) AS p"
				last_performance = db.engine.execute(sql).first()
				if not last_performance.total:
					performance_total = 0
				else:
					performance_total = last_performance.total
	            #获取当月利息，逾期率等参数
				mlmSql = "user_id="+str(user_id)
				mlmSql+=" and DATE_FORMAT(month, '%Y-%m')='"+today+"'"
				mlm_list = SC_Sta_Mlm.query.filter(mlmSql).first()
				#当月逾期金额
				M=0
				#当月瑕疵贷款率
				defact_rate=0
				#当月逾期比率
				overdue_rate=0
				#当月逾期笔数
				overdue_num=0
				#当月利息贡献
				intrest=0
				if mlm_list:
					if mlm_list.overdue_amount:
						M=mlm_list.overdue_amount
					if mlm_list.defact_rate:
						defact_rate =float(mlm_list.defact_rate)
					if mlm_list.overdue_rate:
						overdue_rate =Decimal(mlm_list.overdue_rate)
					if mlm_list.overdue_num:
						overdue_num = mlm_list.overdue_num
					if mlm_list.intrest:
						intrest = Decimal(mlm_list.intrest)
				#获取客户经理上月业绩
				achieve = SC_performance_list.query.filter("manager_id="+str(user_id)+" and DATE_FORMAT(month, '%Y-%m')='"+today+"'").all()
				achieve_count=Decimal(0)
				for i in range(len(achieve)):
					achieve_count+=Decimal(achieve[i].valid_sum)
				#需扣除管户数金额
				company =0
				#需扣除绩效比例
				bit=0
				if defact_rate>=0.1:
					company=Decimal(parameter.A2)*Decimal(achieve_count)
				elif defact_rate>=0.05 and defact_rate<0.1:
					company=Decimal(overdue_num)*Decimal(parameter.A2)*8
				elif defact_rate>0 and defact_rate<0.05:
					company=Decimal(overdue_num)*Decimal(parameter.A2)*4
				if overdue_rate<0.01:
					company+=Decimal(overdue_num)*50
				elif overdue_rate>=0.01 and overdue_rate<0.03:
					bit=(overdue_rate-Decimal(0.01))*20
				else:
					bit=1
				#毛利绩效
				performance_result = 0
				if overdue_rate>=0.01:
					performance_result=(Decimal(performance_total)+Decimal(parameter.A2)*Decimal(achieve_count)+intrest*(Decimal(parameter.A3)/100)*Decimal(parameter.R)/100-Decimal(company))*Decimal(1-bit)
				else:
					performance_result=(Decimal(performance_total)+Decimal(parameter.A2)*Decimal(achieve_count)+intrest*(Decimal(parameter.A3)/100)*Decimal(parameter.R)/100)-Decimal(company)
				#计算最终绩效(评估后)
				if float(score)<60:
					last_performance_result=0
				elif float(score)>=60 and float(score)<100:
					last_performance_result=performance_result
				else:
					last_performance_result=int(performance_result)*1.05
				#当月总工资
				old_total_payment = Decimal(base_payment)+Decimal(last_performance_result)
				year = date.strftime('%Y')
				month = date.strftime('%m')
				#获取3月前日期
				if month<4:
					year=year-1
					if month==1:
						month=10
					elif month==2:
						month=11
					else:
						month=12
				old_3_date = str(year)+"-"+str(month)
				#获取3月前逾期金额
				mlm3Sql = "user_id="+str(user_id)
				mlm3Sql+=" and DATE_FORMAT(month, '%Y-%m')='"+old_3_date+"'"
				mlm3_list = SC_Sta_Mlm.query.filter(mlm3Sql).first()
				#如果总保险金低于逾期扣款
				nega_margin=0
				#风险保证金实体
				margin = SC_risk_margin.query.filter_by(manager_id=user_id).first()
				if not margin:
					margin = self.addScRisk(user_id)
				if mlm3_list:
					if mlm3_list.overdue_amount:
						#逾期保险金增加，总保险金减少
						margin.overduce_margin=Decimal(margin.overduce_margin)+Decimal(mlm3_list.overdue_amount)
						if Decimal(margin.total_margin)>=Decimal(mlm3_list.overdue_amount):               
						    margin.total_margin=Decimal(margin.total_margin)-Decimal(mlm3_list.overdue_amount)
						else:
						    margin.total_margin=0
						    nega_margin=Decimal(mlm3_list.overdue_amount)-Decimal(margin.total_margin)
						#新增逾期记录
						SC_risk_margin_list(user_id,date,mlm3_list.overdue_amount,2,margin.total_margin).add()
	            #计算需缴纳风险保证金
				pay_margin=0
				if old_total_payment<=2000:
					pay_margin = 0
				elif old_total_payment>2000:
					if old_total_payment>5000:
						pay_margin+=Decimal((5000-2000)*0.3)
						if old_total_payment>8000:
							pay_margin+=Decimal((8000-5000)*0.4)
							pay_margin+=(old_total_payment-8000)*Decimal(0.5)
						else:
							pay_margin+=(old_total_payment-5000)*Decimal(0.3)
					else:
						pay_margin+=(old_total_payment-2000)*Decimal(0.3)
				#总保证金变化
				margin.total_margin=margin.total_margin+pay_margin
				#新增风险保险金记录
				SC_risk_margin_list(user_id,date,pay_margin,1,margin.total_margin).add()
				#获取3年前日期
				old_date = str(int(year)-3)+"-"+str(month)
				#返还保证金
				return_margin=0
				if margin.total_margin>=50000:
					riskSql = "manager_id="+str(user_id)
					riskSql+=" and DATE_FORMAT(payment_time, '%Y-%m')='"+old_date+"'"
					riskSql+=" and inout_type=1"
					margin_list = SC_risk_margin_list.query.filter(riskSql).first()
					if margin_list:
						#达到返还要求,获得返还值
						return_margin = margin_list.inout_payment
						#返还总保证金
						margin.given_margin = margin.given_margin+return_margin
						#扣除总值小于逾期总值
						if margin.dedcut_margin<margin.overduce_margin:
							if margin.dedcut_margin+return_margin<=margin.overduce_margin:
								#最终所扣保险金=原先所扣保险金+返还
								margin.dedcut_margin = margin.dedcut_margin+return_margin
								return_margin=0
							else:
								return_margin=margin.dedcut_margin+return_margin-margin.overduce_margin
								margin.dedcut_margin = margin.overduce_margin
						margin.total_margin=margin.total_margin-return_margin
						#新增返还风险保险金记录
						SC_risk_margin_list(user_id,date,return_margin,3,margin.total_margin).add()
				#最终工资计算
				last_payment = old_total_payment-pay_margin+return_margin-nega_margin
				SC_payment_list(user_id,date,base_payment,performance_result,score,
	                last_performance_result,float(pay_margin),float(return_margin),M,float(last_payment)).add()
			db.session.commit()
		except:
			# 回滚
			db.session.rollback()
			logger.exception('exception')

	#后台岗工资计算
	def backPayment(self,user_id,date,score):
		try:
			today = date.strftime('%Y')+"-"+date.strftime('%m')
			sql="select t.*,sc_role.* from sc_payment_list t,sc_userrole,sc_role where DATE_FORMAT(t.payment_time, '%Y-%m')='"+today+"'"
			sql+=" and sc_userrole.user_id = t.manager_id and sc_userrole.role_id=sc_role.id and sc_role.role_level=2"
			paymentData = db.session.execute(sql).fetchall()
			#计算客户经理总绩效
			total =float(0)
			for i in range(len(paymentData)): 
				total+=float(paymentData[i].last_performance)
			#计算平均绩效
			arg = float(total/len(paymentData))
			manager_id = user_id
			parameter = SC_parameter_configure.query.first()
			if parameter:
				#后台岗基本工资
				base_payment = parameter.back_payment
				#计算业务差错
				sql="manager_id="+str(manager_id)
				sql+=" and DATE_FORMAT(create_time, '%Y-%m')='"+today+"'"
				errorData = SC_business_error_list.query.filter(sql).all()
				performance_result=arg*0.8
				#计算最终绩效(评估后)
				if float(score)<60:
					last_performance_result=0
				elif float(score)>=60 and float(score)<100:
					last_performance_result=performance_result
				else:
					last_performance_result=int(performance_result)*1.05
				#计算总工资
				old_total_payment = float(base_payment)+float(last_performance_result)
				#风险保证金实体
				margin = SC_risk_margin.query.filter_by(manager_id=manager_id).first()
				if not margin:
					margin = self.addScRisk(manager_id)
				#需扣差错
				errorSum=0
				if errorData:
					errorSum = len(errorData)*20
					#逾期保险金增加，总保险金减少
					margin.overduce_margin=int(margin.overduce_margin)+errorSum
					#新增逾期记录
					SC_risk_margin_list(manager_id,date,errorSum,2,margin.total_margin).add()
	            #计算需缴纳风险保证金
				pay_margin=0
				if old_total_payment<=2000:
					pay_margin = 0
				elif old_total_payment>2000:
					if old_total_payment>5000:
						pay_margin+=(5000-2000)*0.3
						if old_total_payment>8000:
							pay_margin+=(8000-5000)*0.4
							pay_margin+=(old_total_payment-8000)*0.5
						else:
							pay_margin+=(old_total_payment-5000)*0.3
					else:
						pay_margin+=(old_total_payment-2000)*0.3
				#总保证金变化
				margin.total_margin=float(margin.total_margin)+pay_margin
				#新增风险保险金记录
				SC_risk_margin_list(manager_id,date,pay_margin,1,margin.total_margin).add()
				#获取3年前日期
				old_date = str(int(date.strftime('%Y'))-3)+"-"+str(date.strftime('%m'))
				#返还保证金
				return_margin=0
				if margin.total_margin>=30000:
					riskSql = "manager_id="+str(manager_id)
					riskSql+=" and DATE_FORMAT(payment_time, '%Y-%m')='"+old_date+"'"
					riskSql+=" and inout_type=1"
					margin_list = SC_risk_margin_list.query.filter(riskSql).first()
					if margin_list:
						#达到返还要求,获得返还值
						return_margin = float(margin_list.inout_payment)
						margin.given_margin=float(margin.given_margin)+return_margin
						#所扣总值小于逾期总值
						if float(margin.dedcut_margin)<float(margin.overduce_margin):
							if margin.dedcut_margin+return_margin<=margin.overduce_margin:
								#最终所扣保险金=原先所扣保险金+返还
								margin.dedcut_margin = margin.dedcut_margin+return_margin
								return_margin=0
							else:
								return_margin=margin.dedcut_margin+return_margin-margin.overduce_margin
								margin.dedcut_margin = margin.overduce_margin
						margin.total_margin=margin.total_margin-return_margin
						#新增返还风险保险金记录
						SC_risk_margin_list(manager_id,date,return_margin,3,margin.total_margin).add()
				#最终工资计算
				last_payment = old_total_payment-pay_margin+return_margin
				SC_payment_list(manager_id,date,base_payment,performance_result,score,
	            			last_performance_result,pay_margin,return_margin,errorSum,last_payment).add()
    			db.session.commit()
		except:
			# 回滚
			db.session.rollback()
			logger.exception('exception')

	#不存在风险保证金实体则创建
	def addScRisk(self,user_id):
		try:
			SC_risk_margin(user_id,0,0,0,0).add()
			db.session.commit()
			data = SC_risk_margin.query.filter_by(manager_id=user_id).first()
			return data
		except:
			# 回滚
			db.session.rollback()
			logger.exception('exception')