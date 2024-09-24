{
    # Tên module
    'name': 'Real Estate Module BDS',
    'version': '1.0',

    # Loại module
    'category': 'Tutorial',

    # Độ ưu tiên module trong list module
    # Số càng nhỏ, độ ưu tiên càng cao
    #### Chấp nhận số âm
    'sequence': -1,

    # Mô tả module
    'summary': 'Custom product to real estate product',
    'description': '',
    'images': ['static/description/icon.jpg'],

    # Module dựa trên các category nào
    # Khi hoạt động, category trong 'depends' phải được install
    ### rồi module này mới đc install
    'depends': ['base', 'product', 'website_sale', 'crm', 'WebsiteTemplate_BDS','vietNamAddressAutofill'],

    # Module có được phép install hay không
    # Nếu bạn thắc mắc nếu tắt thì làm sao để install
    # Bạn có thể dùng 'auto_install'
    'installable': True,
    'auto_install': False,
    'application': True,
    
    
    # Import các file cấu hình
    # Những file ảnh hưởng trực tiếp đến giao diện (không phải file để chỉnh sửa giao diện)
    ## hoặc hệ thống (file group, phân quyền)
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/product_type_data.xml',
        'data/product_direction_data.xml',
        # 'data/res_country_district_data.xml',
        # 'data/res_country_ward_data.xml',
        'views/custom_menu_visibility.xml',
        'views/s_website_form_advice.xml',
        'views/product_detail_views.xml',
        'views/product_advice.xml',
        'views/product_shop_template.xml',
        'views/product_menu.xml',
        'views/partner_view.xml',
        'views/request_view.xml',
        'views/custom_duan_ws.xml',
        'views/custom_filter_ws.xml'
    ],
    'post_init_hook': 'post_init_hook',
    'assets': {
        'web.assets_frontend': [
            # 'RealEstateModule_BDS/static/src/snippets/s_website_form/000.js',
            # 'RealEstateModule_BDS/static/src/snippets/s_website_form/option.js',
            'RealEstateModule_BDS/static/src/css/custom_css.css',
            'RealEstateModule_BDS/static/src/js/custom_filter.js'
            
        ],
        'web.assets_backend': [
            'RealEstateModule_BDS/static/src/xml/custom_contact_kanban.xml',
            'RealEstateModule_BDS/static/src/js/custom_contact_kanban.js',
            'RealEstateModule_BDS/static/src/xml/custom_contact_list.xml',
            'RealEstateModule_BDS/static/src/js/custom_contact_list.js',
            # 'RealEstateModule_BDS/static/src/js/custom_filter.js'
        ]
    },
    # Import các file cấu hình (chỉ gọi từ folder 'static')
    # Những file liên quan đến
    ## + các class mà hệ thống sử dụng
    ## + các chỉnh sửa giao diện
    ## + t
    'license': 'LGPL-3',
}
