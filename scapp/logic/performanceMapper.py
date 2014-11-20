#coding:utf-8
from flask.ext.login import login_user, logout_user, current_user, login_required, flash

from scapp.models.performance.sc_parameter_configure import SC_parameter_configure
from scapp.models.performance.sc_business_error_list import SC_business_error_list
from scapp.models.performance.sc_performance_list import SC_performance_list
from scapp.models.performance.sc_account_manager_level import SC_account_manager_level
from scapp.models.performance.sc_examine_rise import SC_examine_rise
from scapp import db
from scapp.config import logger
from scapp.config import PER_PAGE
from scapp.models import SC_User
from scapp.models import SC_Privilege


#参数配置
class Parameter():
    #参数查询
    def query(self):
        parameter_configure = SC_parameter_configure.query.all()
        return parameter_configure

    #保存参数
    def add(self, request):
        try:
            SC_parameter_configure.query.delete()
            db.session.flush()
            level_base_list = request.form.getlist('level_base')
            level_A1_list = request.form.getlist('level_A1')
            level_A2_list = request.form.getlist('level_A2')
            level_A3_list = request.form.getlist('level_A3')
            level_R_list = request.form.getlist('level_R')
            back_payment = request.form['back_payment']
            line_payment = request.form['line_payment']
            performance_a = request.form['performance_a']
            performance_b = request.form['performance_b']
            performance_c = request.form['performance_c']
            level_a = request.form['level_a']
            level_b = request.form['level_b']
            for i in range(len(level_base_list)):
                SC_parameter_configure(i + 1, level_base_list[i], level_A1_list[i], level_A2_list[i],
                                       level_A3_list[i], level_R_list[i], back_payment,line_payment,performance_a, performance_b, performance_c,
                                       level_a, level_b).add()
            # 事务提交
            db.session.commit()
            # 消息闪现
            flash('保存成功', 'success')
        except:
            # 回滚
            db.session.rollback()
            logger.exception('exception')
            # 消息闪现
            flash('保存失败', 'error')

#业务差错统计
class Business():
    #列表查询
    def query(self, page, request):
        beg_time = request.form['beg_time'] + " 00:00:00"
        end_time = request.form['end_time'] + " 23:59:59"
        name = request.form['name']
        sql = "create_time between '" + beg_time + "' and '" + end_time + "'"
        if name:
            sql += " and manager_name like '%" + name + "%'"
        data = SC_business_error_list.query.filter(sql).order_by("create_time asc").paginate(page, per_page=PER_PAGE)
        return data

    #普通员工查询自己
    def queryByPerson(self, user_id, page, request):
        beg_time = request.form['beg_time'] + " 00:00:00"
        end_time = request.form['end_time'] + " 23:59:59"
        sql = "create_time between '" + beg_time + "' and '" + end_time + "'"
        sql += " and manager_id=" + str(user_id)
        data = SC_business_error_list.query.filter(sql).order_by("create_time asc").paginate(page, per_page=PER_PAGE)
        return data

    #新增业务差错记录
    def addError(self, request):
        manager_id = request.form['manager_id']
        manager_name = request.form['manager_name']
        create_time = request.form['create_time']
        error_reason = request.form['error_reason']
        try:
            SC_business_error_list(manager_id, manager_name, create_time, error_reason).add()
            # 事务提交
            db.session.commit()
            # 消息闪现
            flash('保存成功', 'success')
        except:
            # 回滚
            db.session.rollback()
            logger.exception('exception')
            # 消息闪现
            flash('保存失败', 'error')

