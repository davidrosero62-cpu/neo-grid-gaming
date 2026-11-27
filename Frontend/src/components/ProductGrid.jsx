import React, {useState, useEffect, use} from "react";
import { obtenerProductos, agregarAlCarrito, API_URL } from "../../services/api";
import {useNavigate} from 'react-router-dom';

/**
 * @component ProductGrid
 * @description Renderiza de forma dinamica la cuadricula de productos (Catalogo) de Neo Grid Gamning
 * Realiza una peticion HTTP GET hacia la API de Flask para consumir el inventario desde MySQL
 * e implementa el renderizado condicional en caso de que no existan articulos disponibles.
 */

function ProductGrid () {
    // Memoria interna para guardar la lista de productos.
    const [productos, setProductos] = useState([]);
    // Estado para evitar dobles clics
    const [agregandoId, setagregandoId] = useState(null);


    // Efecto para cargar los productos automaticamente al montar el componente.
    useEffect(() => {
        obtenerProductos()
        .then(data => setProductos(data))
        .catch(error => console.error(error));
    }, []);

    const handleAgregarCarrito = async (id_producto) => {
        setagregandoId(id_producto);
        try{
            await agregarAlCarrito({ id_producto, cantidad: 1});
            window.dispatchEvent(new Event("carritoActualizado"));
            alert("Producto agregado al carrito");
        } catch (error) {
            if (error.message.includes("No autenticado") || error.message.includes("inciar sesión")) {
                navigate("/login", {
                    state: {mensajeExito: "Inicia sesión para agregar productos al carrito"}
                });
            } else {
                alert(error.message);
            }
        } finally {
            setagregandoId(null);
        }
    };



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
                                    disabled={agregandoId === producto.id_producto}
                                    onClick={() => handleAgregarCarrito(producto.id_producto)}
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