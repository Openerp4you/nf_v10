import math
import time
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta
import os
from odoo import api, fields, models
from odoo import tools, _
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
from openerp.tools.safe_eval import safe_eval as eval
from odoo.exceptions import UserError, ValidationError


class EmployeeSaving(models.Model):
    _name = 'employee.saving'
    
    @api.onchange('employee_id')
    def onchange_employee_id(self):
        for record in self:
            if record.employee_id:
                employee = self.search([('employee_id', '=', record.employee_id.id)])
                if employee:
                    raise ValidationError('Employee saving record already exists! Please update the existing record.')

    @api.multi
    def _get_amount(self):
        for each in self:
            total =0.0
            for line in each.saving_line_ids:
                total += line.amount
            each.proposed_amount = total    
    
    @api.multi
    def _get_amount_receipt(self):
        for each in self:
            total =0.0
            for line in each.medical_line_ids:
                total += line.amount
            each.bill_amount = total    
    
    @api.multi
    def _get_amount_receipt_hra(self):
        for each in self:
            total =0.0
            for line in each.hra_line_ids:
                total += line.amount
            each.hra_receipt_amount = total    
    
    @api.multi
    def _get_amount_other(self):
        for each in self:
            total =0.0
            for line in each.other_income_ids:
                total += line.amount
            each.other_income_amount = total    
    
    name=fields.Char('Name')
    #'fin_year_id':fields.Many2one('fin.year.mst','Financial Year'),
    company_id=fields.Many2one('res.company','Zone',default=lambda self: self.env['res.company']._company_default_get('employee.saving'))

    employee_id=fields.Many2one('hr.employee','Employee Name')
    proposed_amount=fields.Float(compute='_get_amount', string='Saving Amount',digits=dp.get_precision('Account'))
    saving_line_ids=fields.One2many('saving.line','saving_id','Saving Line')
    medical_line_ids=fields.One2many('medical.bill.line','bill_id','Medical Bill')
    hra_line_ids=fields.One2many('hra.receipt.line','hra_receipt_id','HRA Receipt')
    other_income_ids=fields.One2many('other.source.income','income_id','Other Income')                                                                
    bill_amount=fields.Float(compute='_get_amount_receipt', string='Medical Bill Amount',digits=dp.get_precision('Account'))
    hra_receipt_amount=fields.Float(compute='_get_amount_receipt_hra', string='HRA Receipt Amount',digits=dp.get_precision('Account'))
    other_income_amount=fields.Float(compute='_get_amount_other', string='Other Source Amount',digits=dp.get_precision('Account'))

    gross_income_previous=fields.Float('Gross Income')
    professional_tax_previous=fields.Float('Professional Tax')
    ded_previous_emp=fields.Float('Deduction Made By Previous Employer')
    income_tax_paid=fields.Float('Income Tax Paid')
    car_perks=fields.Float('Car Perks')
    lease_perks=fields.Float('Lease Perks')
    hard_furnishing_perks=fields.Float('Hard Furnishing Perks')
    other_perks=fields.Float('Other Perks')
    entertainment_allowance=fields.Float('Entertainment Allowance')
    lease_exemption=fields.Float('Lease Exemption')
    furniture_rent_recovery=fields.Float('Furniture Rent Recovery')
    actual_lease_rent_paid=fields.Float('Actual Lease Rent Paid')
    furnishing_allowance=fields.Float('Furnishing Allowance')
    conveyance_recovery=fields.Float('Trans Monthly Exempt')
    Date=fields.Date('Date')
    medical_exp_reimbursement=fields.Float('Medical Expense Reimbursement')
    prp_amount=fields.Float('PRP Amount')
    preconstruction_interest=fields.Float('Preconstruction Interest')
    prof_updation_exempt=fields.Float('Professional Updation Exempt')
    uniform_fitment_exempt=fields.Float('Uniform Fitment Exempt')
    property_type=fields.Selection([('S','Self Occupied'),('R','Rent Out')],"Property Type")
    house_income_sl=fields.Float('HP Income (Self Lease)',readonly=True)
    uniform_amount=fields.Float('Uniform Fitment Amount')
                
    
    
class SavingLine(models.Model):
    _name = 'saving.line'
    

    name=fields.Char('Name')
    saving_id=fields.Many2one('employee.saving','Saving Id')
    salary_rule_id=fields.Many2one('hr.salary.rule','Saving Name')
    type= fields.Selection([('P', 'Proposed'),('C', 'Confirmed')], "Saving Type")
    prop_type= fields.Selection([('S', 'Self Occupied'),('R', 'Rented Out')], "Property Type")
    amount=fields.Float('Amount')
    saving_no=fields.Char('Saving Number')
    fin_year_id=fields.Many2one('fin.year.mst','Financial Year')
                
class MedicalBillLine(models.Model):
    _name = 'medical.bill.line'
    
   
    name=fields.Char('Name')
    bill_id=fields.Many2one('employee.saving','Bill Id')
    amount=fields.Float('Amount')
    date=fields.Date('Date')
    type= fields.Selection([('P', 'Proposed'),('C', 'Confirmed')], "Type")
    reference=fields.Char('Reference')
    #'fin_year_id':fields.Many2one('fin.year.mst','Financial Year'),
                
class HraReceiptLine(models.Model):
    _name = 'hra.receipt.line'
    
    
    name=fields.Char('Name')
    hra_receipt_id=fields.Many2one('employee.saving','HRA Receipt Id')
    amount=fields.Float('Amount')
    date=fields.Date('Date')
    type= fields.Selection([('P', 'Proposed'),('C', 'Confirmed')], "Type")
    reference=fields.Char('Reference')
    #'fin_year_id':fields.Many2one('fin.year.mst','Financial Year'),
                
class OtherSourceIncome(models.Model):
    _name = 'other.source.income'
    
    
    name=fields.Char('Name')
    income_source=fields.Selection([('1','Income From House Property'),('2','Interest On FD'),('4','Saving Interest Income'),('3','Other')],'Income Source',required='True')
    income_id=fields.Many2one('employee.saving','Income Id')
    amount=fields.Float('Amount')
    date=fields.Date('Date')
    reference=fields.Char('Reference')
    #SS'fin_year_id':fields.Many2one('fin.year.mst','Financial Year'),
                
    
class EmployeeInternalSaving(models.Model):
    _name = 'employee.internal.saving'
    
    name=fields.Char('Name')
    employee_id=fields.Many2one('hr.employee','Employee Name')
    salary_rule_id=fields.Many2one('hr.salary.rule','Saving Name')
    amount=fields.Float('Amount')
    saving_no=fields.Char('Saving Number')
    date_to=fields.Date('End Date')
    company_id=fields.Many2one('res.company','Zone',default=lambda self: self.env['res.company']._company_default_get('employee.internal.saving'))
    date=fields.Date('Date',default=fields.Date.context_today)
               
    

class SavingCategory(models.Model):
    _name = 'saving.category'
    
    name=fields.Char('Name')
    exempted_amount=fields.Float('Exempted Amount')
                

