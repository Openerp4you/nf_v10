from openerp import api, fields, models, _
from email import _name
from datetime import datetime 
import time
import os
#from openerp.addons.web.http import request
import smtplib
import urlparse
import mimetypes
from email.mime.multipart import MIMEMultipart
from email import encoders
from email.message import Message
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.text import MIMEText
from dateutil.relativedelta import relativedelta
from pygments.lexer import _inherit
from lib2to3.fixer_util import String
from datetime import date, timedelta
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT
from openerp.exceptions import UserError, RedirectWarning, ValidationError
from reportlab.lib.pdfencrypt import computeO
from odoo.exceptions import ValidationError
from openerp.osv import osv


class HrBudget(models.Model):
    _name = "hr.budget"
    _description = "HR Budget"
    
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    
    @api.model
    def _default_user(self):
        return self.env.user.id
    
    name = fields.Char(string="Serial Number")
    dept = fields.Many2one('hr.department',string="Sub Department" , required=True)
    manager = fields.Many2one('hr.employee', string="Manager" )
    date = fields.Date(string='Date',default=fields.datetime.now())
#     branch = fields.Many2one('hr.department',string='Branch')
    branch_id =fields.Many2one('hr.branch','Branch')
    budget_lines = fields.One2many('budget.lines','budget_id',string='Budget Lines')    
    comments = fields.Text(string='Comments')
    user_id = fields.Many2one('res.users','User',default=_default_user)
    send_to = fields.Many2one('res.users',string='Send To')    
    review_by = fields.Many2one('res.users',string='Review By') 
    state = fields.Selection([
            ('draft', 'Draft'),
            ('confirm', 'Confirmed'),
            ('approve', 'Approved'),
            ], track_visibility='onchange' ,default='draft')
    budget_year = fields.Selection([(num, str(num)) for num in range(2012, (datetime.now().year)+5 )], 'Budget Year')
    
    @api.onchange('dept')
    def onchange_field(self):
        if self.dept :
            self.manager = self.dept.manager_id.id
         
    @api.multi
    def _get_sub_total(self):
            
            sum=0
            for lines in self.budget_lines:
                sum+=lines.total_cost
                
            self.sub_total=sum        
    sub_total = fields.Float(string="Budget Sub-Total", compute='_get_sub_total')
    
    @api.model
    def create(self, vals):
        if not vals.get('name'):
            seq = self.env['ir.sequence'].next_by_code('hr.budget')
            vals['name'] = seq
        return super(HrBudget, self).create(vals)
        
    @api.multi
    def send_email_confirm(self):
            
            et=[]
            et1=[]
            for lines in self.budget_lines:
                r = lines.job_id.name
                r1 = str(lines.new_res)
                et.append(r)
                et1.append(r1)
            base_url = self.env['ir.config_parameter'].get_param('web.base.url')
            rec_id = self.id
            print"context====",self._context['params']['action']
#             model = self
            context = self._context
            context.get('active_model')
            action_id = self._context['params']['action']
            a = """ """+str(base_url)+"""/web#id="""+str(self.id)+"""&view_type=form&model="""+str(context.get('active_model'))+"""&action="""+str(action_id)+""" """
            ef = """<a href="""+a+""">"""+self.name+"""</a>"""
            
            
            out_server = self.env['ir.mail_server'].search([])
            if out_server:
                out_server = out_server[0]
                emailfrom=''
                emailto = []
                if out_server.smtp_user:
                    emailfrom =out_server.smtp_user
                if self.send_to:
                    emailto = [self.send_to.login]
                msg = MIMEMultipart()
                if emailfrom and emailto:
                    msg['From'] = emailfrom
                    if emailto:
                        msg['To'] = ", ".join(emailto)
                    msg['Subject'] = 'Please Confirm Budget'
                    html = """<!DOCTYPE html>
                             <html>
                             <p>Dear HOD,</p>
                             <tr>
                                  <td ><left><p>Mr.<b> """+str(self.manager.name)+""" </b>From<b> """+str(self.dept.name)+"""</b> Department<b> """+str(self.branch_id.name)+""" </b>Branch has requested.</P></left></td>
                             </tr>
        
                               <body>
                            
                            <table>
        
                            <tbody>
                            
                            <tr>
                            
                            <td style="width:135px" ><b>Job Position</b></td>
                            
                            <td style="width: 85px;" ><b>New Employees</b></td>
                            
                                             
                            </tr>
                            
                            
                            
                            <tr >
                            
                            <td class="text-center" style="width:135px">"""+ "<br/>".join(et)+""" </td>
                            
                            
                            <td class="text-center" style="width: 85px;">"""+ "<br/>".join(et1)+"""</td>
                            
                            </tr>
                            
                            
                            <tbody>
                            
                            <table>
        
        
        
                           <p>Please Click Here  """+ef+""" to Approve  Budget.</p>
                                
                            
                           
                           <p>Regards</p>
                           <p>Admin</p>
                           </body>
                           
                           
            
                            </html>
                          """
            #        part1 = MIMEText(text, 'plain')
                    part1 = MIMEText(html, 'html')
                    msg.attach(part1)
            #        msg.attach(part2)
                    server = smtplib.SMTP_SSL(out_server.smtp_host,out_server.smtp_port)
            #        server.ehlo()
            #         server.starttls()
                    server.login(emailfrom,out_server.smtp_pass)
                    text = msg.as_string()
                    server.sendmail(emailfrom, emailto , text)
                    server.quit()
            return True
    
    
    @api.multi
    def send_email_revise(self):
            base_url = self.env['ir.config_parameter'].get_param('web.base.url')
            rec_id = self.id
