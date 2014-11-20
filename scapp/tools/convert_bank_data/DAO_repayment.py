# coding:utf-8
"""
银行还款数据转换辅助接口
"""
import DAO_overdue

__author__ = 'johhny'

from config import logger
from db_conn import INSERT_UPDATE_TRAN
from scapp import db


#插入还款记录
def insert_rep(loan_apply_id,tran_no,last_repayment_day,crnt_pr,arfn_pr,crnt_int,arfn_int):
    try:
        f_arfn_pr=float(arfn_pr)#已还本金
        f_arfn_int=float(arfn_int)#已还利息
        f_crnt_pr=float(crnt_pr)#应还本金
        f_crnt_int=float(crnt_int)#应还利息

        if f_arfn_int<f_crnt_int or f_arfn_pr<f_crnt_pr:
            if DAO_overdue.get_is_overdue(loan_apply_id,tran_no):
                status=2
            elif f_arfn_pr==0 and f_arfn_int==0:
                status=0
            else:
                status=1
        else:
            status=3

        total_repayment=f_arfn_pr+f_arfn_int
        logger.info("插入还款编号-"+str(loan_apply_id)+"，期数-"+str(tran_no)+"")
        REP_INSERT_STR="INSERT INTO sc_repayment  \
                       (loan_apply_id,repayment_installments,re_principal,re_interest, \
                       clear_date,total_repayment,status)  \
                       VALUES  \
                       (%s,%s,%s,%s,%s,%s,%s)"%(loan_apply_id,tran_no,arfn_pr,arfn_int,last_repayment_day,total_repayment,status)
        INSERT_UPDATE_TRAN(REP_INSERT_STR)
    except:
        logger.exception('exception')

    return None

#插入错误账号信息
def insert_wrong_account(account_no):
    logger.info("插入错误账号信息-"+str(account_no)+"")
    WRONG_INSERT_STR="INSERT INTO wrong_account_record (account_no) VALUES (%s)"%(account_no)
    INSERT_UPDATE_TRAN(WRONG_INSERT_STR)

    return None


#获得需要更新的期数与账号
def get_need_update_id():
    QUERY_STR="SELECT id,loan_apply_id,repayment_installments FROM sc_repayment WHERE status<>'3'"
    data=db.session.execute(QUERY_STR).fetchall()
    return data

#更新还款记录
def update_rep(loan_apply_id,tran_no,last_repayment_day,crnt_pr,arfn_pr,crnt_int,arfn_int,id):
    f_arfn_pr=float(arfn_pr)#已还本金
    f_arfn_int=float(arfn_int)#已还利息
    f_crnt_pr=float(crnt_pr)#应还本金
    f_crnt_int=float(crnt_int)#应还利息

    if f_arfn_int<f_crnt_int or f_arfn_pr<f_crnt_pr:
        if DAO_overdue.get_is_overdue(loan_apply_id,tran_no):
            status=2
        elif f_arfn_pr==0 and f_arfn_int==0:
            status=0
        else:
            status=1
    else:
        status=3

    total_repayment=f_arfn_pr+f_arfn_int

    logger.info("更新贷款编号-"+str(loan_apply_id)+"，期数-"+str(tran_no)+"")

    REP_UPDATE_STR="UPDATE sc_repayment SET " \
                   "loan_apply_id=%s,repayment_installments=%s,re_principal=%f,re_interest=%f," \
                   "clear_date=%d,total_repayment=%f,status=%d " \
                   "WHERE id=%s"%(loan_apply_id,tran_no,arfn_pr,arfn_int,last_repayment_day,total_repayment,status,id)
    INSERT_UPDATE_TRAN(REP_UPDATE_STR)

    return None

#计算上月利润贡献
def insert_last_month_intrest():
    INSERT_STR="INSERT INTO sc_sta_mlm (user_id,intrest,month) " \
              "SELECT * FROM view_get_last_month_intrest"
    logger.info("============开始更新每月客户利润贡献===========")
    INSERT_UPDATE_TRAN(INSERT_STR)
    logger.info("============每月客户利润贡献更新完毕===========")
    return None

