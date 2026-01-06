# -*- coding: utf-8 -*-
#############################################################################
#
#    Hundred Solutions
#
#    Copyright (C) 2023-TODAY Hundred Solutions(<https://www.hundredsolutions.com/>)
#    Author: Arjun Baidya (arjun.b@hundredsolutions.com)
#
#    You can modify it under the terms of the GNU AFFERO
#    GENERAL PUBLIC LICENSE (AGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU AFFERO GENERAL PUBLIC LICENSE (AGPL v3) for more details.
#
#    You should have received a copy of the GNU AFFERO GENERAL PUBLIC LICENSE
#    (AGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################

{
    'name': 'Customer Queue',
    'version': '16.0.1.0.0',
    'summary': """Manage your customer by smart app""",
    'author': "Hundred Solutions",
    'maintainer': 'Hundred Solutions',
    'company': "Hundred Solutions",
    'website': 'https://www.hundredsolutions.com/',
    'category': 'Industries',
    'description': """
    Helps You To manage customer support.
    """,
    'depends': [
        'base',
        'hr',
        'contacts',
        'mail',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'data/demo_data.xml',
        'views/token_create.xml',
        'views/counter_create.xml',
        'wizard/services.xml',
        'views/token_screen.xml',
        # 'wizard/token_screen.xml',
        'views/menu.xml',
        'views/web_view.xml',
        'data/cron.xml',

    ],
    'images': ['static/description/banner.png'],
    'license': 'AGPL-3',
    'installable': True,
    'application': True,
}
