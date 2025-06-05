from odoo import models, fields, api
from math import radians, cos, sin, asin, sqrt
from odoo import _
import logging
import unicodedata
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class CrmLead(models.Model):
    _inherit = 'crm.lead'

    checkin_latitude = fields.Float(string="Latitud Check-in", digits=(16, 6))
    checkin_longitude = fields.Float(string="Longitud Check-in", digits=(16, 6))
    checkin_datetime = fields.Datetime(string="Fecha del Check-In")
    checkin_distance_km = fields.Float(string="Distancia (km)", digits=(8, 2))

    def get_location(self, location_data):
        latitude = location_data.get('latitude')
        longitude = location_data.get('longitude')
        distance_km = 0.0  # Initialize the variable at the beginning

        # Si no hay datos de ubicación, notificar un error y salir
        if not latitude or not longitude:
            _logger.error("No se recibieron datos de ubicación (latitud o longitud).")
            raise UserError(_("No se pudo obtener la ubicación. Asegúrate de que los servicios de ubicación estén activados."))

        for lead in self:
            partner = lead.partner_id
            if partner:
                address_parts = filter(None, [
                    partner.name,
                    partner.street,
                    partner.street2,
                    partner.zip,
                    partner.city,
                    partner.state_id.name if partner.state_id else '',
                    partner.country_id.name if partner.country_id else ''
                ])
                full_address = ', '.join(address_parts)
                _logger.info(f"Dirección del contacto: {full_address}")

                leadlat, leadlon = self.get_coords_from_address(full_address)
                
                if leadlat is not None and leadlon is not None:
                    _logger.info(f"Coordenadas obtenidas: ({leadlat}, {leadlon})")
                    lat1, lon1 = radians(float(leadlat)), radians(float(leadlon))
                    lat2, lon2 = radians(float(latitude)), radians(float(longitude))

                    # Fórmula de Haversine
                    dlon = lon2 - lon1
                    dlat = lat2 - lat1
                    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
                    c = 2 * asin(sqrt(a))
                    distance_km = 6371 * c  # Radio de la Tierra en km
                    lead.checkin_distance_km = distance_km

                    # Verificar distancia
                    if distance_km > 0.1:  # Más de 100 metros (0.1 km)
                        _logger.warning(f"Check-in rechazado para el lead {lead.name} por estar a {distance_km:.2f} km de distancia. (Más de 100 metros)")
                        # Muestra un mensaje de error y detiene la ejecución
                        return {
                            'distance_km': f"{distance_km:.2f}"
                            }
                else:
                    # Si no se pueden obtener las coordenadas del cliente
                    _logger.warning(f"No se pudieron obtener las coordenadas para la dirección del cliente: {full_address}. No se verificará la distancia.")
                    lead.checkin_distance_km = 0.0 # O un valor que indique que no se pudo calcular la distancia

            else:
                _logger.warning(f"El lead {lead.name} no tiene un contacto asociado para verificar la ubicación.")
                lead.checkin_distance_km = 0.0 # O un valor que indique que no se pudo calcular la distancia

            lead.checkin_latitude = latitude
            lead.checkin_longitude = longitude
            lead.checkin_datetime = fields.Datetime.now()
            _logger.info(f"Checkin: Lead: [{lead.id}] actualizado a {latitude}, {longitude}")

        # Si todo fue bien, retorna la notificación de éxito
        return {
            'distance_km': f"{distance_km:.2f}"
        }

    def get_location_button(self):
        _logger.info("Botón de check-in presionado, obteniendo ubicación...")
        # Este método ahora simplemente inicia el proceso, el resultado se maneja en get_location
        return True

    def get_coords_from_address(self, address):
        import requests
        
        api_key = self.env['ir.config_parameter'].sudo().get_param('google_maps_api_key')
        if not api_key:
            raise UserError (_("No se ha configurado la clave de API de Google Maps en 'ir.config_parameter'"))

        params = {
            'address': address,
            'key': api_key
        }

        try:
            response = requests.get('https://maps.googleapis.com/maps/api/geocode/json', params=params, timeout=10)
            response.raise_for_status()
            result = response.json() 

            if result['status'] == 'OK':
                location = result['results'][0]['geometry']['location']
                latitude = location['lat']
                longitude = location['lng']
                _logger.info(f"Google Maps: Coordenadas para '{address}': ({latitude}, {longitude})")
                return latitude, longitude
        
            else:
                _logger.warning(f"Google Maps: Error en geocodificación para '{address}': {result.get('status')}")
                return None, None
        
        except requests.exceptions.RequestException as e:
            _logger.error(f"Google Maps: Error al hacer la solicitud: {e}")
            return None, None