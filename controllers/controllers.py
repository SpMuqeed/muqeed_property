import logging
import random
import string
import base64
from odoo.http import request

from odoo import http
from odoo.addons.website.controllers.main import Website

_logger = logging.getLogger(__name__)


class PropertyResale(http.Controller):
    @http.route('/', auth='public', website=True)
    def property_resale_page(self):
        properties = request.env['my.property'].sudo().search([])

        return request.render('muqeed_property.property_resale_template',
                              {
                                  'properties': properties
                              })


# class PropertyController(http.Controller):
#     @http.route('/', auth='public', website=True)
#     def properties(self, **kwargs):
#         _logger.info(f"🔍 Received Filters: {kwargs}")  # Debugging line
#
#         name = kwargs.get('name', '').strip()
#         property_type = kwargs.get('property_type', '').strip()
#
#         # Define domain for filtering
#         domain = []
#
#         if name:
#             domain.append(('name', 'ilike', name))  # Case-insensitive search
#
#         if property_type in ['vacant_land', 'villa', 'house', 'commercial_space']:
#             domain.append(('property_type', '=', property_type))
#
#         _logger.info(f"🧐 Applying Domain Filter: {domain}")  # Debugging line
#
#         # Fetch properties based on filters
#         properties = request.env['my.property'].sudo().search(domain)
#
#         _logger.info(f"🏠 Found {len(properties)} properties")  # Debugging line
#
#         return request.render('muqeed_property.property_resale_template', {
#             'properties': properties,
#             'selected_name': name,
#             'selected_property_type': property_type,
#         })

