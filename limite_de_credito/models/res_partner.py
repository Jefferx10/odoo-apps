from odoo import models, fields, api, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    monto_limite_credito = fields.Monetary(store=True, string='Limite de crédito')