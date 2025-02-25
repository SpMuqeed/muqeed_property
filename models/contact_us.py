from odoo import models, fields, api

class ContactUsMessage(models.Model):
    _name = 'contact.us.message'
    _description = 'Contact Us Messages'
    _rec_name = 'name'

    name = fields.Char(string='Name', required=True)
    phone = fields.Char(string='Phone Number', required=True)
    email = fields.Char(string='Email Address', required=True)
    message = fields.Text(string='Message', required=True)
    submission_date = fields.Datetime(string='Submission Date', default=fields.Datetime.now, readonly=True)
