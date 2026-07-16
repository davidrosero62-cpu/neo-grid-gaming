import React, { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import Alertas from './Alertas'; // Ajusta la ruta a tu componente Alertas
import Hero from './Hero';
import ProductGrid from './ProductGrid';

function Home() {
    const location = useLocation();
    const [alertas, setAlertas] = useState([]);

    useEffect(() => {
        if (location.state && location.state.mensajeExito) {
            setAlertas([{ texto: location.state.mensajeExito }]);
            
            // Limpiamos el historial para que no se repita el mensaje al recargar con F5
            window.history.replaceState({}, document.title);
        }
    }, [location]);

    return (
        <div className="home-container">
            {alertas.length > 0 && <Alertas mensajes={alertas} />}
            <Hero />
            <ProductGrid />
        </div>
    );
}

export default Home;