#coding:utf-8

# 信息管理
from scapp.models.information import SC_Target_Customer
from scapp.models.information import SC_Individual_Customer
from scapp.models.information import SC_Dealings
from scapp.models.information import SC_Credentials_Type
from scapp.models.information import SC_Company_Customer
from scapp.models.information import SC_Relations
from scapp.models.information import SC_Relation_Type
from scapp.models.information import SC_Manage_Info
from scapp.models.information import SC_Industry
from scapp.models.information import SC_Asset_Info
from scapp.models.information import SC_Financial_Affairs
from scapp.models.information import SC_Other_Info
from scapp.models.information import SC_Regisiter_Type
from scapp.models.information import SC_Business_Type
from scapp.models.information import SC_Asset_Type
from scapp.models.information import SC_Loan_Purpose

#流程管理
from scapp.models.process import SC_Loan_Apply
from scapp.models.process import SC_Apply_Info
from scapp.models.process import SC_Credit_History
from scapp.models.process import SC_Co_Borrower
from scapp.models.process import SC_Guarantees_For_Others
from scapp.models.process import SC_Guaranty
from scapp.models.process import SC_Guarantees
from scapp.models.process import SC_Financial_Overview
from scapp.models.process import SC_Non_Financial_Analysis
from scapp.models.process import SC_Riskanalysis_And_Findings
from scapp.models.process import SC_Approval_Decision
from scapp.models.process import SC_Credit_Upload

# 系统管理
from scapp.models.system import SC_UserRole
from scapp.models.system import SC_User
from scapp.models.system import SC_Role
from scapp.models.system import SC_Privilege
from scapp.models.system import SC_Menu
from scapp.models.system import SC_Org

#视图管理
from scapp.models.views import View_Query_Loan
from scapp.models.views import View_Get_Cus_Mgr
