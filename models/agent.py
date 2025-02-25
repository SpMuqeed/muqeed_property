import logging
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import re
from datetime import datetime, timedelta

_logger = logging.getLogger(__name__)

class AgentInfo(models.Model):
    _name = "agent.details"
    _description = "Agent Details"

    name = fields.Char(string="Name", required=True)
    email = fields.Char(string="Email", required=True)
    phone = fields.Char(string="Mobile Number")
    email_verified = fields.Boolean(string="Email Verified", default=False)

    def _send_verification_email(self):
        for record in self:
            if not self._is_valid_email(record.email):
                raise ValidationError(_('Invalid email address'))

            # Create a verification link
            base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
            verification_link = f'{base_url}/verify_email?email={record.email}'

            # Log the message for testing (optional)
            _logger.info("Verification email should be sent to %s with link: %s", record.email, verification_link)

            # Retrieve the email template from the module
            template = self.env.ref('muqeed_property.email_template_verification')

            # Replace the placeholder in the email body with the actual verification link
            email_body = template.body_html.replace('${verification_link}', verification_link)

            # Prepare email values
            email_values = {
                'subject': template.subject,
                'body_html': email_body,
                'email_from': template.email_from,
                'email_to': record.email,
                'auto_delete': False,
                'mail_server_id': template.mail_server_id.id if template.mail_server_id else False,
                'model': self._name,
                'res_id': record.id,
                'scheduled_date': datetime.now() + timedelta(minutes=1),  # Schedule to send after 1 minute
            }

            # Create a mail.mail record
            mail = self.env['mail.mail'].create(email_values)
            mail.send()

    def _is_valid_email(self, email):
        email_regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        return re.match(email_regex, email) is not None

    @api.model
    def create(self, vals):
        record = super(AgentInfo, self).create(vals)
        record._send_verification_email()
        return record

    def action_verify_email(self):
        self._send_verification_email()

    def verify_email(self):
        self.write({'email_verified': True})
        return {
            'type': 'ir.actions.act_url',
            'url': '/web#action=home',
            'target': 'self'
        }


