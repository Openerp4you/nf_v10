# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime
import time
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT
from openerp import api, fields, models, tools
from openerp.tools.translate import _
from openerp.exceptions import UserError
from email.message import Message
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.text import MIMEText
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
import mimetypes
from email.mime.multipart import MIMEMultipart
import smtplib
import urlparse
from lxml import etree
from openerp.osv.orm import setup_modifiers

class Applicant(models.Model):
    _inherit = "hr.applicant"
    
    survey_id = fields.Many2one('survey.survey','Survey')
    interviewer_id =fields.Many2one('res.users','Interviewer')
    branch_id =fields.Many2one('res.partner','Branch')
    survey_id1 = fields.Many2many('survey.survey','survey_applicant_rel','applicant_id','survey_id',string="Interview Form")
    response_id1 = fields.Many2many('survey.user_input','response_applicant_rel','applicant_id','response_id','Response')
    interviewer_hist_line = fields.One2many('interviewer.hist.line','applicant_id',string="Interviewers")
    allocat_hr = fields.Many2one('res.users',string='H.R.')
    pan_no = fields.Char('PAN Card Number')
    aadhar_no = fields.Char('Aadhar Number')
    
    _sql_constraints = [
        ('applicant_uniq_email', 'UNIQUE(email_from)', 'Application already exist!'),
        ('applicant_uniq_mobile', 'UNIQUE(partner_phone)', 'Application already exist!'),
        ('applicant_uniq_phone', 'UNIQUE(partner_mobile)', 'Application already exist!'),
        ('applicant_uniq_pan', 'UNIQUE(pan_no)', 'Application already exist!'),
        ('applicant_uniq_aadhar', 'UNIQUE(aadhar_no)', 'Application already exist!')
    ]
    
    
    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        result = super(Applicant, self).fields_view_get(view_id, view_type, toolbar=toolbar, submenu=submenu)
        application_id = self.env.context.get('active_id')
        active_model = self.env.context.get('active_model')
        if self == 'hr.applicant' and application_id:
            application = self.env['hr.applicant'].browse(application_id)
            doc = etree.XML(result['arch'])
            if application.interviewer_id == self.env.user_id.id and doc.xpath("//button[@name='send_email_To_HR']"):
                node = doc.xpath("//button[@name='send_email_To_HR']")[0]
                node.set('invisible', '1')
                setup_modifiers(node, result['button']['send_email_To_HR'])
            result['arch'] = etree.tostring(doc)
        return result
    
#     def fields_view_get(self, cr, uid, view_id=None, view_type=False, context=None, toolbar=False, submenu=False):
#         journal_obj = self
#         if context is None:
#             context = {}
#         print"====contecxttt=====",context,view_type
#         if  view_type == 'form':
#             mmy, view_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'hr_recruitment_extend','hr_applicant_view_form')
#             print"view_id====",view_id
#         res = super(Applicant,self).fields_view_get(cr, uid, view_id=view_id, view_type=view_type, context=context, toolbar=toolbar, submenu=submenu)
#         doc = etree.XML(res['arch'])
#         if view_type == 'form':
#             for node in doc.xpath("//button[@name='send_email_To_HR']"):
#                 print"=============node=============",node
#                 if interviewer_id == uid:
#                     node.set('invisible', '1')
#         res['arch'] = etree.tostring(doc)
#         print"===res==",res
#         return res
    
    
    
    @api.multi
    def action_start_survey(self):
        self.ensure_one()
        # create a response and link it to this applicant
        print"=====self._uid====",self._uid
        if not self.response_id:
            if self.survey_id:
                response = self.env['survey.user_input'].create({'survey_id': self.survey_id.id, 'partner_id': self.partner_id.id})
            else:
                response = self.env['survey.user_input'].create({'survey_id': self.survey.id, 'partner_id': self.partner_id.id})
            self.response_id = response.id
        else:
            response = self.response_id
        # grab the token of the response and start surveying
        if self.survey_id:
            return self.survey_id.with_context(survey_token=response.token).action_start_survey()
        else:
            return self.survey.with_context(survey_token=response.token).action_start_survey()
    
