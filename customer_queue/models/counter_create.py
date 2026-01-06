from odoo import fields, api, models, _


class CounterCreate(models.Model):
    _name = 'counter.counter'

    name = fields.Char(string="COUNTER", required=True, copy=False, randomly=True, index=True,
                       default=lambda self: _('New'))
    counter_name = fields.Char(string="Counter Name")
    department_name = fields.Many2one('hr.department', string="Department")

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('counter.sequence') or _('New')
        result = super(CounterCreate, self).create(vals)
        return result
