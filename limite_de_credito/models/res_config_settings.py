from odoo import models, fields, api, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    permitir_credito = fields.Boolean(string="Limite de crédito")

    def set_values(self):
        super(ResConfigSettings, self).set_values()

        self.env['ir.config_parameter'].set_param(
            'limite_de_credito.permitir_credito', self.permitir_credito)
        
    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        params = self.env['ir.config_parameter'].sudo()
        res.update(
            permitir_credito=params.get_param(
                'limite_de_credito.permitir_credito'),
        )
        return res