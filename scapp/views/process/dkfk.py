# coding:utf-8

import os

from flask import Module, session, request, render_template, redirect, url_for,flash
from flask.ext.login import current_user
import datetime

from scapp import db
from scapp.config import logger
from scapp.config import PER_PAGE
from scapp.config import PROCESS_STATUS_SPJY_TG
from scapp.config import PROCESS_STATUS_DKFKJH

from scapp.models import SC_Individual_Customer
from scapp.models import SC_Company_Customer
from scapp.models import SC_User

from scapp.models import SC_Relations
from scapp.models import SC_Manage_Info
from scapp.models import SC_Financial_Affairs

from scapp.models import SC_Relation_Type
from scapp.models import SC_Industry
from scapp.models import SC_Business_Type
from scapp.models import SC_Loan_Purpose

from scapp.models import SC_Loan_Apply
from scapp.models import SC_Approval_Decision
from scapp.models import SC_Credit_History
from scapp.models import SC_Co_Borrower
from scapp.models import SC_Guarantees_For_Others
from scapp.models import SC_Guaranty
from scapp.models import SC_Guarantees
#from scapp.models import SC_Financial_Overview
#from scapp.models import SC_Non_Financial_Analysis
from scapp.models import SC_Riskanalysis_And_Findings
from scapp.models.repayment.sc_repayment_plan import SC_Repayment_Plan
from scapp.models.repayment.sc_repayment_plan_detail import SC_Repayment_plan_detail

from scapp.models import View_Query_Loan
from scapp.models import SC_Privilege
from scapp.models.performance.sc_loan_income_list import SC_loan_income_list 
from scapp.models.performance.sc_performance_list import SC_performance_list
from scapp.models.performance.sc_parameter_configure import SC_parameter_configure

from scapp import app

from scapp.models import SC_Loan_Product

# 贷款放款
@app.route('/Process/dkfk/dkfk', methods=['GET'])
def Process_dkfk():
    loan_product = SC_Loan_Product.query.all()
    return render_template("Process/dkfk/dkfk_search.html",loan_product=loan_product)
	
# 贷款放款——编辑放款
@app.route('/Process/dkfk/dkfk_search/<int:page>', methods=['GET','POST'])
def dkfk_search(page):
    # 关联查找
    # 打印sql: print db.session.query(SC_Loan_Apply,SC_Apply_Info).join(SC_Apply_Info)
    # loan_apply = db.session.query(SC_Loan_Apply,SC_Apply_Info).join(SC_Apply_Info)
    # loan_apply = SC_Loan_Apply.query.order_by("id").paginate(page, per_page = PER_PAGE)
    customer_name = request.form['customer_name']
    loan_type = request.form['loan_type']
    sql = ""
    if loan_type != '0':
        sql = "loan_type='"+loan_type+"' and "
    sql += " process_status='"+PROCESS_STATUS_SPJY_TG+"'"

    if customer_name:
        sql += " and (company_customer_name like '%"+customer_name+"%' or individual_customer_name like '%"+customer_name+"%')"

    loan_apply = View_Query_Loan.query.filter(sql).paginate(page, per_page = PER_PAGE)
    
    loan_product = SC_Loan_Product.query.all()
    
    return render_template("Process/dkfk/dkfk.html",loan_apply=loan_apply,customer_name=customer_name,loan_type=loan_type,loan_product=loan_product)

# 贷款放款——跳转到编辑放款(放款信息)
@app.route('/Process/dkfk/goto_edit_dkfk/<int:id>', methods=['GET'])
def goto_edit_dkfk(id):
    loan_apply = SC_Loan_Apply.query.filter_by(id=id).first()
    approval_decision = SC_Approval_Decision.query.filter_by(loan_apply_id=id).first()
    repayment_plan_detail = SC_Repayment_plan_detail.query.filter_by(loan_apply_id=id,change_record=1).order_by("id").all()
    return render_template("Process/dkfk/edit_dkfk.html",id=id,loan_apply=loan_apply,approval_decision=approval_decision,
        repayment_plan_detail=repayment_plan_detail)

