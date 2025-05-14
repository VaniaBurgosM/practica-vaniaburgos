{
    'name': "Gestión de inventarios",
    'summary': "Ingreso, edición y vista de inventarios.",
    'description':"Sistema de gestión de invetarios, que permite ingresar, editar, eliminar y ver registros de un negocio determinado a través de formularios CRUD.",
    'author': "VB",
    'website': "https://vaniaburgosm-practica-vaniaburgos-main-20247569.dev.odoo.com/odoo",
    'category': 'Inventory',
    'version': '0.1',

    'depends': ['base', 'stock', 'product'],

    'data': [
        'security/ir.model.access.csv',
        'views/acciones.xml',
        'views/menus.xml',
        'views/producto_views.xml',
        'views/stock_operation_views.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
    'installable': True,
    'application': True,
}
