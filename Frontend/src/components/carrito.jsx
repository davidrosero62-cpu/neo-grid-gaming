import React, { useState, useEffect } from "react";
import { Link, useNavigate, } from "react-router-dom";
import { actualizarCantidadCarrito, eliminarItemCarrito, vaciarCarrito, API_URL, obtenerCarrito } from "../../services/api";
import "../Carrito.css";


/**
 * @component Carrito
 * @description Componente que renderiza la vista del carrito de compras de Neo Grid Gaming, permitiendo consultar los productos agregados, modificar cantidades, eliminar articulos y vaciar el carrito
 */

function Carrito() {
    const navigate = useNavigate();
    const [carrito, setCarrito] = useState({
        items: [], 
        cantidad_total: 0,
        total: 0
    });

    const [cargando, setCargando] = useState(true);
    const [procesandoId, setProcesandoId] = useState(null);

    const cargarCarrito = async () => {
        try {
            const data = await obtenerCarrito();
            setCarrito(data);
        } catch (error) {
            if (error.message.includes("No autenticado") || error.message.includes("iniciar sesión")) {
                navigate("/login", {
                    state: {mensajeExito: "Inicia sesión para ver tu carrito"}
                });
            } else {
                alert(error.message);
            }
        } finally {
            setCargando(false)
        }
    };

    useEffect(() => {
        cargarCarrito()
    }, []);

    const handleCambiarCantidad = async (id_carrito, nuevaCantidad) => {
        if (nuevaCantidad < 1) {
            return 
        }
        setProcesandoId(id_carrito);
        try {
            await actualizarCantidadCarrito({id_carrito, cantidad: nuevaCantidad });
            await cargarCarrito();
            window.dispatchEvent(new Event("carritoActualizado"))
        } catch (error) {
            alert(error.message)
        } finally {
            setProcesandoId(null);
        }
    };

    const handleEliminarItem = async (id_carrito) => {
        setProcesandoId(id_carrito);
        try{
            await eliminarItemCarrito({id_carrito});
            await cargarCarrito();
            window.dispatchEvent(new Event("carritoActualizado"))
        } catch (error) {
            alert(error.message);
        } finally {
            setProcesandoId(null);
        }
    };

    const handleVaciarCarrito = async () => {
        const confirmar = window.confirm("¿Estás seguro de que deseas vaciar el carrito?")

        if(!confirmar){
            return
        };
        setProcesandoId("all");
        try {
            await vaciarCarrito();
            await cargarCarrito();
            window.dispatchEvent(new Event("carritoActualizado"))
        } catch (error) {
            alert(error.message)
        } finally {
            setProcesandoId(null)
        }
    };

    if(cargando) {
        return (
            <section className="contenedor-carrito">
                <p className="mensaje-carga">Cargando tu carrito...</p>
            </section>
        );
    }

    return (
    <section className="contenedor-carrito">
        <h2 className="titulo-seccion">Tu Carrito de Compras</h2>

        {carrito.items.length === 0 ? (
            <div className="carrito-vacio">
                <p>No tienes productos en tu carrito.</p>
                <Link to="/" className="btn-volver-catalogo">
                    Explorar catálogo
                </Link>
            </div>
        ) : (
            <div className="carrito-contenido">
    <div className="lista-items-carrito">
        {carrito.items.map((item) => {
            const estaProcesando = procesandoId === item.id_carrito || procesandoId === "all";

            return (
                <div key={item.id_carrito} className="item-carrito">
                    <img
                        src={`${API_URL}/static/img/productos/${item.imagen}`}
                        alt={item.nombre}
                        className="item-carrito-imagen"
                    />

                    <div className="item-carrito-info">
                        <h3>{item.nombre}</h3>
                        <p>
                            Precio unitario: $
                            {Number(item.precio).toLocaleString("es-CO", {
                                minimumFractionDigits: 2
                            })}
                        </p>
                        <p>
                            Subtotal: $
                            {Number(item.subtotal).toLocaleString("es-CO", {
                                minimumFractionDigits: 2
                            })}
                        </p>
                    </div>


                    <div className="item-carrito-controles">
                        <button
                            type="button"
                            disabled={estaProcesando || item.cantidad <= 1}
                            onClick={() => handleCambiarCantidad(item.id_carrito, item.cantidad - 1)}
                        >
                            -
                        </button>

                        <span>{item.cantidad}</span>

                        <button
                            type="button"
                            disabled={estaProcesando}
                            onClick={() => handleCambiarCantidad(item.id_carrito, item.cantidad + 1)}
                        >
                            +
                        </button>

                        <button
                            type="button"
                            className="btn-eliminar-item"
                            disabled={estaProcesando}
                            onClick={() => handleEliminarItem(item.id_carrito)}
                        >
                            Eliminar
                        </button>
                    </div>
                </div>
            );
        })}

        <button
                type="button"
                className="btn-vaciar-carrito"
                disabled={procesandoId !== null}
                onClick={handleVaciarCarrito}>
                    {procesandoId === "all" ? "Vaciando...": "Vaciar Carrito"}
                </button>
    </div>

    <aside className="resumen-carrito">
        <h3>Resumen del pedido</h3>
        <p>Total de productos: {carrito.cantidad_total}</p>
        <p className="total-pagar">
            Total a pagar: $
            {Number(carrito.total).toLocaleString("es-CO",{
                minimumFractionDigits: 2
            })}
        </p>

        <div className="acciones-resumen">
            <button 
            type="button" 
            className="btn-finalizar-compra">
                Finalizar Compra
            </button>
            
            <Link to="/" className="btn-seguir-comprando">
                Seguir Comprando
            </Link>
        </div>
    </aside>
</div>
        )}
    </section>
    );
}

export default Carrito;