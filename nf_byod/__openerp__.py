{
    'name': 'NF BYOD',
    'version': '1.1',
    'author': 'Mohit Kumar',
    'category': 'custom',
    'website': 'https://www.openerp4you.in/',
    'summary': 'Bring Your Own Device',
    'description': """
    Bring Your Own Device
    """,
    'images': [
               ],
    'depends': ['hr','employee_master'],
    'data': [
             'security/security.xml',
             'nf_byod_view.xml',
             'security/ir.model.access.csv',
             ],
    'demo': [],
    'test': [
        
    ],
    'installable': True,
    'application': True,
    'auto_install': False,

}