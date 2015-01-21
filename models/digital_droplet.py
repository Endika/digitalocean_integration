# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright :
#        (c) 2014 Antiun Ingenieria, SL (Madrid, Spain, http://www.antiun.com)
#                 Endika Iglesias <endikaig@antiun.com>
#                 Antonio Espinosa <antonioea@antiun.com>
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

from openerp.osv import orm, fields
import datetime
from openerp.tools.config import config
import digitalocean
import datetime


class digital_droplet(orm.Model):
    _name = "digital.droplet"
    _description = "Digital Ocean Droplet"
    _columns = {
        'name': fields.char("Subject email", size=200, readonly=True,
                            required=True),
        'email_id': fields.char("Mandrill internal id", size=200,
                                readonly=True,
                                required=True),
        'opens': fields.integer("Opens", size=10, default=0, readonly=True,
                                required=True),
        'clicks': fields.integer("Clicks", size=10, default=0, readonly=True,
                                 required=True),
        'from': fields.char("From", size=200, readonly=True, required=False),
        'to': fields.char("To", size=1000, readonly=True, required=False),
        'state': fields.char("State", size=50, readonly=True, required=False),
        'date': fields.datetime('Register date', readonly=True, required=True),
        'content': fields.char("Content", size=5000, readonly=True,
                               required=False),
    }

    def _token(self, cr, uid, ids, context=None):
        config_pool = self.pool.get('ir.config_parameter')
        token = config_pool.get_param(cr,
                                        uid,
                                        'digital_droplet.token',
                                        default=False,
                                        context=context)
        if token is False or len(token) <= 0:
            return False
        return token

    def call_cron_digital_update(self, cr, uid, context=None):
        token = self._api_key(cr, uid, [],
                                context=context)
        if token is False:
            return False
