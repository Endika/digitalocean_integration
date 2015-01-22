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


class digital_size(orm.Model):
    _name = "digital.size"
    _columns = {'name': fields.char("Name", size=100,
                                    required=True, readonly=True),
                'slug': fields.char("Slug", size=50,
                                    required=True, readonly=True),
                'memory': fields.char("Memory", size=50,
                                      required=True, readonly=True),
                'vcpus': fields.char("CPU's", size=50,
                                     required=True, readonly=True),
                'disk': fields.char("Disk", size=50,
                                    required=True, readonly=True),
                'transfer': fields.char("Transfer", size=50,
                                        required=True, readonly=True),
                'price_monthly': fields.char("Price per month", size=50,
                                             required=True, readonly=True),
                'price_hourly': fields.char("Price per hour", size=50,
                                            required=True, readonly=True),
                }


class digital_image(orm.Model):
    _name = "digital.image"
    _columns = {'name': fields.char("Name", size=100,
                                    required=True, readonly=True),
                'sort_name': fields.char("Name", size=100,
                                         required=True, readonly=True),
                'id': fields.char("ID", size=100,
                                  required=True, readonly=True),
                'slug': fields.char("Slug", size=50,
                                    required=True, readonly=True),
                'distribution': fields.char("Distribution", size=100,
                                            required=True,
                                            readonly=True),
                'date': fields.datetime('Create', readonly=True,
                                        required=True),
                }


class digital_region(orm.Model):
    _name = "digital.region"
    _columns = {'name': fields.char("Name", size=100,
                                    required=True, readonly=True),
                'slug': fields.char("Slug", size=50,
                                    required=True, readonly=True),
                'available': fields.boolean(default=False,
                                            required=True,
                                            help="Enable Backups."),
                }


