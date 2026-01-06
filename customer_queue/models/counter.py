from odoo import models, fields, api
from datetime import datetime
class PatientCounter(models.Model):
    _name = 'patient.counter'
    _description = 'Service Counter'

    name = fields.Char(string='Counter Name', required=True)
    counter_number = fields.Integer(string='Counter Number', required=True)
    active = fields.Boolean(string='Active', default=True)
    employee_id = fields.Many2one('res.users', string='Assigned Employee')
    queue_ids = fields.One2many('patient.queue', 'counter_id', string='Queue')
    current_serving = fields.Many2one('patient.queue', string='Currently Serving', 
                                     compute='_compute_current_serving')
    waiting_count = fields.Integer(string='Waiting Count', compute='_compute_waiting_count')

    @api.depends('queue_ids.state')
    def _compute_current_serving(self):
        for record in self:
            serving = record.queue_ids.filtered(lambda q: q.state == 'serving')
            record.current_serving = serving[0] if serving else False

    @api.depends('queue_ids.state')
    def _compute_waiting_count(self):
        for record in self:
            record.waiting_count = len(record.queue_ids.filtered(
                lambda q: q.state in ['waiting', 'called']
            ))