#             print"====self.env=====",self._model
            print"context====",self._context['params']['action']
#             model = self._model
            context = self._context
            context.get('active_model')
            action_id = self._context['params']['action']
            a = """ """+str(base_url)+"""/web#id="""+str(self.id)+"""&view_type=form&model="""+str(context.get('active_model'))+"""&action="""+str(action_id)+""" """
            ef = """<a href="""+a+""">"""+self.name+"""</a>"""
            
            
            out_server = self.env['ir.mail_server'].search([])
            if out_server:
                out_server = out_server[0]
                emailto=[]
                emailfrom =out_server.smtp_user
                if self.user_id.login:
                    emailto.append(self.user_id.login)
                print"emailfrom==emailto==",emailfrom,emailto
                if emailfrom and emailto:
                    msg = MIMEMultipart()
                    msg['From'] = emailfrom
                    msg['To'] = ", ".join(emailto)
                    msg['Subject'] = 'Please Revise Budget'
            
                    html = """<!DOCTYPE html>
                             <html>
                             
                             <tr>
                                  <td style="color:#FF69B4"><left><h2><p>MR """+str(self.manager.name)+""" From """+str(self.dept.name)+""" Department """+str(self.branch_id.name)+""" Branch has requested  To review  Job Position .</P></h2></left></td>
                             </tr>
        
                               <body>
                           <p>Please Click Here """+ef+""" to Revise Budget.</p>      
                           <p>Regards</p>
                           <p>Admin</p>  
                           
                           </body>
                           
                               
                            </html>
                          """
                    #        part1 = MIMEText(text, 'plain')
                    part1 = MIMEText(html, 'html')
                    msg.attach(part1)
            #        msg.attach(part2)
                    server = smtplib.SMTP_SSL(out_server.smtp_host,out_server.smtp_port)
            #        server.ehlo()
            #         server.starttls()
                    server.login(emailfrom,out_server.smtp_pass)
                    text = msg.as_string()
                    server.sendmail(emailfrom, emailto , text)
                    server.quit()
            return True      
    
    
    @api.multi
    def send_email_approve(self):
            
            et=[]
            et1=[]
            for lines in self.budget_lines:
                r = lines.job_id.name
                r1 = str(lines.new_res)
                et.append(r)
                et1.append(r1)
            base_url = self.env['ir.config_parameter'].get_param('web.base.url')
            rec_id = self.id
#             print"====self.env=====",self._model
            print"context====",self._context['params']['action']
#             model = self._model
            context = self._context

            context.get('active_model')
            action_id = self._context['params']['action']
            a = """ """+str(base_url)+"""/web#id="""+str(self.id)+"""&view_type=form&model="""+str(context.get('active_model'))+"""&action="""+str(action_id)+""" """
            ef = """<a href="""+a+"""> """+self.name+"""</a>"""
            
            
            out_server = self.env['ir.mail_server'].search([])
            if out_server:
                out_server = out_server[0]
                emailfrom =out_server.smtp_user
                emailto = [self.manager.work_email]
                msg = MIMEMultipart()
                if emailfrom:
                    msg['From'] = emailfrom
                    if emailto:
                        msg['To'] = ", ".join(emailto)
                    msg['Subject'] = 'For Budget Approved '
                    html = """<!DOCTYPE html>
                             <html>
                             <p>Dear HOD,</p>
                             <tr>
                                  <td ><left><p>Mr.<b> """+str(self.manager.name)+""" </b>From<b> """+str(self.dept.name)+"""</b> Department<b> """+str(self.branch_id.name)+""" </b>Branch has requested.</P></left></td>
                             </tr>
        
                               <body>
                            
                            <table>
        
                            <tbody>
                            
                            <tr>
                            
                            <td style="width:135px" ><b>Job Position</b></td>
                            
                            <td style="width: 85px;" ><b>New Employees</b></td>
                            
                                             
                            </tr>
                            
                            
                            
                            <tr >
                            
                            <td class="text-center" style="width:135px">"""+ "<br/>".join(et)+""" </td>
                            
                            
                            <td class="text-center" style="width: 85px;">"""+ "<br/>".join(et1)+"""</td>
                            
                            </tr>
                            
                            
                            <tbody>
                            
                            <table>
        
        
        
                           <p>Here is your """+ef+"""  Approved  Budget.</p>
                                
                           <p>Keep up the Great Work of Now Floats.</p>  
                           
                           <p>Regards</p>
                           <p>Admin</p>
                           </body>
                           
                           
            
                            </html>
                          """
            #        part1 = MIMEText(text, 'plain')
                    part1 = MIMEText(html, 'html')
                    msg.attach(part1)
            #        msg.attach(part2)
                    server = smtplib.SMTP_SSL(out_server.smtp_host,out_server.smtp_port)
            #        server.ehlo()
            #         server.starttls()
                    server.login(emailfrom,out_server.smtp_pass)
                    text = msg.as_string()
                    server.sendmail(emailfrom, emailto , text)
                    server.quit()
            return True
    
    
    @api.multi
    def confirm_budget(self):
