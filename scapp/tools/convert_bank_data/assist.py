# coding:utf-8
"""
银行数据转换辅助操作
"""
__author__ = 'johhny'

import datetime,calendar
from scapp import db


#通过账号获得loan_apply_id
def get_lai_by_account(account):
    QUERY_STR="SELECT loan_apply_id FROM sc_approval_decision WHERE loan_account='%s'"%(account)
    data=db.execute(QUERY_STR).fetchall()
    if len(data) > 0:
        id=data[0]['loan_apply_id']
    else :
        id=None
    return id

#通过loan_apply_id 获得A岗用户id
def get_user_id_by_lai(loan_apply_id):
    QUERY_STR="SELECT A_loan_officer FROM sc_apply_info WHERE loan_apply_id='%s'"%(loan_apply_id)
    data=db.execute(QUERY_STR).fetchall()
    if len(data) > 0:
        id=data[0]['A_loan_officer']
    else :
        id=None
    return id

#对应期数转为计算绩效的月份
def convert_installment_to_month(installment,loan_apply_id):
    QUERY_STR="SELECT clear_date FROM sc_repayment_plan_detail WHERE loan_apply_id=%s " \
              "AND repayment_installments='1'"%(loan_apply_id)
    data=db.execute(QUERY_STR).fetchall()
    if len(data)>0:
        beg_date=data[0]['clear_date']
        return add_month(beg_date,installment-1)


#加月份
def add_month(beg_date,num):
    month=beg_date.month-1+num
    year=beg_date.year+month/12
    month=month%12+1
    day=min(beg_date.day,calendar.monthrange(year,month)[1])
    return datetime.date(year,month,day)





