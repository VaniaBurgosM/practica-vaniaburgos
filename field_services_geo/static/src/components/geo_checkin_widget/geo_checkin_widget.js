// static/src/components/geo_checkin_widget/geo_checkin_widget.js
/** @odoo-module **/

import { Component, xml } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { Field } from "@web/views/fields/field"; // Para heredar de Field si quieres un widget de campo completo
import { _t } from "@web/core/l10n/translation"; // Nueva forma de importar _t
import { AlertDialog } from "@web/core/errors/error_dialogs"; // Para notificaciones

export class GeoCheckinWidget extends Field { // Extiende Field para que se comporte como un widget de campo de Odoo
    setup() {
        super.setup();
        this.orm = useService("orm"); // Nuevo servicio para llamadas RPC
        this.notification = useService("notification"); // Nuevo servicio de notificación
        this.checkin_status = 'pending'; // pending, loading, success, error
    }

    // Método para obtener el ID de la tarea
    get taskId() {
        return this.props.record.resId; // En Odoo 18, el ID está en record.resId
    }

    // Getter para la plantilla
    static template = "field_services_geo.GeoCheckinWidget"; // Referencia a la plantilla QWeb Owl

    async _updateButtonState() {
        // En Owl, _render se llama automáticamente cuando el estado cambia.
        // Aquí puedes actualizar propiedades que afecten la vista.
        // Para actualizar el texto y la clase del botón, lo haremos en la plantilla directamente con el estado.
        // O podrías tener propiedades computadas si el estado fuera más complejo.
        this.render(); // Fuerza una re-renderización del componente
    }

    async onClickCheckin(ev) { // Renombrado a onClickCheckin por convención en Owl
        ev.preventDefault();

        if (!navigator.geolocation) {
            this.notification.add(_t("Tu navegador no soporta geolocalización."), { type: "danger" });
            return;
        }

        this.checkin_status = 'loading';
        this.render(); // Actualiza el botón a "Obteniendo ubicación..."

        try {
            const position = await new Promise((resolve, reject) => {
                navigator.geolocation.getCurrentPosition(resolve, reject, {
                    enableHighAccuracy: true,
                    timeout: 15000,
                    maximumAge: 0,
                });
            });

            const latitude = position.coords.latitude;
            const longitude = position.coords.longitude;

            const result = await this.orm.call(
                'project.task',
                'action_geo_checkin',
                [[this.taskId], latitude, longitude]
            );

            if (result.status === 'success') {
                this.checkin_status = 'success';
                this.notification.add(_t("Check-In Exitoso"), {
                    message: `${result.message}\nDistancia: ${result.distance_km.toFixed(2)} km`,
                    type: "success",
                });
                // Recargar el registro para que los campos del modelo se actualicen
                await this.props.record.load(); // Vuelve a cargar el registro para ver los datos actualizados
            } else {
                this.checkin_status = 'error';
                this.notification.add(_t("No se pudo registrar el check-in."), { type: "danger" });
            }
        } catch (error) {
            this.checkin_status = 'error';
            console.error("Error durante el check-in:", error);
            this.notification.add(_t("Error al obtener la ubicación o al registrar el check-in."), {
                type: "danger",
                sticky: true, // Deja la notificación visible para depurar
            });
            // Opcional: mostrar un AlertDialog más detallado si el error es grave
            if (error instanceof GeolocationPositionError) {
                this.env.services.dialog.add(AlertDialog, {
                    body: _t("Error de geolocalización: ") + error.message,
                });
            } else {
                 this.env.services.dialog.add(AlertDialog, {
                    body: _t("Error del servidor: ") + (error.message?.data?.message || error.message || "Desconocido"),
                });
            }
        } finally {
            this.render(); // Asegura que el botón se actualice al estado final
        }
    }

    // Propiedad computada para el texto del botón
    get buttonText() {
        switch (this.checkin_status) {
            case 'loading': return _t('Obteniendo ubicación...');
            case 'success': return _t('Check-In Registrado');
            case 'error': return _t('Reintentar Check-In');
            default: return _t('Registrar Check-In');
        }
    }

    // Propiedad computada para las clases del botón
    get buttonClass() {
        switch (this.checkin_status) {
            case 'loading': return 'btn-secondary';
            case 'success': return 'btn-success';
            case 'error': return 'btn-danger';
            default: return 'btn-primary';
        }
    }

    // Propiedad computada para el estado de deshabilitado del botón
    get buttonDisabled() {
        return this.checkin_status === 'loading';
    }
}