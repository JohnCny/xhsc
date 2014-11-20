# coding:utf-8
"""
数据库接口
"""
import config

__author__ = 'johhny'

import sqlalchemy
from config import logger
from scapp import db

#事务插入或者更新记录
def INSERT_UPDATE_TRAN(SQL_STR):
	try:
		db.session.execute(SQL_STR)
		db.session.commit()
	except:
		logger.exception('exception')
		db.session.rollback()


