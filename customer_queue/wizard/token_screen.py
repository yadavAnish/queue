from odoo import fields, models, api, SUPERUSER_ID


class TokenScreen(models.TransientModel):
    _name = 'token.show'
    _description = "Token number show"

    token_number = fields.Char(string="Token Number")

    # default = "TOKEN001"

