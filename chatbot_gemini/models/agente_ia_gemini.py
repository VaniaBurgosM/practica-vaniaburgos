from odoo import models, fields, api
import requests
import logging
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class AgenteGemini(models.Model):
    _inherit = 'discuss.channel'

    is_gemini_enabled = fields.Boolean(
        string="Activar Gemini AI", 
        default=False,
        help="Habilita la integración con Gemini AI para este canal"
    )
    
    GEMINI_API_KEY = 'AIzaSyDXrQZm5xZEDuJVQqjqo7R6-68sgab9tws'
    GEMINI_API_URL = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash'

    def _message_post_after_hook(self, message, msg_vals):
        """Override para añadir respuesta de la IA cuando sea necesario"""
        result = super()._message_post_after_hook(message, msg_vals)
        
        # Solo continuar si estamos en un único canal con Gemini habilitado
        if len(self) != 1 or not self.is_gemini_enabled:
            return result
            
        try:
            # Verificar que no es un mensaje del bot
            bot_user = self.env.ref('chatbot_gemini.gemini_ai_user', raise_if_not_found=False)
            if not bot_user or message.author_id == bot_user.partner_id:
                return result
                
            # Verificar si el mensaje menciona al bot o comienza con un trigger
            contenido = message.body.lower()
            if "@gemini" in contenido or contenido.startswith("gemini"):
                _logger.info(f"_message_post_after_hook: procesando mensaje: {message.body[:50]}")
                self.with_user(bot_user)._handle_ai_response_gemini(message)
                
        except Exception as e:
            _logger.error(f"Error en _message_post_after_hook: {e}")
            # No propagamos la excepción para evitar interrumpir el flujo normal
            
        return result

    def _handle_ai_response_gemini(self, message):
        """Maneja la generación y publicación de la respuesta de Gemini AI"""
        try:
            _logger.info("Iniciando _handle_ai_response_gemini")
            mensaje_usuario = message.body
            respuesta_ia = self.enviar_a_gemini(mensaje_usuario)

            if respuesta_ia:
                bot_user = self.env.ref('chatbot_gemini.gemini_ai_user')
                self.with_user(bot_user).message_post(
                    body=respuesta_ia,
                    message_type='comment',
                    subtype_xmlid='mail.mt_comment'
                )
            _logger.info("Finalizado _handle_ai_response_gemini")
        except Exception as e:
            _logger.error(f"Error en _handle_ai_response_gemini: {e}")
            # Intentamos publicar un mensaje de error, pero no propagamos la excepción
            try:
                bot_user = self.env.ref('chatbot_gemini.gemini_ai_user')
                self.with_user(bot_user).message_post(
                    body="Ocurrió un error al procesar tu solicitud.",
                    message_type='comment',
                    subtype_xmlid='mail.mt_comment'
                )
            except:
                pass

    def enviar_a_gemini(self, mensaje):
        """Envía un mensaje a la API de Gemini y retorna la respuesta"""
        self.ensure_one()
        api_key = self.GEMINI_API_KEY
        api_url = self.GEMINI_API_URL + ":generateContent"

        if not api_key or not api_url:
            _logger.error("Las credenciales de la API de Gemini no están configuradas")
            return "<p>Error de configuración: API de Gemini no configurada.</p>"

        try:
            # Obtener los últimos mensajes para el contexto (máximo 5 para evitar sobrecarga)
            history = self.env['mail.message'].search([
                ('model', '=', 'discuss.channel'),
                ('res_id', '=', self.id), 
                ('message_type', '=', 'comment'),
            ], limit=5, order='id desc')

            # Construir el histórico de conversación en el formato correcto para Gemini
            contents = []
            for msg in reversed(history):
                role = "model" if msg.author_id == self.env.ref('chatbot_gemini.gemini_ai_user').partner_id else "user"
                contents.append({
                    "role": role,
                    "parts": [{"text": msg.body}]
                })

            # Añadir el mensaje actual
            contents.append({
                "role": "user",
                "parts": [{"text": mensaje}]
            })

            params = {'key': api_key}
            headers = {'Content-Type': 'application/json'}
            data = {
                "contents": contents,
                "generationConfig": {
                    "temperature": 0.7,
                    "topK": 40,
                    "topP": 0.95,
                    "maxOutputTokens": 1024
                }
            }

            _logger.info(f"Enviando mensaje a Gemini: {mensaje[:50]}")
            response = requests.post(api_url, params=params, headers=headers, json=data, timeout=15)
            
            if response.status_code != 200:
                _logger.error(f"Error en la API de Gemini: {response.status_code} - {response.text}")
                return f"<p>Error en la API de Gemini: {response.status_code}</p>"
                
            response_json = response.json()
            
            if 'candidates' in response_json and len(response_json['candidates']) > 0:
                texto_respuesta = response_json['candidates'][0]['content']['parts'][0]['text']
                return texto_respuesta
            else:
                _logger.warning("La API de Gemini devolvió una respuesta vacía")
                return "<p>No pude generar una respuesta adecuada.</p>"
                
        except requests.exceptions.Timeout:
            error_message = "Tiempo de espera agotado al comunicarse con la API de Gemini"
            _logger.error(error_message)
            return f"<p>{error_message}</p>"
            
        except requests.exceptions.RequestException as e:
            error_message = f"Error de comunicación con la API de Gemini: {str(e)}"
            _logger.error(error_message)
            return f"<p>{error_message}</p>"
            
        except Exception as e:
            error_message = f"Error inesperado: {str(e)}"
            _logger.error(error_message)
            return f"<p>{error_message}</p>"