# 贷款放款——编辑放款(放款信息)
@app.route('/Process/dkfk/edit_dkfk/<int:id>', methods=['POST'])
def edit_dkfk(id):
    try:
        #保存SC_Approval_Decision剩余信息
        approval_decision = SC_Approval_Decision.query.filter_by(loan_apply_id=id).first()
        approval_decision.loan_date = request.form['loan_date']
        approval_decision.first_repayment_date = request.form['first_repayment_date']
        #approval_decision.management_coats = request.form['management_coats']
        #approval_decision.agency_coats = request.form['agency_coats']
        approval_decision.contract_date = request.form['contract_date']
        approval_decision.loan_account = request.form['loan_account']
        #approval_decision.bank_customer_no = request.form['bank_customer_no']
        approval_decision.loan_contract_number = request.form['loan_contract_number']
        approval_decision.guarantee_contract_number = request.form['guarantee_contract_number']
        approval_decision.collateral_contract_number = request.form['collateral_contract_number']

        #保存还款计划
        repayment_plan_id = 0
        repayment_plan = SC_Repayment_Plan.query.filter_by(loan_apply_id=id).first()
        if repayment_plan:
            repayment_plan_id = repayment_plan.id
            repayment_plan.repayment_type=request.form['repayment_type']
            repayment_plan.amount=request.form['amount']
            repayment_plan.lending_date=request.form['loan_date']
            repayment_plan.first_repayment_date=request.form['first_repayment_date']
            repayment_plan.ratio=request.form['rates']
            repayment_plan.installmenst=request.form['deadline']
            repayment_plan.modify_user=current_user.id
            repayment_plan.modify_date=datetime.datetime.now()
        else:
            repayment_plan_new = SC_Repayment_Plan(id,request.form['repayment_type'],request.form['amount'],
                request.form['loan_date'],request.form['loan_date'],request.form['rates'],
                request.form['deadline'])
            repayment_plan_new.add()
            db.session.flush()
            repayment_plan_id = repayment_plan_new.id

        #保存还款细则
        SC_Repayment_plan_detail.query.filter_by(loan_apply_id=id,change_record=1).delete()
        db.session.flush()
        for i in range(1,int(request.form['deadline'])+1):
            SC_Repayment_plan_detail(repayment_plan_id,id,None,request.form['rates'],
                request.form['mybj%d' % i],request.form['mylx%d' % i],
                request.form['mybx%d' % i],i,request.form['myrq%d' % i],None,1).add() 

        loan_apply = SC_Loan_Apply.query.filter_by(id=id).first()
        loan_apply.process_status = PROCESS_STATUS_DKFKJH

        # 事务提交
        db.session.commit()
        #计算绩效
        # reckonIncome(id)
        # 消息闪现
        flash('保存成功','success')
    except:
        # 回滚
        db.session.rollback()
        logger.exception('exception')
        # 消息闪现 
        flash('保存失败','error')
    return redirect("Process/dkfk/dkfk")    

def reckonIncome(id):
    #计算绩效
    data = SC_Loan_Apply.query.filter_by(id=id).first()
    level = SC_Privilege.query.filter_by(priviliege_master_id=data.A_loan_officer,privilege_master="SC_User",priviliege_access="sc_account_manager_level").first()
    information = SC_Approval_Decision.query.filter_by(loan_apply_id=id).first()
    #获取放贷日期
    lending_date = information.loan_date
    #计算绩效日期
    year = int(lending_date.strftime('%Y'))
    month = int(lending_date.strftime('%m'))
    if month==12:
        year = year+1
        month=1
    payment_date = datetime.date(year,month,1)
    if month<10:
        month = "0"+str(month)
    after_date = str(year)+"-"+str(month)
    #是否已配置客户经理层级
    if level:
        #查询层级
        level_id = level.priviliege_access_value
        #查询所有绩效参数
        parameter = SC_parameter_configure.query.filter_by(level_id=level_id).first()
        #折算笔数
        inCount = amount(int(information.amount))
        #所得绩效
        total = float(parameter.A1)*inCount
        yunying_total = total*0.1
        A_total = total*0.6
        B_total = total*0.3
        #获取当月业绩记录
        sql="DATE_FORMAT(month, '%Y-%m')='"+after_date+"'"
        sql+=" and manager_id="+str(data.A_loan_officer)
        perform = SC_performance_list.query.filter(sql).first()
        if not perform:
            SC_performance_list(payment_date,data.A_loan_officer,inCount,0,0,0,level_id).add()
        else:
            perform.count=int(perform.count)+inCount
        try:
            SC_loan_income_list(id,data.yunying_loan_officer,yunying_total,data.A_loan_officer,
                A_total,data.B_loan_officer,B_total,payment_date).add()
            # 事务提交
            db.session.commit()
            # 消息闪现
            flash('保存成功','success')
        except:
            # 回滚
            db.session.rollback()
            logger.exception('exception')
            # 消息闪现
            flash('保存失败','error')
    


# 贷款放款——编辑放款(还款计划)
@app.route('/Process/dkfk/hkjh', methods=['GET'])
def dkfk_hkjh():
    return render_template("Process/dkfk/hkjh.html")

#折算笔数
def amount(am):
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