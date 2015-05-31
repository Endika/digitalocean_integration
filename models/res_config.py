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

from openerp import models, fields, api


class DigitalConfigSettings(models.TransientModel):
    _name = 'digital.config.settings'
    _inherit = 'res.config.settings'

    token = fields.Char('Token')

    @api.multi
    def get_default_token(self):
        conf_par = self.env['ir.config_parameter']
        token = conf_par.get_param('digital_droplet.token', default="")

        return {'token': token}

    @api.multi
    def set_token(self):
        conf_par = self.env['ir.config_parameter']
        conf_par.set_param('digital_droplet.token', self.token)