#         self.send_email_confirm()
        self.write({'state':'confirm'})
        
    @api.multi
    def approve_budget(self):
        for line in self.budget_lines:
            print'========position=====',line.job_id
            budgeted_emp = line.new_res #line.job_id.budgeted_emp +
            line.job_id.write({'budgeted_emp':budgeted_emp})
            print"========complete=========="
        self.write({'state':'approve'})
#         self.send_email_approve()
        return True
    
#             sql = """
#                 UPDATE public.hr_job
#                     SET budgeted_emp = (
#                         SELECT new_res
#                         FROM public.budget_lines
#                         WHERE public.budget_lines.id = public.hr_job.id
#         );
#     
#                 """
#         self.env.cr.execute(sql, (self.id, ))
        
         
      
    @api.multi
    def revise_budget(self):
#         self.send_email_revise()
        for line in self.budget_lines:
            if self.state == 'approve':
                budgeted_emp = line.job_id.budgeted_emp - line.new_res
                line.job_id.write({'budgeted_emp':budgeted_emp})
        self.write({'state':'draft'})
     
    
    
  
class budget_lines(models.Model):
    _name="budget.lines"
    _description="Budget Lines"
    
    @api.model
    def default_get(self, fields):
        rec =  super(budget_lines, self).default_get(fields)
        if 'budget_year' in self._context:
            year = self._context.get('budget_year')
            if not year:
                raise ValidationError("Please select budget year")
            date = str(year) + '04' + '01'
    #             date = time.strftime('%Y-04-01')
            self.env.cr.execute("select * from get_month(%s)",(date,))
            temp = [(0,False,{'date':val}) for val in self.env.cr.fetchone()]
            rec.update({'monthly_budget_line_ids':temp})
        return rec
    
    name = fields.Char(string='Position')
    budget_id = fields.Many2one('hr.budget',string="Budget",invisible=1)
    job_id = fields.Many2one('hr.job',string="Job Position")
    emp_total = fields.Integer(string='Existing Resources', compute='onchange_emp_total')
    new_res = fields.Integer(string='New Resources')
    level = fields.Char(string='Level')
    avg_cost = fields.Float(string='Average Cost (Rs.)')
    year = fields.Selection([(num, str(num)) for num in range(2000, (datetime.now().year)+1 )], 'Year')
    total_cost = fields.Integer(string='Total Cost')
    manager_id = fields.Many2one('hr.employee', string="Manager" , domain="[('job_id','=',1)]")
    date = fields.Date('Create Date', default=fields.datetime.now())
    user_id = fields.Many2one('res.users','User')
    monthly_budget_line_ids = fields.One2many('monthly.budget.line','budget_line_id',string="Monthly Budget")
    
    @api.onchange('emp_total', 'avg_cost')
    def onchange_field(self):
        if self.emp_total or self.avg_cost:
            self.total_cost = self.emp_total * self.avg_cost
    
    @api.onchange('job_id')
    def onchange_emp_total(self):
        for line in self:
            if line.job_id:
                line.emp_total=line.job_id.no_of_employee
                
class monthly_budget_line(models.Model):
    _name="monthly.budget.line"
    _order = 'date'
    
    date = fields.Date(string='Month',help="select first date or any date of the month")
    headcount = fields.Integer(string='Head Count')
    budget_line_id = fields.Many2one('budget.line',string='Budget Line')
    
class HrRequisition(models.Model):
    _name="hr.requisition"
    _description="Requisition"
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    @api.model
    def _default_user(self):
        return self.env.user.id
    
    @api.multi
    def _get_total(self):
            sum=0
            for lines in self.requisition_line:
                print "lines=====",lines
                sum+=lines.avail_budget
            self.total_avail_budget=sum
            
    def get_employee(self):
        return self.env['hr.employee'].search([('user_id','=',self.env.uid)],limit = 1)        
     
    name = fields.Char(string="Requisition Number")
    department = fields.Many2one('hr.department',string="Sub Department")
    requested_by = fields.Many2one('hr.employee',string='Requested By',default=get_employee)
    requested_to = fields.Many2one('res.users',string='Requested To')
    allocated_to = fields.Many2one('res.users',string='Allocated To TL')
    user_id = fields.Many2one('res.users','Created By',default=_default_user)
    manager = fields.Many2one('hr.employee',string='Manager' , domain="[('job_id','=',1)]")
