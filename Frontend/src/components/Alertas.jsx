import React from 'react';

/**
 *  @component Alertas
 *  @description Componente encargado de renderizar de forma dinamica las notificaciones,
 * mensajes de exito o errores enviados desde el Backend (API de Flask).
 * Reutiliza los estilos de CSS cyberpunk originales del contenedor de alertas.
 */

function Alertas ({ mensajes }) {
    return (
        <div className="contenedor-alertas" style={{maxWidth: '1200px', margin: '20px auto', padding: '0 20px'}}>
            {mensajes && mensajes.length > 0 && mensajes.map((alerta, index) => (
                <div key={index} className="alerta">
                    <i className="fas fa-info-circle" style={{color: '#00ffcc', marginRight: '10px' }}></i>
                    {alerta.texto}
                </div>
            ))}
        </div>
    );
}
export default Alertas;