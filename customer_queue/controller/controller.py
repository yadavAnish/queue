from odoo import http

class CustomerQueue(http.Controller):

    @http.route('/token/generate/', website=True ,auth='public')
    def index(self, **kw):
        return http.request.render("customer_queue.web_customer_queue",{})