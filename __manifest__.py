{
    'name': "To Do",
    'version': "14.0.1.0",
    'sequence': "0",
    'depends': ['base', 'mail'],
    'data': [
        'data/activity.xml',
        'security/groups.xml',
        'security/ir.model.access.csv',
        'security/rules.xml',
        'views/to_do.xml',
        'views/assign_wizard.xml',

    ],
    'demo': [],
    'summary': "logic_to_do",
    'description': "this_is_my_app",
    'installable': True,
    'auto_install': False,
    'license': "LGPL-3",
    'application': False
}