class Properties(http.Controller):
    @http.route('/properties', auth='public', website=True)
    def properties(self, sales=None, prop=None, min=None, max=None, minArea=None, maxArea=None, **kwargs):
        # Default filter values
        sales_filter = sales if sales in ['sale', 'rent'] else 'all'
        prop_filter = prop if prop in ['vacant_land', 'villa', 'house', 'commercial_space'] else 'all'

        # Build the domain for filtering properties
        domain = []

        # Sales type filter
        if sales_filter != 'all':
            domain.append(('sales_type', '=', sales_filter))

        # Property type filter
        if prop_filter != 'all':
            domain.append(('property_type', '=', prop_filter))

        # Price range filter
        if min and min.isdigit():
            domain.append(('amount', '>=', float(min)))
        if max and max.isdigit():
            domain.append(('amount', '<=', float(max)))

        # Area range filter
        if minArea and minArea.isdigit():
            domain.append(('property_area', '>=', float(minArea)))
        if maxArea and maxArea.isdigit():
            domain.append(('property_area', '<=', float(maxArea)))

        # Search for properties based on the constructed domain
        properties = request.env['my.property'].sudo().search(domain)

        # Pass data to the template
        return request.render('muqeed_property.my_property_template', {
            'properties': properties,
            'selected_sales_type': sales_filter,
            'selected_property_type': prop_filter,
            'min_price': min,
            'max_price': max,
            'min_area': minArea,
            'max_area': maxArea,
        })

    class PropertyController(http.Controller):
        @http.route(['/properties'], type='http', auth='public', website=True)
        def properties(self, page=1, **kwargs):
            Property = request.env['my.property'].sudo()
            per_page = 6  # Number of properties per page
            offset = (int(page) - 1) * per_page
            total_properties = Property.search_count([])

            properties = Property.search([], limit=per_page, offset=offset)

            total_pages = (total_properties // per_page) + (1 if total_properties % per_page > 0 else 0)

            return request.render('muqeed_property.my_property_template', {
                'properties': properties,
                'page': int(page),
                'total_pages': total_pages
            })


class PropertyDetailController(http.Controller):
    @http.route('/property/detail/<int:property_id>', auth='public', website=True)
    def property_detail(self, property_id, **kwargs):
        properties = request.env['my.property'].sudo().search([])
        property = request.env['my.property'].sudo().browse(property_id)
        if not property:
            return request.not_found()

        return request.render('muqeed_property.property_detail_template', {
            'property': property,
            'properties': properties
        })


class PropertyController(http.Controller):

    @http.route('/properties/rent', type='http', auth='public', website=True)
    def properties_rent(self, **kwargs):
        properties = request.env['my.property'].search([('sales_type', '=', 'rent')])
        return request.render('muqeed_property.my_property_template', {
            'properties': properties,
            'filter_type': 'rent'
        })

    @http.route('/properties/sale', type='http', auth='public', website=True)
    def properties_sale(self, **kwargs):
        properties = request.env['my.property'].search([('sales_type', '=', 'sale')])
        return request.render('muqeed_property.my_property_template', {
            'properties': properties,
            'filter_type': 'sale'
        })

    @http.route('/properties/max_amount', type='json', auth='public')
    def get_max_amount(self):
        max_amount = request.env['my.property'].sudo().search([], limit=1, order='amount desc').amount
        return {'max_amount': max_amount or 0}


class MyPropertyController(http.Controller):

    @http.route('/properties/type/<string:property_type>', type='http', auth='public', website=True)
    def properties_by_type(self, property_type, **kwargs):
        if property_type == 'all':
            properties = request.env['my.property'].search([])
        else:
            properties = request.env['my.property'].search([('property_type', '=', property_type)])

        return request.render('muqeed_property.my_property_template', {
            'properties': properties,
            'selected_property_type': property_type  # Pass the selected property type
        })


class ContactUs(http.Controller):

    @http.route('/contact', type='http', auth='public', website=True)
    def contact_us(self, **kwargs):
        return request.render('muqeed_property.contact_us_template')

    @http.route('/contact/thanks', type='http', auth='public', website=True)
    def thanks_page(self, **kwargs):
        return request.render('muqeed_property.thanks_template')

    @http.route('/contact/submit', type='http', auth='public', website=True, csrf=False)
    def submit_contact(self, **kwargs):
        # Process form data
        name = kwargs.get('name')
        phone = kwargs.get('phone')
        email = kwargs.get('email')
        message = kwargs.get('message')

        # Save the data to the `contact.us.message` model
        request.env['contact.us.message'].sudo().create({
            'name': name,
            'phone': phone,
            'email': email,
            'message': message,
        })

        return request.redirect('/contact/thanks')


class PropertyController1(http.Controller):
    @http.route('/properties/map', type='http', auth='public', website=True)
    def property_map(self, property_id=None):
        properties = request.env['my.property'].sudo().search([])
        selected_property = None
        if property_id:
            selected_property = request.env['my.property'].sudo().browse(int(property_id))
            if not selected_property.exist():
                selected_property = None

        return request.render('muqeed_property.property_detail_template', {
            'properties': properties,
            'selected_property': selected_property,
        })


# class PropertyInterest(http.Controller):
#     @http.route('/property_interest/submit', type='http', auth='public', methods=['POST'], csrf=True)
#     def submit_interest(self, **post):
#         request.env['property.interested.message'].create({
#             'name': post.get('name'),
#             'phone': post.get('phone'),
#             'email': post.get('email'),
#             'property_id': post.get('property_id'),
#             'message': post.get('message'),
#         })
#         return request.redirect('/contact/thanks')


class PropertyInterest(http.Controller):
    @http.route('/property_interest/submit', type='http', auth='public', methods=['POST'], csrf=True)
    def submit_interest(self, **post):
        try:
            # Debugging: Print received data
            print("Received Data:", post)

            # Extract data
            name = post.get('name', '').strip()
            phone = post.get('phone', '').strip()
            email = post.get('email', '').strip()
            property_name = post.get('property_id', '').strip()
            message = post.get('message', '').strip()

            # Ensure required fields are present
            if not name or not email or not property_name:
                return "Error: Name, Email, and Property Name are required."

            # Create CRM Lead
            lead = request.env['crm.lead'].sudo().create({
                'name': f'Interest in {property_name}',  # Lead title
                'partner_name': name,
                'contact_name': name,
                'phone': phone,
                'email_from': email,
                'description': message,
            })

            # Ensure only one lead is returned
            lead.ensure_one()  # This prevents the multiple record error

            return request.redirect('/contact/thanks')

        except Exception as e:
            return f"Error: {str(e)}"


class PropertyController(Website):

    @http.route('/academy/academy', auth='public', website=True)
    def index(self, property_type='', search='', **kwargs):
        # Create domain for filtering properties
        domain = []

        if property_type:
            domain.append(('property_type', '=', property_type))
        if search:
            domain.append(('name', 'ilike', search))  # Search by property name

        # Fetch the filtered properties
        properties = request.env['my.property'].search(domain)

        # Prepare the data for returning via AJAX
        property_data = []
        for property in properties:
            property_data.append({
                'name': property.name,
                'description': property.description,
                'property_type': property.property_type,
                'image_url': property.image_ids[0].url if property.image_ids else '',  # Handle property image URL
            })

        # Return the filtered properties as JSON
        return request.make_response({
            'properties': property_data
        }, content_type='application/json')


class AgentRegistration(http.Controller):

    @http.route('/agent/submit_registration', type='http', auth='public', website=True, csrf=True)
    def agent_registration(self, **kwargs):
        name = kwargs.get('name')
        phone = kwargs.get('phone')
        email = kwargs.get('email')
        message = kwargs.get('message')

        # Ensure email is unique
        existing_user = request.env['res.users'].sudo().search([('login', '=', email)], limit=10)
        if existing_user:
            return request.render("muqeed_property.template_error", {'error_message': "Email already exists!"})

        # Generate a random password
        password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))

        # Create a new user (agent)
        user_vals = {
            'name': name,
            'login': email,
            'email': email,
            'phone': phone,
            'password': password,  # Store the generated password securely
            'company_id': request.env.company.id,
            'groups_id': [(6, 0, [request.env.ref('base.group_user').id])]  # Assign to the 'Internal User' group
        }
        new_user = request.env['res.users'].sudo().create(user_vals)

        # Send an email with login credentials (Optional)
        template = request.env.ref('muqeed_property.agent_welcome_email_template')
        template.sudo().send_mail(new_user.id, force_send=True)

        # Redirect to a success page
        return request.render("muqeed_property.registration_success",
                              {'agent_name': name, 'email': email, 'password': password})