#   
    @api.multi
    def send_email_To_TA(self):
        base_url = self.env['ir.config_parameter'].get_param('web.base.url')
        rec_id = self.id
        print"context====",self._context
        model = self
        action_id = self._context['params']['action']
        active_id =self._context['active_id']
        a = """ """+str(base_url)+"""/web#id="""+str(self.id)+"""&view_type=form&model="""+str(model)+"""&action=150&active_id="""+str(active_id)+"""&menu_id=142 """
        
        ef = """<a href="""+a+""">Click Here """+self.name+"""</a>"""
        
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
                msg['Subject'] = 'For Next Schedule '
        
                html = """<!DOCTYPE html>
                         <html>
                         <p>Dear Sir,</p>
                         
                         <p>Interview has been completed. </p>
                         <p>You can hold next round of interviews .</p>
                         <p>Please """+ef+""" to perform next Step.</p>
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
    def send_email_To_HR(self):
        base_url = self.env['ir.config_parameter'].get_param('web.base.url')
        rec_id = self.id
        print"context====",self._context['params']['action']
        model = self
        action_id = self._context['params']['action']
        active_id =self._context['active_id']
        a = """ """+str(base_url)+"""/web#id="""+str(self.id)+"""&view_type=form&model="""+str(model)+"""&action=150&active_id="""+str(active_id)+"""&menu_id=142 """
        ef = """<a href="""+a+""">Click Here """+self.name+"""</a>"""
    
        out_server = self.env['ir.mail_server'].search([])
        if out_server:
            out_server = out_server[0]
            
            emailfrom =out_server.smtp_user
            emailto =[]
            if self.allocat_hr and self.allocat_hr.login:
                emailto.append(self.allocat_hr.login)
               
            if emailfrom and emailto:
                
                msg = MIMEMultipart()
                msg['From'] = emailfrom
                msg['To'] = ", ".join(emailto)
                msg['Subject'] = 'For Next Schedule'
        
                html = """<!DOCTYPE html>
                         <html>
                         <p>Dear Sir,</p>
                         
                         <p>Interview has been completed. </p>
                         <p>You can hold next round of interviews .</p>
                         <p>Please """+ef+""" to perform next Step.</p>
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
    
    @api.onchange('job_id')
    def onchange_job_id(self):
        vals = self._onchange_job_id_internal(self.job_id.id)
        self.department_id = vals['value']['department_id']
        self.user_id = vals['value']['user_id']
        self.stage_id = vals['value']['stage_id']
        self.allocat_hr = vals['value']['allocat_hr']
        self.branch_id = vals['value']['branch_id']
    
    def _onchange_job_id_internal(self, job_id):
        department_id = False
        allocat_hr=False
        user_id = False
        branch_id = False
        print "onchange=========",job_id
        stage_id = self.stage_id.id
        if job_id:
            job = self.env['hr.job'].browse(job_id)
            department_id = job.department_id.id
            print"=========",job.allocat_hr
            user_id = job.user_id.id
            allocat_hr = job.allocat_hr.id
            branch_id = job.branch_id.id
            if not self.stage_id:
                stage_ids = self.env['hr.recruitment.stage'].search([
                    ('job_id', '=', job.id),
                    ('fold', '=', False)
                ], order='sequence asc', limit=1).ids
                stage_id = stage_ids[0] if stage_ids else False
        print"custt end====",branch_id
        return {'value': {
            'department_id': department_id,
            'user_id': user_id,
            'allocat_hr':allocat_hr,
            'branch_id':branch_id,
            'stage_id': stage_id
            
        }}
      
#     @api.multi
#     def write(self, vals):
#         # user_id change: update date_open
#         if vals.get('user_id'):
#             vals['date_open'] = fields.Datetime.now()
#         print"====vals and not self.survey_id====",vals ,self.survey,self.survey_id
#         if not self.survey_id:
#             print"44444"
#             if 'survey' in vals:
#                 print"2222"
#                 vals['survey_id'] = vals['survey']
#             else:
#                 print"1111"
#                 vals['survey_id'] = self.survey.id
#         
#         # stage_id: track last stage before update
#         if 'stage_id' in vals:
#             vals['date_last_stage_update'] = fields.Datetime.now()
#             vals.update(self._onchange_stage_id_internal(vals.get('stage_id'))['value'])
#             for applicant in self:
#                 vals['last_stage_id'] = applicant.stage_id.id
#                 res = super(Applicant, self).write(vals)
#         else:
#             res = super(Applicant, self).write(vals)
# 
#         # post processing: if stage changed, post a message in the chatter
#         if vals.get('stage_id'):
#             if self.stage_id.template_id:
#                 self.message_post_with_template(self.stage_id.template_id.id, notify=True, composition_mode='mass_mail')
#         return res

    @api.multi
    def create_employee_from_applicant(self):
        """ Create an hr.employee from the hr.applicants """
        employee = False
        for applicant in self:
            address_id = contact_name = False
            if applicant.partner_id:
                address_id = applicant.partner_id.address_get(['contact'])['contact']
                contact_name = applicant.partner_id.name_get()[0][1]
            if applicant.job_id and (applicant.partner_name or contact_name):
                applicant.job_id.write({'no_of_hired_employee': applicant.job_id.no_of_hired_employee + 1})
                employee = self.env['hr.employee'].create({'name': applicant.partner_name or contact_name,
                                               'job_id': applicant.job_id.id,
                                               'address_home_id': address_id,
                                               'department_id': applicant.department_id.id or False,
                                               'branch_id':applicant.branch_id.id or False,
                                               'address_id': applicant.company_id and applicant.company_id.partner_id and applicant.company_id.partner_id.id or False,
                                               'work_email': applicant.department_id and applicant.department_id.company_id and applicant.department_id.company_id.email or False,
                                               'work_phone': applicant.department_id and applicant.department_id.company_id and applicant.department_id.company_id.phone or False})
                applicant.write({'emp_id': employee.id})
                applicant.job_id.message_post(
                    body=_('New Employee %s Hired') % applicant.partner_name if applicant.partner_name else applicant.name,
                    subtype="hr_recruitment.mt_job_applicant_hired")
                employee._broadcast_welcome()
            else:
                raise UserError(_('You must define an Applied Job and a Contact Name for this applicant.'))

        employee_action = self.env.ref('hr.open_view_employee_list')
        dict_act_window = employee_action.read([])[0]
        if employee:
            dict_act_window['res_id'] = employee.id
        dict_act_window['view_mode'] = 'form,tree'
        
        return dict_act_window
    
    
    
class InterviewerHistLine(models.Model):
    _name="interviewer.hist.line"
    
#     def default_get(self, cr, uid, ids, context=None):
#         res = {}
#         print"====default_get===",context
#         if context:
#             context_keys = context.keys()
#             next_sequence = 1
#             if 'sequence' in context_keys:
#                 print"context_keys===",context_keys
#                 if len(context.get('sequence')) > 0:
#                     next_sequence = len(context.get('sequence')) + 1
#                     print"next_sequence===",next_sequence
#         res.update({'sequence': next_sequence})
#         return res
    
    sequence = fields.Integer(string='Sequence',index=True, help="Gives the sequence order.")
    name = fields.Integer('Name')
    survey_id = fields.Many2one('survey.survey','Survey')
    user_id =fields.Many2one('res.users','Interviewer')
    title_action = fields.Char('Action')
    date_action = fields.Date('Date')
    response_id = fields.Many2one('survey.user_input','Response')
    applicant_id = fields.Many2one('hr.applicant','Applicant')
    
    @api.multi
    def action_start_survey(self):
        self.ensure_one()
        response = self.response_id
        if response:
            return self.survey_id.with_context(survey_token=response.token).action_start_survey()

class task_subject(models.Model):
    _name = 'task.subject'
    
    name=fields.Char('Subject')
    description= fields.Char('Content')
    alert_days =fields.Integer('Alert Before Days')
    

class Task(models.Model):
    _inherit = 'project.task'   
    
#     @api.multi
    @api.model
    def triger_task_email(self, ids=None):
        line_ids= self.env['project.task'].search([])
        print"lines=====",ids,line_ids
        for val in line_ids:
            send_mail = False
            print"val======",val,"----", datetime.now().strftime('%Y-%m-%d')
            today_date=time.strftime(DEFAULT_SERVER_DATE_FORMAT)
            today_date = datetime.strptime(today_date,"%Y-%m-%d")
            if val.date_deadline:
                expiry_date=time.strftime(val.date_deadline)
                date1 = datetime.strptime(expiry_date,"%Y-%m-%d")
                before_day = date1 - timedelta(days=1)
                if before_day == today_date:
                    send_mail = True
            
            if send_mail:
#                 partner_id = [val.user_id.id]
#                 values = {
#                       'subject':'Document Expire Soon',
#                       'author_id':partner_id[0],
#                       'notified_partner_ids':[(6,0,partner_id)],
#                       'body':val.code + val.doc_no + val.description,
#                       }
#                 self.env['mail.message'].create(values)
                
                base_url = self.env['ir.config_parameter'].get_param('web.base.url')
                rec_id = val.id
#                 print"====self.env=====",self.env.context
#                 print"context====",self._context['params']['action']
                model = self
#                 action_id = self._context['params']['action']
                a = """ """+str(base_url)+"""/web#id="""+str(val.id)+"""&view_type=form&model="""+str(model)+"""&action='"""+str(698)+"""' """
                ef = """<a href="""+a+""">"""+val.name+"""</a>"""
            
            
                out_server = self.env['ir.mail_server'].search([])
                emailto = []
                emailfrom= ''
                if out_server:
                    out_server = out_server[0]
                    if out_server.smtp_user:
                        emailfrom =out_server.smtp_user
                    if val.user_id and val.user_id.login:
                        emailto.append(val.user_id.login)
                    if emailfrom and len(emailto) >= 1:
                        msg = MIMEMultipart()
                        msg['From'] = emailfrom
                        msg['To'] = ", ".join(emailto)
                        msg['Subject'] = 'Your Task Has Been Created'
                        
                        html = """<!DOCTYPE html>
                                 <html>
                                 Dear Sir,
                                 <br/>
                                 Your Task has been Created and Assigned to you.
                                 <br/>
                                 Please """+ef+""" to revise Task.
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
       
       
    
    
    
    
    
    
    
    
    