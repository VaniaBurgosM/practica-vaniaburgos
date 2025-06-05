odoo.define('crm_geo_checkin.geo_widget', function (require) {
    "use strict";

    const AbstractField = require('web.AbstractField');
    const fieldRegistry = require('web.field_registry');
    const rpc = require('web.rpc');
    const core = require('web.core');

    const _t = core._t;

    const GeoCheckinWidget = AbstractField.extend({
        template: 'GeoCheckinWidget',
        events: {
            'click .o_geo_checkin_btn': '_onCheckinClick',
        },

        init: function () {
            this._super.apply(this, arguments);
            this.checkin_status = 'pending'; // pending, loading, success, error
        },

        _render: function () {
            this._super.apply(this, arguments);
            this._updateButtonState();
        },

        _updateButtonState: function () {
            const $button = this.$('.o_geo_checkin_btn');
            const $status = this.$('.o_checkin_status');
            
            $button.removeClass('btn-primary btn-secondary btn-success btn-danger');
            
            switch (this.checkin_status) {
                case 'loading':
                    $button.addClass('btn-secondary').prop('disabled', true);
                    $button.text(_t('Obteniendo ubicación...'));
                    break;
                case 'success':
                    $button.addClass('btn-success').prop('disabled', false);
                    $button.text(_t('Check-In Registrado'));
                    break;
                case 'error':
                    $button.addClass('btn-danger').prop('disabled', false);
                    $button.text(_t('Reintentar Check-In'));
                    break;
                default:
                    $button.addClass('btn-primary').prop('disabled', false);
                    $button.text(_t('Registrar Check-In'));
            }
        },

        _onCheckinClick: function (event) {
            event.preventDefault();
            const self = this;

            if (!navigator.geolocation) {
                this.displayNotification({
                    title: _t("Error"),
                    message: _t("Tu navegador no soporta geolocalización."),
                    type: 'danger',
                });
                return;
            }

            this.checkin_status = 'loading';
            this._updateButtonState();

            navigator.geolocation.getCurrentPosition(
                function (position) {
                    const latitude = position.coords.latitude;
                    const longitude = position.coords.longitude;

                    rpc.query({
                        model: 'project.task',
                        method: 'action_geo_checkin',
                        args: [[self.res_id], latitude, longitude],
                    }).then(function (result) {
                        if (result.status === 'success') {
                            self.checkin_status = 'success';
                            self._updateButtonState();
                            
                            self.displayNotification({
                                title: _t("Check-In Exitoso"),
                                message: `${result.message}\nDistancia: ${result.distance_km.toFixed(2)} km`,
                                type: 'success',
                            });
                            
                            // Recargar el formulario para mostrar datos actualizados
                            self.trigger_up('reload');
                        } else {
                            self.checkin_status = 'error';
                            self._updateButtonState();
                            
                            self.displayNotification({
                                title: _t("Error"),
                                message: _t("No se pudo registrar el check-in."),
                                type: 'danger',
                            });
                        }
                    }).catch(function (error) {
                        self.checkin_status = 'error';
                        self._updateButtonState();
                        
                        self.displayNotification({
                            title: _t("Error"),
                            message: _t("Error del servidor: ") + (error.message || 'Error desconocido'),
                            type: 'danger',
                        });
                    });
                },
                function (error) {
                    self.checkin_status = 'error';
                    self._updateButtonState();
                    
                    self.displayNotification({
                        title: _t("Error"),
                        message: _t("No se pudo obtener la ubicación: ") + error.message,
                        type: 'danger',
                    });
                },
                {
                    enableHighAccuracy: true,
                    timeout: 15000,
                    maximumAge: 0,
                }
            );
        },
    });

    fieldRegistry.add('geo_checkin_widget', GeoCheckinWidget);

    return GeoCheckinWidget;
});