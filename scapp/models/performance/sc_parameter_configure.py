#coding:utf-8
__author__ = 'hejia'

from scapp import db
import datetime

class SC_parameter_configure(db.Model):
    '''
    参数配置表
    '''
    __tablename__ = 'sc_parameter_configure'
    id = db.Column(db.Integer, primary_key=True)
    level_id=db.Column(db.Integer)#客户经理级别
    base_payment=db.Column(db.String(11))#基本工资
    A1=db.Column(db.String(11))#A1
    A2=db.Column(db.String(11))#A2
    A3=db.Column(db.String(11))#A3
    R=db.Column(db.String(11))#R
    back_payment=db.Column(db.String(11))#后台岗基本工资
    line_payment=db.Column(db.String(11))#易贷通系数
    performance_a=db.Column(db.String(11))#绩效评估人A
    performance_b=db.Column(db.String(11))#绩效评估人B
    performance_c=db.Column(db.String(11))#绩效评估人C
    level_a=db.Column(db.String(11))#层级评估人A
    level_b=db.Column(db.String(11))#层级评估人B

    def __init__(self,level_id,base_payment,A1,A2,A3,R,back_payment,line_payment,performance_a,performance_b,
        performance_c,level_a,level_b):
    	self.level_id = level_id
    	self.base_payment = base_payment
    	self.A1 = A1
    	self.A2 = A2
    	self.A3 = A3
        self.R = R
        self.back_payment = back_payment
        self.line_payment = line_payment
        self.performance_a = performance_a
        self.performance_b = performance_b
        self.performance_c = performance_c
        self.level_a = level_a
        self.level_b = level_b

    def add(self):
        db.session.add(self)