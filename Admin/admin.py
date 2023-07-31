from flask import Blueprint,render_template,redirect,request,url_for,flash
from flask_login import login_required
from Admin.function import data
import datetime
import calendar
from database import db,Registration

adminRoute=Blueprint('admin',__name__)
func = data(adminRoute)

@adminRoute.route('/admin')
def admin():
       return redirect('/loginPage')

@adminRoute.route('/admin/<id>',methods=['GET','POST'])
@login_required
def panel(id):
       cnt = func.Member_Count()
       c = []
       for i in cnt:
              c.append(i[0])
       ct = func.Staff_Count()
       cn = func.Equipment_Count()
       typ = func.Read_Member(id)
       paid_cust_cnt = func.Unpaid_Customer_Count()
       data_graph = func.Graphical_Representation()
       plan = func.Query_Plan()
       graph = []
       for row in data_graph:
              graph.append(row)
       l = len(graph)
       monthly_data = []
       for rows in range(l):
              graph_data={
                     'Month_Name':graph[rows].Month_Name,
                     'Member_Count':graph[rows].Member_Count
              }
              monthly_data.append(graph_data)
       existing_months = set(data['Month_Name'] for data in monthly_data)
       all_months = [calendar.month_name[i] for i in range(1, 13)]
       for month in all_months:
              if month not in existing_months:
                     monthly_data.append({'Month_Name': month, 'Member_Count': 0})
       monthly_data.sort(key=lambda x: all_months.index(x['Month_Name']))
       l1 = len(monthly_data)
       return render_template('/admin/adminpanel.html',plan=plan,list_graph=monthly_data,cust=paid_cust_cnt,cnt=cnt,typ=typ,ct=ct,cn=cn,l=l1,c=c)

@adminRoute.route('/admmin/pending/<adminId>')
@login_required
def pending_member(adminId):
       typ = func.Read_Member(adminId)
       user = func.Data_Unpaid_Customer()
       l = len(user)
       return render_template('/admin/pendingpayment.html',l=l,user=user,typ=typ)

@adminRoute.route('/amdin/unpaid_customer/registration/<adminId>/<userId>',methods=['GET','POST'])
@login_required
def unpaid_customer(adminId,userId):
       if request.method=="POST":
              cust = request.form
              typ = func.Read_Member(adminId)
              memb = func.Member_all()
              jon = func.new_customer(cust)
              last = func.Read_Unpaid_Customer(userId)
              if last.User_Id in memb:
                     return render_template('/admin/error.html')
              else:
                     jon.Cust_Id = last.User_Id
              db.session.add(jon)
              db.session.commit()
              return redirect(url_for('admin.member_data',adminId=typ.User_Id))
       if request.method=="GET":
              typ = func.Read_Member(adminId)
              member = func.Member_data()
              equipment = func.Equipment_with_Charge()
              last = func.Read_Unpaid_Customer(userId)
              equip_list = []
              for row in equipment:       
                     equip_list.append(row)
              len_equip_list = len(equip_list)
              trainer = func.Trainer()
              plan = func.Query_Plan()
              return render_template('customerregistration.html',member=member,len_equip_list=len_equip_list,typ=typ,trainer=trainer,plan=plan,equip_list=equip_list,newbies_data=last)

@adminRoute.route('/admin/members/<adminId>',methods=["GET","POST"])
@login_required
def member_data(adminId):
       typ = func.Read_Member(adminId)
       memb = func.Member_data()
       memb_list = []
       for row in memb:
              memb_list.append(row)
       l=len(memb_list)
       member_list=[]
       for rows in range(l):
              memb_data={
                     'Serial No.':rows+1,
                     'Member_Id':memb_list[rows].Member_Id,
                     'User_Id':memb_list[rows].Cust_Id,
                     'Name':memb_list[rows].Fullname,
                     'Gender':memb_list[rows].Gender,
                     'Plans':memb_list[rows].Plan_Name,
                     'Trainers':func.select_Trainer(memb_list[rows].Reg_Id).Fullname,
                     'Months':memb_list[rows].Time_Period,
                     'Trainer_Fee':memb_list[rows].Fees,
                     'Equipment':memb_list[rows].Name,
                     'Total_Fee':memb_list[rows].Total_Fees,
                     'Contact':memb_list[rows].Contact,
                     'Start_Date':memb_list[rows].Start_Date
              }
              if memb_list[rows].Plan_Name == "Silver":
                     memb_data['End_Date'] = memb_list[rows].Start_Date + datetime.timedelta(days=30)
              elif memb_list[rows].Plan_Name == "Gold":
                     memb_data['End_Date'] = memb_list[rows].Start_Date + datetime.timedelta(days=90)
              else:
                     memb_data['End_Date'] = memb_list[rows].Start_Date + datetime.timedelta(days=365)
              member_list.append(memb_data)
       return render_template('/admin/members.html',l=l,memb=member_list,typ=typ)

