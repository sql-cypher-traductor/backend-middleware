"""
Servicio de envío de correos electrónicos.

Este módulo proporciona funcionalidad para enviar emails relacionados con:
- Restablecimiento de contraseña
- Notificaciones de seguridad
- Otros tipos de emails del sistema

Nota: Implementación mock para desarrollo. En producción debe integrarse
con un servicio SMTP real o API de email (SendGrid, AWS SES, etc.).
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)


class EmailService:
    """Servicio para envío de correos electrónicos (implementación mock)."""

    @staticmethod
    def send_password_reset_email(
        to_email: str,
        token: str,
        reset_url: Optional[str] = None,
    ) -> bool:
        """
        Envía email con enlace para restablecer contraseña.

        Args:
            to_email: Dirección de email del destinatario
            token: Token de restablecimiento de contraseña
            reset_url: URL base del frontend (opcional)

        Returns:
            True si el email se envió exitosamente, False en caso contrario

        Note:
            Esta es una implementación mock que solo registra el email en los logs.
            En producción debe reemplazarse con un servicio SMTP real.
        """
        # Construir URL de reset
        if reset_url is None:
            reset_url = "http://localhost:3000/reset-password"

        full_reset_url = f"{reset_url}/{token}"

        # Mock: Solo registrar en logs (en producción enviar email real)
        logger.info("=" * 80)
        logger.info("📧 MOCK EMAIL - Password Reset Request")
        logger.info("=" * 80)
        logger.info(f"To: {to_email}")
        logger.info("Subject: Restablece tu contraseña")
        logger.info("-" * 80)
        logger.info("Hola,")
        logger.info("")
        logger.info(
            "Recibimos una solicitud para restablecer la contraseña de tu cuenta."
        )
        logger.info("Para continuar, haz clic en el siguiente enlace:")
        logger.info("")
        logger.info(f"  {full_reset_url}")
        logger.info("")
        logger.info("Este enlace es válido por 30 minutos y solo puede usarse una vez.")
        logger.info("")
        logger.info(
            "Si no solicitaste restablecer tu contraseña, puedes ignorar este email."
        )
        logger.info("")
        logger.info("Saludos,")
        logger.info("El equipo de soporte")
        logger.info("=" * 80)

        # En un entorno real, aquí iría el código para enviar el email:
        # try:
        #     smtp_client.send_email(
        #         to=to_email,
        #         subject="Restablece tu contraseña",
        #         html_body=html_template,
        #         text_body=text_template
        #     )
        #     return True
        # except Exception as e:
        #     logger.error(f"Error sending email: {e}")
        #     return False

        # Mock siempre retorna True
        return True

    @staticmethod
    def send_password_changed_notification(to_email: str) -> bool:
        """
        Envía notificación de que la contraseña fue cambiada exitosamente.

        Args:
            to_email: Dirección de email del destinatario

        Returns:
            True si el email se envió exitosamente, False en caso contrario
        """
        logger.info("=" * 80)
        logger.info("📧 MOCK EMAIL - Password Changed Notification")
        logger.info("=" * 80)
        logger.info(f"To: {to_email}")
        logger.info("Subject: Tu contraseña ha sido actualizada")
        logger.info("-" * 80)
        logger.info("Hola,")
        logger.info("")
        logger.info("Tu contraseña ha sido cambiada exitosamente.")
        logger.info("")
        logger.info("Si no realizaste este cambio, contacta inmediatamente a soporte.")
        logger.info("")
        logger.info("Saludos,")
        logger.info("El equipo de soporte")
        logger.info("=" * 80)

        return True
