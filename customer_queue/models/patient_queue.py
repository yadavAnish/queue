# models/patient_queue.py - COMPLETE FIXED VERSION
from odoo import models, fields, api
from datetime import datetime, timedelta
import logging      
_logger = logging.getLogger(__name__)

class PatientQueue(models.Model):
    _name = 'patient.queue'
    _description = 'Patient Queue Management'
    _order = 'registration_date asc, id asc'

    name = fields.Char(string='Patient Name', required=True)
    phone = fields.Char(string='Phone Number', required=True)
    email = fields.Char(string='Email')
    token_number = fields.Char(string='Token Number', readonly=True, copy=False)
    registration_date = fields.Datetime(string='Registration Date', default=fields.Datetime.now, readonly=True)
    counter_id = fields.Many2one('patient.counter', string='Assigned Counter')
    position = fields.Integer(string='Position in Queue', compute='_compute_position', store=False)
    state = fields.Selection([
        ('waiting', 'Waiting'),
        ('called', 'Called'),
        ('serving', 'Being Served'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='waiting', tracking=True)
    
    _sql_constraints = [
        ('unique_token', 'unique(token_number)', 'Token number must be unique!')
    ]

    @api.model
    def create(self, vals):
        # Generate token number safely
        if not vals.get('token_number'):
            for _ in range(5):  # try up to 5 times
                token = self.env['ir.sequence'].next_by_code('patient.queue.token')
                if not token:
                    token = f"TKN-{int(fields.Datetime.now().timestamp())}"
                # Ensure uniqueness in DB
                if not self.search([('token_number', '=', token)], limit=1):
                    vals['token_number'] = token
                    break
            else:
                # fallback unique timestamp
                vals['token_number'] = f"TKN-{int(fields.Datetime.now().timestamp())}"

        # Set registration date if not provided
        if not vals.get('registration_date'):
            vals['registration_date'] = fields.Datetime.now()

        # Assign to counter with smallest queue
        if not vals.get('counter_id'):
            counter = self._get_available_counter()
            if counter:
                vals['counter_id'] = counter.id

        record = super(PatientQueue, self).create(vals)
        _logger.info(f"Patient created: {record.name}, Token: {record.token_number}, Counter: {record.counter_id.name if record.counter_id else 'None'}")
        return record


    def write(self, vals):
        """Override write to recompute positions when state changes"""
        result = super(PatientQueue, self).write(vals)
        
        # If state changed, trigger recompute of positions for all waiting patients in same counter
        if 'state' in vals:
            for record in self:
                if record.counter_id:
                    waiting_patients = self.search([
                        ('counter_id', '=', record.counter_id.id),
                        ('state', '=', 'waiting')
                    ])
                    waiting_patients._compute_position()
        
        return result

    def _get_available_counter(self):
        """Get counter with smallest queue"""
        counters = self.env['patient.counter'].search([('active', '=', True)])
        if not counters:
            return None
        
        min_counter = None
        min_count = float('inf')
        
        for counter in counters:
            queue_count = self.search_count([
                ('counter_id', '=', counter.id),
                ('state', 'in', ['waiting', 'called'])
            ])
            if queue_count < min_count:
                min_count = queue_count
                min_counter = counter
        
        return min_counter

    @api.depends('counter_id', 'state', 'registration_date')
    def _compute_position(self):
        """Compute position in queue for waiting patients"""
        for record in self:
            # Reset position if not waiting or no counter assigned
            if record.state != 'waiting' or not record.counter_id:
                record.position = 0
                continue
            
            # Skip if record is not yet saved (NewId)
            if not record.id or isinstance(record.id, models.NewId):
                record.position = 0
                continue
            
            # Count patients who registered before this patient and are still waiting
            position = self.search_count([
                ('counter_id', '=', record.counter_id.id),
                ('state', '=', 'waiting'),
                ('registration_date', '<', record.registration_date)
            ]) + 1
            
            record.position = position

    def get_position_in_queue(self):
        """Alternative method to get position without computed field issues"""
        self.ensure_one()
        
        if self.state != 'waiting' or not self.counter_id:
            return 0
        
        if not self.id or isinstance(self.id, models.NewId):
            return 0
        
        position = self.search_count([
            ('counter_id', '=', self.counter_id.id),
            ('state', '=', 'waiting'),
            ('registration_date', '<', self.registration_date)
        ]) + 1
        
        return position

    def action_call_patient(self):
        """Call next patient in queue"""
        self.ensure_one()
        self.write({'state': 'called'})
        
        # You can add notification logic here
        # self._notify_patient()
        
        return True

    def action_serve_patient(self):
        """Start serving patient"""
        self.ensure_one()
        self.write({'state': 'serving'})
        return True

    def action_complete(self):
        """Complete service"""
        self.ensure_one()
        self.write({'state': 'completed'})
        return True

    def action_cancel(self):
        """Cancel patient"""
        self.ensure_one()
        self.write({'state': 'cancelled'})
        return True

    @api.model
    def _cron_cleanup_old_records(self):
        """Cron job to cleanup old completed/cancelled records"""
        # Delete records older than 7 days that are completed or cancelled
        cutoff_date = fields.Datetime.now() - timedelta(days=7)
        old_records = self.search([
            ('registration_date', '<', cutoff_date),
            ('state', 'in', ['completed', 'cancelled'])
        ])
        old_records.unlink()
        
    def check_duplicate_phone_today(self, phone):
        """Check if phone number already has an active token today"""
        today_start = fields.Datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        existing = self.search([
            ('phone', '=', phone),
            ('registration_date', '>=', today_start),
            ('state', 'in', ['waiting', 'called', 'serving'])
        ], limit=1)
        
        return existing