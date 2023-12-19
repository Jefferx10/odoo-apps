from odoo import models, fields, api, _
from odoo.exceptions import UserError


class SaleOrder(models.Model):
   _inherit = 'sale.order'

   tipo_de_pago = fields.Selection([('efectivo', 'Efectivo'),('transferencia', 'Transferencia'),('credito', 'Crédito')], store=True, string='Tipo de pago')
   pie_de_pago = fields.Monetary(string='Pie de pago')
   monto_de_credito_cliente = fields.Monetary(related='partner_id.monto_limite_credito', readonly=True)
   monto_utilizado = fields.Monetary(compute='compute_partner_limite_credito', store=True, string='Monto utilizado')
   monto_adeudado = fields.Monetary(related='partner_id.credit', readonly=True)
   monto_adeudado_vencido = fields.Monetary(related='partner_id.total_overdue', readonly=True)
   
   @api.depends('monto_utilizado','monto_adeudado','amount_total','pie_de_pago')
   def compute_partner_limite_credito(self):
      for record in self:
         record.monto_utilizado =  record.monto_adeudado + record.amount_total - record.pie_de_pago
    
   def action_confirm(self):
      result = super(SaleOrder, self).action_confirm()
      for record in self:
         if self.env['ir.config_parameter'].sudo().get_param('limite_de_credito.permitir_credito'):
            if record.monto_utilizado > record.monto_de_credito_cliente and record.monto_de_credito_cliente !=0:
               raise UserError("El cliente ya excedió su límite de crédito")
            elif record.monto_adeudado_vencido > 0:
               raise UserError("El cliente tiene un monto adeudado vencido")
      return result
   