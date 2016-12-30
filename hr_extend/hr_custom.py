from odoo import api, fields, models
from odoo.exceptions import UserError, RedirectWarning, ValidationError
import re
class hrr_rates(models.Model):
    _name = 'hrr.rates'
    
    name=fields.Char('Name')
    area_from=fields.Float('Area From')
    area_to=fields.Float('Area To')
    amount=fields.Float('Amount')
                
class fin_year_mst(models.Model):
    _name = 'fin.year.mst'
      
    name=fields.Char('Code')
    start_date=fields.Date('Start Date')
    end_date=fields.Date('End Date')
                
class bank_mst(models.Model):
    _name = 'bank.mst'
    
    name=fields.Char('Name')
    code=fields.Char('Code')
                
class con_recovery_rates(models.Model):
    _name = 'con.recovery.rates'
    
     
    name=fields.Char('Name')
    grade_id=fields.Many2one('hr.grade','Grade')
    max_journey=fields.Float('Maximum Journey')
    amount=fields.Float('Amount')
    pattern= fields.Selection([('IDA','IDA'),('CDA','CDA')],"Pattern")
                

class hr_grade(models.Model):
    _name = 'hr.grade'
    
    name=fields.Char('Grade',required='True')
    level=fields.Char('Level')
    cadre_id=fields.Many2one('emp.cadre','Cadre')
#     payscale_id=fields.Many2one('hr.payscale','Payscale')
#     new_payscale_id=fields.Many2one('hr.payscale','New Payscale')
                
    
class hr_professional_tax(models.Model):
    _name = 'hr.professional.tax'
     
    name=fields.Char('Name')
    state_id=fields.Many2one('state.mst','State')
    amount_from=fields.Float('Amount From')
    amount_to=fields.Float('Amount To')
    pro_tax_amount=fields.Float('Tax Amount')
    month_from= fields.Selection([('1','JAN'),('2','FEB'),('3','MAR'),('4','APR'),('5','MAY'),('6','JUN'),('7','JUL'),('8','AUG'),('9','SEP'),('10','OCT'),('11','NOV'),('12','DEC')],'Month From')
    month_to= fields.Selection([('1','JAN'),('2','FEB'),('3','MAR'),('4','APR'),('5','MAY'),('6','JUN'),('7','JUL'),('8','AUG'),('9','SEP'),('10','OCT'),('11','NOV'),('12','DEC')],'Month To')
    half_yearly=fields.Boolean('Half Yearly')
    gross_annual=fields.Boolean('Gross Annual')
                

class da_rates(models.Model): 
    _name = 'da.rates'
      
    name=fields.Char('Description',required='True')
    effective_from=fields.Date('Effective From Date',required='True')
    effective_to=fields.Date('Effective End Date')
    pattern=fields.Selection([('IDA','IDA'),('CDA','CDA')],"DA Pattern",required='True')
    rate=fields.Float('Rate(%)',required='True')
    active=fields.Boolean('Active')
                
class hr_location(models.Model):
    _name = 'hr.location'
      
    code=fields.Char('Code')
    name=fields.Char('Name',required='True')
    state_id=fields.Many2one('state.mst','State')
    type=fields.Selection([('X','X'),('Y','Y'),('Z','Z')],'Type')
    hra_rates=fields.Float('HRA Rates(%)')
    type_for_conveyance=fields.Selection([('X','X'),('Y','Y'),('Z','Z')],'Type For Conveyance')
    region_id=fields.Many2one('employee.region','Region')
    is_metro=fields.Selection([('Y','YES'),('N','NO')],'Is Metro' )
    professional_tax=fields.Boolean('Professional Tax')
    professional_tax_type=fields.Selection([('F','Fixed'),('V','Variable')],'Tax Type' )
    pro_tax_amount=fields.Float('Amount')
                
class emp_cadre(models.Model):
    _name = 'emp.cadre'
    
    name = fields.Char('Name',required='True')
                
