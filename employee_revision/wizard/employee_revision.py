from openerp import api, fields, models, _
from email import _name
from datetime import datetime 
import time


class employee_revision(models.Model):
    _name="employee.revision"
    _description="Employee Revision"
    
    name = fields.Char(string="Employee Revision")
    info_type = fields.Selection([('position', 'Position Change'), ('department', 'Department Change'), ('status','Status Change'),('branch','Branch Change'),('division','Division Change')], string="Information Type")
    current_status = fields.Selection([('active','Active'),('inactive','Inactive')], string='Current Status') 
    effective_start_date = fields.Date(string='Effective Date',default=fields.Date.context_today)
    emp_name= fields.Many2one('hr.employee',string="Employee")
    new_status = fields.Selection([('active','Active'),('inactive','Inactive')],'New Status') 
    current_dept = fields.Many2one('hr.department',string="Current Department" )
    current_branch = fields.Many2one('hr.branch',string="Current Branch" )
    new_branch = fields.Many2one('hr.branch',string="New Branch" )
    
    new_dept = fields.Many2one('hr.department',string=" New Department" )
    current_position = fields.Many2one('hr.job',string='Current Designation')
    new_designation = fields.Many2one('hr.job',string='New Designation')
    
    current_division = fields.Many2one('hr.division',string='Current Division')
    new_division = fields.Many2one('hr.division',string='New Division')    

    @api.onchange('emp_name')    
    def onchange_field(self):
        if self.emp_name:
            if self.info_type == 'department':
                if self.emp_name.department_id:
                    self.current_dept=self.emp_name.department_id and self.emp_name.department_id.id or False
                
            if self.info_type == 'status':
                if self.emp_name.active:
                    self.current_status = 'active'
                else:
                    self.current_status = 'inactive'
            if self.info_type == 'position':
                self.current_position=self.emp_name.job_id and self.emp_name.job_id.id or False
            if self.info_type == 'branch':
                self.current_branch=self.emp_name.branch_id and self.emp_name.branch_id.id or False
            if self.info_type == 'division':
                self.current_division=self.emp_name.division_id and self.emp_name.division_id.id or False  
        else:
            self.current_dept=False
            self.current_status=False
            self.current_position=False
            self.current_branch=False
            self.current_division=False
            
    @api.multi
    def update_info(self):
        if self.info_type=='department':
            self.emp_name.write({'department_id':self.new_dept.id,'dept_date':self.effective_start_date,'department_lines':[(0,False,{'name':self.emp_name.id,'till_date':self.effective_start_date,'start_date':self.emp_name.dept_date,'department_id':self.current_dept.id})],})
              
        elif self.info_type=='status':
            if self.new_status == 'active':
                state = True
            else:
                state = False
            self.emp_name.write({'active':state,'state_date':self.effective_start_date,'states_lines':[(0,False,{'name':self.emp_name.id,'till_date':self.effective_start_date,'start_date':self.emp_name.state_date,'states':self.current_status})]})
    
        elif self.info_type=='position':
            self.emp_name.write({'job_id':self.new_designation.id,'desig_date':self.effective_start_date,'designation_lines':[(0,False,{'name':self.emp_name.id,'till_date':self.effective_start_date,'start_date':self.emp_name.desig_date,'desig_id':self.current_position.id})],})    
    
        
        elif self.info_type=='branch':
            self.emp_name.write({'branch_id':self.new_branch.id,'branch_date':self.effective_start_date,'branch_lines':[(0,False,{'name':self.emp_name.id,'till_date':self.effective_start_date,'start_date':self.emp_name.branch_date,'branch_id':self.current_branch.id})],})
            
        elif self.info_type=='division':
            self.emp_name.write({'division_id':self.new_division.id,'division_date':self.effective_start_date,'division_lines':[(0,False,{'name':self.emp_name.id,'till_date':self.effective_start_date,'start_date':self.emp_name.division_date,'branch_id':self.current_division.id})],})         
        
    
    
    