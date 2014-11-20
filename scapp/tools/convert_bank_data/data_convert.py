# coding:utf-8
"""
银行每日还款数据转换主程
"""

__author__ = 'johhny'

import config
import assist
import Interface_bank_data
from scapp import db

logger=config.logger
from scapp.models.loan.sc_bank_loans_main import SC_Bank_Loans_Main
from scapp.config import WEBSERVICE_URL
import SOAPpy
import datetime
import json

s_wrong_account = set('')
s_info_wrong_account = set('')


def insert_update_data():
    #获取所有正在放贷信息
    sc_bank_loans_main = SC_Bank_Loans_Main.query.filter("loan_status!=5").all()
    logger.info("=======开始更新银行贷款信息========")
    logger.info("=======更新银行贷款帐号========")
    for data in sc_bank_loans_main:
        # 接口调用---贷款更新
        return_updateLoan(data)
    # sc_bank_loans_main = SC_Bank_Loans_Main.query.filter("loan_apply_id=11111").first()#测试
    # return_updateLoan(sc_bank_loans_main)#测试
    sql = "select * from sc_approval_decision where id not in (select loan_apply_id from sc_bank_loans_main)"
    main = db.session.execute(sql).fetchall()
    logger.info("=======新增银行贷款帐号========")
    for data in main:
        # 接口调用---贷款新增
        if data.loan_account:
            return_addLoan(data) 
    # return_addLoan("11111","3212810554010000000164")#测试

    #更新还款信息
    sc_bank_loans_main = SC_Bank_Loans_Main.query.filter("loan_status in (1,2,3,6)").all()
    for data in sc_bank_loans_main:
        # 接口调用---还款更新
        return_updateRepay(data)
    # sc_bank_loans_main = SC_Bank_Loans_Main.query.filter("loan_apply_id=11111").first()#测试
    # return_updateRepay(sc_bank_loans_main)#测试
     #有效管数更新   
    Interface_bank_data.update_valid_num()
    Interface_bank_data.update_overdue_rate()

#回调函数--更新贷款信息
def return_updateLoan(loan):
    try:
        server = SOAPpy.SOAPProxy(WEBSERVICE_URL)
        dd = server.DaiKuan(loan.loan_account)
        if dd!=0:
            logger.info(loan.loan_account)
            data = json.loads(dd)
            loan.loan_account=data[0]['DKZH']#还款账号
            loan.loan_status=data[0]['ZHZT']#贷款状态
            loan.loan_total_amount=data[0]['DKZE']#贷款总额
            loan.loan_balance=data[0]['DKYE']#贷款余额
            loan.loan_deliver_date=data[0]['FKRQ']#放款日期
            loan.loan_due_date=data[0]['DQRQ']#贷款到期日期
            loan.loan_closed_date=data[0]['JQRQ']#贷款结清日期，未结清为0
            loan.loan_cleared_pr_n=data[0]['YHBJQS']#已还本金期数
            loan.loan_cleared_in_n=data[0]['YHLXQS']#已还利息期数
            
            loan.loan_overdue_date=data[0]['YQTS']#逾期天数
            if float(loan.loan_overdue_date)<1:
                loan.loan_overdue_amount=0#逾期金额
            else:
                loan.loan_overdue_amount=loan.loan_balance
            db.session.commit()
    except:
        logger.exception('exception')
#回调函数--新增贷款信息
def return_addLoan(loan):
    try:
        logger.info("loan_account:"+loan.loan_account)
        server = SOAPpy.SOAPProxy(WEBSERVICE_URL)
        dd = server.DaiKuan(loan.loan_account)
        if dd!=0:
            logger.info(loan.loan_account)
            data = json.loads(dd)
            loan_account=data[0]['DKZH']#还款账号
            loan_status=data[0]['ZHZT']#贷款状态
            loan_total_amount=data[0]['DKZE']#贷款总额
            loan_balance=data[0]['DKYE']#贷款余额
            loan_deliver_date=data[0]['FKRQ']#放款日期
            loan_due_date=data[0]['DQRQ']#贷款到期日期
            loan_closed_date=data[0]['JQRQ']#贷款结清日期，未结清为0
            loan_cleared_pr_n=data[0]['YHBJQS']#已还本金期数
            loan_cleared_in_n=data[0]['YHLXQS']#已还利息期数
            loan_overdue_date=data[0]['YQTS']#逾期天数
            if float(loan_overdue_date)<1:
                loan_overdue_amount=0#逾期金额
            else:
                loan_overdue_amount=loan_balance
            SC_Bank_Loans_Main(loan.loan_apply_id,loan_account,
                 loan_status,loan_total_amount,loan_balance,loan_deliver_date,loan_due_date,
                 loan_closed_date,loan_cleared_pr_n,loan_cleared_in_n,loan_overdue_amount,loan_overdue_date).add()

            db.session.commit()
    except:
        logger.exception('exception')
        db.session.rollback()

#更新还款信息
def return_updateRepay(loan):
    try:
        logger.info("=======开始导入还款信息========")
        server = SOAPpy.SOAPProxy(WEBSERVICE_URL)
        dd = server.HuaiKuan(loan.loan_account)
        data = json.loads(dd)
        account = data[0]['DKZH']#还款账号
        tran_no = data[0]['QS']#期数
        repayment_day = data[0]['MQHBR']#每期还本日
        last_repayment_day = data[0]['ZHHKRQ']#实际每期最后还款日期
        crnt_pr = data[0]['BQBJ']#应还本金
        arfn_pr = data[0]['YHBJ']#已还本金
        crnt_int = data[0]['BQLX']#应还利息
        arfn_int = data[0]['YHLX']#已还利息

        loan_apply_id = loan.loan_apply_id
        '''
            当loan_apply_id不为空时向数据表中插入数据
        '''
        #获得需要更新的id
        update_id = Interface_bank_data.get_need_update_id()
        INSERT_FLAG=True
        if len(update_id)>0:
            for item in update_id:
                if loan_apply_id == item.loan_apply_id and tran_no == item.repayment_installments:
                    INSERT_FLAG=False
                    result = Interface_bank_data.update_rep(loan_apply_id, tran_no, last_repayment_day, crnt_pr,
                                                            arfn_pr, crnt_int, arfn_int, item.id)
        if INSERT_FLAG:
            result = Interface_bank_data.insert_rep(loan_apply_id, tran_no, last_repayment_day, crnt_pr, arfn_pr,
                                                    crnt_int, arfn_int)

    except:
        logger.exception('exception')
    logger.info("=======导入还款信息结束========")