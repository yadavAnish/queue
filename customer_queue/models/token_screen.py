
from odoo import fields, models, api
# from selenium import webdriver
# import time
# from  selenium.webdriver.chrome.service import Service


class TokenScreen(models.Model):
    _name = 'token.show'
    _description = "Token number show"

    token_number = fields.Char(string="Token Number")

    # default = "TOKEN001"

    @api.model
    def cron_start(self):
        print("hello")
        # browser = webdriver.Chrome()
        # browser.get('https://chat.openai.com/chat/d14430ac-bbea-4c90-a84c-b2d6a5b090c9')
        # time.sleep(5)
        # browser.refresh()
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }
