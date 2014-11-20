# coding:utf-8
"""
银行账款信息统计接口
"""
__author__ = 'johhny'

from config import logger
from db_conn import INSERT_UPDATE_TRAN
import datetime
from scapp import db
from scapp.models.loan.sc_bank_loans_main import SC_Bank_Loans_Main

#新增贷款信息
def insert_bank_loans_info(loan_apply_id,loan_account,
                 loan_status,loan_total_amount,loan_balance,loan_deliver_date,loan_due_date,
                 loan_closed_date,loan_cleared_pr_n,loan_cleared_in_n,loan_overdue_amount,loan_overdue_date):
    logger.info("插入贷款编号-"+str(loan_apply_id)+"，账号-"+str(loan_account)+"")
#     INFO_INSERT_STR="INSERT INTO sc_bank_loans_main  \
#     (loan_apply_id,loan_account,loan_status,loan_total_amount,loan_balance,loan_deliver_date, \
#       loan_due_date,loan_closed_date,loan_cleared_pr_n,loan_cleared_in_n,loan_overdue_amount,loan_overdue_date) \
# VALUES (%s,%s,%s,%f,%f,%d,%d,%d,%s,%s,%s,%s)",(loan_apply_id,loan_account,loan_status,loan_total_amount,loan_balance,loan_deliver_date,loan_due_date,loan_closed_date,loan_cleared_pr_n,loan_cleared_in_n,loan_overdue_amount,loan_overdue_date)
    
#     INFO_INSERT_STR="INSERT INTO sc_bank_loans_main (loan_apply_id,loan_account,loan_status,loan_total_amount,loan_balance,loan_deliver_date, \
#       loan_due_date,loan_closed_date,loan_cleared_pr_n,loan_cleared_in_n,loan_overdue_amount,loan_overdue_date) \
# VALUES ("+loan_apply_id+"','"+loan_account+"','"+loan_status+"','"+loan_total_amount+"','"+loan_balance+"','"+loan_deliver_date+"','"+loan_due_date+"','"+loan_closed_date+"','"+loan_cleared_pr_n+"','"+loan_cleared_in_n+"','"+loan_overdue_amount+"','"+loan_overdue_date+"')"
    
    return INSERT_UPDATE_TRAN(INFO_INSERT_STR)


#更新贷款信息
def update_bank_loans_info(loan_apply_id,loan_account,
                 loan_status,loan_total_amount,loan_balance,loan_deliver_date,loan_due_date,
                 loan_closed_date,loan_cleared_pr_n,loan_cleared_in_n,loan_overdue_amount,loan_overdue_date):
    logger.info("更新贷款编号-"+str(loan_apply_id)+"，账号-"+str(loan_account)+"")
    INFO_UPDATE_STR="UPDATE sc_bank_loans_main " \
                    "SET loan_account=%s,loan_status=%s,loan_total_amount=%f," \
                    "loan_balance=%f,loan_deliver_date=%d,loan_due_date=%d,loan_closed_date=%d," \
                    "loan_cleared_pr_n=%s,loan_cleared_in_n=%s,loan_overdue_amount=%f,loan_overdue_date=%s " \
                    "WHERE loan_apply_id=%s"\
                    %(loan_account,loan_status,loan_total_amount,loan_balance,loan_deliver_date,loan_due_date,
                    loan_closed_date,loan_cleared_pr_n,loan_cleared_in_n,loan_overdue_amount,loan_overdue_date,loan_apply_id)

    return INSERT_UPDATE_TRAN(INFO_UPDATE_STR)

#获取需要新增的贷款编号
def get_need_update():
    QUERY_STR="SELECT id,loan_apply_id FROM sc_bank_loans_main WHERE loan_status<>'5'"
    return db.session.execute(QUERY_STR).fetchall()


#获得某个用户有效管户
def get_hold_amount_by_user(user_id):
    QUERY_STR="SELECT COUNT(sblm.loan_apply_id) AS valid_sum,sla.A_loan_officer AS manager_id" \
              " FROM sc_bank_loans_main sblm INNER JOIN sc_loan_apply sla ON sblm.loan_apply_id = sla.id " \
              "WHERE sblm.loan_status<>'5' AND sla.A_loan_officer=%s"%(user_id)
    return db.session.execute(QUERY_STR).fetchall()[0]['valid_sum']

#获得所有管户信息
def get_hold_amount():
    QUERY_STR="SELECT COUNT(sblm.loan_apply_id) AS valid_sum,sla.A_loan_officer AS manager_id  \
              FROM sc_bank_loans_main sblm INNER JOIN sc_loan_apply sla ON sblm.loan_apply_id = sla.id  \
              WHERE sblm.loan_status<>'5' GROUP BY sla.A_loan_officer"
    return db.session.execute(QUERY_STR).fetchall()


#更新有效管户
def update_valid_num():
    data=get_hold_amount()
    if data:
        #获取当前时间并转换为%Y-%m格式 用来与数据库中数据匹配
        now=datetime.datetime.now()
        month=datetime.datetime.strftime(now,'%Y-%m')
        
        for obj in data:
            UPDATE_STR="UPDATE sc_performance_list SET valid_sum=%s " \
                       "WHERE manager_id=%d AND date_format(month,'%%%%Y-%%%%m')='%s' "%(obj['valid_sum'],obj['manager_id'],month)
            INSERT_UPDATE_TRAN(UPDATE_STR)     

#更新逾期信息
def update_overdue_info():
    QUERY_STR="SELECT COUNT(sblm.loan_apply_id) AS overdue_sum,SUM(sblm.loan_overdue_amount) AS overdue_amount,sla.A_loan_officer AS user_id " \
              "FROM sc_bank_loans_main sblm INNER JOIN sc_loan_apply sla ON sblm.loan_apply_id = sla.id " \
              "WHERE sblm.loan_status='2' or sblm.loan_status='6' GROUP BY sla.A_loan_officer"
    data=db.session.execute(QUERY_STR).fetchall()

    if len(data):
        #获取当前时间并转换为%Y-%m格式 用来与数据库中数据匹配
        now=datetime.datetime.now()
        month=datetime.datetime.strftime(now,'%Y-%m')
        for obj in data:
            hold_amount=get_hold_amount_by_user(obj['user_id'])
            overdue_rate=obj['overdue_sum']/hold_amount
            UPDATE_STR="UPDATE sc_sta_mlm SET overdue_num=%s,overdue_amount=%s,overdue_rate=%f " \
                       "WHERE user_id=%d AND date_format(month,'%%%%Y-%%%%m')='%s'"\
                       %(obj['overdue_sum'],obj['overdue_amount'],overdue_rate,int(obj['user_id']),month)
            INSERT_UPDATE_TRAN(UPDATE_STR)

# #更新瑕疵贷款信息
# def update_defact_info():
#     QUERY_STR="SELECT * FROM view_defact_loan "
#     data=local_db_conn.execute(QUERY_STR)
#
#     if len(data):
#         now=datetime.datetime.now()
#         month=datetime.datetime.strftime(now,'%Y-%m')
#         for obj in data:
#             hold_amount=get_hold_amount(obj['user_id'])
#
#             UPDATE_STR=""

# #获取贷款信息
# def connector_loan(data.loan_account):

# #获取模拟利润
# def connector_profit(id,lst_fist,lst_last):










