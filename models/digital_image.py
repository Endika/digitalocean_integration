# -*- coding: utf-8 -*-
##############################################################################
#
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

import digitalocean
from openerp import models, fields, api
from openerp.osv import osv
from openerp.tools.translate import _


class DigitalImage(models.Model):
    _name = "digital.image"

    name = fields.Char("Name", size=100, required=True, readonly=True)
    sort_name = fields.Char(
        "Sort name", size=100, required=True)
    code = fields.Char("ID", size=100, required=True, readonly=True)
    slug = fields.Char("Slug", size=50, required=False, readonly=True)
    distribution = fields.Char(
        "Distribution", size=100, required=True, readonly=True)
    date = fields.Datetime('Create', readonly=True, required=True)
    public = fields.Boolean(
        'Public', default=False, readonly=True, help="Is public Image.")

    def _token(self):
        config_pool = self.env['ir.config_parameter']
        token = config_pool.get_param('digital_droplet.token', default=False)
        if token is False or len(token) <= 0:
            return False
        return token

    def on_change_name(self, vals):
        token = self._token()
        if token is False:
            return False
        try:
            manager = digitalocean.Manager(token=token)
            image = manager.get_image(self.code)
            image.rename(vals['sort_name'])
        except Exception, e:
            raise osv.except_osv(_('Error!'), _("Cannot rename image: "
                                                "%s" % (e)))

    @api.multi
    def write(self, vals):
        if vals.get('sort_name') and self.code:
            self.on_change_name(vals)
            vals['name'] = self.distribution + '/' + vals['sort_name']
        return super(DigitalImage, self).write(vals)
