odoo.define('crm_geo_checkin.geo_checkin', function (require) {
    "use strict";

    const FormController = require('web.FormController');
    const rpc = require('web.rpc');
    const core = require('web.core');

    const _t = core._t;

    FormController.include({
        renderView: function () {
            const self = this;

            return this._super.apply(this, arguments).then(function () {
                if (self.modelName === 'project.task') {
                    if (navigator.geolocation) {
                        navigator.geolocation.getCurrentPosition(
                            function (position) {
                                const latitude = position.coords.latitude;
                                const longitude = position.coords.longitude;
                                const now = new Date().toISOString();

                                self.model.notifyChanges(self.handle, {
                                    checkin_latitude: latitude,
                                    checkin_longitude: longitude,
                                    checkin_datetime: now,
                                });
                            },
                            function (error) {
                                self.displayNotification({
                                    title: _t("Error"),
                                    message: _t("No se pudo obtener la ubicación automáticamente: ") + error.message,
                                    type: 'danger',
                                });
                            },
                            {
                                enableHighAccuracy: true,
                                timeout: 10000,
                                maximumAge: 0,
                            }
                        );
                    }
                }
            });
        },

        _onButtonClicked: function (event) {
            const self = this;

            if (event.data.attrs.class && event.data.attrs.class.includes('o_geo_checkin_button')) {
                if (!navigator.geolocation) {
                    this.displayNotification({
                        title: _t("Error"),
                        message: _t("Tu navegador no soporta geolocalización."),
                        type: 'danger',
                    });
                    return;
                }

                navigator.geolocation.getCurrentPosition(
                    function (position) {
                        const latitude = position.coords.latitude;
                        const longitude = position.coords.longitude;

                        rpc.query({
                            model: 'project.task',
                            method: 'action_geo_checkin',
                            args: [[self.model.get(self.handle).res_id], latitude, longitude],
                        }).then(function (result) {
                            if (result.status === 'success') {
                                self.displayNotification({
                                    title: _t("Check-In Exitoso"),
                                    message: `${result.message}\nDistancia: ${result.distance_km.toFixed(2)} km`,
                                    type: 'success',
                                });
                                self.reload();
                            } else {
                                self.displayNotification({
                                    title: _t("Error"),
                                    message: _t("No se pudo registrar el check-in."),
                                    type: 'danger',
                                });
                            }
                        });
                    },
                    function (error) {
                        self.displayNotification({
                            title: _t("Error"),
                            message: _t("No se pudo obtener la ubicación: ") + error.message,
                            type: 'danger',
                        });
                    },
                    {
                        enableHighAccuracy: true,
                        timeout: 10000,
                        maximumAge: 0,
                    }
                );
            } else {
                this._super.apply(this, arguments);
            }
        }
    });
});