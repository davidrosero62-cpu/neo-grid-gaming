import React, {useState, useEffect} from "react";
import { obtenerProductos, API_URL } from "../../services/api";

/**
 * @component ProductGrid
 * @description Renderiza de forma dinamica la cuadricula de productos (Catalogo) de Neo Grid Gamning
 * Realiza una peticion HTTP GET hacia la API de Flask para consumir el inventario desde MySQL
 * e implementa el renderizado condicional en caso de que no existan articulos disponibles.
 */

function ProductGrid () {
    // Memoria interna para guardar la lista de productos.
    const [productos, setProductos] = useState([]);

    // Obtenemos la URL base desde las variables de entorno de Vite o usamos localhost por defecto
    const API_URL = import.meta.env.VITE_API_URL || "http://localhost:5000";

    // Efecto para cargar los productos automaticamente al montar el componente.
    useEffect(() => {
        obtenerProductos()
        .then(data => setProductos(data))
        .catch(error => console.error(error));
    }, []);

    return (
        <section id="catalogo" className="contenedor-productos">
            <h2 className="titulo-seccion">Nuestros Productos</h2>

            <div className="grid-productos">
                {productos.length > 0 ? (
                    productos.map((producto) => (
                        <div key={producto.id_producto} className="tarjeta-producto">
                            <div className="imagen-producto">
                                <img
                                    src={`${API_URL}/static/img/productos/${producto.imagen}`}
                                    alt={producto.nombre}
                                />
                            </div>
                            <div className="info-producto">
                                <h3>{producto.nombre}</h3>
                                <p className="descripcion-corta">{producto.descripcion}</p>
                                <p className="precio">
                                    ${Number(producto.precio).toLocaleString('es-Co', { minimumFractionDigits: 2})}
                                </p>
                                {/* Boton "Agregar al carritpo"*/}
                                <button
                                    type="button"
                                    className="btn-agregar-carrito"
                                    onClick={() => console.log(`Producto ${producto.id_producto} agregado`)}
                                    >
                                    Agregar al Carrito
                                </button>
                            </div>
                        </div>
                    ))
                ) : (
                    <p className="no-productos">No hay productos disponibles...</p>
                )}
            </div>
        </section>
    );
}

export default ProductGrid;