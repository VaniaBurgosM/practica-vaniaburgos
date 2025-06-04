odoo.define('field_services_geo.geo_checkin', function (require) {
    "use strict";
    
    const FormController = require('web.FormController');
    const FormView = require('web.FormView');
    const rpc = require('web.rpc');
    const core = require('web.core');
    const _t = core._t; 
    
    // Interceptar tanto en FormView como en FormController
    FormView.include({
        init: function() {
            this._super.apply(this, arguments);
            this._setupGeoButtonHandler();
        },
        
        _setupGeoButtonHandler: function() {
            const self = this;
            
            // Usar delegación de eventos para capturar clics
            $(document).off('click.geo_checkin').on('click.geo_checkin', '.o_geo_checkin_button', function(e) {
                console.log('🎯 Botón geo check-in clickeado - Iniciando captura automática');
                
                // Detener COMPLETAMENTE cualquier procesamiento de Odoo
                e.stopImmediatePropagation();
                e.preventDefault();
                
                // Ejecutar captura automática de coordenadas
                self._captureCoordinatesAutomatically();
                
                return false;
            });
        },
        
        _captureCoordinatesAutomatically: function() {
            const self = this;
            
            console.log('📍 Iniciando captura automática de coordenadas...');
            
            // Verificar soporte de geolocalización
            if (!navigator.geolocation) {
                console.error('❌ Navegador no soporta geolocalización');
                this._showNotification({
                    title: _t("Error"),
                    message: _t("Tu navegador no soporta geolocalización."),
                    type: 'danger',
                });
                return;
            }
            
            // Mostrar notificación de que estamos obteniendo ubicación
            this._showNotification({
                title: _t("📍 Ubicación"),
                message: _t("Capturando coordenadas automáticamente..."),
                type: 'info',
            });
            
            // Configuración optimizada para captura automática
            const geoOptions = {
                enableHighAccuracy: true,    // Usar GPS de alta precisión
                timeout: 20000,              // 20 segundos de timeout
                maximumAge: 30000            // Cache de 30 segundos
            };
            
            console.log('🔍 Solicitando ubicación con opciones:', geoOptions);
            
            // Capturar coordenadas automáticamente
            navigator.geolocation.getCurrentPosition(
                // Éxito - coordenadas capturadas
                function(position) {
                    console.log('✅ Coordenadas capturadas automáticamente:', position);
                    
                    const coords = {
                        latitude: position.coords.latitude,
                        longitude: position.coords.longitude,
                        accuracy: position.coords.accuracy,
                        timestamp: new Date().toISOString()
                    };
                    
                    console.log('📊 Datos de ubicación:', coords);
                    
                    // Verificar precisión
                    if (coords.accuracy > 100) {
                        console.warn('⚠️ Precisión baja:', coords.accuracy + 'm');
                        self._showNotification({
                            title: _t("⚠️ Precisión Baja"),
                            message: _t(`Precisión: ${coords.accuracy.toFixed(0)}m. Procesando de todos modos...`),
                            type: 'warning',
                        });
                    }
                    
                    // Procesar las coordenadas capturadas
                    self._processCoordinates(coords);
                },
                
                // Error en captura de coordenadas
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
        
        _processCoordinates: function(coords) {
            const self = this;
            
            console.log('🔄 Procesando coordenadas capturadas:', coords);
            
            // Obtener ID del registro actual (múltiples métodos para mayor compatibilidad)
            let recordId = null;
            
            // Método 1: Desde FormView controller
            if (this.controller && this.controller.initialState && this.controller.initialState.data) {
                recordId = this.controller.initialState.data.id;
            }
            
            // Método 2: Desde FormView model
            if (!recordId && this.model && this.model.localData) {
                const handle = this.model.handle;
                const data = this.model.localData[handle];
                recordId = data && data.data && data.data.id;
            }
            
            // Método 3: Desde URL/contexto
            if (!recordId) {
                const urlParams = new URLSearchParams(window.location.search);
                recordId = urlParams.get('id') || 
                          (this.initialState && this.initialState.context && this.initialState.context.active_id);
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
            
            // Enviar coordenadas capturadas al backend
            rpc.query({
                model: 'project.task',
                method: 'action_geo_checkin',
                args: [[recordId], coords.latitude, coords.longitude],
                kwargs: {
                    accuracy: coords.accuracy,
                    timestamp: coords.timestamp,
                    auto_captured: true  // Indicar que fue captura automática
                }
            }).then(function(result) {
                console.log('✅ Respuesta del servidor:', result);
                
                if (result && result.status === 'success') {
                    self._showNotification({
                        title: _t("✅ Check-In Automático Exitoso"),
                        message: `${result.message}\n📍 Coordenadas: ${coords.latitude.toFixed(6)}, ${coords.longitude.toFixed(6)}\n📏 Distancia: ${result.distance_km.toFixed(2)} km\n🎯 Precisión: ${coords.accuracy.toFixed(0)}m`,
                        type: 'success',
                    });
                    
                    // Recargar 6
                    if (self.controller && self.controller.reload) {
                        self.controller.reload();
                    }
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
        
        _showNotification: function(notification) {
            if (this.controller && this.controller.displayNotification) {
                this.controller.displayNotification(notification);
            } else {
                // Fallback para versiones diferentes de Odoo
                console.log('📢 Notificación:', notification);
                alert(notification.title + ': ' + notification.message);
            }
        }
    });
    
    // Interceptar en FormController para doble seguridad
    FormController.include({
        _onButtonClicked: function(event) {
            // Si es nuestro botón, no hacer nada (ya se maneja en FormView)
            if (event.data.attrs && event.data.attrs.class && 
                event.data.attrs.class.includes('o_geo_checkin_button')) {
                console.log('🛑 Interceptando en FormController - redirigiendo a FormView');
                return;
            }
            
            return this._super.apply(this, arguments);
        }
    });
});