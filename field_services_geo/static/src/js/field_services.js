odoo.define('field_services_geo.geo_checkin', function (require) {
    "use strict";
    
    const FormController = require('web.FormController');
    const rpc = require('web.rpc');
    const core = require('web.core');
    const _t = core._t; 
    
    FormController.include({
        _onButtonClicked(event) {
            const self = this;
            
            // Detecta el botón
            if (event.data.attrs.class === 'o_geo_checkin_button') {
                
                // Verificar soporte de geolocalización
                if (!navigator.geolocation) {
                    this.displayNotification({
                        title: _t("Error"),
                        message: _t("Tu navegador no soporta geolocalización."),
                        type: 'danger',
                    });
                    return;
                }
                
                this.displayNotification({
                    title: _t("Ubicación"),
                    message: _t("Obteniendo ubicación..."),
                    type: 'info',
                });
                
                const options = {
                    enableHighAccuracy: true,
                    timeout: 15000, //Más tiempo para GPS
                    maximumAge: 40000 //
                };
                
                navigator.geolocation.getCurrentPosition(
                    function (position) {
                        const latitude = position.coords.latitude;
                        const longitude = position.coords.longitude;
                        const accuracy = position.coords.accuracy;
                        
                        // Verificar precisión
                        if (accuracy > 100) {
                            self.displayNotification({
                                title: _t("Advertencia"),
                                message: _t(`Precisión baja: ${accuracy.toFixed(0)}m. ¿Continuar?`),
                                type: 'warning',
                            });
                        }
                        
                        // Verificar que existe el ID del registro
                        const recordId = self.initialState && self.initialState.data && self.initialState.data.id;
                        if (!recordId) {
                            self.displayNotification({
                                title: _t("Error"),
                                message: _t("No se pudo identificar el registro actual."),
                                type: 'danger',
                            });
                            return;
                        }
                        
                        // Llamada RPC 
                        rpc.query({
                            model: 'project.task',
                            method: 'action_geo_checkin',
                            args: [[recordId], latitude, longitude],
                            kwargs: {
                                accuracy: accuracy,
                                timestamp: new Date().toISOString()
                            }
                        }).then(function (result) {
                            if (result && result.status === 'success') {
                                self.displayNotification({
                                    title: _t("Check-In Exitoso"),
                                    message: `${result.message}\nDistancia: ${result.distance_km.toFixed(2)} km\nPrecisión: ${accuracy.toFixed(0)}m`,
                                    type: 'success',
                                });
                                self.reload(); // Refresca el formulario
                            } else {
                                self.displayNotification({
                                    title: _t("Error"),
                                    message: result && result.message ? result.message : _t("No se pudo registrar el check-in."),
                                    type: 'danger',
                                });
                            }
                        }).catch(function (error) {
                            // Manejo de errores RPC
                            console.error('Error en RPC:', error);
                            self.displayNotification({
                                title: _t("Error de Conexión"),
                                message: _t("Error al comunicarse con el servidor: ") + (error.message || error.data?.message || 'Error desconocido'),
                                type: 'danger',
                            });
                        });
                    },
                    function (error) {
                        // Manejo de errores de geolocalización
                        let errorMessage = _t("Error desconocido");
                        
                        switch (error.code) {
                            case error.PERMISSION_DENIED:
                                errorMessage = _t("Permiso de ubicación denegado, permite el acceso a la ubicación.");
                                break;
                            case error.POSITION_UNAVAILABLE:
                                errorMessage = _t("Información de ubicación no disponible. Verifica tu conexión GPS.");
                                break;
                            case error.TIMEOUT:
                                errorMessage = _t("Tiempo agotado para obtener la ubicación. Inténtalo nuevamente.");
                                break;
                            default:
                                errorMessage = _t("Error al obtener ubicación: ") + error.message;
                        }
                        
                        self.displayNotification({
                            title: _t("Error de Geolocalización"),
                            message: errorMessage,
                            type: 'danger',
                        });
                    },
                    options
                );
            } else {
                //Llamar al método padre 
                return this._super.apply(this, arguments);
            }
        }
    });
});