#     branch = fields.Many2one('hr.department',string='Branch')
    branch_id =fields.Many2one('hr.branch','Branch')
    date = fields.Date(string='Date',default=fields.datetime.now())
    replacement = fields.Selection([('yes', 'YES'), ('no', 'NO')], string="Replacement")
    replace_of = fields.Many2one('hr.employee',string='Replacement Of')
     
    requisition_line = fields.One2many('requisition.line','requisition_id',string='Requisition Lines')    
    comments = fields.Text(string='Comments')
    total_avail_budget = fields.Float(string="Total Available Budget", compute='_get_total')     
    state = fields.Selection([
            ('draft', 'Draft'),
            ('confirm', 'Confirmed'),
            ('approve', 'Approved'),
            ], track_visibility='onchange',default='draft')
    month = fields.Selection([(4,'Apr'),(5,'May'),(6,'June'),(7,'July'),(8,'Aug'),(9,'Sept'),(10,'Oct'),(11,'Nov'),(12,'Dec'),(1,'Jan'),(2,'Feb'),(3,'Mar')],string='Month')
    year = fields.Selection([(num, str(num)) for num in range(2015, (datetime.now().year)+5 )], string='Year')
    
    @api.onchange('branch_id')
    def onchange_field(self):
        if self.branch_id:
            self.manager = self.branch_id.manager_id
            self.allocated_to = self.branch_id.tl_manager_id
                
    @api.model
    def create(self, vals):
        if not vals.get('name'):
            seq = self.env['ir.sequence'].next_by_code('hr.requisition')
            vals['name'] = seq
        return super(HrRequisition, self).create(vals)
    
    
    @api.multi
    def send_email_to_hod(self):
        base_url = self.env['ir.config_parameter'].get_param('web.base.url')
        rec_id = self.id
#         print"====self.env=====",self._model
        print"context====",self._context['params']['action']
#         model = self._model
        context = self._context
        context.get('active_model')
        action_id = self._context['params']['action']
        a = """ """+str(base_url)+"""/web#id="""+str(self.id)+"""&view_type=form&model="""+str(context.get('active_model'))+"""&action="""+str(action_id)+""" """
        ef = """<a href="""+a+""">Click Here """+self.name+"""</a>"""
    
        out_server = self.env['ir.mail_server'].search([])
        if out_server:
            out_server = out_server[0]
            
            emailfrom =out_server.smtp_user
            emailto =[]
            if self.requested_by and self.requested_by.work_email:
                emailto.append(self.requested_by.work_email)
            if self.manager and self.manager.work_email:
                emailto.append(self.manager.work_email)
                
            if emailfrom and emailto:
                
                msg = MIMEMultipart()
                msg['From'] = emailfrom
                msg['To'] = ", ".join(emailto)
                msg['Subject'] = 'Requisition Approved'
        
                html = """<!DOCTYPE html>
                         <html>
                         <p>Dear Sir,</p>
                         
                         <p>Your request has been approved and sent to Talent team. </p>
                         <p>You can expect interviews next week.</p>
                         <p>Please """+ef+""" to view requisition.</p>
                           <body>
                            
                       <p>Regards</p>
                       
                       <p>HR</p>  
                       </body>
                       
                           
                        </html>
                      """
        #        part1 = MIMEText(text, 'plain')
                part1 = MIMEText(html, 'html')
                msg.attach(part1)
        #        msg.attach(part2)
                server = smtplib.SMTP_SSL(out_server.smtp_host,out_server.smtp_port)
        #        server.ehlo()
        #         server.starttls()
                server.login(emailfrom,out_server.smtp_pass)
                text = msg.as_string()
                server.sendmail(emailfrom, emailto , text)
                server.quit()
        return True
    
    @api.multi
    def send_email_confirm_requisition(self):
        base_url = self.env['ir.config_parameter'].get_param('web.base.url')
        rec_id = self.id
#         print"====self.env=====",self._model
        print"context====",self._context['params']['action']
#         model = self._model
        context = self._context

        context.get('active_model')
        
        action_id = self._context['params']['action']
        a = """ """+str(base_url)+"""/web#id="""+str(self.id)+"""&view_type=form&model="""+str(context.get('active_model'))+"""&action="""+str(action_id)+""" """
        ef = """<a href="""+a+"""> """+self.name+"""</a>"""
    
        out_server = self.env['ir.mail_server'].search([])
        if out_server:
            out_server = out_server[0]
            
            emailfrom =out_server.smtp_user
            emailto =[]
            if self.requested_to and self.requested_to.login:
                emailto.append(self.requested_to.login)
            if emailfrom and emailto:
                msg = MIMEMultipart()
                msg['From'] = emailfrom
                msg['To'] = ", ".join(emailto)
                msg['Subject'] = 'For Requisition Approval'
        
                html = """<!DOCTYPE html>
                         <html>
                         <p>Dear Sir,</p>
                         <br/>
                         <p>Your request has been Confirmed and sent to Talent team. </p>
                         <br></br>
                         <p>Please Click Here """+ef+""" to view requisition.</p>
                           <body>
                            
                       <p>Regards</p>
                       
                       <p>HR</p>  
                       </body>
                       
                           
                        </html>
                      """
        #        part1 = MIMEText(text, 'plain')
                part1 = MIMEText(html, 'html')
                msg.attach(part1)
        #        msg.attach(part2)
                server = smtplib.SMTP_SSL(out_server.smtp_host,out_server.smtp_port)
        #        server.ehlo()
        #         server.starttls()
                server.login(emailfrom,out_server.smtp_pass)
                text = msg.as_string()
                server.sendmail(emailfrom, emailto , text)
                server.quit()
        return True
    
    @api.multi
    def send_email_revise_req(self):
            base_url = self.env['ir.config_parameter'].get_param('web.base.url')
            rec_id = self.id
