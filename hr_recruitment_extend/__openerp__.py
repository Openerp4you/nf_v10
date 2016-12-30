{
    'name' : 'Recruitment Extend',
    'version' : '1.1',
    'author' : 'OpenERP4You',
    'category' : 'Human Resources',
    'description' : """
Recruitment Process having multiple stages and assign Interviewer
====================================
""",
    'summary':"""Jobs, Recruitment, Applications, Job Interviews, Surveys""",
    'website': 'https://www.openerp4you.com',
    'depends' : ['base_setup','hr','base','hr_recruitment','project','survey'],
    'data': [
        'security/ir.model.access.csv',
        'security/hr_security.xml',
        'wizard/wiz_interview_form_view.xml',
        'views/hr_recruitment_view.xml',
        'views/scheduler.xml'
        
        
    ],
    'qweb' : [
       
    ],
    'demo': [
       
    ],
    'test': [
       ],
    'installable': True,
    'auto_install': False,
    'application':True
}