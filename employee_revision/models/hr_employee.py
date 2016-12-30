from openerp import api, fields, models, _
from email import _name
from datetime import datetime 
import time
from openerp.osv import osv

class hr_employee(osv.osv):
    _inherit="hr.employee"
    
    dept_date = fields.Date(string='Department Date')
    desig_date = fields.Date(string='Designation Date')
    state_date = fields.Date(string='States Date')
    branch_date = fields.Date(string='Branch Date')
    division_date = fields.Date(string='Division Date')
    designation_lines = fields.One2many('designation.lines','name',string='Designation LINES')
    states_lines = fields.One2many('states.lines','name',string='Status Lines')
    department_lines = fields.One2many('department.lines','name',string='Department Lines')
    branch_lines = fields.One2many('branch.lines','name',string='Branch Lines')
    division_lines = fields.One2many('division.line','name',string='Division Lines')
    
    @api.model
    def create(self,vals):
        vals['dept_date'] = fields.Datetime.now()
        vals['desig_date'] = fields.Datetime.now()
        vals['state_date'] = fields.Datetime.now()
        vals['branch_date'] = fields.Datetime.now()
        res = super(hr_employee,self).create(vals)
        self.env.cr.execute("select leave_allocation(%s)",(res.id,))
        return res
    
class designation_lines(osv.osv):
    _name='designation.lines'
    _description='Designation Lines'
    
    name = fields.Many2one('hr.employee',string='Name')
    start_date = fields.Date(string='Start Date')
    till_date = fields.Date('Till Date')
    desig_id = fields.Many2one('hr.job',string='Previous  Designation')    
    
class states_lines(osv.Model):
    _name='states.lines'
    _description='States Lines'
    
    name = fields.Many2one('hr.employee',string='Name')
    states = fields.Selection([('active', 'ACTIVE'), ('inactive', 'INACTIVE')], string=" Previous Status")
    start_date = fields.Date(string='Start Date')
    till_date = fields.Date('Till Date')

class department_lines(osv.osv):
    _name='department.lines'
    
    name = fields.Many2one('hr.employee',string='Name')
    start_date = fields.Date(string='Start Date')
    till_date = fields.Date(string='Till Date')
    department_id = fields.Many2one('hr.department',string=" Previous Department")
    
   
    
class Branch_lines(osv.osv):
    _name='branch.lines'
    
    name = fields.Many2one('hr.employee',string='Name')
    start_date = fields.Date(string='Start Date')
    till_date = fields.Date(string='Till Date')
    branch_id = fields.Many2one('hr.branch',string=" Previous Branch")
    
class division_line(osv.osv):
    _name='division.line'
    
    name = fields.Many2one('hr.employee',string='Name')
    start_date = fields.Date(string='Start Date')
    till_date = fields.Date(string='Till Date')
    division_id = fields.Many2one('hr.division',string=" Previous Branch")    
        
    
 
    
    
    
    
        
        