#             print"====self.env=====",self._model
            print"context====",self._context['params']['action']
#             model = self._model
            context = self._context
            context.get('active_model')
            action_id = self._context['params']['action']
            a = """ """+str(base_url)+"""/web#id="""+str(self.id)+"""&view_type=form&model="""+str(context.get('active_model'))+"""&action="""+str(action_id)+""" """
            ef = """<a href="""+a+""">"""+self.name+"""</a>"""
            
            
            out_server = self.env['ir.mail_server'].search([])
            if out_server:
                out_server = out_server[0]
                
                emailfrom =out_server.smtp_user
                emailto =[]
                if self.user_id and self.user_id.login:
                    emailto.append(self.user_id.login)
                if emailfrom and emailto:
            
                    msg = MIMEMultipart()
                    msg['From'] = emailfrom
                    msg['To'] = ", ".join(emailto)
                    msg['Subject'] = 'Please Revise Requisition'
            
                    html = """<!DOCTYPE html>
                             <html>
                             
                             Your Request has been Cancelled .
        
                               <body>
                           <p>Please Click Here """+ef+""" to Revise Requisition.</p>      
                           <p>Regards</p>
                           <p>Admin</p>  
                           
                           </body>
                           
                               
                            </html>
                          """
                    #        part1 = MIMEText(text, 'plain')
                    part1 = MIMEText(html, 'html')
                    msg.attach(part1)
            #        msg.attach(part2)
                    server = smtplib.SMTP_SSL(out_server.smtp_host,out_server.smtp_port)
            #        server.ehlo()
            #         server.starttls()
                    server.login(emailfrom,out_server.smtp_pass)
                    text = msg.as_string()
                    server.sendmail(emailfrom, emailto , text)
                    server.quit()
            return True  
    
    @api.multi
    def confirm_requisition(self):
        self.write({'state':'confirm'})
        self.send_email_confirm_requisition()
    
    @api.multi
    def approve_requisition(self):
        self.send_email_to_hod()
        
        for line in self.requisition_line:
            print"jbbbbb=====",line.job_id
            line.job_id.write({'no_of_recruitment':line.emp_total,'user_id':self.allocated_to.id,  'allocat_hr':self.requested_to.id,'branch_id':self.branch_id.id})
            line.job_id.set_recruit()
        self.write({'state':'approve'})

    @api.multi
    def revise_requisition(self):
#         self.send_email_revise_req()
        self.write({'state':'draft'})            
    
class requisition_line(models.Model):
    _name="requisition.line"
    _description="Requisition Line"
    
    @api.one
    @api.depends('requisition_id.month','requisition_id.year','requisition_id.department','requisition_id.branch_id','job_id')
    def get_available_budget(self):
        for line in self:
            month = line.requisition_id.month
            year = line.requisition_id.year
            department_id = line.requisition_id.department and line.requisition_id.department.id or False
            branch_id = line.requisition_id.branch_id and line.requisition_id.branch_id.id or False
            avail_budget = 0
            if line.job_id and month and department_id and branch_id and year:
                job_id = line.job_id.id
                self.env.cr.execute("select coalesce(sum(headcount),0) from monthly_budget_line_view where \
                department_id = %s and branch_id  = %s and job_id = %s and month = %s and year = %s",(department_id,branch_id,job_id,month,year))
                temp = self.env.cr.fetchall()
                if temp:
                    avail_budget = temp[0][0]
            line.avail_budget = avail_budget
        
    name = fields.Char(string='Requisition')
    requisition_id = fields.Many2one('hr.requisition',string='requisition')
    job_id = fields.Many2one('hr.job',string="Job Position")
    job_desc = fields.Char(string='Job Description')
    emp_total = fields.Integer(string='Required Number Of Employees')
    existing = fields.Integer(string='Existing Number Of Employees', compute='onchange_emp_total')
    avail_budget = fields.Integer(compute='get_available_budget',string='Available Budget',store=True)
    salary_range = fields.Float(string="Salary Range")  
    manager_id = fields.Many2one('hr.employee',string='Manager' , domain="[('job_id','=',1)]")
    date = fields.Date('Create Date', default=fields.datetime.now())
    requested_by = fields.Many2one('hr.employee',string='Requested By')
    user_id = fields.Many2one('res.users','User')
    
    @api.onchange('job_id')
    def onchange_job_id(self):
        for line in self:
            line.existing=line.job_id.no_of_employee
    
    @api.onchange('emp_total')
    def onchange_emp_total(self):
        for line in self:
            if line.emp_total:
                if line.avail_budget < line.emp_total:
                    warning = {
                                'title': _('Warning!'),
                                'message': _('Please Re-enter Values Current Budget Exceeded Available Budget !'),
                                }
                    return {'warning': warning}

                         
