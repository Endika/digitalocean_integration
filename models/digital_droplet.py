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

import datetime
import digitalocean
from openerp import models, fields, api
from openerp.osv import osv
from openerp.tools.translate import _
from json import load
from urllib2 import urlopen

import logging
from pprint import pformat
_logger = logging.getLogger(__name__)


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


class DigitalImage(models.Model):
    _name = "digital.image"

    name = fields.Char("Name", size=100, required=True, readonly=True)
    sort_name = fields.Char(
        "Sort name", size=100, required=True, readonly=True)
    code = fields.Char("ID", size=100, required=True, readonly=True)
    slug = fields.Char("Slug", size=50, required=False, readonly=True)
    distribution = fields.Char(
        "Distribution", size=100, required=True, readonly=True)
    date = fields.Datetime('Create', readonly=True, required=True)
    public = fields.Boolean(
        'Public', default=False, readonly=True, help="Is public Image.")


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


class DigitalCategory(osv.osv):
    _name = "digital.category"

    name = fields.Char('Name', required=True, translate=True)


class DigitalDroplet(models.Model):
    _name = "digital.droplet"
    _description = "Digital Ocean Droplet"

    name = fields.Char("Server name", size=100, required=True)
    code = fields.Char("ID", size=100, readonly=True)
    region = fields.Many2one('digital.region', 'Region', required=False)
    size = fields.Many2one('digital.size', 'Size', required=False)
    size_vcpus = fields.Char(
        "CPU's", size=50, related='size.vcpus', readonly=True)
    size_disk = fields.Char(
        "Disk", size=50, related='size.disk', readonly=True)
    size_transfer = fields.Char(
        "Transfer", size=50, related='size.transfer', readonly=True)
    size_price_monthly = fields.Char(
        "Price per month", size=50, related='size.price_monthly',
        readonly=True)
    size_price_hourly = fields.Char(
        "Price per hour", size=50, related='size.price_hourly', readonly=True)
    image = fields.Many2one('digital.image', 'Image', required=False)
    backups = fields.Boolean(
        'Backups', default=False, required=False, help="Enable Backups.")
    status = fields.Char("Status", size=50, readonly=True)
    date = fields.Datetime('Created', readonly=True)
    kernel = fields.Char("Kernel", size=1000, readonly=True)
    logs_ids = fields.One2many(
        string="Logs", comodel_name='digital.log', inverse_name='droplet')
    network_ids = fields.One2many(
        string="Networks", comodel_name='digital.network',
        inverse_name='droplet')
    state = fields.Selection(
        selection=[('draft', 'Draft'),
                   ('power_on', 'Power ON'),
                   ('power_off', 'Power OFF'),
                   ('delete', 'Delete')],
        string='Status', default='draft', required=True)
    localhost = fields.Boolean(
        string='Current machine', help='Is the current machine',
        default=False, readonly=True)
    categ_ids = fields.Many2many(
        comodel_name='digital.category', string='Tags')

    @api.one
    def unlink(self):
        if self.state == 'delete':
            return super(DigitalDroplet, self).unlink()
        raise osv.except_osv(_('Error!'), _("Cannot delete droplet "
                                            "because the droplet need "
                                            "state delete."))

    @api.one
    @api.onchange('name')
    def on_change_name(self):
        if self.state in ['draft', 'delete']:
            return
        token = self._token()
        if token is False:
            return False
        try:
            manager = digitalocean.Manager(token=token)
            droplet = manager.get_droplet(self.code)
            droplet.rename(self.name)
        except Exception, e:
            raise osv.except_osv(_('Error!'), _("Cannot rename droplet: "
                                                "%s" % (e)))

    @api.one
    @api.onchange('backups')
    def on_change_backups(self):
        if self.state in ['draft', 'delete']:
            return
        token = self._token()
        if token is False:
            return False
        try:
            manager = digitalocean.Manager(token=token)
            droplet = manager.get_droplet(self.code)
            if self.backups:
                # droplet.enable_backups()
                raise osv.except_osv(_('Error!'), _("Cannot enable "
                                                    "backups: "
                                                    "Not yet implemented "
                                                    "in APIv2"))
            else:
                droplet.disable_backups()
        except Exception, e:
            raise osv.except_osv(_('Error!'), _("Cannot enable/disable "
                                                "backups: %s" % (e)))

    def _token(self):
        config_pool = self.env['ir.config_parameter']
        token = config_pool.get_param('digital_droplet.token', default=False)
        if token is False or len(token) <= 0:
            return False
        return token

    def _get_region(self, slug):
        reg_obj = self.env['digital.region']
        reg_ids = reg_obj.search([('slug', '=', slug)])
        if not reg_ids:
            return False
        return reg_ids[0]

    def _get_size(self, slug):
        siz_obj = self.env['digital.size']
        siz_ids = siz_obj.search([('slug', '=', slug)])
        if not siz_ids:
            return False
        return siz_ids[0]

    def _sincro_size(self, size_list):
        size_obj = self.env['digital.size']
        for size in size_list:
            size_ids = size_obj.search([('slug', '=', size.slug)])
            map_size = {'name': size.slug,
                        'slug': size.slug,
                        'memory': size.memory,
                        'vcpus': size.vcpus,
                        'disk': size.disk,
                        'transfer': size.transfer,
                        'price_monthly': size.price_monthly,
                        'price_hourly': size.price_hourly,
                        }
            try:
                if not size_ids:
                    size_obj.create(map_size)
                    continue
                size_ids.write(map_size)
            except Exception, e:
                _logger.info("_sincro_size::Exception " + pformat(e))

    def _sincro_image(self, image_list):
        img_obj = self.env['digital.image']
        for image in image_list:
            image_ids = img_obj.search([('code', '=', image.id)])
            distro = str(image.distribution)
            img_name = str(image.name)
            map_image = {'name': distro + "/" + img_name,
                         'sort_name': image.name,
                         'code': image.id,
                         'slug': image.slug,
                         'distribution': image.distribution,
                         'date': image.created_at,
                         'public': image.public,
                         }
            try:
                if not image_ids:
                    img_obj.create(map_image)
                    continue
                image_ids.write(map_image)
            except Exception, e:
                _logger.info("_sincro_image::Exception " + pformat(e))

    def _get_img(self, img):
        img_obj = self.env['digital.image']
        img_ids = img_obj.search([('code', '=', img['id'])])
        if not img_ids:
            distro = str(img['distribution'])
            img_name = str(img['name'])
            map_image = {'name': distro + "/" + img_name,
                         'sort_name': img['name'],
                         'code': img['id'],
                         'slug': img['slug'],
                         'distribution': img['distribution'],
                         'date': img['created_at'],
                         }
            return img_obj.create(map_image)
        return img_ids[0]

    def _get_action_log(self, droplet):
        log_model = self.env['digital.log']
        droplet_actions = droplet.get_actions()
        for action in droplet_actions:
            log_obj = log_model.search([('log_id', '=', action.id)])
            if log_obj and log_obj.droplet and log_obj.status == 'completed':
                continue
            droplet_obj = self.env['digital.droplet'].search(
                [('code', '=', droplet.id)])
            map_log = {'log_id': action.id,
                       'droplet': droplet_obj.id,
                       'status': action.status,
                       'started_at': action.started_at,
                       'completed_at': action.completed_at,
                       'action_type': action.type,
                       }
            try:
                if not log_obj:
                    log_model.create(map_log)
                    continue
                log_obj.write(map_log)
            except Exception, e:
                _logger.info("_get_action_log::Exception " + pformat(e))

    def _sincro_region(self, region_list):
        region_obj = self.env['digital.region']
        for region in region_list:
            region_ids = region_obj.search([('slug', '=', region.slug)])
            map_region = {'name': region.name,
                          'slug': region.slug,
                          'available': region.available,
                          }
            try:
                if not region_ids:
                    region_obj.create(map_region)
                    continue
                region_ids.write(map_region)
            except Exception, e:
                _logger.info("_sincro_region::Exception " + pformat(e))

    def _sincro_network(self, droplet):
        d_model = self.env['digital.droplet']
        net_model = self.env['digital.network']
        d_obj = d_model.search([('code', '=', droplet.id)])
        for net_version in droplet.networks.keys():
            for net in droplet.networks[net_version]:
                net_obj = net_model.search(
                    [('ip_address', '=', net["ip_address"]),
                     ('droplet', '=', d_obj.id)])
                if not net_obj:
                    net_map = {
                        'version': net_version,
                        'net_type': net['type'],
                        'netmask': net['netmask'],
                        'ip_address': net['ip_address'],
                        'gateway': net['gateway'],
                        'droplet': d_obj.id
                    }
                    net_model.create(net_map)

    def _detect_localhost(self, droplet):
        public_ip = load(urlopen('https://api.ipify.org/?format=json'))['ip']
        for net in droplet.networks['v4']:
            if public_ip == net['ip_address']:
                return True
        return False

    def _sincro_droplet(self, droplet_list):
        d_obj = self.env['digital.droplet']
        for droplet in droplet_list:
            droplet_ids = d_obj.search([('code', '=', droplet.id)])
            map_droplet = {
                'name': droplet.name,
                'code': droplet.id,
                'region': self._get_region(droplet.region['slug']).id,
                'size': self._get_size(droplet.size_slug).id,
                'image': self._get_img(droplet.image).id,
                'backups': True if droplet.backups is True else False,
                'status': droplet.status,
                'date': droplet.created_at,
                'kernel': droplet.kernel['name'],
                'state': 'power_on' if droplet.status == 'active'
                else 'power_off',
                'localhost': self._detect_localhost(droplet)}
            try:
                if not droplet_ids:
                    d_obj.create(map_droplet)
                else:
                    droplet_ids.write(map_droplet)
                self._sincro_network(droplet)
                self._get_action_log(droplet)
            except Exception, e:
                _logger.info("_sincro_droplet::Exception " + pformat(e))

    @api.one
    def action_create_new_droplet(self):
        if self.state != 'draft':
            raise osv.except_osv(_('Error!'), _("Cannot create droplet "
                                                "because the droplet exist."))
        token = self._token()
        if token is False:
            return False
        if not (self.name and self.region and self.image and self.size):
            raise osv.except_osv(_('Error!'), _("Cannot create droplet "
                                                "because the droplet need"
                                                "name, region, image and "
                                                "size"))
        try:
            droplet = digitalocean.Droplet(
                token=token, name=self.name, region=self.region.slug,
                image=self.image.slug, size_slug=self.size.slug,
                backups=self.backups)
            droplet.create()
            self.write({'state': 'power_on'})
            self.write({'code': droplet.id})
        except Exception, e:
            raise osv.except_osv(_('Error!'), _("Cannot create droplet: "
                                                "%s" % (e)))

    @api.one
    def action_delete_droplet(self):
        if self.state == 'draft':
            raise osv.except_osv(_('Error!'), _("Cannot delete droplet "
                                                "because the droplet "
                                                "never created."))
        token = self._token()
        if token is False:
            return False
        try:
            manager = digitalocean.Manager(token=token)
            droplet = manager.get_droplet(self.code)
            droplet.destroy()
            self.write({'state': 'delete'})
        except Exception, e:
            raise osv.except_osv(_('Error!'), _("Cannot delete droplet: "
                                                "%s" % (e)))

    @api.one
    def action_power_off_droplet(self):
        if self.state == 'draft' or self.state == 'delete':
            raise osv.except_osv(_('Error!'), _("Cannot shutdown droplet "
                                                "because the droplet "
                                                "no exist."))
        token = self._token()
        if token is False:
            return False
        try:
            manager = digitalocean.Manager(token=token)
            droplet = manager.get_droplet(self.code)
            droplet.power_off()
            self.write({'state': 'power_off'})
        except Exception, e:
            raise osv.except_osv(_('Error!'), _("Cannot shutdown droplet: "
                                                "%s" % (e)))

    @api.one
    def action_power_on_droplet(self):
        if self.state == 'draft' or self.state == 'delete':
            raise osv.except_osv(_('Error!'), _("Cannot power on droplet "
                                                "because the droplet "
                                                "no exist."))
        token = self._token()
        if token is False:
            return False
        try:
            manager = digitalocean.Manager(token=token)
            droplet = manager.get_droplet(self.code)
            droplet.power_on()
            self.write({'state': 'power_on'})
        except Exception, e:
            raise osv.except_osv(_('Error!'), _("Cannot power on droplet: "
                                                "%s" % (e)))

    @api.one
    def action_reboot_droplet(self):
        if self.state == 'draft' or self.state == 'delete':
            raise osv.except_osv(_('Error!'), _("Cannot reboot droplet "
                                                "because the droplet "
                                                "no exist."))
        token = self._token()
        if token is False:
            return False
        try:
            manager = digitalocean.Manager(token=token)
            droplet = manager.get_droplet(self.code)
            droplet.reboot()
            self.write({'state': 'power_off'})
        except Exception, e:
            raise osv.except_osv(_('Error!'), _("Cannot reboot droplet: "
                                                "%s" % (e)))

    @api.one
    def action_reset_root_password_droplet(self):
        token = self._token()
        if token is False:
            return False
        try:
            manager = digitalocean.Manager(token=token)
            droplet = manager.get_droplet(self.code)
            droplet.reset_root_password()
        except Exception, e:
            raise osv.except_osv(_('Error!'), _("Cannot reset password: "
                                                "%s" % (e)))

    @api.one
    def action_refresh_droplet(self):
        if not self.code or self.state == 'draft' or self.state == 'delete':
            raise osv.except_osv(_('Error!'), _("Cannot refresh droplet "
                                                "because the droplet "
                                                "no exist."))
        token = self._token()
        if token is False:
            return False
        try:
            manager = digitalocean.Manager(token=token)
            droplet = manager.get_droplet(self.code)
            self._sincro_droplet([droplet])
        except Exception, e:
            raise osv.except_osv(_('Error!'), _("Cannot refresh droplet: "
                                                "%s" % (e)))

    @api.one
    def action_take_snapshot_droplet(self):
        token = self._token()
        if token is False:
            return False
        try:
            manager = digitalocean.Manager(token=token)
            droplet = manager.get_droplet(self.code)
            name_snapshot = str(
                self.name) + '_' + datetime.datetime.now().strftime("%Y_%m_%d")
            droplet.take_snapshot(name_snapshot)
        except Exception, e:
            raise osv.except_osv(_('Error!'), _("Cannot snapshot droplet: "
                                                "%s" % (e)))

    @api.one
    def action_resize_droplet(self):
        token = self._token()
        if token is False:
            return False
        try:
            manager = digitalocean.Manager(token=token)
            droplet = manager.get_droplet(self.code)
            droplet.resize(self.size.slug)
        except Exception, e:
            raise osv.except_osv(_('Error!'), _("Cannot resize droplet: "
                                                "%s" % (e)))
    """
    @api.one
    def action_restore_droplet(self):
        token = self._token()
        if token is False:
            return False
        try:
            manager = digitalocean.Manager(token=token)
            droplet = manager.get_droplet(self.code)
            droplet.restore(self.image.code)
        except Exception, e:
            raise osv.except_osv(_('Error!'), _("Cannot restore droplet: "
                                                "%s" % (e)))

    @api.one
    def action_rebuid_droplet(self):
        token = self._token()
        if token is False:
            return False
        try:
            manager = digitalocean.Manager(token=token)
            droplet = manager.get_droplet(self.code)
            droplet.rebuid(self.image.code)
        except Exception, e:
            raise osv.except_osv(_('Error!'), _("Cannot restore droplet: "
                                                "%s" % (e)))
    """

    @api.model
    def call_cron_digital_update(self):
        token = self._token()
        if token is False:
            return False
        manager = digitalocean.Manager(token=token)
        size_list = manager.get_all_sizes()
        self._sincro_size(size_list)
        image_list = manager.get_all_images()
        self._sincro_image(image_list)
        region_list = manager.get_all_regions()
        self._sincro_region(region_list)

    @api.model
    def call_cron_droplet_update(self):
        token = self._token()
        if token is False:
            return False
        manager = digitalocean.Manager(token=token)
        droplet_list = manager.get_all_droplets()
        self._sincro_droplet(droplet_list)
