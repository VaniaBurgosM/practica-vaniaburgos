from odoo import models, fields, api
import requests
import logging
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class AgenteGemini(models.Model):
    _inherit = 'mail.channel'

    GEMINI_API_KEY = 'AIzaSyDXrQZm5xZEDuJVQqjqo7R6-68sgab9tws'
    GEMINI_API_URL = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash'

    def _message_post_after_hook(self, message, msg_vals):
        """Override para añadir respuesta de la IA cuando sea necesario"""
        result = super()._message_post_after_hook(message, msg_vals)
        bot_user = self.env.ref('chatbot_gemini.gemini_ai_user')

        if message.author_id != bot_user.partner_id:
            try:
                self.with_user(bot_user)._handle_ai_response_gemini(message)
            except Exception as e:
                _logger.error(f"Error en _handle_ai_response_gemini: {e}")

                self.with_user(bot_user).message_post(
                    body="Ocurrió un error al procesar tu solicitud.",
                    message_type='comment',
                    subtype_xmlid='mail.mt_comment'
                )

        return result

    def _handle_ai_response_gemini(self, message):
        """Maneja la generación y publicación de la respuesta de Gemini AI"""
        mensaje_usuario = message.body
        respuesta_ia = self.enviar_a_gemini(mensaje_usuario)

        if respuesta_ia:
            bot_user = self.env.ref('chatbot_gemini.gemini_ai_user')
            self.with_user(bot_user).message_post(
                body=respuesta_ia,
                message_type='comment',
                subtype_xmlid='mail.mt_comment'
            )

    def enviar_a_gemini(self, mensaje):
        """Envía el mensaje a la API de Gemini y devuelve la respuesta"""
        api_key = self.GEMINI_API_KEY
        api_url = self.GEMINI_API_URL

        if not api_key or not api_url:
            raise UserError("Las credenciales de la API de Gemini no están configuradas (directamente en el código).")

        # Obtener los últimos mensajes para el contexto
        history = self.env['mail.message'].search([
            ('model', '=', 'discuss.channel'),
            ('res_id', '=', self.id), 
            ('message_type', '=', 'comment'),
        ], limit=10, order='id desc')

        messages = []

        for msg in reversed(history):
            role = "assistant" if msg.author_id == self.env.ref('chatbot_gemini.gemini_ai_user').partner_id else "user"
            messages.append({
                "role": role,
                "content": msg.body,
            })

        messages.append({"role": "user", "content": mensaje})

        params = {'key': api_key}
        headers = {'Content-Type': 'application/json'}
        data = {'contents': [{'parts': [{'text': ' '.join([m["content"] for m in messages])}]}]}

        try:
            response = requests.post(f"{api_url}", params=params, headers=headers, json=data, timeout=10)
            response.raise_for_status()
            response_json = response.json()
            if 'candidates' in response_json and len(response_json['candidates']) > 0:
                return response_json['candidates'][0]['content']['parts'][0]['text']

            else:
                _logger.warning("La API de Gemini devolvió una respuesta vacía.")
                return "<p>La API de Gemini devolvió una respuesta vacía.</p>"

        except requests.exceptions.RequestException as e:
            error_message = f"Error al comunicarse con la API de Gemini: {e}"
            _logger.error(error_message)
            raise UserError(error_message)