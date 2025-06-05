// static/src/js/field_services.js
/** @odoo-module **/

import { registry } from "@web/core/registry";
import { GeoCheckinWidget } from "@field_services_geo/components/geo_checkin_widget/geo_checkin_widget"; // Importa tu componente Owl

// Registra el widget de campo
registry.category("fields").add("geo_checkin_widget", GeoCheckinWidget);