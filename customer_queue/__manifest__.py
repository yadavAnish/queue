{
    'name': 'Patient Queue Management',
    'version': '1.0',
    'category': 'Healthcare',
    'summary': 'Patient Queue Management with Token System',
    'description': """
        Patient Queue Management System
        ================================
        * Patient registration with token generation
        * Queue management
        * Counter assignment
        * REST API for external integration
    """,
    'author': 'Your Company',
    'depends': ['base', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'views/patient_queue_views.xml',
        'views/counter_views.xml',
        'data/sequence.xml',
    ],
    'installable': True,
    'application': True,
}
