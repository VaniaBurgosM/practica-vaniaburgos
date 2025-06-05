from odoo import models, fields, api
from math import radians, cos, sin, asin, sqrt
from odoo import _
import logging
import requests
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

                full_address = f"{street}, {city}, {state}, {country}"
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
                    # Puedes decidir si esto debe ser un fallo o solo una advertencia
                    # raise UserError(_("No se pudieron obtener las coordenadas del cliente para verificar la distancia."))
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
        address = unicodedata.normalize('NFKD', address).encode('ascii', 'ignore').decode('utf-8')
        
        # Try multiple address variations for better geocoding success
        address_variations = [
            address,  # Original full address
            # Remove specific details like "Bodega 4A" that might not be in geocoding databases
            ', '.join([part.strip() for part in address.split(',') if 'bodega' not in part.lower() and 'oficina' not in part.lower()]),
            # Try with just street, city, and country
            f"{address.split(',')[0]}, {address.split(',')[2] if len(address.split(',')) > 2 else ''}, {address.split(',')[-1]}".replace(', ,', ',').strip(','),
        ]
        
        url = 'https://nominatim.openstreetmap.org/search'
        headers = {
            'User-Agent': 'OdooGeoCheckin/1.0'
        }
        
        for attempt, addr in enumerate(address_variations, 1):
            if not addr.strip():
                continue
                
            params = {
                'q': addr.strip(),
                'format': 'json',
                'limit': 1,
            }

            import urllib.parse
            query_string = urllib.parse.urlencode(params)
            _logger.info(f"Intento {attempt} - URL de consulta: {url}?{query_string}")
            _logger.info(f"Dirección buscada: {addr}")

            try:
                response = requests.get(url, params=params, headers=headers, timeout=10)
                response.raise_for_status()

                _logger.info(f"Response status: {response.status_code}")
                _logger.info(f"Response content: {response.text}")

                data = response.json()
                if data:
                    latitude = data[0]['lat']
                    longitude = data[0]['lon']
                    _logger.info(f"Coordenadas encontradas en intento {attempt} para '{addr}': ({latitude}, {longitude})")
                    return latitude, longitude
                else:
                    _logger.warning(f"Intento {attempt}: No se encontraron coordenadas para la dirección: {addr}")
                    
            except requests.exceptions.RequestException as e:
                _logger.error(f"Intento {attempt}: Error al consultar Nominatim para la dirección '{addr}': {e}")
                
            # Add a small delay between requests to be respectful to the API
            import time
            time.sleep(1)
        
        _logger.warning(f"No se pudieron obtener coordenadas después de {len(address_variations)} intentos para: {address}")
        return None, None