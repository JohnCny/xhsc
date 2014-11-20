# coding:utf-8
"""
统一接口
"""
import DAO_repayment, DAO_bank_loans, DAO_overdue

__author__ = 'johhny'
#DAO_repayment


def insert_rep(loan_apply_id, tran_no, last_repayment_day, crnt_pr, arfn_pr, crnt_int, arfn_int):
    """
    插入还款信息
    @param loan_apply_id:贷款id
    @param tran_no: 期数
    @param last_repayment_day:实际最后还款日
    @param crnt_pr: 应还本金
    @param arfn_pr: 已还本金
    @param crnt_int: 应还利息
    @param arfn_int: 已还利息
    @return:None
    """
    return DAO_repayment.insert_rep(loan_apply_id, tran_no, last_repayment_day, crnt_pr, arfn_pr, crnt_int, arfn_int)


def insert_wrong_account(account_no):
    """
    插入错误账号信息
    @param account_no: 账户号
    @return:None
    """
    return DAO_repayment.insert_wrong_account(account_no)


def get_need_update_id():
    """
    获得需要更新的账户ID
    @return:需要更新账户id列表
    """
    return DAO_repayment.get_need_update_id()


def update_rep(loan_apply_id,tran_no,last_repayment_day,crnt_pr,arfn_pr,crnt_int,arfn_int,id):
    """
    更新还款信息
    @param loan_apply_id:贷款id
    @param tran_no: 期数
    @param last_repayment_day:实际最后还款日
    @param crnt_pr: 应还本金
    @param arfn_pr: 已还本金
    @param crnt_int: 应还利息
    @param arfn_int: 已还利息
    @param id: id
    @return:None
    """
    return DAO_repayment.update_rep(loan_apply_id,tran_no,last_repayment_day,crnt_pr,arfn_pr,crnt_int,arfn_int,id)



def insert_last_month_intrest():
    """
    计算上个月利润贡献,插入sc_sta_mlm表中
    @return:None
    """
    return DAO_repayment.insert_last_month_intrest()

#DAO_overdue


def get_is_overdue(loan_apply_id,installments):
    """
    判断贷款在当前期数在目前的时间是否已逾期
    @param loan_apply_id: 贷款编号
    @param installments: 期数
    @return:False 逾期 or True 未逾期
    """
    return DAO_overdue.get_is_overdue(loan_apply_id,installments)



#DAO_bank_loans

def insert_bank_loans_info(loan_apply_id,loan_account,
                 loan_status,loan_total_amount,loan_balance,loan_deliver_date,loan_due_date,
                 loan_closed_date,loan_cleared_pr_n,loan_cleared_in_n,loan_overdue_amount,loan_overdue_date):
    """
    新增银行贷款信息
    @param loan_apply_id:
    @param loan_account: 贷款账号
    @param loan_status: 贷款状态
    @param loan_total_amount: 贷款总额
    @param loan_balance: 贷款余额
    @param loan_deliver_date: 放款日期
    @param loan_due_date: 到期日
    @param loan_closed_date: 结清日
    @param loan_cleared_pr_n: 已还本金期数
    @param loan_cleared_in_n: 已还利息期数
    @param loan_overdue_amount: 逾期本金
    @param loan_overdue_date: 逾期日
    @return: None
    """
    return DAO_bank_loans.insert_bank_loans_info(loan_apply_id,loan_account,
                 loan_status,loan_total_amount,loan_balance,loan_deliver_date,loan_due_date,
                 loan_closed_date,loan_cleared_pr_n,loan_cleared_in_n,loan_overdue_amount,loan_overdue_date)



def update_bank_loans_info(id,loan_apply_id,loan_account,
                 loan_status,loan_total_amount,loan_balance,loan_deliver_date,loan_due_date,
                 loan_closed_date,loan_cleared_pr_n,loan_cleared_in_n,loan_overdue_amount,loan_overdue_date):
    """
    更新银行贷款信息
    @param id: 主键ID
    @param loan_apply_id:
    @param loan_account: 贷款账号
    @param loan_status: 贷款状态
    @param loan_total_amount: 贷款总额
    @param loan_balance: 贷款余额
    @param loan_deliver_date: 放款日期
    @param loan_due_date: 到期日
    @param loan_closed_date: 结清日
    @param loan_cleared_pr_n: 已还本金期数
    @param loan_cleared_in_n: 已还利息期数
    @param loan_overdue_amount: 逾期本金
    @param loan_overdue_date: 逾期日
    @return: None
    """
    return DAO_bank_loans.update_bank_loans_info(id,loan_apply_id,loan_account,
                 loan_status,loan_total_amount,loan_balance,loan_deliver_date,loan_due_date,
                 loan_closed_date,loan_cleared_pr_n,loan_cleared_in_n,loan_overdue_amount,loan_overdue_date)


def get_need_update_bli():
    """
    获取需要更新的银行贷款信息id
    @return:需要更新的银行贷款信息id与loan_apply_id
    """
    return DAO_bank_loans.get_need_update()


def update_valid_num():
    """
    更新有效管户
    @return:None
    """
    return DAO_bank_loans.update_valid_num()

def update_overdue_rate():
    """
    更新所有人逾期率
    @return:None
    """
    return DAO_bank_loans.update_overdue_info()

def connector_loan(loan_account):
    """
    获取贷款信息
    @return:None
    """
    return DAO_bank_loans.connector_loan(loan_account)

def connector_profit(id,lst_fist,lst_last):
    """
    获取模拟利润
    @return:None
    """
    return DAO_bank_loans.connector_profit(id,lst_fist,lst_last)