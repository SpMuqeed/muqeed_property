from odoo import models, fields

class PropertyInterestedMessage(models.Model):
    _name = 'property.interested.message'
    _description = 'Property Interested Messages'
    _rec_name = 'name'

    name = fields.Char(string='Name', required=True)
    phone = fields.Char(string='Phone Number', required=True)
    email = fields.Char(string='Email Address', required=True)
    property_id = fields.Char( string='Property Name')
    message = fields.Text(string='Message', required=True)
    submission_date = fields.Datetime(string='Submission Date', default=fields.Datetime.now, readonly=True)