@adminRoute.route('/admin/member/registration/<id>',methods=['GET','POST']) # type: ignore
@login_required
def add_user(id):
       if request.method=='POST':
              fetch = request.form
              save = request.files
              username = Registration.query.filter_by(Username=fetch["Username"]).all()
              email = Registration.query.filter_by(Email=fetch["Email"]).all()
              contact = Registration.query.filter_by(Contact=fetch["Contact"]).all()
              if username:
                     flash('Already There!','error')
                     return render_template('/user/join.html')
              elif email:
                     flash('Already There!','same')
                     return render_template('/user/join.html')
              elif contact:
                     flash('Already There!','there')
                     return render_template('/user/join.html')
              data = func.new_user(fetch,save)
              db.session.add(data)
              db.session.commit()
              typ = func.Read_Member(id)
              if data.Type=="Admin":
                     return redirect(url_for('admin.member_data',id=typ.User_Id))
              elif data.Type=="Employee":
                     return redirect(url_for('admin.new_recruit',adminid=typ.User_Id))
              else:
                     return redirect(url_for('admin.new_customer',adminId=typ.User_Id))
       if request.method=='GET':
              typ = func.Read_Member(id)
              return render_template('/admin/commonregistration.html',typ=typ)

@adminRoute.route('/admin/member/delete/<adminid>/<custId>/<user_Id>')
@login_required
def delete(adminid,custId,user_Id):
       typ = func.Read_Member(adminid)
       rem = func.Read_Customer(custId)
       user = func.Read_Member(user_Id)
       db.session.delete(rem)
       db.session.delete(user)
       db.session.commit()
       return redirect(url_for('admin.member_data',adminId=typ.User_Id))
       
@adminRoute.route('/admin/equipment/<adminId>')
@login_required
def equipment_data(adminId):
       typ = func.Read_Member(adminId)
       equip = func.Equipment_Data()
       l=len(equip)
       return render_template('/admin/equipments.html',l=l,equip=equip,typ=typ)

@adminRoute.route('/admin/equipment/newTool/<adminId>',methods=['GET','POST']) # type: ignore
@login_required
def new_equipment(adminId):
       if request.method=='POST':
              dat = request.form
              savy = request.files
              rem=func.Read_Member(adminId)
              equip = func.equipment(dat,savy)
              db.session.add(equip)
              db.session.commit()
              return redirect(url_for('admin.equipment_data',adminId=rem.User_Id))
       if request.method=='GET':
              rem=func.Read_Member(adminId)
              return render_template('/admin/equipmentsregistration.html',rem=rem)

@adminRoute.route('/admin/equipment/update/<adminId>/<EquipId>',methods=['GET','POST'])
@login_required
def update_equipment(adminId,EquipId):
       if request.method=="POST":
              req = request.form
              ref = request.files
              rem = func.Read_Member(adminId)
              func.Equipment_Update(req,ref,EquipId)
              db.session.commit()
              return redirect(url_for('admin.equipment_data',adminId = rem.User_Id))
       if request.method=="GET":
              rem = func.Read_Member(adminId)
              tool_upgrade = func.select_Equipment(EquipId)
              return render_template('/admin/updateEquipment.html',tool_upgrade=tool_upgrade,rem=rem)

@adminRoute.route('/admin/equipment/delete/<adminId>/<EquipId>')
@login_required
def remove_equipment(adminId,EquipId):
       typ = func.Read_Member(adminId)
       rem = func.Read_Equipment(EquipId)
       db.session.delete(rem)
       db.session.commit()
       return redirect(url_for('admin.equipment_data',adminId = typ.User_Id))
       
@adminRoute.route('/admin/staff/<adminId>')
@login_required
def employees(adminId):
       typ = func.Read_Member(adminId)
       employee = func.Staff_Data()
       employee_list=[]
       for row in employee:
              employee_list.append(row)
       l = len(employee_list)
       data_employee=[]
       for rows in range(l):
              employee_data = {
                     'Serial No.':rows+1,
                     'User_Id':employee_list[rows].User_Id,
                     'Staff_id':employee_list[rows].Staff_id,
                     'Name':employee_list[rows].Fullname,
                     'Email':employee_list[rows].Email,
                     'Contact':employee_list[rows].Contact,
                     'Gender':employee_list[rows].Gender,
                     'Occupation':employee_list[rows].Occupation,
                     'Working_Days':employee_list[rows].Working_Days,
                     'Experience':employee_list[rows].Experience,
                     'Salary':employee_list[rows].Salary,
                     'Fees':employee_list[rows].Fees,
                     'Total':employee_list[rows].Total
              }
              data_employee.append(employee_data)
       return render_template('/admin/staff.html',wager=data_employee,typ=typ,l=l)

@adminRoute.route('/admin/staff/delete/<adminid>/<staffId>/<userId>')
@login_required
def rem_staff(adminid,staffId,userId):
       typ = func.Read_Member(adminid)
       rem = func.Read_Staff(staffId)
       db.session.delete(rem)
       user = func.Read_Member(userId)
       db.session.delete(user)
       db.session.commit()
       return redirect(url_for('admin.employees',adminId=typ.User_Id))

