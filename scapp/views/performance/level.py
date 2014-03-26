# coding:utf-8
from flask import Module, session, request, render_template, redirect, url_for
from flask.ext.login import login_user, logout_user, current_user, login_required
from scapp import app,db
from scapp.logic.performanceMapper import Level
from scapp.models import SC_User
from scapp.models import SC_UserRole



# 级别定义——搜索
@app.route('/Performance/khjlgl/jbdy_search', methods=['GET'])
def jbdy_search():
	return render_template("Performance/khjlgl/jbdy_search.html")

# 级别定义——列表
@app.route('/Performance/khjlgl/jbdy/<int:page>', methods=['POST'])
def jbdy(page):
	level = Level()
	data = level.queryList(request)
	return render_template("Performance/khjlgl/jbdy.html",data=data,level_id = request.form['level_id']
		,manager_name = request.form['manager_name'])

# 级别定义——修改
@app.route('/Performance/khjlgl/edit', methods=['POST'])
def edit():
	user_id = request.form['user_id']
	option_id = request.form['option_id']
	level = Level()
	level.edit(user_id,option_id)
	data = level.queryList(request)
	return render_template("Performance/khjlgl/jbdy.html",data=data,level_id=request.form['level_id'],
			manager_name=request.form['manager_name'])