class digital_droplet(orm.Model):
    _name = "digital.droplet"
    _description = "Digital Ocean Droplet"
    _columns = {
        'name': fields.char("Server name", size=100, required=True),
        'id': fields.char("ID", size=100, readonly=True),
        'region': fields.many2one('digital.region', 'Region', required=True),
        'size': fields.many2one('digital.size', 'Size', required=True),
        'image': fields.many2one('digital.image', 'Image', required=True),
        'backups': fields.boolean(default=False,
                                  required=True,
                                  help="Enable Backups."),
        'status': fields.char("Status", size=50, readonly=True),
        'date': fields.datetime('Created', readonly=True),
        'networks': fields.char("Network", size=2000, readonly=True),
        'kernel': fields.char("Kernel", size=1000, readonly=True),

    }

    def create(self, cr, uid, vals, context=None):
        # Crear el droplet en DIGITAL OCEAN
        super(self, cr, uid, vals, context)

    def write(self, cr, uid, vals, context=None):
        # Editar el droplet en DIGITAL OCEAN
        super(self, cr, uid, vals, context)

    def unlink(self, cr, uid, ids, context=None):
        # eliminar el droplet en DIGITAL OCEAN
        super(self, cr, uid, ids, context)

    def _token(self, cr, uid, ids, context=None):
        config_pool = self.pool.get('ir.config_parameter')
        token = config_pool.get_param(cr, uid,
                                      'digital_droplet.token',
                                      default=False,
                                      context=context)
        if token is False or len(token) <= 0:
            return False
        return token

    def _get_region(self, cr, uid, slug, context=None):
        dreg_obj = self.pool['digital.region']
        reg_ids = dreg_obj.search(cr, uid,
                                  [('slug', '=', slug)],
                                  context=context)
        if not reg_ids:
            return False
        return reg_ids[0]

    def _get_size(self, cr, uid, slug, context=None):
        dsiz_obj = self.pool['digital.size']
        siz_ids = dsiz_obj.search(cr, uid,
                                  [('slug', '=', slug)],
                                  context=context)
        if not siz_ids:
            return False
        return siz_ids[0]

    def _get_img(self, cr, uid, id, context=None):
        dimg_obj = self.pool['digital.image']
        img_ids = dimg_obj.search(cr, uid,
                                  [('id', '=', id)],
                                  context=context)
        if not img_ids:
            return False
        return img_ids[0]

    def _sincro_size(self, cr, uid, size_list, context=None):
        dsize_obj = self.pool['digital.size']
        for size in size_list:
            size_ids = dsize_obj.search(cr, uid,
                                        [('slug', '=', size.slug)],
                                        context=context)

            map_size = {'name': size.slug,
                        'slug': size.slug,
                        'memory': size.memory,
                        'vcpus': size.vcpus,
                        'disk': size.disk,
                        'transfer': size.transfer,
                        'price_monthly': size.price_monthly,
                        'price_hourly': size.price_hourly,
                        }
            if not size_ids:
                dsize_obj.create(cr, uid,
                                 map_size,
                                 context=context)
                continue
            dsize_obj.write(cr, uid, size_ids,
                            map_size,
                            context=context)

    def _sincro_image(self, cr, uid, image_list, context=None):
        dimg_obj = self.pool['digital.image']
        for image in image_list:
            image_ids = dimg_obj.search(cr, uid,
                                        [('id', '=', image.id)],
                                        context=context)

            map_image = {'name': str(image.distribution) + str(image.name),
                         'sort_name': image.name,
                         'id': image.id,
                         'slug': image.slug,
                         'distribution': image.distribution,
                         'date': image.created_at,
                         }

            if not image_ids:
                dimg_obj.create(cr, uid,
                                map_image,
                                context=context)
                continue
            dimg_obj.write(cr, uid, image_ids,
                           map_image,
                           context=context)

    def _sincro_region(self, cr, uid, region_list, context=None):
        dregion_obj = self.pool['digital.region']
        for region in region_list:
            region_ids = dregion_obj.search(cr, uid,
                                            [('slug', '=', region.slug)],
                                            context=context)

            map_region = {'name': region.name,
                          'slug': region.slug,
                          'available': region.available,
                          }

            if not region_ids:
                dregion_obj.create(cr, uid,
                                   map_region,
                                   context=context)
                continue
            dregion_obj.write(cr, uid, region_ids,
                              map_region,
                              context=context)

    def _sincro_droplet(self, cr, uid, droplet_list, context=None):
        dd_obj = self.pool['digital.droplet']
        for droplet in droplet_list:
            droplet_ids = dd_obj.search(cr, uid,
                                        [('id', '=', droplet.id)],
                                        context=context)

            netv4 = ""
            for i in droplet.networks['v4'][0].keys():
                netv4 += str(i)+" "
            backups = True if droplet.backups is True else False
            map_droplet = {'name': droplet.name,
                           'id': droplet.id,
                           'region': self._get_region(cr, uid,
                                                      droplet.region['slug'],
                                                      context),
                           'size': self._get_region(cr, uid,
                                                    droplet.size_slug,
                                                    context),
                           'image': self._get_image(cr, uid,
                                                    droplet.image['id'],
                                                    context),
                           'backups': backups,
                           'status': droplet.status,
                           'date': droplet.created_at,
                           'networks': netv4,
                           'kernel': droplet.kernel['name']
                           }

            if not droplet_ids:
                dd_obj.create(cr, uid,
                              map_droplet,
                              context=context)
                continue
            dd_obj.write(cr, uid, droplet_ids,
                         map_droplet,
                         context=context)

    def call_cron_digital_update(self, cr, uid, context=None):
        token = self._api_key(cr, uid, [], context=context)
        if token is False:
            return False
        manager = digitalocean.Manager(token=token)

        size_list = manager.get_all_sizes()
        self._sincro_size(cr, uid, size_list, context)
        image_list = manager.get_all_images()
        self._sincro_image(cr, uid, image_list, context)
        region_list = manager.get_all_regions()
        self._sincro_region(cr, uid, region_list, context)
        droplet_list = manager.get_all_droplets()
        self._sincro_droplet(cr, uid, droplet_list, context)
