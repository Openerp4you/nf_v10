#-*- coding:utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    d$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta

from openerp import tools
from odoo import api, fields, models, _
from openerp.osv import osv
import openerp.addons.decimal_precision as dp

from openerp.tools.safe_eval import safe_eval as eval

class hr_payleave(osv.osv):
    _name = 'hr.payleave'
    
    name = fields.Char(string = 'Name')
    employee_id = fields.Many2one('hr.employee',string = 'Employee')
    employee_no = fields.Char(string = 'Employee Number')
    leave_type = fields.Many2one('hr.holidays.status',string = 'Leave Type')
    from_date = fields.Date(string = 'From Date')
    to_date = fields.Date(string = 'To Date')
    reason = fields.Char(string = 'Reason')
    approving_authority = fields.Char(string = 'Approving Authority')
    remarks = fields.Char(string = 'Remarks')
    contact_address = fields.Char(string = 'Contact Address')
    no_of_days = fields.Float(string = 'Number Of Days')
    txn_type = fields.Selection([('C','C'),('D','D')],string = 'Type')
    previous_balance = fields.Float(string = 'Previous Balance')
    new_balance = fields.Float(string = 'New Balance')
    record_type = fields.Selection([('L','L'),('E','E'),('C','C')],string = 'Record Type')
    payroll_month = fields.Date(string = 'Payroll Month')
                
    
class hr_leave_credit(models.Model):
    _name = 'hr.leave.credit'
    
    name = fields.Char('Name')
    filter = fields.Selection([('R','Region Wise'),('E','Employee Wise')],string = 'Filter' )
    region_id = fields.Many2one('employee.region',string = 'Region')
    employee_id = fields.Many2one('hr.employee',string = 'Employee')
    leave_type = fields.Selection([('EL','EL'),('HPL','HPL'),('CL','CL'),('RH','RH')],string = 'Leave Type')
    start_date = fields.Date(string = 'Start Date')
    end_date = fields.Date(string = 'End Date',readonly=True)
    data_generated = fields.Boolean(string = 'Data Generated')
    leave_credited = fields.Boolean(string = 'Leave Credited')
    credit_line = fields.One2many('hr.leave.credit.line','credit_id',string = 'Credit Line')
    user = fields.Many2one('res.users',string = 'USER',default=lambda self: self.env.user)
    
    @api.multi
    def unlink(self):
        for credit in self:
            if credit.leave_credited==True:
                raise osv.except_osv(_('Warning'), _('You can not delete record in leave credited state.'))
        return super(hr_leave_credit, self).unlink()
        
    @api.multi
    def generate_data(self):
        for record in self:
             record.data_generated = True
        return True     
    
    @api.multi
    def credit_leave(self):
        for record in self:
             record.leave_credited = True
        return True
            
        
    
class hr_leave_credit_line(osv.osv):
    _name = 'hr.leave.credit.line'
    
    name = fields.Char('Name')
    employee_id = fields.Many2one('hr.employee',string = 'Employee',readonly=True)
    leave_type = fields.Selection([('EL','EL'),('HPL','HPL'),('CL','CL'),('RH','RH')],string = 'Leave Type',readonly=True)
    prev_bal = fields.Float(string = 'Previous Balance',readonly=True)
    credit_days = fields.Float(string = 'Credit Days')
    new_bal = fields.Float(string = 'New Balance')
    credit_id = fields.Many2one('hr.leave.credit', string = 'Credit Id',readonly=True)
    
class hr_leave_balance_entry(models.Model):
    _name = 'hr.leave.balance.entry'
    
    name = fields.Char(string = 'Name')
    employee_id = fields.Many2one('hr.employee',string = 'Employee')
    leave_type = fields.Selection([('EL','EL'),('CL','CL'),('RH','RH'),('HPL','HPL')],string = 'Leave Type')
    remarks = fields.Char(string = 'Remarks')
    current_balance = fields.Float(string = 'Current Balance')
    new_balance = fields.Float(string = 'New Balance')
    done = fields.Boolean(string = 'Done')

    
    @api.multi
    def unlink(self):
        for encash in self:
            if encash.done==True:
                raise osv.except_osv(_('Warning'), _('You can not delete record in done state.'))
        return super(hr_leave_balance_entry, self).unlink()
        
    @api.multi
    def get_balance(self):
        self.current_balance = 1
        return True
    
    @api.multi
    def update_balance(self):
        self.done = True
        return True
        
        

class hr_payleave_encash(osv.osv):
    _name = 'hr.payleave.encash'
    
    name = fields.Char('Name')
    employee_id = fields.Many2one('hr.employee',string = 'Employee')
    encashment_days = fields.Float(string = 'Encashment Days')
    remarks = fields.Text(string = 'Remarks',required=True)
    tax_exempted = fields.Boolean(string = 'Tax Exempted?')
    done = fields.Boolean(string = 'Done')
    
    @api.multi
    def unlink(self):
        for encash in self:
            if encash.done==True:
                raise osv.except_osv(_('Warning'), _('You can not delete record in done state.'))
        return super(hr_payleave_encash).unlink()
    
    @api.multi
    def encash_leave(self):
        for record in self:
            record.done = True
        return True