class state_mst(models.Model):
    _name = 'state.mst'
    name= fields.Char('Name',required='True')
    code= fields.Char('Code',required='True')
                
    
class employee_unit(models.Model):
    _name = 'employee.unit'
      
    name= fields.Char('Name',required='True')
    code= fields.Char('Code',required='True')
    region_id=fields.Many2one('employee.region','Region')
                
class employee_region(models.Model):
    _name = 'employee.region'
      
    name=fields.Char('Name',required='True')
    code=fields.Char('Code',required='True')
    company_id=fields.Many2one('res.company','Zone')
                
class employee_type(models.Model):
    _name = 'employee.type'
    
      
    name=fields.Char('Name',required='True')
                
    
class hr_employee(models.Model):
    _inherit = 'hr.employee'
    _order = 'employee_no'
    
    
    
    @api.multi
    def name_get(self):
        result = []
        name=''
        for record in self:
            if record.employee_no:
                name =  "[%s] %s" % (record.employee_no ,record.name)
            else:
                name =  "%s" % (record.name)
            result.append((record.id, name))
        return result
    
    
    
    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        recs = self.browse()
        if name:
            recs = self.search([('name', '=', name)] + args, limit=limit)
        
            recs = self.search([('employee_no', '=', name)] + args, limit=limit)
        
        
        if not recs:
            recs = self.search([('name', operator, name)] + args, limit=limit)
            recs = self.search([('employee_no', operator, name)] + args, limit=limit)

        return recs.name_get()

    
    @api.multi
    def _check_ifsc_code(self):
        str="^-?[a-zA-Z0-9]+$"
        obj=self.browse()[0]
        name=obj.ifsc_code
        if name and len(name) != 11:
            raise UserError(_('Invalid IFSC Code'), _('IFSC Code must contain 11 Alphanumeric only.'))
        if name and re.match(str,name) == None:
            return False
        else:
            return True
        
      
    def default_country(self):
        return self.env['res.country'].search([('name','=','India')])
    
    company_id=fields.Many2one('res.company','Company')
    grade_id=fields.Many2one('hr.grade','Grade')
    benefits_grade_id=fields.Many2one('hr.grade','Benefits Grade')
    doj=fields.Date('Joining Date')
    employee_no=fields.Char('Employee No.')
    father_name= fields.Char('Father Name', size=32, )
    bank_account= fields.Char('Bank Account', size=32, )
    ifsc_code=fields.Char('IFSC Code', size=32,)
    Date_of_birth= fields.Date('Date of Birth')
    retire_date= fields.Date('Retirement Date')
    pf_account= fields.Char('PF Account No')
    pan_number= fields.Char('Pan Number')
    bank_name= fields.Char('Bank Name')
    bank_address= fields.Char('Bank Address')
    region_id= fields.Many2one('employee.region','Region')
    unit= fields.Char('Place Of Appointment')
    catering_unit= fields.Many2one('employee.unit','Catering Unit')
    pattern= fields.Selection([('IDA','IDA'),('CDA','CDA')],"DA Pattern")
    mode_of_pay= fields.Selection([('Bank','Bank'),('Cheque','Cheque'),('NEFT','NEFT'),('Cash','Cash')],'Mode of Pay')
    location_id=fields.Many2one('hr.location','Location')
    old_location_id=fields.Many2one('hr.location','Old Location')
    last_transfer_date=fields.Date('Last Transfer Date')
    last_promotion_date=fields.Date('Last Promotion Date')
    employee_type_id=fields.Many2one('employee.type','Employee Type')
    disability= fields.Selection([('P','YES-Partial Disable'),('F','YES-Fully Disable'),('N','No')],"Disability")
    desig_in_railway=fields.Char('Designation In Railway')
    gl_region=fields.Char('GL Region')
    lob=fields.Char('Line Of Bussiness')
    status=fields.Char('Status')
    from_date=fields.Date('From Date')
    to_date=fields.Date('To Date')
    uan=fields.Char('UAN')
    salary_done=fields.Boolean('Salary Done')
    
    empl_id=fields.Char('Employee ID')
    branch_id = fields.Many2one('hr.branch','Branch')
    division_id = fields.Many2one('hr.division','Division')
    sub_dep = fields.Many2one('hr.department','Sub Department')
    cost_centr = fields.Many2one('account.analytic.account','CC Control Code')
    coach_id = fields.Many2one('hr.employee', string='Reporting Head')
    job_id= fields.Many2one('hr.job', 'Job Position')
    intrnl_desig = fields.Many2one('hr.job','Internal Designation')
    hr = fields.Many2one('hr.employee','HR')
    
    street = fields.Char(string='Address')  
    street2 = fields.Char(string='Address')
    city = fields.Char(string='City')
    state_id = fields.Many2one('res.country.state',string='State')
    country_id1 = fields.Many2one('res.country',string='Country',default=default_country)
    zip = fields.Char(string='ZIP')
    
    @api.model
    def create(self, vals):
        res = super(hr_employee, self).create(vals)
        branch = 'branch_id' in vals and vals['branch_id'] or None
        division = 'division_id' in vals and vals['division_id'] or None
        self.env.cr.execute("select id from account_analytic_account where branch_id = %s and division_id = %s",(branch,division,))
        temp = self.env.cr.fetchall()
        analytic_account_id = None
        if temp:
            analytic_account_id = temp[0][0]
            
        elif 'branch_id' in vals and vals['branch_id'] and 'division_id' in vals and vals['division_id']:
            name = str(res.branch_id.name) + '/' + str(res.division_id.name)
            code = self.env['ir.sequence'].next_by_code('account.analytic.account')
            analytic_account  =self.env['account.analytic.account'].create({'name':name,'code':code,'branch_id':vals['branch_id'],'division_id':vals['division_id']})
            analytic_account_id = analytic_account.id
        self.env.cr.execute("update hr_employee set cost_centr = %s where id = %s",(analytic_account_id,res.id))
        return res
    
    
    @api.multi
    def write(self, vals):
        if vals.get('appraisal_date') and fields.Date.from_string(vals.get('appraisal_date')) < datetime.date.today():
            raise UserError(_("The date of the next appraisal cannot be in the past"))
        else:
            res = super(hr_employee, self).write(vals)
            if 'branch_id' in vals or 'division_id' in vals:
                branch = self.branch_id and self.branch_id.id or None
                division = self.division_id and self.division_id.id or None
                self.env.cr.execute("select id from account_analytic_account where branch_id = %s and division_id = %s",(branch,division,))
                temp = self.env.cr.fetchall()
                analytic_account_id = None
                if temp:
                    analytic_account_id = temp[0][0]
                    
                elif self.branch_id and self.division_id:
                    name = str(self.branch_id.name) + '/' + str(self.division_id.name)
                    code = self.env['ir.sequence'].next_by_code('account.analytic.account')
                    analytic_account  =self.env['account.analytic.account'].create({'name':name,'code':code,'branch_id':self.branch_id.id,'division_id':self.division_id.id})
                    analytic_account_id = analytic_account.id
                self.env.cr.execute("update hr_employee set cost_centr = %s where id = %s",(analytic_account_id,self.id))
            return res
        
        
    @api.onchange('branch_id')
    def onchange_branch(self):
        for record in self:
            if record.branch_id:
               branch = record.branch_id
               record.street = branch.street
               record.street2 = branch.street2
               record.city = branch.city
               record.state_id = branch.state_id
               record.country_id1 = branch.country_id
               record.zip = branch.zip
               
                    
    
