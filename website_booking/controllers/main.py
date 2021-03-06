# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (c) 2015 be-cloud.be
#                       Jerome Sonnet <jerome.sonnet@be-cloud.be>
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
import logging
import time
import werkzeug.utils
import json

from openerp import http
from openerp.http import request
from openerp.addons.auth_oauth.controllers.main import OAuthLogin as Home

_logger = logging.getLogger(__name__)

class BookingLoginController(Home):
    
    @http.route('/booking/login_providers', type='json', auth="none")
    def booking_login(self, redirect=None, *args, **kw):
        return self.list_providers()

class BookingController(http.Controller):

    @http.route('/booking', type='http', auth='public', website=True)
    def booking_browser(self, debug=False, **k):
        return request.render('website_booking.index')

    @http.route('/booking/category', type='json', auth='public', website=True)
    def booking_category(self, id=False, debug=False, **k):
        return request.env['school.asset.category'].sudo().search_read([('id', '=', id)],['name','display_name','sequence','parent_id','is_leaf'])

    @http.route('/booking/categories', type='json', auth='public', website=True)
    def booking_categories(self, root=False, parent_id=False, debug=False, **k):
        if root :
            _logger.info('Get Root Categories')
            return request.env['school.asset.category'].sudo().search_read([('parent_id', '=', False)],['name','display_name','sequence','parent_id','is_leaf'])
        else :
            _logger.info('Get Leaf Categories')
            return request.env['school.asset.category'].sudo().search_read([('parent_id', '=', parent_id)],['name','display_name','sequence','parent_id','is_leaf'])

    @http.route('/booking/categories/image/<int:category_id>', type='http', auth='public', website=True)
    def booking_category_image(self, category_id, debug=False, **k):
        category = request.env['school.asset.category'].sudo().browse(category_id)
        if category.image:
            response = werkzeug.wrappers.Response()
            response.mimetype = 'image/png'
            response.headers['Cache-Control'] = 'public, max-age=604800'
            response.headers['Access-Control-Allow-Origin'] = '*'
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST'
            response.headers['Connection'] = 'close'
            response.headers['Date'] = time.strftime("%a, %d-%b-%Y %T GMT", time.gmtime())
            response.headers['Expires'] = time.strftime("%a, %d-%b-%Y %T GMT", time.gmtime(time.time()+604800*60))
            response.data = category.image.decode('base64')
            return response
        else :
            return werkzeug.exceptions.NotFound('No image found for this category.')
    
    @http.route('/booking/assets', type='json', auth='public', website=True)
    def booking_assets(self, category_id=False, debug=False, **k):
        if category_id:
            return request.env['school.asset'].sudo().search_read([('category_id', '=', category_id)],['name'])
        else:
            return [];
        
    @http.route('/booking/events', type='json', auth='public', website=True)
    def booking_events(self, start, end, timezone=False, category_id=False, asset_id=False):
        _logger.info([start, end, timezone, category_id, asset_id])
        # TODO : ugply transform
        start = start.replace('T',' ').replace('Z',' ').replace('.000','').strip()
        end = end.replace('T',' ').replace('Z',' ').replace('.000','').strip()
        fields = ['name','start','stop','allday','room_id','user_id','final_date','recurrency']
        if(category_id):
            domain = [
                ('start', '<=', end),    
                ('stop', '>=', start),
                '|',('asset_ids.category_id', '=', category_id),('room_id.category_id', '=', category_id),
            ]
            ret = request.env['calendar.event'].sudo().with_context({'virtual_id': True}).search_read(domain,fields)
        else:
            domain = [
                ('start', '<=', end),    
                ('stop', '>=', start),
                '|',('asset_ids', '=', asset_id),('room_id', '=', asset_id),
            ]
            ret = request.env['calendar.event'].sudo().with_context({'virtual_id': True}).search_read(domain,fields)
        _logger.info(domain)
        _logger.info(ret)
        return ret
        
    @http.route('/booking/editor', type='http', auth='user', website=True)
    def booking_editor(self, debug=False, **k):
        return request.render('website_booking.editor')
        
        
        