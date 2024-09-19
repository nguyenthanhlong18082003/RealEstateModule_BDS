# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import base64
import json
import random
import string


from markupsafe import Markup
from psycopg2 import IntegrityError
from werkzeug.exceptions import BadRequest
from datetime import datetime, timedelta
from odoo import http, SUPERUSER_ID, _, _lt
from odoo.addons.base.models.ir_qweb_fields import nl2br, nl2br_enclose
from odoo.http import request
from odoo.tools import plaintext2html
from odoo.exceptions import AccessDenied, ValidationError, UserError
from odoo.tools.misc import hmac, consteq


class WebsiteForm(http.Controller):

    def get_partner(self, user_name, email, phone_number):
        partner = None

        if email and phone_number:
            partner = request.env['res.partner'].sudo().search([('email', '=', email), ('phone', '=', phone_number)], limit=1)
        elif email:
            partner = request.env['res.partner'].sudo().search([('email', '=', email)], limit=1)
        elif phone_number:
            partner = request.env['res.partner'].sudo().search([('phone', '=', phone_number)], limit=1)

        if partner:
            return partner
        else:
            # Tạo một đối tác mới nếu không tìm thấy
            new_partner_vals = {
                'name': user_name,
                'email': email,
                'phone': phone_number,
            }
            new_partner = request.env['res.partner'].sudo().create(new_partner_vals)

            # Lấy nhóm Public User
            public_group = request.env.ref('base.group_public')

            # Tạo người dùng mới và liên kết với đối tác mới
            new_user_vals = {
                'name': user_name,
                'login': email or phone_number or ''.join(random.choices(string.ascii_letters + string.digits, k=8)),
                'password': phone_number,  # Password có thể là số điện thoại hoặc một giá trị mặc định khác
                'email': email,
                'active': True,
                'phone': phone_number,
                'partner_id': new_partner.id,
                'groups_id': [(6, 0, [public_group.id])]  # Thiết lập nhóm người dùng công cộng
            }
            new_user = request.env['res.users'].sudo().create(new_user_vals)

            return new_partner

    # Phương thức tìm kiếm activity_user_id bằng id của sản phẩm 
    def get_activity_user_id(self, product_id):
        domain = [('id', '=', product_id)]
        # Tìm kiếm sản phẩm 
        res_product = http.request.env['product.template'].sudo().search(domain)
        # Nếu sản phẩm tồn tại và nếu trong sản phẩm trường activity_user_id có giá trị (Là đã được đặt người quản lý )
        if res_product and res_product.activity_user_id:
            # Lấy Id của activity_user_id 
            activity_user_id = res_product.activity_user_id.id
            act_id = [('id', '=', activity_user_id)]
            # Tìm kiếm người dùng và trả về người dùng 
            activity_user = http.request.env['res.users'].sudo().search(act_id)
            return activity_user
        else: 
            return False
    # phương thức tạo lịch hẹn 
    def create_calendar_event(self, event_data):
        # Sử dụng phương thức create để tạo mới bản ghi
        new_event = request.env['calendar.event'].sudo().create(event_data)
        return new_event  # Trả về ID của bản ghi mới

    # Tìm kiếm và cập nhật calendar_event_ids cho crm.lead (kiểu one2many)
    def update_lead_calendar_event_ids(self, id_record, calendar_event_id):
        # Tìm kiếm bản ghi crm.lead dựa trên id_record
        domain = [('id', '=', id_record)]
        lead_record = request.env['crm.lead'].sudo().search(domain)

        # Kiểm tra nếu bản ghi crm.lead tồn tại
        if lead_record:
            # Gắn calendar.event dựa trên calendar_event_id
            event_domain = [('id', '=', calendar_event_id)]
            calendar_event_record = request.env['calendar.event'].sudo().search(event_domain)

            # Kiểm tra nếu bản ghi calendar.event tồn tại
            if calendar_event_record:
                calendar_event_record.write({
                    'opportunity_id': lead_record.id
                })
                # Cập nhật trường one2many calendar_event_ids của crm.lead
                lead_record.write({
                    'calendar_event_ids': [calendar_event_record.id]
                })
                return calendar_event_record
            else:
                print("Calendar event with ID", calendar_event_id, "not found.")
        else:
            print("Lead record with ID", id_record, "not found.")




    @http.route('/website/form', type='http', auth="public", methods=['POST'], multilang=False)
    def website_form_empty(self, **kwargs):
        # This is a workaround to don't add language prefix to <form action="/website/form/" ...>
        return ""

    # Check and insert values from the form on the model <model>
    @http.route('/website/form/<string:model_name>', type='http', auth="public", methods=['POST'], website=True, csrf=False)
    def website_form(self, model_name, **kwargs):
        # Partial CSRF check, only performed when session is authenticated, as there
        # is no real risk for unauthenticated sessions here. It's a common case for
        # embedded forms now: SameSite policy rejects the cookies, so the session
        # is lost, and the CSRF check fails, breaking the post for no good reason.
        csrf_token = request.params.pop('csrf_token', None)
        if request.session.uid and not request.validate_csrf(csrf_token):
            raise BadRequest('Session expired (invalid CSRF token)')

        try:
            # The except clause below should not let what has been done inside
            # here be committed. It should not either roll back everything in
            # this controller method. Instead, we use a savepoint to roll back
            # what has been done inside the try clause.
            with request.env.cr.savepoint():
                if request.env['ir.http']._verify_request_recaptcha_token('website_form'):
                    # request.params was modified, update kwargs to reflect the changes
                    kwargs = dict(request.params)
                    kwargs.pop('model_name')
                    return self._handle_website_form(model_name, **kwargs)
            error = _("Suspicious activity detected by Google reCaptcha.")
        except (ValidationError, UserError) as e:
            error = e.args[0]
        return json.dumps({
            'error': error,
        })

    def _handle_website_form(self, model_name, **kwargs):
        # Tìm kiếm model trong hệ thống 
        model_record = request.env['ir.model'].sudo().search([('model', '=', model_name), ('website_form_access', '=', True)])
        # Trường hợp tìm không thấy model thì trả về lỗi
        if not model_record:
            return json.dumps({
                'error': _("The form's specified model does not exist")
            })

        try:
            # Trích xuất dữ liệu bằng cách gọi tới phương thức etract_data 
            data = self.extract_data(model_record, kwargs)
        # Nếu gặp sự cố khi trích xuất dữ liệu
        except ValidationError as e:
            # Trả về một ngoại lệ 
            return json.dumps({'error_fields': e.args[0]})
        #  Nếu tìm được dự liệu 
        try:
            # Chèn / tạo một bản ghi bằng phương thức insert_record 
            # dựâ theo model đã được tìm kiếm trước đó, và các thành phần khác sau đó lấy id của một record gán cho id_record
            id_record = self.insert_record(request, model_record, data['record'], data['custom'], data.get('meta'))
            # nếu tạo bản ghi thành công 
            if id_record:
                # Lấy danh sách người dùng để bỏ vào lịch 
                if model_name == 'crm.lead':
                    partner_ids = [data['record']['partner_id'], data['record']['user_id']]
                    datetime_local = data['meeting']['meeting_display_date']
                    if datetime_local and partner_ids:
                        # Chuyển đổi datetime_local thành đối tượng datetime
                        start_datetime = datetime.strptime(datetime_local, '%Y-%m-%dT%H:%M')
                        if start_datetime: 
                            # Tạo một calendar.event
                            calendar_event_data = {
                                'name': data['record']['name'],
                                'start': start_datetime.strftime('%Y-%m-%d %H:%M:%S'),  # Định dạng mới
                                'start_date': start_datetime.strftime('%Y-%m-%d'),
                                'stop': (start_datetime + timedelta(minutes=30)).strftime('%Y-%m-%d %H:%M:%S'),  # Thêm 30 phút và định dạng mới
                                'stop_date': start_datetime.strftime('%Y-%m-%d'),
                                'allday' : False,
                                'recurrency': False,
                                'user_id': data['record']['user_id'],
                                'description': 'Ngày khách hẹn',
                                'active': True,
                                'event_tz':'Etc / GMT + 1 ',
                                'duration': 1.0,
                                'privacy':'public',
                                'location': 'Thêm sau',
                                'partner_ids': [(6, 0, partner_ids)]
                            }

                            # Tạo lịch hẹn
                            id_event = self.create_calendar_event(event_data=calendar_event_data)
                            if id_event:
                                self.update_lead_calendar_event_ids(id_record=id_record, calendar_event_id=id_event.id)
                # Nếu có tệp đính kèm thì sẽ chèn vào tệp đính kèm bằng insert_attachment 
                self.insert_attachment(model_record, id_record, data['attachments'])

                # Trong trường hợp gửi một email thì sẽ thực hiện gửi mail ngay

                if model_name == 'mail.mail':
                    form_has_email_cc = {'email_cc', 'email_bcc'} & kwargs.keys() or \
                        'email_cc' in kwargs["website_form_signature"]
                    # remove the email_cc information from the signature
                    kwargs["website_form_signature"] = kwargs["website_form_signature"].split(':')[0]
                    if kwargs.get("email_to"):
                        value = kwargs['email_to'] + (':email_cc' if form_has_email_cc else '')
                        hash_value = hmac(model_record.env, 'website_form_signature', value)
                        if not consteq(kwargs["website_form_signature"], hash_value):
                            raise AccessDenied('invalid website_form_signature')
                    request.env[model_name].sudo().browse(id_record).send()

        # Một số trường có các ràng buộc SQL bổ sung mà không thể kiểm tra tổng quát
        # Ví dụ: crm.lead.probability là số float giữa 0 và 1
        # TODO: Làm thế nào để có được tên của trường sai?
        except IntegrityError:
            return json.dumps(False)

        request.session['form_builder_model_model'] = model_record.model
        request.session['form_builder_model'] = model_record.name
        request.session['form_builder_id'] = id_record

        return json.dumps({'id': id_record})

    # Constants string to make metadata readable on a text field

    _meta_label = _lt("Metadata")  # Title for meta data

    # Dict of dynamically called filters following type of field to be fault tolerent

    def identity(self, field_label, field_input):
        return field_input

    def integer(self, field_label, field_input):
        return int(field_input)

    def floating(self, field_label, field_input):
        return float(field_input)

    def html(self, field_label, field_input):
        return plaintext2html(field_input)

    def boolean(self, field_label, field_input):
        return bool(field_input)

    def binary(self, field_label, field_input):
        return base64.b64encode(field_input.read())

    def one2many(self, field_label, field_input):
        return [int(i) for i in field_input.split(',')]

    def many2many(self, field_label, field_input, *args):
        return [(args[0] if args else (6, 0)) + (self.one2many(field_label, field_input),)]

    _input_filters = {
        'char': identity,
        'text': identity,
        'html': html,
        'date': identity,
        'datetime': identity,
        'many2one': integer,
        'one2many': one2many,
        'many2many': many2many,
        'selection': identity,
        'boolean': boolean,
        'integer': integer,
        'float': floating,
        'binary': binary,
        'monetary': floating,
    }

    # Trích xuất tất cả dữ liệu được gửi theo biểu mẫu và sắp xếp nó trên một số thuộc tính
    def extract_data(self, model, values):
        # Tìm kiếm model dự trên model truyền vào 
        dest_model = request.env[model.sudo().model]
        # data trả về gồm: 
        data = {
            'record': {},        # Giá trị để tạo bản ghi
            'meeting': {},
            'attachments': [],  # File đính kèm
            'custom': '',        # Giá trị trường tùy chỉnh
            'meta': '',         # Thêm siêu dữ liệu nếu được bật
        }
        # các trường được ủy quyền, có sẵn tìm kiếm dựa vào superuser_id được import bên trên 
        # Phương thức _get_form_writable_fields được khai báo ở trong odoo, chỉ lấy ra xài 
        authorized_fields = model.with_user(SUPERUSER_ID)._get_form_writable_fields()
        error_fields = []
        custom_fields = []
        
        if dest_model._name == 'crm.lead':
            # Kiểm tra sự tồn tại của 3 trường
            email_from = values.get('email_from', None)
            contact_name = values.get('contact_name', None)
            phone = values.get('phone', None)

            # # Kiểm tra xem có đủ 3 trường hay không
            # if contact_name and phone and email_from:
            #     # Tiến hành xử lý các trường
            partner_value = self.get_partner(user_name=contact_name, email=email_from, phone_number=phone)
            if partner_value:
                data['record']['partner_id'] = partner_value.id
            else:
                # Handle the case where partner_value contains multiple records
                raise ValueError("partner_value không có giá trị trả về")



        productId = values.get('productId', None)
        if productId and dest_model._name == 'crm.lead':
            # Thêm sản phẩm vào trường product_relation 
            data['record']['product_relation'] = productId
            res_user = self.get_activity_user_id(product_id=productId)
            if res_user:
                # Người chịu trách nhiệm Opp 
                data['record']['user_id'] = res_user.id

        meeting_date = values.get('meeting_display_date', None)
        if meeting_date and dest_model._name == 'crm.lead':
            data['meeting']['meeting_display_date'] = meeting_date
        else: 
            data['meeting']['meeting_display_date'] = None
        # Lọc giá trị theo cặp tên trường và giá trị trường trong mỗi items của values được truyền vào ngay đầu phương thức 
        for field_name, field_value in values.items():
            # If the value of the field if a file
            if hasattr(field_value, 'filename'): # Nếu giá trị trường là một tệp tin
                # Hoàn tác lập chỉ mục tên trường tải lên tệp
                field_name = field_name.split('[', 1)[0]

                # Nếu đó là trường nhị phân thực tế, hãy chuyển đổi tệp đầu vào
                # Nếu không, chúng tôi sẽ sử dụng tệp đính kèm để thay thế
                # Nếu field_name có trong danh sách authorized_fields và kiểu dữ liệu của field_name này là binary 
                if field_name in authorized_fields and authorized_fields[field_name]['type'] == 'binary':
                    data['record'][field_name] = base64.b64encode(field_value.read())
                    field_value.stream.seek(0)  # do not consume value forever
                    if authorized_fields[field_name]['manual'] and field_name + "_filename" in dest_model:
                        data['record'][field_name + "_filename"] = field_value.filename
                else:
                    field_value.field_name = field_name
                    data['attachments'].append(field_value)   
            
            
            # Nếu field_name của items (giá trị mỗi vòng lặp values) có trong danh sách các trường được ủy quyền (authorized_fields)
            
            elif field_name in authorized_fields:
                try:
                    # gắn kiểu dữ liệu tương ứng dựa vào danh sách kiểu dữ liệu được khai báo ở trong _input_filters
                    input_filter = self._input_filters[authorized_fields[field_name]['type']]
                    # lưu giá trị đã lọc vào data['record']
                    data['record'][field_name] = input_filter(self, field_name, field_value)
                except ValueError:
                    # Nếu có lỗi gắn xảy ra thì sẽ gắn vào trường error_fields
                    error_fields.append(field_name)
                # Nếu model là mail.mail và có trường email_from thì sẽ gán giá trị của trường email_form vào phần custom 
                if dest_model._name == 'mail.mail' and field_name == 'email_from':
                    # As the "email_from" is used to populate the email_from of the
                    # sent mail.mail, it could be filtered out at sending time if no
                    # outgoing mail server "from_filter" match the sender email.
                    # To make sure the email contains that (important) information
                    # we also add it to the "custom message" that will be included
                    # in the body of the email sent.
                    custom_fields.append((_('email'), field_value))
                if dest_model._name == 'mail.mail' and field_name == 'partner_id':
                    continue
                if dest_model._name == 'crm.lead' and (field_name == 'contact_name' or field_name=='email_from' or field_name == 'phone'):
                    if field_name == 'contact_name':
                        custom_fields.append(('Nickname:', field_value))
                    if field_name == 'email_from':
                        custom_fields.append(('Email:', field_value))
                    if field_name == 'phone':
                        custom_fields.append(('Phone:', field_value))
                if dest_model._name == 'crm.lead' and (field_name=='email_from' or field_name == 'phone' or field_name == 'user_id'):
                    continue
            # nếu field name này không tồn tai thì sẽ chèn nó vào trường custom_fields 
            elif field_name not in ('context', 'website_form_signature'): 
                if field_name == "productId":
                    continue
                if field_name == 'email_to':
                    continue
                custom_fields.append((field_name, field_value))

        data['custom'] = "\n".join([u"%s : %s" % v for v in custom_fields])

        # Add metadata if enabled  # ICP for retrocompatibility
        if request.env['ir.config_parameter'].sudo().get_param('website_form_enable_metadata'):
            environ = request.httprequest.headers.environ
            data['meta'] += "%s : %s\n%s : %s\n%s : %s\n%s : %s\n" % (
                "IP", environ.get("REMOTE_ADDR"),
                "USER_AGENT", environ.get("HTTP_USER_AGENT"),
                "ACCEPT_LANGUAGE", environ.get("HTTP_ACCEPT_LANGUAGE"),
                "REFERER", environ.get("HTTP_REFERER")
            )

        # This function can be defined on any model to provide
        # a model-specific filtering of the record values
        # Example:
        # def website_form_input_filter(self, values):
        #     values['name'] = '%s\'s Application' % values['partner_name']
        #     return values
        if hasattr(dest_model, "website_form_input_filter"):
            data['record'] = dest_model.website_form_input_filter(request, data['record'])

        missing_required_fields = [label for label, field in authorized_fields.items() if field['required'] and label not in data['record']]
        if any(error_fields):
            raise ValidationError(error_fields + missing_required_fields)

        return data

    def insert_record(self, request, model, values, custom, meta=None):
        model_name = model.sudo().model
        if model_name == 'mail.mail':
            email_from = _('"%s form submission" <%s>') % (request.env.company.name, request.env.company.email)
            values.update({'reply_to': values.get('email_from'), 'email_from': email_from})
        record = request.env[model_name].with_user(SUPERUSER_ID).with_context(
            mail_create_nosubscribe=True,
        ).create(values)
        if custom or meta:
            _custom_label = "%s\n___________\n\n" % _("Other Information:")  # Title for custom fields
            if model_name == 'mail.mail':
                _custom_label = "%s\n___________\n\n" % _("This message has been posted on your website!")
            default_field = model.website_form_default_field_id
            default_field_data = values.get(default_field.name, '')
            custom_content = (default_field_data + "\n\n" if default_field_data else '') \
                + (_custom_label + custom + "\n\n" if custom else '') \
                + (self._meta_label + "\n________\n\n" + meta if meta else '')

            # If there is a default field configured for this model, use it.
            # If there isn't, put the custom data in a message instead
            if default_field.name:
                if default_field.ttype == 'html' or model_name == 'mail.mail':
                    custom_content = nl2br_enclose(custom_content)
                record.update({default_field.name: custom_content})
            elif hasattr(record, '_message_log'):
                record._message_log(
                    body=nl2br_enclose(custom_content, 'p'),
                    message_type='comment',
                )

        return record.id

    # Link all files attached on the form
    def insert_attachment(self, model, id_record, files):
        orphan_attachment_ids = []
        model_name = model.sudo().model
        record = model.env[model_name].browse(id_record)
        authorized_fields = model.with_user(SUPERUSER_ID)._get_form_writable_fields()
        for file in files:
            custom_field = file.field_name not in authorized_fields
            attachment_value = {
                'name': file.filename,
                'datas': base64.encodebytes(file.read()),
                'res_model': model_name,
                'res_id': record.id,
            }
            attachment_id = request.env['ir.attachment'].sudo().create(attachment_value)
            if attachment_id and not custom_field:
                record_sudo = record.sudo()
                value = [(4, attachment_id.id)]
                if record_sudo._fields[file.field_name].type == 'many2one':
                    value = attachment_id.id
                record_sudo[file.field_name] = value
            else:
                orphan_attachment_ids.append(attachment_id.id)

        if model_name != 'mail.mail' and hasattr(record, '_message_log') and orphan_attachment_ids:
            # If some attachments didn't match a field on the model,
            # we create a mail.message to link them to the record
            record._message_log(
                attachment_ids=[(6, 0, orphan_attachment_ids)],
                body=Markup(_('<p>Attached files: </p>')),
                message_type='comment',
            )
        elif model_name == 'mail.mail' and orphan_attachment_ids:
            # If the model is mail.mail then we have no other choice but to
            # attach the custom binary field files on the attachment_ids field.
            for attachment_id_id in orphan_attachment_ids:
                record.attachment_ids = [(4, attachment_id_id)]