class Branch(models.Model):
    _name="branch"
    _description="Branch"
    
    name = fields.Char('Name')
        
class hr_contract(models.Model):
    _inherit = 'hr.contract'
     
    grade_pay=fields.Float('Grade Pay')
    old_wage=fields.Float('Old Basic')
    last_mth_wage=fields.Float('Last Month Wage')
    
    hra_hrr_lease= fields.Boolean('Lease')
    lease_type=fields.Selection([('1','Individual'),('2','Company'),('3','Partnership')],'Landlord Type')
    ownership_type= fields.Selection([('N','Self Lease'),('NR','Near Relative'),('C','Company Accomodation'),('Y','Company Lease')],'Ownership Type')
    flat_area=fields.Float('Flat Area')
    address=fields.Char('Address')
    lease_amount=fields.Float('Actual Rent Amount')
    lease_start_date=fields.Date('Lease Start Date')
    lease_end_date=fields.Date('Lease End Date')
    lease_notes=fields.Text('Notes')
    
    monthly_inc_amount= fields.Float('Monthly Increment Amount')
    ne_increment_month=fields.Date('Next Increment Date')
    increment_month= fields.Selection([('1','JAN'),('2','FEB'),('3','MAR'),('4','APR'),('5','MAY'),('6','JUN'),('7','JUL'),('8','AUG'),('9','SEP'),('10','OCT'),('11','NOV'),('12','DEC')],'Increment Month')
    increment_status=fields.Char('Increment Status')
    vpf_amount= fields.Float('VPF Amount')
    child_ed_allow=fields.Boolean('Child Education Allowance')
    electricity_allow=fields.Boolean('Electricity Allowance')
    entertain_allow=fields.Boolean('Entertainment Allowance')
    vehi_conveyence_allow=fields.Boolean('Vehicle Conveyance Allowance')
    hard_soft_fur=fields.Boolean('Hard And Soft Furnishing')
    lunch_dinner_coup=fields.Boolean('Lunch Dinner Coupon')
    prof_up_allow=fields.Boolean('Professional Updation Allowance')
    medical_allow=fields.Boolean('Medical Allowance')
    uniform_fit_allow=fields.Boolean('Uniform Allowance')
    meal_coupon_allow=fields.Boolean('Meal Coupon')
    washing_allow=fields.Boolean('Washing Allowance')
    nps=fields.Boolean('NPS')
    cafeteria_aggregate=fields.Float('Cafeteria Percentage Aggregate')
    deputed_from_same_station=fields.Boolean('Deputed From same Station')
    eligible_for_deputaion=fields.Boolean('Eligible For Deputation Allowance')
    eligible_for_conveyance=fields.Boolean('Eligible For Conveyance Allowance')
    eligible_for_hra=fields.Boolean('Eligible For HRA')
    opted_for_medical=fields.Boolean('Opted For Medical Allowance')
    opted_for_furnishing=fields.Boolean('Opted For Furnishing Allowance')
    opted_for_washing=fields.Boolean('Opted For Washing Allowance')              
    nha_worked=fields.Float('National Holiday Worked Days')
    nda_hours=fields.Integer('Night Duty Hours')
    monthly_rent_paid=fields.Float('Monthly Quarter Rent')
    spouse_opting_rly_medical=fields.Boolean('Spouse Opting Railway/PSU Medical Allowance')
    previous_railway_employee=fields.Boolean('Previous Railway Employee')
    special_pf_amount=fields.Float('Special PF Amount')
    pf_stop_flag=fields.Boolean('PF Stop')
    new_wage=fields.Float('New Basic(CDA)')
    trial_date_start= fields.Date('Trial Start Date')
    wage=fields.Float('Salary', digits=(16, 2), required=True, help="Basic Salary of the employee")
    division=fields.Many2one('hr.division','Division')
    job_id= fields.Many2one('hr.job', 'Designation')
    
class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'
    
    branch_id = fields.Many2one('hr.branch','Branch')
    division_id=fields.Many2one('hr.division','Division')
        



# class railway_division(osv.Model):
#     _name = 'railway.division'
#     
#      = 
#                 'name':fields.Char('Name',required='True'),
#                 'code':fields.Char('Code',required='True'),
#                 
#     
    
    
    