from odoo import api, fields, models, _
from email import _name

class hr_division(models.Model):
    _name="hr.division"
    _description = "HR Division"
    
    name = fields.Char(string='Division')
    dept_id = fields.Many2one('hr.department','Departments')
    
    
class HrBranch(models.Model):
    _name="hr.branch"
    
    def default_country(self):
        return self.env['res.country'].search([('name','=','India')])
    
    name=fields.Char(string='Branch')
    street = fields.Char(string='Address')  
    street2 = fields.Char(string='Address')
    city = fields.Char(string='City')
    state_id = fields.Many2one('res.country.state',string='State')
    country_id = fields.Many2one('res.country',string='Country',default=default_country)
    zip = fields.Char(string='ZIP')  
    phone = fields.Char(string='Phone')
    fax = fields.Char(string='Fax')
    email = fields.Char(string='Email')   
    website = fields.Char(string='Website')
    manager_id = fields.Many2one('hr.employee','Manager')
    tl_manager_id = fields.Many2one('res.users','TL Manager')
    branch_hr_id = fields.Many2one('hr.employee','HR')
    
    
    