import React from 'react';


/**
 * @component Hero
 * @description Renderiza el banner principal de impacto visual (Hero Section) de Neo Grid Gaming.
 * Porporciona un llamdo a la accior (CTA) mediante un boton con anclaje directo
 * hacia la seccion del catalogo de productos.
 */

function Hero() {
    return (
       <section className="hero">
            
                <div className="hero-contenido">
                    <button
                        type="button"
                        className='boton-catalogo'
                        >
                            Ver Catálogo
                        </button>
                </div>
        </section>
    );
}

export default Hero;



