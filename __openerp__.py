# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright :
#        (c) 2015 Endika Iglesias <endika2@gmail.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    "name": "Digital Ocean integration",
    "version": "0.1",
    'author': 'Endika Iglesias',
    'maintainer': 'Endika Iglesias',
    'website': 'http://www.endikaiglesias.com',
    'license': 'AGPL-3',
    "category": "Connector",
    "description": """
Digital Ocean Integration
=====================
Synchronize your droplet whith Odoo
TODO: create, modify and delete droplets
    """,
    "depends": ['project'],
    'external_dependencies': {
        'python': ['digitalocean'],
    },
    "data": [
        "views/digital_droplet_view.xml",
        "views/project_project_view.xml",
        "views/res_config_view.xml",
        "views/digital_cron.xml",
        "security/ir.model.access.csv",
    ],
    "installable": True,
}
