#coding:utf-8
__author__ = 'Johnny'

from scapp import db
import datetime
# 已发放贷款主档
class SC_Bank_Loans_Main(db.Model):
    '''
    已发放贷款主档
    '''
    __tablename__ = 'sc_bank_loans_main'
    id = db.Column(db.Integer, primary_key=True)
    loan_apply_id=db.Column(db.Integer)#贷款编号
    loan_account=db.Column(db.String(32))#贷款账号

    #贷款状态，与省联社核心数据库文档一致
    #’ ’ -开户未放款
    #’1’ -正常
    #’2’ -逾期
    #’3’ –非应计
    #’5’ -结清
    #’6’ -部分逾期
    loan_status=db.Column(db.Integer)

    loan_total_amount=db.Column(db.DECIMAL(18,2))#贷款总额
    loan_balance=db.Column(db.DECIMAL(18,2))#贷款余额
    loan_deliver_date=db.Column(db.Date)#放款日期
    loan_due_date=db.Column(db.Date)#贷款到期日期
    loan_closed_date=db.Column(db.Date)#贷款结清日期，未结清为0
    loan_cleared_pr_n=db.Column(db.Integer)#已还本金期数
    loan_cleared_in_n=db.Column(db.Integer)#已还利息期数
    loan_overdue_amount=db.Column(db.DECIMAL(18,2))#逾期金额
    loan_overdue_date=db.Column(db.String(32))#逾期天数



    def __init__(self,loan_apply_id,loan_account,
                 loan_status,loan_total_amount,loan_balance,loan_deliver_date,loan_due_date,
                 loan_closed_date,loan_cleared_pr_n,loan_cleared_in_n,loan_overdue_amount,loan_overdue_date):
    	self.loan_apply_id = loan_apply_id
    	self.loan_account = loan_account
    	self.loan_status = loan_status
    	self.loan_total_amount = loan_total_amount
    	self.loan_balance = loan_balance
        self.loan_deliver_date = loan_deliver_date
    	self.loan_due_date = loan_due_date
    	self.loan_closed_date = loan_closed_date
    	self.loan_cleared_pr_n = loan_cleared_pr_n
    	self.loan_cleared_in_n = loan_cleared_in_n
        self.loan_overdue_amount = loan_overdue_amount
    	self.loan_overdue_date = loan_overdue_date

    def add(self):
        db.session.add(self)