#客户经理级别
class Level():
    def queryList(self, request):
        level_id = request.form['level_id']
        manager_name = request.form['manager_name']
        sql = " select sc_user.id AS user_id,sc_user.login_name AS login_name,"
        sql += " sc_privilege.priviliege_access_value AS priviliege_access_value"
        sql += " FROM (select sc_user.* from sc_userrole,sc_role,sc_user where "
        sql += " sc_userrole.role_id=sc_role.id and sc_role.role_level=2 and sc_user.id=sc_userrole.user_id"
        if manager_name:
            sql += " and sc_user.login_name like '%%" + manager_name + "%%'"
        sql += " )sc_user"
        if level_id != "0":
            sql += " ,sc_privilege where"
        else:
            sql += " LEFT JOIN sc_privilege ON"
        sql += " 1 = 1"
        if level_id != "0":
            sql += " and sc_privilege.priviliege_access_value=" + level_id
        sql += " and sc_privilege.privilege_master='SC_User' "
        sql += " and sc_privilege.priviliege_access = 'sc_account_manager_level'"
        sql += " and sc_privilege.priviliege_master_id=sc_user.id order by sc_privilege.priviliege_access_value,sc_user.id"
        data = db.engine.execute(sql)
        return data

    def edit(self, user_id, level_id):
        data = SC_Privilege.query.filter_by(priviliege_master_id=user_id, privilege_master="SC_User", priviliege_access
        ="sc_account_manager_level").first()
        if data:
            SC_Privilege.query.filter_by(priviliege_master_id=user_id, privilege_master="SC_User", priviliege_access
            ="sc_account_manager_level").update({"priviliege_access_value": level_id})
            db.session.commit()
        else:
            try:
                SC_Privilege("SC_User", user_id, "sc_account_manager_level", level_id, 0).add()
                # 事务提交
                db.session.commit()
                # 消息闪现
                flash('保存成功', 'success')
            except:
                # 回滚
                db.session.rollback()
                logger.exception('exception')
                # 消息闪现
                flash('保存失败', 'error')

    #层级查询
    def queryPerform(self, request):
        level_id = request.form['level_id']
        manager_name = request.form['manager_name']
        sql = "select a.month AS month,a.manager_id AS manager_id,d.level_name AS level_name,"
        sql += " a.count AS count,a.valid_sum AS valid_sum,a.month_rest as month_rest,a.balance_scale as balance_scale,"
        sql += " b.login_name as login_name,c.total as assess_result"
        sql += " from"
        if level_id != "0":
            if manager_name:
                sql += " (select p.* from sc_performance_list p,sc_user q where p.manager_id=q.id and level_id=" + level_id + " and q.login_name like '%%" + manager_name + "%%') a"
            else:
                sql += " (select p.* from sc_performance_list p where level_id=" + level_id + ") a"
        else:
            if manager_name:
                sql += " (select p.* from sc_performance_list p,sc_user q where p.manager_id=q.id and q.login_name like '%%" + manager_name + "%%') a"
            else:
                sql += " sc_performance_list a"
        sql += " LEFT JOIN  sc_kpi_officer c"
        sql += " on DATE_FORMAT(c.assess_date, '%%Y-%%M')=DATE_FORMAT(a.MONTH, '%%Y-%%M') and c.user_id=a.manager_id"
        sql += " LEFT JOIN sc_user b ON b.id = a.manager_id"
        sql += " LEFT JOIN sc_account_manager_level d ON d.level_id = a.level_id order by a.month desc"
        data = db.engine.execute(sql)
        return data

    #晋级查询
    def queryRise(self):
        data = db.session.query(SC_examine_rise, SC_Privilege, SC_account_manager_level, SC_User).filter(
            SC_examine_rise.manager_id == SC_User.id, SC_Privilege.priviliege_master_id == SC_User.id,
            SC_Privilege.privilege_master == "SC_User",
            SC_Privilege.priviliege_access == "sc_account_manager_level",
            SC_account_manager_level.level_id == SC_Privilege.priviliege_access_value).all()
        return data

    #晋级审核
    def editRise(self, manager_id, apply_type, level_id, apply_result):
        try:
            #同意
            if apply_result == '2':
                #晋级
                if apply_type == '1':
                    SC_Privilege.query.filter_by(priviliege_master_id=manager_id, privilege_master="SC_User",
                                                 priviliege_access
                                                 ="sc_account_manager_level").update(
                        {"priviliege_access_value": int(level_id) + 1})
                else:
                    SC_Privilege.query.filter_by(priviliege_master_id=manager_id, privilege_master="SC_User",
                                                 priviliege_access
                                                 ="sc_account_manager_level").update(
                        {"priviliege_access_value": int(level_id) - 1})
            SC_examine_rise.query.filter_by(manager_id=manager_id, apply_result=1).update(
                {"apply_result": apply_result})
            # 事务提交
            db.session.commit()
        except:
            # 回滚
            db.session.rollback()
            logger.exception('exception')