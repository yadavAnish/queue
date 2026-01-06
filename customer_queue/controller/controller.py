from odoo import http, fields
from odoo.http import request
import json
import logging

_logger = logging.getLogger(__name__)

class CustomerQueue(http.Controller):

    @http.route('/api/patient/register', type='http', auth='public', methods=['POST'], csrf=False)
    def register_patient(self, **kwargs):
        try:
            # Read raw JSON data
            data = json.loads(request.httprequest.data.decode('utf-8'))
            _logger.info(f"Received patient registration data: {data}")

            # Validate required fields
            if not data.get('name') or not data.get('phone'):
                return request.make_response(
                    json.dumps({'success': False, 'error': 'Missing required field: name or phone'}),
                    headers=[('Content-Type', 'application/json')],
                    status=400
                )

            # Check if phone already registered today
            existing = request.env['patient.queue'].sudo().search([
                ('phone', '=', data['phone']),
                ('registration_date', '>=', fields.Date.today())
            ], limit=1)
            if existing:
                return request.make_response(
                    json.dumps({'success': False, 'error': 'Phone number already registered today'}),
                    headers=[('Content-Type', 'application/json')],
                    status=400
                )

            # Create patient
            patient = request.env['patient.queue'].sudo().create({
                'name': data['name'],
                'phone': data['phone'],
                'email': data.get('email', ''),
            })
            _logger.info(f"Patient created: {patient.name}, Token: {patient.token_number}")

            # Return REST-style JSON response
            return request.make_response(
                json.dumps({
                    'success': True,
                    'data': {
                        'token_number': patient.token_number,
                        'counter_number': patient.counter_id.counter_number if patient.counter_id else None,
                        'position': patient.position,
                        'message': 'Patient registered successfully'
                    }
                }),
                headers=[('Content-Type', 'application/json')],
                status=201  # Created
            )

        except Exception as e:
            _logger.exception("Error in patient registration")
            return request.make_response(
                json.dumps({'success': False, 'error': str(e)}),
                headers=[('Content-Type', 'application/json')],
                status=500
            )


    # --------------------------
    # Get Patient Status by Token
    # --------------------------
    @http.route('/api/patient/status/<string:token>', type='http', auth='public', methods=['GET'], csrf=False)
    def get_patient_status(self, token, **kwargs):
        patient = request.env['patient.queue'].sudo().search([
            ('token_number', '=', token)
        ], limit=1)

        if not patient:
            return request.make_response(
                json.dumps({'success': False, 'error': 'Invalid token number'}),
                headers=[('Content-Type', 'application/json')]
            )

        return request.make_response(
            json.dumps({
                'success': True,
                'data': {
                    'token_number': patient.token_number,
                    'name': patient.name,
                    'counter_number': patient.counter_id.counter_number if patient.counter_id else None,
                    'position': patient.position,
                    'status': patient.state,
                    'registration_time': patient.registration_date.strftime('%Y-%m-%d %H:%M:%S')
                }
            }),
            headers=[('Content-Type', 'application/json')]
        )

    # --------------------------
    # Call Next Patient
    # --------------------------
    @http.route('/api/counter/next', type='http', auth='user', methods=['POST'], csrf=False)
    def call_next_patient(self, **kwargs):
        try:
            data = json.loads(request.httprequest.data)
        except Exception:
            return request.make_response(
                json.dumps({'success': False, 'error': 'Invalid JSON'}),
                headers=[('Content-Type', 'application/json')]
            )

        counter_id = data.get('counter_id')
        if not counter_id:
            return request.make_response(
                json.dumps({'success': False, 'error': 'Counter ID required'}),
                headers=[('Content-Type', 'application/json')]
            )

        next_patient = request.env['patient.queue'].sudo().search([
            ('counter_id', '=', counter_id),
            ('state', '=', 'waiting')
        ], order='id asc', limit=1)

        if not next_patient:
            return request.make_response(
                json.dumps({'success': False, 'error': 'No patients waiting'}),
                headers=[('Content-Type', 'application/json')]
            )

        # Call patient (custom method in model)
        next_patient.action_call_patient()

        return request.make_response(
            json.dumps({
                'success': True,
                'data': {
                    'token_number': next_patient.token_number,
                    'name': next_patient.name,
                    'phone': next_patient.phone
                }
            }),
            headers=[('Content-Type', 'application/json')]
        )

    # --------------------------
    # Get Active Counters
    # --------------------------
    @http.route('/api/counters', type='http', auth='public', methods=['GET'], csrf=False)
    def get_counters(self, **kwargs):
        counters = request.env['patient.counter'].sudo().search([
            ('active', '=', True)
        ])

        counter_list = [{
            'id': counter.id,
            'name': counter.name,
            'counter_number': counter.counter_number,
            'waiting_count': counter.waiting_count
        } for counter in counters]

        return request.make_response(
            json.dumps({'success': True, 'data': counter_list}),
            headers=[('Content-Type', 'application/json')]
        )
