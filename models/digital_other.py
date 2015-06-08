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

from openerp import models, fields


class DigitalSize(models.Model):
    _name = "digital.size"

    name = fields.Char("Name", size=100, required=True, readonly=True)
    slug = fields.Char("Slug", size=50, required=True, readonly=True)
    memory = fields.Char("Memory", size=50, required=True, readonly=True)
    vcpus = fields.Char("CPU's", size=50, required=True, readonly=True)
    disk = fields.Char("Disk", size=50, required=True, readonly=True)
    transfer = fields.Char("Transfer", size=50, required=True, readonly=True)
    price_monthly = fields.Char(
        "Price per month", size=50, required=True, readonly=True)
    price_hourly = fields.Char(
        "Price per hour", size=50, required=True, readonly=True)


class DigitalRegion(models.Model):
    _name = "digital.region"

    name = fields.Char("Name", size=100, required=True, readonly=True)
    slug = fields.Char("Slug", size=50, required=True, readonly=True)
    available = fields.Boolean(
        'Available', default=False, required=True,
        readonly=True, help="Enable Backups.")


class DigitalLog(models.Model):
    _name = "digital.log"

    log_id = fields.Char(string="ID", size=100, required=True, readonly=True)
    droplet = fields.Many2one(
        comodel_name='digital.droplet', string='Droplet',
        required=True, readonly=True)
    status = fields.Char(string='Status', size=10, readonly=True)
    started_at = fields.Datetime(string='Started At', readonly=True)
    completed_at = fields.Datetime(string='Completed At', readonly=True)
    action_type = fields.Char(string='Type', size=10, readonly=True)


class DigitalNetwork(models.Model):
    _name = 'digital.network'

    droplet = fields.Many2one(
        comodel_name='digital.droplet', string='Droplet',
        required=True, readonly=True)
    version = fields.Char(string='Version', size=10, readonly=True)
    net_type = fields.Char(string='Type', size=10, readonly=True)
    netmask = fields.Char(string='Netmask', size=16, readonly=True)
    ip_address = fields.Char(string='IP address', size=16, readonly=True)
    gateway = fields.Char(string='Gateway', size=16, readonly=True)


class DigitalCategory(models.Model):
    _name = "digital.category"

    name = fields.Char(string='Name', required=True, translate=True)
