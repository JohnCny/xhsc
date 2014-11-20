#coding:utf-8
__author__ = 'hejia'

from scapp import db
import datetime

class SC_loan_income_list(db.Model):
    '''
    薪酬详单表
    '''
    __tablename__ = 'sc_loan_income_list'
    id = db.Column(db.Integer, primary_key=True)
    loan_apply_id=db.Column(db.String(11))#贷款编号
    manager_id=db.Column(db.String(11))#运营岗员工工号
    singel_performance=db.Column(db.String(11))#所得绩效
    manager_id_A=db.Column(db.String(11))#A岗员工工号
    singel_performance_A=db.Column(db.String(11))#所得绩效
    manager_id_B=db.Column(db.String(11))#B岗员工工号
    singel_performance_B=db.Column(db.String(11))#所得绩效
    create_time=db.Column(db.DateTime)#绩效时间
    income_type=db.Column(db.Integer)#贷款类型

    def __init__(self,loan_apply_id,manager_id,singel_performance,manager_id_A,
        singel_performance_A,manager_id_B,singel_performance_B,create_time,income_type):
    	self.loan_apply_id = loan_apply_id
        self.manager_id = manager_id
    	self.singel_performance = singel_performance
        self.manager_id_A = manager_id_A
        self.singel_performance_A = singel_performance_A
        self.manager_id_B = manager_id_B
        self.singel_performance_B = singel_performance_B      
        self.create_time = create_time
        self.income_type = income_type
    def add(self):
        db.session.add(self)