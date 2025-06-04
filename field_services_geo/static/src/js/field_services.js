odoo.define('field_services_geo.geo_checkin', function (require) {
    "use strict";

    const FormController = require('web.FormController');
    const rpc = require('web.rpc');
    const core = require('web.core');
    const _t = core._t;

    FormController.include({
        /**
         * Sobreescribe el método _onButtonClicked para manejar botones personalizados.
         * Este método se ejecuta cuando se hace clic en cualquier botón del formulario.
         * @override
         */
        _onButtonClicked: function(event) {
            const self = this;
            const buttonAttrs = event.data.attrs;0

            // Verificar si el botón clickeado es nuestro botón personalizado
            if (buttonAttrs && buttonAttrs.class && buttonAttrs.class.includes('o_geo_checkin_button')) {
                console.log('🎯 Botón de geolocalización clickeado - Interceptado en FormController.');

                // ¡CRÍTICO! Detener la propagación del evento inmediatamente.
                // Esto evita que Odoo intente procesar este botón con su lógica por defecto
                // (que espera un 'type' diferente a "button" para acciones de servidor).
                event.stopPropagation();
                event.preventDefault(); 

                // Llamar a la función personalizada para manejar la geolocalización
                this._captureCoordinatesAutomatically();

                return;
            } else {
                // Si no es nuestro botón, permite que el método original de Odoo lo maneje.
                return this._super.apply(this, arguments);
            }
        },

        /**
         * Muestra una notificación usando el sistema de notificaciones de Odoo.
         * @param {Object} notification - Objeto de notificación (título, mensaje, tipo).
         */
        _showNotification: function(notification) {
            // FormController tiene el método displayNotification disponible directamente.
            this.displayNotification(notification);
        },

        /**
         * Inicia el proceso de captura automática de coordenadas GPS.
         */
        _captureCoordinatesAutomatically: function() {
            const self = this;

            console.log('📍 Iniciando captura automática de coordenadas...');

            if (!navigator.geolocation) {
                console.error('❌ Navegador no soporta geolocalización');
                this._showNotification({
                    title: _t("Error"),
                    message: _t("Tu navegador no soporta geolocalización."),
                    type: 'danger',
                });
                return;
            }

            this._showNotification({
                title: _t("📍 Ubicación"),
                message: _t("Capturando coordenadas automáticamente..."),
                type: 'info',
            });

            const geoOptions = {
                enableHighAccuracy: true,
                timeout: 20000,
                maximumAge: 30000
            };

            console.log('🔍 Solicitando ubicación con opciones:', geoOptions);

            navigator.geolocation.getCurrentPosition(
                function(position) {
                    console.log('✅ Coordenadas capturadas automáticamente:', position);
                    const coords = {
                        latitude: position.coords.latitude,
                        longitude: position.coords.longitude,
                        accuracy: position.coords.accuracy,
                        timestamp: new Date().toISOString()
                    };
                    console.log('📊 Datos de ubicación:', coords);

                    if (coords.accuracy > 100) {
                        console.warn('⚠️ Precisión baja:', coords.accuracy + 'm');
                        self._showNotification({
                            title: _t("⚠️ Precisión Baja"),
                            message: _t(`Precisión: ${coords.accuracy.toFixed(0)}m. Procesando de todos modos...`),
                            type: 'warning',
                        });
                    }
                    self._processCoordinates(coords);
                },
                function(error) {
                    console.error('❌ Error capturando coordenadas:', error);
                    let errorMessage = _t("Error desconocido capturando coordenadas");
                    let troubleshooting = "";

                    switch (error.code) {
                        case error.PERMISSION_DENIED:
                            errorMessage = _t("Permiso de ubicación denegado");
                            troubleshooting = _t("Solución: Permite el acceso a la ubicación en tu navegador");
                            break;
                        case error.POSITION_UNAVAILABLE:
                            errorMessage = _t("Ubicación no disponible");
                            troubleshooting = _t("Solución: Verifica tu conexión GPS/WiFi");
                            break;
                        case error.TIMEOUT:
                            errorMessage = _t("Tiempo agotado para capturar ubicación");
                            troubleshooting = _t("Solución: Inténtalo nuevamente en un lugar con mejor señal");
                            break;
                        default:
                            errorMessage = _t("Error: ") + error.message;
                    }
                    self._showNotification({
                        title: _t("❌ Error de Captura Automática"),
                        message: errorMessage + "\n" + troubleshooting,
                        type: 'danger',
                    });
                },
                geoOptions
            );
        },

        /**
         * Envía las coordenadas capturadas al servidor Odoo.
         * @param {Object} coords - Objeto con latitud, longitud, precisión y timestamp.
         */
        _processCoordinates: function(coords) {
            const self = this;

            console.log('🔄 Procesando coordenadas capturadas:', coords);

            let recordId = null;
            // Forma más fiable de obtener el ID del registro desde FormController
            if (this.handle && this.model.localData[this.handle] && this.model.localData[this.handle].data) {
                recordId = this.model.localData[this.handle].data.id;
            }

            if (!recordId) {
                console.error('❌ No se encontró ID del registro');
                this._showNotification({
                    title: _t("Error"),
                    message: _t("No se pudo identificar el registro actual."),
                    type: 'danger',
                });
                return;
            }

            console.log('📤 Enviando coordenadas al servidor para registro:', recordId);

            rpc.query({
                model: 'project.task',
                method: 'action_geo_checkin',
                args: [[recordId], coords.latitude, coords.longitude],
                kwargs: {
                    accuracy: coords.accuracy,
                    timestamp: coords.timestamp,
                    auto_captured: true
                }
            }).then(function(result) {
                console.log('✅ Respuesta del servidor:', result);
                if (result && result.status === 'success') {
                    self._showNotification({
                        title: _t("✅ Check-In Automático Exitoso"),
                        message: `${result.message}\n📍 Coordenadas: ${coords.latitude.toFixed(6)}, ${coords.longitude.toFixed(6)}\n📏 Distancia: ${result.distance_km.toFixed(2)} km\n🎯 Precisión: ${coords.accuracy.toFixed(0)}m`,
                        type: 'success',
                    });
                    // Recargar el formulario 
                    self.reload();
                } else {
                    console.error('❌ Error en respuesta del servidor:', result);
                    self._showNotification({
                        title: _t("❌ Error de Registro"),
                        message: result && result.message ? result.message : _t("No se pudieron procesar las coordenadas capturadas."),
                        type: 'danger',
                    });
                }
            }).catch(function(error) {
                console.error('❌ Error RPC:', error);
                self._showNotification({
                    title: _t("❌ Error de Conexión"),
                    message: _t("Error enviando coordenadas al servidor: ") + (error.message || error.data?.message || 'Error desconocido'),
                    type: 'danger',
                });
            });
        },
    });
});