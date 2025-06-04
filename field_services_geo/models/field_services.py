from odoo import models, fields, api
from odoo.exceptions import UserError
import logging
import math

# Heredar project.task
logger = logging.getLogger(__name__)

class FieldServices(models.Model):
    _inherit = 'project.task'

    # Variables para guardar información del check-in
    checkin_latitude = fields.Float("Latitud de Check-In")
    checkin_longitude = fields.Float("Longitud de Check-In")
    checkin_datetime = fields.Datetime("Fecha y Hora de Check-In")
    checkin_distance_km = fields.Float("Distancia al cliente (km)", compute="_compute_checkin_distance", store=True)

    # Coordenadas del cliente, relacionadas desde el partner
    partner_latitude = fields.Float(related='partner_id.partner_latitude', store=True)
    partner_longitude = fields.Float(related='partner_id.partner_longitude', store=True)

    def action_geo_checkin(self, latitude, longitude):
        self.ensure_one()

        if not latitude or not longitude:
            raise UserError("No se recibieron coordenadas válidas para el check-in.")

        self.checkin_latitude = latitude
        self.checkin_longitude = longitude
        self.checkin_datetime = fields.Datetime.now()
        self._compute_checkin_distance()

        return {
            'status': 'success',
            'message': 'Check-in registrado correctamente',
            'datetime': self.checkin_datetime,
            'distance_km': self.checkin_distance_km,
        }

    @api.depends('checkin_latitude', 'checkin_longitude', 'partner_latitude', 'partner_longitude')
    def _compute_checkin_distance(self):
        """Calcula la distancia entre el check-in y el cliente usando la fórmula de Haversine."""
        for lead in self:
            if all([
                lead.checkin_latitude,
                lead.checkin_longitude,
                lead.partner_latitude,
                lead.partner_longitude
            ]):
                lead.checkin_distance_km = self._haversine(
                    lead.partner_latitude,
                    lead.partner_longitude,
                    lead.checkin_latitude,
                    lead.checkin_longitude
                )
            else:
                lead.checkin_distance_km = 0.0

    def _haversine(self, lat1, lon1, lat2, lon2):
        """Fórmula de Haversine para calcular distancia entre 2 coordenadas en km."""
        R = 6371.0  # radio de la Tierra en km

        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)

        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad

        a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        return R * c

    def dummy_checkin(self):
        """Método necesario para que Odoo cargue la vista con el botón."""
        return True
