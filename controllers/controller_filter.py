from odoo import http
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.http import request
import logging

_logger = logging.getLogger(__name__)

class WebsiteSaleCustomFilter(WebsiteSale):
    
    @http.route(['/shop'], type='http', auth="public", website=True)
    def shop(self, page=0, category=None, search='', **post):

        city_filter = post.get('city_filter', '')
        direction_filter = post.get('direction_filter', '')
        category_filter = post.get('category_filter', '')
        price_filter = post.get('price_filter', '')
        
        _logger.info(f" price_filter + { price_filter}")
       
        
        
        
        # Tạo domain để lọc sản phẩm dựa trên thành phố
        domain = [('sale_ok', '=', True)]
        # if city_filter:
        #     domain.append(('state_id', '=', int(city_filter)))
        if city_filter:
            domain.append(('province_id', '=', int(city_filter)))
        if category_filter:
            domain.append(('product_type_id', '=',int(category_filter)))
        if direction_filter:
            domain.append(('direction_id', '=',int(direction_filter)))
        if price_filter:
            price_range = price_filter.split('-')
            if len(price_range) == 2:
                domain.append(('list_price', '>=', float(price_range[0])))
                domain.append(('list_price', '<=', float(price_range[1])))
            elif len(price_range) == 1 and price_range[0]:
                domain.append(('list_price', '>=', float(price_range[0])))
       
        
        products = request.env['product.template'].search(domain)
        ribbon_values = request.env['product.ribbon'].search([("id","=","5")] ,limit=1)
        _logger.info(f" ribbon_values + { ribbon_values}")
        # city_values = request.env['res.country.state'].search([])
        # _logger.info(f" city_values + { city_values}")
        city_values = request.env['vietnam.province'].search([])
        _logger.info(f" city_values + { city_values}")
        category_values = request.env['product.type'].search([])
        _logger.info(f" category_values + { category_values}")
        direction_values = request.env['product.direction'].search([])
        _logger.info(f" direction_values + { direction_values}")
        
        response = super(WebsiteSaleCustomFilter, self).shop(page=page, category=category, search="", **post)
        bins = []
        row = []
        products_per_row = 4
        for idx, product in enumerate(products):
                # Kiểm tra nếu ribbon tồn tại, nếu không thì gán None
                row.append({
                    'product': product,
                    'x': 1,  # Tùy chỉnh chiều ngang của mỗi sản phẩm trong ô (bin)
                    'y': 1,  # Tùy chỉnh chiều dọc của mỗi sản phẩm trong ô (bin)
                    'ribbon':  product.website_ribbon_id if product.website_ribbon_id else ribbon_values # Gán giá trị ribbon, nếu không có thì để None
                })
                
                # Khi số lượng sản phẩm trong hàng đạt giới hạn, tạo hàng mới
                if (idx + 1) % products_per_row == 0:
                    bins.append(row)
                    row = []
            
            # Thêm hàng cuối nếu còn sản phẩm
        if row:
                bins.append(row)
                
    

        response.qcontext.update({
                'city_values': city_values,
                'products': products,
                'category_values': category_values,
                'direction_values': direction_values,
                "bins": bins,
            })
 

        _logger.info(f" response.qcontext + { response.qcontext}")
        return response
    
    
        
