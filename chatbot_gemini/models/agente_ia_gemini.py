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

        # Verificar que no es un mensaje del bot
        bot_user = self.env.ref('chatbot_gemini.gemini_ai_user', raise_if_not_found=False)
        if not bot_user or message.author_id == bot_user.partner_id:
            return result    
            
        try:    
            _logger.info(f"_message_post_after_hook: procesando mensaje: {message.body[:50]}")
            self.with_user(bot_user)._handle_ai_response_gemini(message)
                
        except Exception as e:
            _logger.error(f"Error en _message_post_after_hook: {e}")
            
        return result

    def _handle_ai_response_gemini(self, message):
        """Maneja la generación y publicación de la respuesta de Gemini AI"""
        try:
            _logger.info("Iniciando _handle_ai_response_gemini")
            mensaje_usuario = message.body
            respuesta_ia = self.enviar_a_gemini(mensaje_usuario, message)  # Pasamos el mensaje como parámetro

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
            except Exception as inner_e:
                _logger.error(f"Error al enviar mensaje de error: {inner_e}")

    def enviar_a_gemini(self, mensaje, mensaje_original=None):
        """Envía un mensaje a la API de Gemini y retorna la respuesta
    
        Args:
            mensaje: El texto del mensaje a enviar
            mensaje_original: El objeto mensaje original (opcional)
        """
        self.ensure_one()
        api_key = self.GEMINI_API_KEY
        api_url = self.GEMINI_API_URL + ":generateContent"

        if not api_key or not api_url:
            _logger.error("Las credenciales de la API de Gemini no están configuradas")
            return "Error de configuración: API de Gemini no configurada."

        try:
            history = self.env['mail.message'].search([
                ('model', '=', 'discuss.channel'),
                ('res_id', '=', self.id), 
                ('message_type', '=', 'comment'),
            ], limit=10, order='id desc')

            # Obtener productos activos en venta
            productos = self.env['product.template'].search([('active', '=', True), ('sale_ok', '=', True)])

            # Total de productos
            total_productos = len(productos)

            # Producto más caro
            producto_caro = max(productos, key=lambda p: p.list_price, default=None)

            # Producto más barato 
            producto_barato = min(productos.filtered(lambda p: p.list_price > 0), key=lambda p: p.list_price, default=None)

            # Agrupar por categoría
            categorias = {}
            for p in productos:
                nombre_cat = p.categ_id.name or "Sin categoría"
                categorias[nombre_cat] = categorias.get(nombre_cat, 0) + 1

            # Armar resumen para dar contexto a la IA
            resumen = f"Tienes {total_productos} productos activos.\n\n"

            if producto_caro:
                resumen += f"Producto más caro: {producto_caro.name} (${producto_caro.list_price}) - Categoría: {producto_caro.categ_id.name}\n"

            if producto_barato:
                resumen += f"Producto más barato: {producto_barato.name} (${producto_barato.list_price}) - Categoría: {producto_barato.categ_id.name}\n"

            resumen += "\nProductos por categoría:\n"
            for nombre_cat, cantidad in categorias.items():
                resumen += f"- {nombre_cat}: {cantidad} productos\n"

            resumen += "\nCategorías disponibles:\n"
            resumen += ", ".join(categorias.keys())

            # Construir el histórico de conversación 
            contents = []
            contents.append({
                "role": "user",
                "parts": [{"text": "Eres un asistente de ventas que responde en español. A continuación, continúa la conversación:"}]
            })

            bot_user = self.env.ref('chatbot_gemini.gemini_ai_user', raise_if_not_found=False)
            bot_partner_id = bot_user.partner_id if bot_user else False

            for msg in reversed(history):
                role = "model" if msg.author_id.id == bot_partner_id.id else "user"
                contents.append({
                    "role": role,
                    "parts": [{"text": msg.body}]
                })

            contents.append({
                "role": "user",
                "parts": [{"text": "Contexto adicional del negocio:\n" + resumen}]
            })

            if mensaje_original and mensaje_original.id not in history.mapped('id'):
                contents.append({
                    "role": "user",
                    "parts": [{"text": mensaje_original.body}]
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
                },
                "safetySettings": [
                    {
                        "category": "HARM_CATEGORY_HARASSMENT",
                        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                    }
                ]
            }

            _logger.info(f"Enviando mensaje a Gemini: {mensaje[:50]}")
            response = requests.post(api_url, params=params, headers=headers, json=data, timeout=15)

            if response.status_code != 200:
                error_msg = f"Error en la API de Gemini: {response.status_code}"
                _logger.error(f"{error_msg} - {response.text}")
                return error_msg

            response_json = response.json()

            if 'candidates' in response_json and len(response_json['candidates']) > 0:
                texto_respuesta = response_json['candidates'][0]['content']['parts'][0]['text']
                return texto_respuesta
            else:
                _logger.warning("La API de Gemini devolvió una respuesta vacía")
                return "No pude generar una respuesta adecuada."

        except requests.exceptions.Timeout:
            error_message = "Tiempo de espera agotado al comunicarse con la API de Gemini"
            _logger.error(error_message)
            return error_message

        except requests.exceptions.RequestException as e:
            error_message = f"Error de comunicación con la API de Gemini: {str(e)}"
            _logger.error(error_message)
            return error_message

        except Exception as e:
            error_message = f"Error inesperado: {str(e)}"
            _logger.error(error_message)
            return error_message