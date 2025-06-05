/** @odoo-module **/

import { rpc } from "@web/core/network/rpc";

let observer = null;
let isInitialized = false;

// Función para inicializar cuando el DOM esté listo
function initializeGeoCheckin() {
    if (isInitialized || !document.body) {
        return;
    }
    
    isInitialized = true;
    console.log('Inicializando Geo Checkin...');
    
    // Crear el observer después de que document.body exista
    observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.type === 'childList') {
                // Buscar el botón en los nodos añadidos
                const addedNodes = Array.from(mutation.addedNodes);
                addedNodes.forEach(node => {
                    if (node.nodeType === Node.ELEMENT_NODE) {
                        const button = node.querySelector && node.querySelector('.get_location_button');
                        if (button && !button.dataset.geoListenerAdded) {
                            console.log('Botón detectado dinámicamente:', button);
                            setupButtonListener(button);
                        }
                    }
                });
            }
        });
    });

    // Observar cambios en el DOM solo si document.body existe
    if (document.body) {
        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
        
        // También buscar el botón si ya existe
        const existingButton = document.querySelector('.get_location_button');
        if (existingButton) {
            console.log('Botón encontrado al inicializar:', existingButton);
            setupButtonListener(existingButton);
        }
    }
    
    // Ejecutar test de geolocalización
    testGeolocation();
}



function getCrmIdFromUrl() {
    const pathParts = window.location.pathname.split('/');
    const crmIndex = pathParts.indexOf('crm');
    if (crmIndex !== -1 && pathParts.length > crmIndex + 1) {
        const id = parseInt(pathParts[crmIndex + 1]);
        if (!isNaN(id)) {
            return id;
        }
    }
    return null;
}

// Función para configurar el listener del botón
function setupButtonListener(button) {
    if (button.dataset.geoListenerAdded) {
        return;
    }
    button.dataset.geoListenerAdded = 'true';

    button.addEventListener('click', function(e) {
        e.preventDefault();
        e.stopPropagation();
        console.log('Botón de geolocalización clicked!');

        const originalText = button.textContent;
        button.textContent = 'Obteniendo ubicación...';
        button.disabled = true;

        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(
                function(position) {
                    const lat = position.coords.latitude;
                    const lng = position.coords.longitude;
                    console.log('Ubicación obtenida:', lat, lng);

                    triggerCrmLocationUpdate(getCrmIdFromUrl(), lat, lng).then(result => {
                        if (result && result.distance_km !== undefined) {
                            if (result.distance_km > 0.1) {
                                console.log('Distancia al destino:', result.distance_km, 'km');
                                alert('No se pudo realizar el checkin, estás demasiado lejos. Distancia al destino: ' + result.distance_km + ' km');
                            } else {
                                alert('Checkin realizado correctamente');
                            }
                        }

                        // Restaurar botón
                        button.textContent = originalText;
                        button.disabled = false;
                    }).catch(error => {
                        console.error('Error al actualizar CRM:', error);
                        alert('Hubo un problema al actualizar la ubicación en el CRM.');

                        button.textContent = originalText;
                        button.disabled = false;
                    });
                },
                function(error) {
                    console.error('Error obteniendo ubicación:', error);
                    alert('Error obteniendo ubicación: ' + error.message);

                    button.textContent = originalText;
                    button.disabled = false;
                },
                {
                    enableHighAccuracy: true,
                    timeout: 15000,
                    maximumAge: 300000
                }
            );
        } else {
            alert('Geolocalización no soportada por el navegador');
            button.textContent = originalText;
            button.disabled = false;
        }
    });
}

// Browser geolocation test
function testGeolocation() {
    if (navigator.geolocation) {
        console.log('🌍 Geolocalización disponible - Probando...');
        
        navigator.geolocation.getCurrentPosition(
            function(position) {
                console.log("🌍 Geolocation test successful:");
                console.log("📍 Latitud:", position.coords.latitude);
                console.log("📍 Longitud:", position.coords.longitude);
                console.log("🎯 Precisión:", position.coords.accuracy, "metros");
            },
            function(error) {
                console.warn("Geolocation test failed:");
                switch(error.code) {
                    case error.PERMISSION_DENIED:
                        console.warn("Usuario denegó la solicitud de geolocalización.");
                        break;
                    case error.POSITION_UNAVAILABLE:
                        console.warn("Información de ubicación no disponible.");
                        break;
                    case error.TIMEOUT:
                        console.warn("Tiempo de espera agotado.");
                        break;
                    default:
                        console.warn("Error desconocido:", error.message);
                        break;
                }
            },
            {
                enableHighAccuracy: false, // Menos precisión para el test
                timeout: 5000,
                maximumAge: 300000
            }
        );
    } else {
        console.error("Geolocalización no soportada en este navegador.");
    }
}

// Function to manually trigger CRM location update
function triggerCrmLocationUpdate(leadID, latitude, longitude) {
    console.log("Enviando coordenadas al CRM:", latitude, longitude);
    
    return rpc('/web/dataset/call_kw', {
        model: 'crm.lead',
        method: 'get_location',
        args: [[leadID], {
            latitude: latitude,
            longitude: longitude
        }],
        kwargs: {}
    }).then(result => {
        console.log("✅ Respuesta del CRM:", result);
        return result;
    }).catch(error => {
        console.error("❌ Error al enviar al CRM:", error);
        return null;
    });
}

// Función principal de inicialización con múltiples estrategias
function waitForDOM() {
    if (document.body) {
        initializeGeoCheckin();
    } else if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initializeGeoCheckin);
    } else {
        // Fallback: esperar un poco más
        setTimeout(() => {
            if (document.body) {
                initializeGeoCheckin();
            } else {
                console.warn('document.body aún no disponible, reintentando...');
                setTimeout(waitForDOM, 100);
            }
        }, 50);
    }
}

// Inicializar cuando sea seguro
if (typeof window !== 'undefined') {
    // Estrategia 1: Inmediata si ya está listo
    if (document.readyState === 'complete') {
        initializeGeoCheckin();
    }
    // Estrategia 2: Esperar a que esté listo
    else if (document.readyState === 'interactive' || document.readyState === 'loading') {
        waitForDOM();
    }
    // Estrategia 3: Fallback
    else {
        setTimeout(waitForDOM, 100);
    }
}

// Export para uso en consola de desarrollo
window.geoCheckinUtils = {
    testGeolocation,
    triggerCrmLocationUpdate,
    initializeGeoCheckin
};