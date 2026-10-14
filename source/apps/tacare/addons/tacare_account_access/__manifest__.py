{
    'name': 'TA.CARE - Account Website Access',
    'version': '19.0.2.0.0',
    'author': 'TA.CARE',
    'license': 'LGPL-3',
    'depends': ['website', 'portal', 'auth_signup'],
    'data': ['security/groups.xml', 'views/res_users_views.xml'],
    'post_init_hook': 'post_init_hook',
    'installable': True,
    'application': False,
}
