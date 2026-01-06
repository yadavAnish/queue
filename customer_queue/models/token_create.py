from odoo import fields, api, models, _


class TokenCreate(models.Model):
    _name = 'token.token'

    name = fields.Char(string="TOKEN", required=True, copy=False, randomly=True, index=True,
                       default=lambda self: _('New'))
    customer_name = fields.Char(string="Customer Name")
    customer_mobile = fields.Integer(string="Mobile")
    department = fields.Many2one('hr.department', string="Department")
    service_done = fields.Boolean(default=False, string="Service Done?")

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('customer.sequence') or _('New')
        result = super(TokenCreate, self).create(vals)
        return result