class hr_job(models.Model):
    _inherit="hr.job"
    
    @api.one
    @api.depends('month','year','department_id','branch_id','job_id')
    def get_available_budget(self):
        for line in self:
            print"========line==========",line
            month = line.month
            year = line.year
            department_id = line.department_id and line.department_id.id or False
            branch_id = line.branch_id and line.branch_id.id or False
            avail_budget = 0
            print"==========line.job_id======",line.job_id
            if line.job_id and month and department_id and branch_id and year:
                job_id = line.job_id.id
                self.env.cr.execute("select coalesce(sum(headcount),0) from monthly_budget_line_view where \
                department_id = %s and branch_id  = %s and job_id = %s and month = %s and year = %s",(department_id,branch_id,job_id,month,year))
                temp = self.env.cr.fetchall()
                if temp:
                    avail_budget = temp[0][0]
            line.avail_budget = avail_budget
    
    name = fields.Char(string='HR JOB')
    budgeted_emp = fields.Integer(string='Budgeted Employees')    
    budget_lines = fields.One2many('budget.lines','job_id','Budget History')
    requisition_lines = fields.One2many('requisition.line','job_id','Requisition History')
    branch_id =fields.Many2one('hr.branch','Branch')
    allocat_hr = fields.Many2one('res.users',string='H.R.')
    parent = fields.Boolean('Parent')
    avail_budget = fields.Integer(compute='get_available_budget',string='Available Budget',store=True)
    month = fields.Selection([(4,'Apr'),(5,'May'),(6,'June'),(7,'July'),(8,'Aug'),(9,'Sept'),(10,'Oct'),(11,'Nov'),(12,'Dec'),(1,'Jan'),(2,'Feb'),(3,'Mar')],string='Month')
    year = fields.Selection([(num, str(num)) for num in range(2015, (datetime.now().year)+5 )], string='Year')
    expected_no_of_emp = fields.Integer('Expected No. Of Employee')
    job_id = fields.Many2one('hr.job','Job Position')
    
class upload_docs(models.Model):
    _name="upload.docs"
    _description="Upload Documents"
    
    name = fields.Many2one('hr.employee',string="Employee")
    docs_lines = fields.One2many('docs.lines','doc_id',string='Document Details')
    intimate_to = fields.Many2one('hr.employee',string="Intimate To")
    
    @api.model
    def send_inbox_message(self, ids=None):
#         parameter_ids = self.pool.get('ir.config_parameter').search([('key','=','doc_expiry_message_to')])
#         para_rec = self.pool.get('ir.config_parameter').browse(parameter_ids[0])
        line_ids= self.env['docs.lines'].search([])
        for val in line_ids:
            send_mail = False
            today_date=time.strftime(DEFAULT_SERVER_DATE_FORMAT)
            today_date = datetime.strptime(today_date,"%Y-%m-%d")
            expiry_date=time.strftime(val.expiry_date)
            date1 = datetime.strptime(expiry_date,"%Y-%m-%d")
            two_days_before = date1 - timedelta(days=2)
            if val.alert_date == datetime.now().strftime('%Y-%m-%d'):
                send_mail = True
            elif two_days_before == today_date:
                send_mail = True
            elif expiry_date == today_date:
                send_mail = True
            if send_mail:
                partner_id = [self.intimate_to.user_id.partner_id.id]
                values = {
                      'subject':'Document Expire Soon',
                      'author_id':partner_id[0],
                      'notified_partner_ids':[(6,0,partner_id)],
                      'body':val.code + val.doc_no + val.description,
                      }
                val.write({'alert_check':True,'msg_send':True})
                self.env['mail.message'].create(values)
                
                base_url = self.env['ir.config_parameter'].get_param('web.base.url')
