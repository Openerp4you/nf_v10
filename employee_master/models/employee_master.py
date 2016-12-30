
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import time
from odoo.fields import Date

class hr_contract(models.Model):
    
    _inherit = "hr.contract"
    
    name=fields.Char('Name')
    old_basic=fields.Float(string='Old Basic')
    grade_pay=fields.Float(string='Grade Pay')
    last_wage=fields.Float(string='Last Month Wage')
    new_basic=fields.Float('New Basic (CDA)')
       
    driver_salary=fields.Boolean(string='Driver Salary')
    house_rent_all=fields.Float('House Rent Allowance(%)')
    supplementary_allowance=fields.Float('Supplementary Allowance')
        
    tds=fields.Float('TDS')
    voluntary_provident_fund=fields.Float('Voluntary Provident Fund')
    medical_insurance=fields.Float(string="Medical Insurance")
       
    deputed_from_same_station=fields.Boolean(string='Deputed From Same Station')
    deputation_allowance=fields.Boolean('Eligible For Deputation Allowance')
    conveyance_allowance=fields.Boolean('Eligible For Conveyance Allowance')
    hra=fields.Boolean('Eligible For HRA')
    medical_all=fields.Boolean('Opted For Medical Allowance')
    furnishing_all=fields.Boolean('Opted For Furnishing Allowance')
    pf_stop=fields.Boolean('PF Stop')
    spouse_railway=fields.Boolean('Spouse Opting Railway/PSU Medical Allowance')
    previous_railway_empl=fields.Boolean('Previous Railway Employee')
    washing_allowance=fields.Boolean('Opted For Washing Allowance')
    holiday_worked_Day=fields.Integer('National Holiday Worked Days')
    night_duty_hr=fields.Float('Night Duty Hours',widget='Float_time')
    monthly_rent=fields.Float('Monthly Quarter Rent')
    pf_amt=fields.Float('Special PF Amounts')   
    
class hr_employee(models.Model):
    _inherit="hr.employee"
    
#         'name=fields.Char('Name')
    empl_unique_id=fields.Char('Employee Unique ID')
    virtual_mob_no=fields.Char('Virtual Mobile Number')
    pf_id=fields.Char('PF ID')
    uan=fields.Char('UAN')
    empl_type=fields.Char('Employee Type')
    emp_id=fields.Char('Employee ID')
    join_date=fields.Date('Date Of Joining')
    visibility=fields.Char('Visibility')
    
    display_name=fields.Char('Display Name')
    state=fields.Char('State')

    sales_chanel=fields.Char('sales_chanel')
    nf_dept=fields.Many2one('hr.department','NF Department')
    sub_dept=fields.Many2one('hr.department','Sub Department')
    intrnal_desig=fields.Char('Internal Designation')
    high_edu_qual=fields.Char('Highest Education Qualification')
    hr_name=fields.Char('HR Name')
    reporting_head=fields.Many2one('hr.employee','Reporting Head')
    grade=fields.Char('Grade')
    level=fields.Char('Level')
    aadhar_no=fields.Char('Aadhar Number')
    emp_father=fields.Char(string="Employee Father's Name") 
    data_form=fields.Binary('Data Form')
    emp_size=fields.Char('Employee Shirt Size')
    pan=fields.Char('PAN')
    currnt_addr=fields.Char('Current Address')
    alternate_contact=fields.Char('Alternate Contact Number')
    permanent_addr=fields.Char('Permanent Address')
    personal_email=fields.Char('Personal Email')
    
    offer_letter=fields.Binary('Offer Letter')
    nda=fields.Binary('NDA')
    current_addr_proof=fields.Binary('Current Address Proof')
    permanent_addr_proof=fields.Binary('Permanent Address Proof')
    id_proof=fields.Binary('ID Proof')
    certif_12=fields.Binary('12 Certificate')
    ug_certifcate=fields.Binary('UG Certificate')
    previous_pay_slip=fields.Binary("Previous Company's Pay Slip")
    prev_reliving_lttr=fields.Binary("Previous Company's Relieving Letter")
    
    reliving_leter=fields.Binary('Relieving Letter')
    othr_docs=fields.Binary('Any Other Document')
    last_working_date=fields.Date('Last Working Date')
    empl_status=fields.Selection([('active', 'ACTIVE') ,('inactive', 'INACTIVE')], string='Employee Status')
    reason_for_leaving=fields.Char('Reason For Leaving Now Floats')
    empl_attrtion=fields.Binary('Employee Attrition')     
    ifsc_Code = fields.Char('IFSC Code')

    
    
    
    
    
    
    
    