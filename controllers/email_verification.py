import logging
from odoo import http, _
from odoo.http import request

_logger = logging.getLogger(__name__)

class AgentController(http.Controller):
    @http.route('/agent/submit_registration', type='http', auth="public", methods=['POST'], csrf=True)
    def submit_registration(self, **post):
        _logger.info("Processing agent registration with data: %s", post)
        name = post.get('name')
        email = post.get('email')
        phone = post.get('phone')

        if not name or not email or not phone:
            _logger.error("Missing required fields for agent registration.")
            return request.render('muqeed_property.registration_failed')

        if not request.env['agent.details']._is_valid_email(email):
            _logger.error("Invalid email provided: %s", email)
            return request.render('muqeed_property.invalid_email')

        existing_agent = request.env['agent.details'].sudo().search([('email', '=', email)])
        if existing_agent:
            _logger.error("Email already used: %s", email)
            return request.render('muqeed_property.email_already_used')

        agent = request.env['agent.details'].sudo().create({
            'name': name,
            'email': email,
            'phone': phone,
        })
        _logger.info("Agent created successfully: %s", agent.name)

        # Send verification email
        agent._send_verification_email()
        return request.render('muqeed_property.registration_successful', {'email': email})

    @http.route('/agent/registration', type='http', auth='public', website=True)
    def display_agent_registration_form(self, **kwargs):
        return request.render("muqeed_property.agent_registration_form_template1")

    @http.route('/verify_email', type='http', auth="public")
    def verify_email(self, email, **kwargs):
        agents = request.env['agent.details'].sudo().search([('email', '=', email)])
        if not agents:
            return request.render('muqeed_property.email_verification_failed')

        for agent in agents:
            if agent.email_verified:
                return request.render('muqeed_property.email_already_verified')
            agent.verify_email()

        return request.render('muqeed_property.email_verification_success')