class AgentProfileController(http.Controller):

    @http.route('/agent/profile', type='http', auth='user', website=True)
    def agent_profile(self, **kwargs):
        user = request.env.user
        properties = request.env['my.property'].search([('owner_id', '=', user.id)])

        values = {
            'name': user.partner_id.name,
            'email': user.partner_id.email,
            'phone': user.partner_id.phone,
            'image_url': f"/web/image/res.users/{user.id}/image_1920",
            'properties': properties,
        }

        return request.render('muqeed_property.agent_profile_template', values)

    class AgentProfileController(http.Controller):

        @http.route('/agent/profile/update', type='http', auth='user', website=True, csrf=False)
        def update_agent_profile(self, **post):
            user = request.env.user  # Get the logged-in user

            # Check if an image is uploaded
            if 'profile_image' in request.httprequest.files:
                file = request.httprequest.files['profile_image']
                image_data = file.read()  # Read the file content

                # Convert image to base64 (Odoo stores images in base64 format)
                encoded_image = base64.b64encode(image_data)

                # Update the user's profile image
                user.write({'image_1920': encoded_image})

            return request.redirect('/agent/profile')






class PropertyController(http.Controller):
    @http.route('/submit/property', type='http', auth='public', website=True, methods=['POST'], csrf=False)
    def submit_property(self, **post):
        # Extract values from the form
        property_vals = {
            'name': post.get('name'),
            'description': post.get('description'),
            'property_type': post.get('property_type'),
            'sales_type': post.get('sales_type'),
            'amount': post.get('amount'),
            'city': post.get('city'),
            'address': post.get('address'),
            'latitude': post.get('lat'),
            'longitude': post.get('long'),
            'bedrooms': post.get('bedrooms'),
            'bathrooms': post.get('bathrooms'),
            'balcony': post.get('balcony'),
            'video_file': post.get('video'),
            'property_area': post.get('area')
        }

        # Handle features (Many2many relation)
        feature_names = request.httprequest.form.getlist('features')
        feature_ids = []
        feature_icon_mapping = {
            'wifi': 'fa-wifi',
            'parking': 'fa-car',
            'pool': 'fa-swimming-pool',
            'security': 'fa-shield-alt'
        }

        for feature_name in feature_names:
            existing_feature = request.env['property.features'].sudo().search([('name', '=', feature_name)], limit=1)
            if existing_feature:
                feature_ids.append(existing_feature.id)
            elif feature_name in feature_icon_mapping:
                new_feature = request.env['property.features'].sudo().create({
                    'name': feature_name,
                    'icon': feature_icon_mapping[feature_name],
                    'color': '#FF5722',
                })
                feature_ids.append(new_feature.id)

        if feature_ids:
            property_vals['features_ids'] = [(6, 0, feature_ids)]

        # Create property record
        property_record = request.env['my.property'].sudo().create(property_vals)

        # Handle image uploads
        image_files = request.httprequest.files.getlist('image_ids[]')
        image_ids = []

        for image in image_files:
            if image and image.filename:
                image_data = base64.b64encode(image.read()).decode('utf-8')  # Proper base64 encoding
                attachment = request.env['ir.attachment'].sudo().create({
                    'name': image.filename,
                    'datas': image_data,
                    'res_model': 'my.property',
                    'res_id': property_record.id,
                    'mimetype': image.mimetype
                })
                image_ids.append(attachment.id)

        if image_ids:
            property_record.sudo().write({'image_ids': [(6, 0, image_ids)]})

        return request.render('muqeed_property.property_submission_success')
