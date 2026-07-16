import React from "react";

/**
 * @component Footer
 * @description Renderiza el pie de pagina institucional de Neo Grid Gaming.
 * mantiene la estetica cyberpubnk con los derechos reservados y la firma de desarrollo
 */

function Footer () {
    return (
        <footer className="footer">
           
            {/* Boton flotante Whatsapp*/}
            <a href="https://wa.me/573020000000" className="btn-whatsapp" target="_blank" rel="noopener noreferrer">
                <img src="https://upload.wikimedia.org/wikipedia/commons/6/6b/WhatsApp.svg" alt="Whatsapp" />
            </a>

            <div className="footer-info">
                <div className="contacto-detalles">
                    <p>📞 +57 3020000000</p>
                    <p>📍 Calle 38 a #13a - 24 - Villavicencio. Colombia.</p>
                    <p>🕒 Horario de Atención: de Lunes a Sábado de 11 a.m a 6 p.m</p>
                </div>

                <div className="notas-importantes">
                    <p><strong>LA SEDE</strong> es únicamente para Asesorías, Pagos Presenciales, Garantías y Soporte Técnico.</p>
                    <p><strong>RECUERDE</strong> QUE TODOS LOS PRODUCTOS SON POR DESPACHO DIRECTO A CLIENTE DESDE VILLAVICENCIO.</p>
                </div>

                <div className="politicas">
                    <h4>Políticas de Garanía y productos:</h4>
                    <a href="https//www.neogridgaming.co/refund-policy" target="_blank" rel="noopener noreferre">https://www.neogridgaming.co/refund-policy</a>
                </div>

                <div className="politicas">
                    <span>MÉTODOS DE PAGO ACEPTADOS</span>
                    <div className="logos-pago">
                        <img src="/img/mastercard.png" alt="mastercard" />
                        <img src="/img/visa.png" alt="visa" />
                        <img src="/img/epayco.png" alt="epayco"/>
                        <img src="/img/pse.png" alt="pse" />
                    </div>

                    <p>&copy; 2026 Neo Grid Gaming. Todos los derechos reservados.</p>
                </div>
            </div>
        </footer>
    );
}

export default Footer;