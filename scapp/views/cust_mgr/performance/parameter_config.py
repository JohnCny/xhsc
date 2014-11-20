# coding:utf-8
from flask import Module, session, request, render_template, redirect, url_for
from scapp import app,db
from scapp.logic.performanceMapper import Parameter
from scapp.models import SC_User



# 参数配置查询
@app.route('/Performance/config', methods=['GET'])
def config():
	parameter = Parameter()
	queryInform = parameter.query()
	if len(queryInform)!=0:
		inform = queryInform[0]
		back_payment = inform.back_payment
		line_payment = inform.line_payment
		if inform.performance_a:
			inform_name_a = SC_User.query.filter_by(id=inform.performance_a).first().login_name
		else:
			inform_name_a=""
		if inform.performance_b:
			inform_name_b = SC_User.query.filter_by(id=inform.performance_b).first().login_name
		else:
			inform_name_b=""
		if inform.performance_c:
			inform_name_c = SC_User.query.filter_by(id=inform.performance_c).first().login_name
		else:
			inform_name_c=""
		if inform.level_a:
			inform_name_d = SC_User.query.filter_by(id=inform.level_a).first().login_name
		else:
			inform_name_d=""
		if inform.level_b:
			inform_name_e = SC_User.query.filter_by(id=inform.level_b).first().login_name
		else:
			inform_name_e=""	
	else:
		inform = ""
		inform_name_a=""
		inform_name_b=""
		inform_name_c=""
		inform_name_d=""
		inform_name_e=""
		back_payment=""
		# line_payment=""
	queryInform_1 = ""	
	queryInform_2 = ""
	queryInform_3 = ""	
	queryInform_4 = ""
	queryInform_5 = ""	
	queryInform_6 = ""
	for i in range(len(queryInform)):
		if queryInform[i].level_id==1:
			queryInform_1 = queryInform[i]
		if queryInform[i].level_id==2:
			queryInform_2 = queryInform[i]
		if queryInform[i].level_id==3:
			queryInform_3 = queryInform[i]
		if queryInform[i].level_id==4:
			queryInform_4 = queryInform[i]
		if queryInform[i].level_id==5:
			queryInform_5 = queryInform[i]
		if queryInform[i].level_id==6:
			queryInform_6 = queryInform[i]
	user = SC_User.query.order_by("id").all()
	return render_template("Performance/jxxc/xccspz.html",inform=inform,queryInform_1=queryInform_1,
		queryInform_2=queryInform_2,queryInform_3=queryInform_3,queryInform_4=queryInform_4,queryInform_5=queryInform_5,
		queryInform_6=queryInform_6,user=user,inform_name_a=inform_name_a,inform_name_b=inform_name_b,
		inform_name_c=inform_name_c,inform_name_d=inform_name_d,inform_name_e=inform_name_e,back_payment=back_payment,line_payment=line_payment)

# 参数配置新增
@app.route('/Performance/add', methods=['POST'])
def add():
	parameter = Parameter()
	parameter.add(request)
	return redirect("/Performance/config")