#             rec_id = self.id
#             print"====self.env=====",self._model
#             print"context====",self._context
#             model = self._model
#             action_id = self._context['params']['action']
#             a = """ """+str(base_url)+"""/web#id="""+str(self.id)+"""&view_type=form&model="""+str(self._model)+"""&action="""+str(action_id)+""" """
                doc = val.code+ ' ' + str(val.doc_no) + ' ' + val.description
                a = """"""+str(base_url)+"""/web?#view_type=form&model=board.board&menu_id=1&action=187"""
                ef = """<a href="""+a+""">Click Here</a>"""
            
            
                out_server = self.env['ir.mail_server'].search([])[0]
                emailto = []
                emailfrom= ''
                if out_server:
                    if out_server.smtp_user:
                        emailfrom =out_server.smtp_user
                    if val.doc_id.intimate_to.work_email:
                        emailto.append(val.doc_id.intimate_to.work_email)
                    print"======emailto===",emailfrom,emailto
                    if emailfrom and len(emailto) >= 1:
                        msg = MIMEMultipart()
                        msg['From'] = emailfrom
                        msg['To'] = ", ".join(emailto)
                        msg['Subject'] = 'Please Revise Document'
                        
                        html = """<!DOCTYPE html>
                                 <html>
                                 
                                 Documents has been expired .
                                 <br/>
                                 Please """+ef+""" to revise documents.
                                   <body>
                                     
                               <p>Regards</p>
                               <p>Admin</p>  
                               
                               </body>
                               
                                   
                                </html>
                              """
                        #        part1 = MIMEText(text, 'plain')
                        part1 = MIMEText(html, 'html')
                        msg.attach(part1)
                #        msg.attach(part2)
                        server = smtplib.SMTP_SSL(out_server.smtp_host,out_server.smtp_port)
                #        server.ehlo()
                #         server.starttls()
                        server.login(emailfrom,out_server.smtp_pass)
                        text = msg.as_string()
                        server.sendmail(emailfrom, emailto , text)
                        server.quit()
                        print"sent===="
            
                
            
            
        return True
    
    
class docs_lines(models.Model):
    _name="docs.lines"
    _description="Document Line"
    
    @api.one
    @api.depends('alert_before','expiry_date')
    def _get_alert_date(self):
        for line in self:
            if line.expiry_date:
                expiry_date=time.strftime(line.expiry_date)
                date1 = datetime.strptime(expiry_date,"%Y-%m-%d")
                alert_date = date1 - timedelta(days=line.alert_before)
                line.alert_date = alert_date
        

    @api.multi
    @api.depends('alert_before','expiry_date')
    def _get_alert_check(self):
        if self.expiry_date:
            today_date=time.strftime(DEFAULT_SERVER_DATE_FORMAT)
            today_date = datetime.strptime(today_date,"%Y-%m-%d")
            expiry_date=time.strftime(self.expiry_date)
            date1 = datetime.strptime(expiry_date,"%Y-%m-%d")
            alert_date = date1 - timedelta(days=self.alert_before)
            print"alert_date <= today_date===",alert_date, today_date
            if alert_date <= today_date:
                    self.alert_check = True
            else:
                self.alert_check = False
        
    
    name = fields.Char(string='Name')
    doc_id = fields.Many2one('upload.docs',string="Docs Details")
    emp_name= fields.Many2one('hr.employee',string="Employee Name")
    code = fields.Char(string='Code')
    description = fields.Char(string='Description')
    doc_no = fields.Char(string='Document Number')
    issue_date = fields.Date(string='Issue Date')
    expiry_date = fields.Date(string='Expiry Date')
    issue_phase = fields.Char(string='Issue Phase')
    status = fields.Selection([('normal', 'Active'), ('closed', 'Archived')], string="Status")
    alert_before = fields.Integer(string='Alert Before',default=7)
    attach = fields.Binary(string='Attachments')
    alert_check = fields.Boolean('Alert Check',compute='_get_alert_check',method=True,store=True)
    alert_date = fields.Date(string='Alert Date',compute='_get_alert_date',method=True,store=True)
    msg_send=fields.Boolean('Message Send')
    
    @api.onchange('expiry_date')
    def onchange_expiry_date(self):
        res={}
        if self.expiry_date >= self.alert_date:
            self.msg_send=False
    
    
    
class resign(models.Model):
    _name="resign"
    _description="Resignation"
    
    def get_employee(self):
        return self.env['hr.employee'].search([('user_id','=',self.env.uid)],limit = 1)
    
    name = fields.Many2one('hr.employee',string="Employee",default=get_employee)
        
    work_phone = fields.Char(string='Work Phone')
    work_loc = fields.Char(string='Work Location')
    address_id = fields.Char(string='Office Location')
    designation = fields.Many2one('hr.job',string='Designation')    
    work_mobile = fields.Char(string='Work Mobile')
    reason_for_leaving = fields.Char(string='Reason For Leaving')
    notes = fields.Text(string='Notes')
    confirm_date = fields.Date('Confirm Date')
    create_date = fields.Date(string='Create Date',default=fields.datetime.now())
    
    @api.onchange('name')
    def onchange_field(self):
            if self.name:
                self.designation=self.name.job_id
                self.address_id=self.name.work_location
                self.work_phone=self.name.work_phone
                self.work_mobile=self.name.mobile_phone
    
    @api.multi
    def confirm_resign(self):
        if self.name:
            self.confirm_date=fields.Datetime.now()            
            self.name.write({'active':False,'state_date':self.confirm_date,'states_lines':[(0,False,{'name':self.name.id,'till_date':self.confirm_date,'start_date':self.name.state_date,'states':'active'})]})
                
                                
