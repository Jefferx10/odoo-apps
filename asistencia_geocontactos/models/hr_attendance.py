from odoo import fields, models

class HrAttendance(models.Model):
    _inherit = 'hr.attendance'

    contact_id = fields.Many2one('res.partner', string="Contacto")

    checkin_address = fields.Char(string='Dirección de entrada', store=True, help="Dirección de entrada del usuario")
    checkout_address = fields.Char(string='Dirección de salida', store=True, help="Dirección de salida del usuario")
    checkin_latitude = fields.Char(string='Latitud de entrada', store=True, help="Latitud de entrada del usuario")
    checkout_latitude = fields.Char(string='Latitud de salida', store=True, help="Latitud de salida del usuario")
    checkin_longitude = fields.Char(string='Longitud de entrada', store=True, help="Longitud de entrada del usuario")
    checkout_longitude = fields.Char(string='Longitud de salida', store=True, help="Longitud de salida del usuario")
    checkin_location = fields.Char(string='Link localización de entrada', store=True, help="Link localización de entrada del usuario")
    checkout_location = fields.Char(string='Link localización de salida', store=True, help="Link localización de salida del usuario")
