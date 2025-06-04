from odoo import models, fields, api
from odoo.exceptions import UserError
import logging
import math

logger = logging.getLogger(__name__)

class ProjectTaskGeoCheckin(models.Model):
    _inherit = 'project.task'

    # Variables para guardar información del check-in
    checkin_latitude = fields.Float("Latitud de Check-In")
    checkin_longitude = fields.Float("Longitud de Check-In")
    checkin_datetime = fields.Datetime("Fecha y Hora de Check-In")
    checkin_distance_km = fields.Float("Distancia al cliente (km)", compute="_compute_checkin_distance", store=True)

    # Coordenadas del cliente, relacionadas desde el partner
    partner_latitude = fields.Float(related='partner_id.partner_latitude', store=True)
    partner_longitude = fields.Float(related='partner_id.partner_longitude', store=True)

    @api.model
    def action_geo_checkin(self, task_ids, latitude, longitude):
        """
        Método para registrar check-in geográfico.
        Se llama desde JavaScript con los parámetros: task_ids (list), latitude, longitude
        """
        if not task_ids:
            raise UserError("No se especificó ninguna tarea para el check-in.")
        
        if not isinstance(task_ids, list):
            task_ids = [task_ids]
            
        task = self.browse(task_ids[0])
        
        if not task.exists():
            raise UserError("La tarea especificada no existe.")

        if not latitude or not longitude:
            raise UserError("No se recibieron coordenadas válidas para el check-in.")

        try:
            # Actualizar campos de check-in
            task.write({
                'checkin_latitude': latitude,
                'checkin_longitude': longitude,
                'checkin_datetime': fields.Datetime.now(),
            })
            
            # Forzar recálculo de distancia
            task._compute_checkin_distance()
            
            logger.info(f"Check-in registrado para tarea {task.id}: lat={latitude}, lon={longitude}")
            
            return {
                'status': 'success',
                'message': 'Check-in registrado correctamente',
                'datetime': task.checkin_datetime.isoformat() if task.checkin_datetime else None,
                'distance_km': task.checkin_distance_km,
            }
            
        except Exception as e:
            logger.error(f"Error en action_geo_checkin: {str(e)}")
            raise UserError(f"Error al registrar check-in: {str(e)}")

    @api.depends('checkin_latitude', 'checkin_longitude', 'partner_latitude', 'partner_longitude')
    def _compute_checkin_distance(self):
        """Calcula la distancia entre el check-in y el cliente usando la fórmula de Haversine."""
        for task in self:
            if all([
                task.checkin_latitude,
                task.checkin_longitude,
                task.partner_latitude,
                task.partner_longitude
            ]):
                task.checkin_distance_km = self._haversine(
                    task.partner_latitude,
                    task.partner_longitude,
                    task.checkin_latitude,
                    task.checkin_longitude
                )
            else:
                task.checkin_distance_km = 0.0

    def _haversine(self, lat1, lon1, lat2, lon2):
        """Fórmula de Haversine para calcular distancia entre 2 coordenadas en km."""
        try:
            R = 6371.0  # radio de la Tierra en km

            lat1_rad = math.radians(float(lat1))
            lon1_rad = math.radians(float(lon1))
            lat2_rad = math.radians(float(lat2))
            lon2_rad = math.radians(float(lon2))

            dlat = lat2_rad - lat1_rad
            dlon = lon2_rad - lon1_rad

            a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

            return R * c
        except (ValueError, TypeError) as e:
            logger.error(f"Error en cálculo Haversine: {str(e)}")
            return 0.0

    def dummy_checkin(self):
        """Método dummy - no se usa en la funcionalidad real."""
        return {
            'type': 'ir.actions.act_window_close',
        }