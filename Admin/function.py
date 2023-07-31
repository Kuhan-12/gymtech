from database import db,Registration,Equipment,Member,Staff,Plans,Payment
from sqlalchemy import text
import datetime
from werkzeug.utils import secure_filename
from flask import current_app
import razorpay
import os

client = razorpay.Client(auth=("rzp_live_OlSWv9YA7i7L6E", "wuXOynB8EdJN1aW80Uylihve"))

client.set_app_details({"title" : "Techpath", "version" : "0.1"})
UPLOAD_FOLDER = 'static/dist/img'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}


def allowed_file(filename):
        return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

class data:
    def __init__(self,app):
        self.app = app  
    def new_user(self,req,ref):
        user = Registration(        
            Fullname = req.get('Fullname'),
            Email = req.get('Email'),
            Username = req.get('Username'),
            Password = req.get('Password'),
            Contact = req.get('Contact'),
            Gender = req.get('Gender'),
            Type = req.get('Type'),
            file = ref.get('file')
            )
        if user.file and allowed_file(user.file.filename): 
              filename = secure_filename(user.file.filename)
              user.file.save(os.path.join(UPLOAD_FOLDER, filename))
              user.file=UPLOAD_FOLDER+'/'+filename
        else:
            user.file='static/dist/img/user_logo.png'
        return user
    def Member_data(self):
        query = db.session.execute(text('select Members.Member_Id,Members.Cust_Id,User.Username,User.Fullname,User.Gender,User.Contact,Plans.Plan_Name,Plans.Time_Period,Staff.Reg_Id,Staff.Fees,Members.Total_Fees,Members.Start_Date,Equipment.Name from Staff,Plans,Members,User,Equipment where Members.Cust_Id = User.User_Id and Members.Plan_Id = Plans.Plans_Id and Members.Trainer_Id = Staff.Staff_id and Members.Equipment_Id = Equipment.Equipment_Id Order by Member_Id ASC'))
        return query
    def Member_Count(self):    
        with current_app.app_context():
            quer = text('select COUNT(Member_Id) from Members')
            count = db.session.execute(quer)
            return count
    def Staff_Count(self):
        with current_app.app_context():
            quer = text('select COUNT(Staff_id) from Staff')
            cnt = db.session.execute(quer)
            return cnt
    def Unpaid_Customer_Count(self):    
        with current_app.app_context():
            quer = text('select COUNT(Order_Id) from Payment where Status = "Success"')
            count = db.session.execute(quer)
            return count
    def Equipment_Count(self):
        with current_app.app_context():
            count = db.session.execute(text('select COUNT(Equipment_Id) from Equipment'))
            return count
    def Member_all(self):
        query = db.session.query(Member).order_by(Member.Member_Id).all()
        return query
    def equipment(self,form,fil):
        kit = Equipment(
             Name = form.get('Name'),
             Quantity = form.get('Quantity'),
             Image = fil.get('Image'),
             Weight = form.get('Weight'),
             Category = form.get('Category'),
             Company = form.get('Company'),
             Equipment_Charge = form.get('Equipment_Charge')
             )
        if kit.Image and allowed_file(kit.Image.filename):
             filename = secure_filename(kit.Image.filename)
             kit.Image.save(os.path.join(UPLOAD_FOLDER, filename))
             kit.Image=UPLOAD_FOLDER+'/'+filename
        return kit
    def Equipment_Data(self):
        query = db.session.query(Equipment).order_by(Equipment.Equipment_Id).all()
        return query
    def Read_Equipment(self,Id):
        query = db.session.query(Equipment).filter_by(Equipment_Id=Id).first()
        return query
    def Equipment_with_Charge(self):
        with current_app.app_context():
            query = db.session.execute(text('select Equipment_Id,Name from Equipment where Equipment_Charge != "0"'))
            return query
    def Read_Member(self,id):
        query = db.session.query(Registration).filter_by(User_Id=id).first()
        return query
    def Read_Customer(self,id):
        query = db.session.query(Member).filter_by(Member_Id=id).first()
        return query
        return query
    def check_member(self):
         with current_app.app_context():
            user = db.session.execute(text('select * from User order by User_Id DESC limit 1'))
            return user
    def new_customer(self,req):
        customer = Member(
        Trainer_Id = req.get("Trainer_Id"),
        Start_Date = datetime.date.today(),
        Plan_Id = req.get("Plan_Id"),
        Cust_Id = req.get("Cust_Id"),
        Equipment_Id = req.get('Equipment_Id'),
        Total_Fees = req.get('Total_Fees')
        )
        trainer_Fees = data(current_app).select_Trainer_fees(req.get("Trainer_Id")).Fees
        plan_price = data(current_app).select_Plan(req.get("Plan_Id")).Price
        equipment_charge = data(current_app).select_Equipment(req.get("Equipment_Id")).Equipment_Charge
        customer.Total_Fees = int(trainer_Fees) + int(plan_price) + int(equipment_charge)
        return customer
    def new_employee(self,req):
        emp = Staff(
             Occupation = req.get("Occupation"),
             Working_Days = req.get("Working_Days"),
             Experience = req.get("Experience"),
             Salary = req.get("Salary"),
             Fees = req.get("Fees"),
             Total = req.get("Total"),
             Reg_Id = req.get("Reg_Id")
        )
        emp.Total = int(emp.Salary)+int(emp.Fees)
        return emp
    def Staff_Data(self):
         query = db.session.execute(text('select User.User_Id,User.Fullname,User.Email,User.Contact,User.Gender,Staff.Occupation,Staff.Working_Days,Staff.Experience,Staff.Salary,Staff.Fees,Staff.Total,Staff.Staff_id from User,Staff where Staff.Reg_Id = User.User_Id and User.Type = "Employee" Order BY Staff_id ASC'))
         return query
    def trainer_data(self):
        query = db.session.query(Staff).join(Registration).add_columns(Registration.Fullname,Staff.Fees,Staff.Occupation,Staff.Experience,Registration.file).order_by(Staff.Staff_id).filter(Staff.Occupation=="Trainer").all()
        return query
    def Read_Staff(self,Id):
         query = db.session.query(Staff).filter_by(Staff_id=Id).first()
         return query
    def Remove_User(self,userId):
         query = db.session.execute(db.delete(Registration).filter_by(User_Id=userId)).scalar()
         return query
    def Trainer(self):
         query = db.session.query(Staff).join(Registration).add_columns(Registration.Fullname,Staff.Staff_id,Staff.Fees).filter(Staff.Reg_Id==Registration.User_Id,Staff.Occupation=="Trainer").all()
         return query
    def select_Trainer(self,staffId):
        query = db.session.query(Staff).join(Registration).add_columns(Registration.Fullname,Registration.Contact,Registration.Email,Registration.Gender,Staff.Reg_Id).filter_by(User_Id=staffId).first()
        return query
    def select_Trainer_fees(self,staffId):
        query = db.session.query(Staff).filter_by(Staff_id=staffId).first()
        return query
    def select_Plan(self,planId):
        query = db.session.query(Plans).filter_by(Plans_Id=planId).first()
        return query
    def select_Equipment(self,equipId):
        query = db.session.query(Equipment).filter_by(Equipment_Id=equipId).first()
        return query
    def Query_Plan(self):
        query = db.session.query(Plans).order_by(Plans.Plans_Id).all()
        return query
    def Member_Update(self,req,ref,membId,useId):
        query = data(current_app).Read_Customer(membId)
        query_registration = data(current_app).Read_Member(useId) 
        query_registration.Fullname = req.get('Fullname')
        query_registration.Contact = req.get('Contact')
        query_registration.Gender = req.get('Gender')
        query_registration.Email = req.get('Email')
        query_registration.file = ref.get('file')
        if query_registration.file and allowed_file(query_registration.file.filename): 
              filename = secure_filename(query_registration.file.filename)  # type: ignore
              query_registration.file.save(os.path.join(UPLOAD_FOLDER, filename))
              query_registration.file=UPLOAD_FOLDER+'/'+filename
        else:
            query_registration.file='static/dist/img/user_logo.png'
        query.Trainer_Id = req.get('Trainer_Id')
        query.Plan_Id = req.get('Plan_Id')
        query.Equipment_Id = req.get('Equipment_Id')
        query.Start_Date = datetime.date.today()
        trainer_Fees = data(current_app).select_Trainer_fees(req.get("Trainer_Id")).Fees
        plan_price = data(current_app).select_Plan(req.get("Plan_Id")).Price
        equipment_charge = data(current_app).select_Equipment(req.get("Equipment_Id")).Equipment_Charge
        query.Total_Fees = int(trainer_Fees) + int(plan_price) + int(equipment_charge)
        return query_registration.Fullname,query_registration.Gender,query_registration.file,query_registration.Email,query_registration.Contact,query.Trainer_Id,query.Plan_Id,query.Equipment_Id,query.Total_Fees
    def Staff_Update(self,req,ref,staffId,userId):
        staff_query = data(current_app).Read_Staff(staffId)
        member_query = data(current_app).Read_Member(userId)
        member_query.Fullname = req.get('Fullname')
        member_query.Contact = req.get('Contact')
        member_query.Email = req.get('Email')
        member_query.file = ref.get('file')
        if member_query.file and allowed_file(member_query.file.filename): 
            filename = secure_filename(member_query.file.filename)
            member_query.file.save(os.path.join(UPLOAD_FOLDER, filename))
            member_query.file=UPLOAD_FOLDER+'/'+filename
        else:
            member_query.file='static/dist/img/user_logo.png'
        staff_query.Experience = req.get('Experience')
        staff_query.Working_Days = req.get('Working_Days')
        staff_query.Fees = req.get('Fees')
        staff_query.Salary = req.get('Salary')
        staff_query.Total = int(staff_query.Fees) + int(staff_query.Salary)
        return member_query.Fullname,member_query.Contact,member_query.file,member_query.Email,staff_query.Experience,staff_query.Working_Days,staff_query.Total
    def Equipment_Update(self,req,ref,equipment_Id):
        equipment_query = data(current_app).select_Equipment(equipment_Id)
        equipment_query.Name = req.get('Name')
        equipment_query.Quantity = req.get('Quantity')
        equipment_query.Weight = req.get('Weight')
        equipment_query.Category = req.get('Category')
        equipment_query.Company = req.get('Company')
        equipment_query.Equipment_Charge = req.get('Equipment_Charge')
        equipment_query.Image = ref.get('Image')
        if equipment_query.Image and allowed_file(equipment_query.Image.filename):
             filename = secure_filename(equipment_query.Image.filename)
             equipment_query.Image.save(os.path.join(UPLOAD_FOLDER, filename))
             equipment_query.Image=UPLOAD_FOLDER+'/'+filename
             print(equipment_query.Image)
        else:
            equipment_query.Image='static/dist/img/user_logo.png'
        return equipment_query.Name,equipment_query.Quantity,equipment_query.Weight,equipment_query.Category,equipment_query.Company,equipment_query.Equipment_Charge,equipment_query.Image
    def Data_Unpaid_Customer(self):
        query = db.session.query(Payment).join(Registration and Plans).add_columns(Registration.User_Id,Registration.Fullname,Registration.Gender,Registration.Email,Registration.Contact,Plans.Plan_Name).filter(Payment.Customer_Id==Registration.User_Id,Payment.Plan_Id==Plans.Plans_Id,Payment.Status=="Success").order_by(Registration.User_Id).all()
        return query
    def Read_Unpaid_Customer(self,userId):
        query = db.session.query(Registration).filter_by(User_Id=userId).first()
        return query
    def date_Member(self):
        query = db.session.execute(db.select(Member.Start_Date).order_by(Member.Member_Id)).all()
        return query
    def Count_MemberId(self):
        query =db.session.execute(db.select(Member.Member_Id).order_by(Member.Member_Id)).all()
        return query
    def generate_order_id(self,price):
            data = { "amount": int(price)*100, "currency": "INR", "receipt": "order_rcptid_11" }
            payment = client.order.create(data=data)
            order_id=payment['id']
            return order_id
    def Graphical_Representation(self):
        query = db.session.execute(text('select MONTH(Start_Date) as Month_Number,MONTHNAME(Start_Date) as Month_Name,COUNT(*) as Member_Count from Members group by MONTH(Start_Date),MONTHNAME(Start_Date) order by MONTH(Start_Date)'))
        return query
    def Plan_Update(self,req,planId):
        plans = data(current_app).select_Plan(planId)
        plans.Price=req.get('Price')
        return plans.Price
    def payment(self,req):
        paid = Payment(
            Cutomer_Id = req.get('Customer_Id'),
            Plan_Id = req.get('Plan_Id'),
            Date = datetime.date.today(),
            Order_Id_RZP = req.get('Order_Id_RZP'),
            Payment_Id_RZP = req.get('Payment_Id_RZP')
        )
        return paid