class termination(models.Model):
    _name="termination"
    _description="Termination"
    
    name = fields.Many2one('hr.employee',string="Employee")
    
    reason = fields.Char(string='Reason Lay Off')
    designation = fields.Many2one('hr.job',string='Designation') 
    hr_remark = fields.Text(string='HR Remarks')    
    ceo_remark = fields.Text(string='C.E.O. Remarks')
    confirm_date = fields.Date('Confirm Date')

    @api.onchange('name')
    def onchange_field(self):
            if self.name:
                self.designation=self.name.job_id
    
    @api.multi
    def confirm_terminate(self):
        if self.name:
            self.confirm_date=fields.Datetime.now()            
            self.name.write({'active':False,'state_date':self.confirm_date,'states_lines':[(0,False,{'name':self.name.id,'till_date':self.confirm_date,'start_date':self.name.state_date,'states':'active'})]})
                      
         
class travel_details(models.Model):
    _name="travel.details"
    _description="Travel Details"
    
    def default_login_employee(self):
        return self.env['hr.employee'].search([('user_id','=',self.env.uid)],limit = 1)
    
    name = fields.Char(string='Refrence Number')
    emp_name= fields.Many2one('hr.employee',string="Employee",default=default_login_employee)
    designation = fields.Many2one('hr.job',string='Designation')   
    emp_id = fields.Char(string='ID')
    dob = fields.Date(string='Date Of Birth')
    contact_no = fields.Char(string='Contact Number')
    off_email = fields.Char(string='Office Email Id')
    
    travel_req_date = fields.Date(string='Travel Request Date')
    id_proof = fields.Char(string='Type Of Id Proof')
    travel_from = fields.Char(string='Travelling From')
    travel_to = fields.Char(string='Travelling To')
    return_to = fields.Date(string='Returning To')
    mode = fields.Selection([('public_transport', 'Public Transport'), ('own_vehicle', 'Own Vehicle'),('flight','By Flight')], string="Mode Of Travel")
    preffered_time = fields.Float(string='Preffered Time-If Any')
    preffered_return_time = fields.Float(string='Preffered Return Time - If Any')
    
    date_travel = fields.Date(string='Date Of Travel')
    reason_for_travel = fields.Char(string='Reason For Travel')
    return_date_travel = fields.Date(string='Return Date Of Travel')
    
    nf_dept = fields.Char('NF Department')
    nf_state = fields.Char(string='NF State')
    financial_approval = fields.Char(string='Financial Approval')
    
    accommodation_req = fields.Selection([('yes', 'Yes'), ('no', 'No')], string="Accommodation Required")
    
    
    @api.onchange('emp_name')
    def onchange_employee(self):
        for record in self:
            if record.emp_name:
                emp = record.emp_name
                record.designation = emp.intrnl_desig and emp.intrnl_desig.id or False
                record.emp_id = emp.employee_no
                record.dob = emp.birthday
                record.contact_no = emp.mobile_phone
                record.off_email = emp.work_email
                
            else:
                record.designation = False
                record.emp_id = ''
                record.dob = False
                record.contact_no = ''
                record.off_email = ''
                    
class medical_insurance(models.Model):
    _name="medical.insurance"
    _description = "Medical Insurance"
    
    def default_login_employee(self):
        return self.env['hr.employee'].search([('user_id','=',self.env.uid)],limit = 1)
    
    name = fields.Many2one('hr.employee',string="Employee",default=default_login_employee)
    ref_no = fields.Char(string='Reference Number')
    date = fields.Date('Date')
    plan = fields.Char('Plan')
    sum_assured = fields.Integer('Sum Insured')
    family_detail_lines = fields.One2many('family.lines','family_id',string='Family Details')
    
class family_lines(models.Model):
    _name="family.lines"
    
    name=fields.Char('Name')
    family_id = fields.Many2one('medical.insurance',string='Family Id')  
    dob = fields.Date('Date Of Birth')
    gender = fields.Selection([('male','Male'), ('female','FEMALE')])  
    relationship = fields.Char('Relationship')
    
class purchase_request(models.Model):
    _name="purchase.request"
    
    def default_login_employee(self):
        return self.env['hr.employee'].search([('user_id','=',self.env.uid)],limit = 1) 
    
    name = fields.Many2one('hr.employee',string="Employee",default=default_login_employee)
    ref_no = fields.Char(string='Reference Number')
    des_of_purchase = fields.Char('Description Of Purchase')
    outline_purchase = fields.Char('Outline Of the Purchase')
    references = fields.Text('References (If Any)')
    expenditure = fields.Float('Estimated Expenditure')
    attachment = fields.Many2many('attachments','purchase_attachment_rel','purchase_attachment_id','attach_id',string='Attachment')
    
    
class  attachments(models.Model):
    _name="attachments"
    
    name=fields.Char('File Name')
    attach = fields.Binary(string='Attachments')
        
    
    
    