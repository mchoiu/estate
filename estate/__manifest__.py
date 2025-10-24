{
    'name': 'Real Estate',
    'version': '1.0',
    'category': 'Real Estate/Brokerage',
    'author': 'Sokati',
    'website': 'https://www.facebook.com/tikeo168',
    'depends': ['base'],
    'data': ['security/ir.model.access.csv', 'views/estate_property_views.xml', 'views/estate_property_type_views.xml',
             'views/estate_property_tag_views.xml', 'views/estate_property_offer_views.xml',
             'views/estate_menus.xml'],
    'installable': True,
    'auto_install': False,
    'application': True,
}