@adminRoute.route('/admin/staff/update/<adminid>/<staffId>/<userId>',methods=['GET','POST'])
@login_required
def staff_update(adminid,staffId,userId):
       if request.method=="POST":
              req = request.form
              ref = request.files
              typ = func.Read_Member(adminid)
              func.Staff_Update(req,ref,staffId,userId)
              db.session.commit()
              return redirect(url_for('admin.employees',adminId=typ.User_Id))
       if request.method=="GET":
              typ = func.Read_Member(adminid)
              employee_update = func.Read_Staff(staffId)
              user_update = func.Read_Member(userId)
              return render_template('/admin/updatestaff.html',employee_update=employee_update,user_update=user_update,typ=typ)

@adminRoute.route('/amdin/customer/registration/<adminId>',methods=['GET','POST'])
@login_required
def new_customer(adminId):
       if request.method=="POST":
              cust = request.form
              typ = func.Read_Member(adminId)
              last = func.check_member()
              newbies_data=[]
              for row in last:
                     newbies_data.append(row)
              jon = func.new_customer(cust)
              jon.Cust_Id = newbies_data[0][0]          
              db.session.add(jon)
              db.session.commit()
              return redirect(url_for('admin.member_data',adminId=typ.User_Id))
       if request.method=="GET":
              typ = func.Read_Member(adminId)
              member = func.Member_data()
              equipment = func.Equipment_with_Charge()
              last = func.check_member()
              newbies_data=[]
              for row in last:
                     newbies_data.append(row)
              equip_list = []
              for row in equipment:       
                     equip_list.append(row)
              len_equip_list = len(equip_list)
              trainer = func.Trainer()
              plan = func.Query_Plan()
              return render_template('/admin/membersregistration.html',member=member,len_equip_list=len_equip_list,typ=typ,trainer=trainer,plan=plan,equip_list=equip_list,newbies_data=newbies_data)

@adminRoute.route('/admin/staff/registration/<adminid>',methods=["GET","POST"])
@login_required
def new_recruit(adminid):
       if request.method=="POST":
              new = request.form
              rem = func.Read_Member(adminid)
              last = func.check_member()
              newbies_data =[]
              for row in last:
                     newbies_data.append(row)
              recruit = func.new_employee(new)
              recruit.Reg_Id=newbies_data[0][0]
              db.session.add(recruit)
              db.session.commit()
              return redirect(url_for('admin.employees',adminId=rem.User_Id))
       if request.method=="GET":
              rem = func.Read_Member(adminid)
              last = func.check_member()
              newbies_data =[]
              for row in last:
                     newbies_data.append(row)
              return render_template('/admin/staffregistration.html',rem=rem,newbies_data=newbies_data)
       
@adminRoute.route('/admin/member/update/<adminId>/<membId>/<userId>',methods=["GET","POST"]) # type: ignore
@login_required
def update_customer(adminId,membId,userId):
       if request.method=="POST":
              req = request.form
              ref = request.files
              typ = func.Read_Member(adminId)
              func.Member_Update(req,ref,membId,userId)
              db.session.commit()
              return redirect(url_for('admin.member_data',adminId=typ.User_Id))
       if request.method=="GET":
              typ = func.Read_Member(adminId)
              customer_update = func.Read_Customer(membId)
              member_update = func.Read_Member(userId)
              trainer_data = func.select_Trainer_fees(customer_update.Trainer_Id)
              trainer_name = func.Read_Member(trainer_data.Reg_Id)
              plan_data = func.select_Plan(customer_update.Plan_Id)
              equipment_data = func.Read_Equipment(customer_update.Equipment_Id)
              equipment = func.Equipment_with_Charge()
              equip_list = []
              for row in equipment:
                     equip_list.append(row)
              len_equip_list = len(equip_list)
              trainer = func.Trainer()
              plan = func.Query_Plan()
              return render_template('/admin/updatemembers.html',typ=typ,plan_data=plan_data,equipment_data=equipment_data,trainer_data=trainer_data,trainer_name=trainer_name,equip_list=equip_list,customer_update=customer_update,member_update=member_update,len_equip_list=len_equip_list,trainer=trainer,plan=plan)

@adminRoute.route('/admin/Plans/<adminId>')
def show_plans(adminId):
       plan = func.Query_Plan()
       typ = func.Read_Member(adminId)
       return render_template('/admin/planupdate.html',plan=plan,typ=typ)

@adminRoute.route('/admin/Plans/Update/<adminId>/<planId>',methods=['POST'])
def update_plans(adminId,planId):
       if request.method=='POST':
              req = request.form
              typ = func.Read_Member(adminId)
              func.Plan_Update(req,planId)
              db.session.commit()
              return redirect(url_for('admin.show_plans',adminId=typ.User_Id))