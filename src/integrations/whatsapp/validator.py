
"""
BestStag v9.1 - Validador de Assinatura WhatsApp
Implementa validação segura de assinatura HMAC-SHA256 para webhooks WhatsApp
"""

import hmac
import hashlib
import logging
from typing import Union

logger = logging.getLogger('beststag.integrations.whatsapp.validator')


class SignatureValidator:
    """
    Validador de assinatura para webhooks WhatsApp Cloud API
    
    Implementa validação HMAC-SHA256 conforme especificação do WhatsApp
    """
    
    def __init__(self, webhook_secret: str):
        """
        Inicializa o validador
        
        Args:
            webhook_secret: Secret compartilhado configurado no WhatsApp
        """
        if not webhook_secret:
            raise ValueError("Webhook secret é obrigatório")
        
        self.webhook_secret = webhook_secret.encode('utf-8')
        logger.info("Validador de assinatura WhatsApp inicializado")
    
    def generate_signature(self, payload: Union[str, bytes]) -> str:
        """
        Gera assinatura HMAC-SHA256 para um payload
        
        Args:
            payload: Dados para assinar
            
        Returns:
            Assinatura no formato 'sha256=<hash>'
        """
        if isinstance(payload, str):
            payload = payload.encode('utf-8')
        
        # Calcular HMAC-SHA256
        signature = hmac.new(
            key=self.webhook_secret,
            msg=payload,
            digestmod=hashlib.sha256
        ).hexdigest()
        
        return f"sha256={signature}"
    
    def validate_signature(self, payload: Union[str, bytes], received_signature: str) -> bool:
        """
        Valida assinatura recebida contra payload
        
        Args:
            payload: Dados recebidos
            received_signature: Assinatura recebida no header
            
        Returns:
            True se assinatura é válida, False caso contrário
        """
        try:
            # Gerar assinatura esperada
            expected_signature = self.generate_signature(payload)
            
            # Comparação segura contra timing attacks
            is_valid = hmac.compare_digest(expected_signature, received_signature)
            
            if is_valid:
                logger.debug("Assinatura validada com sucesso")
            else:
                logger.warning(
                    f"Assinatura inválida - Esperada: {expected_signature[:20]}..., "
                    f"Recebida: {received_signature[:20]}..."
                )
            
            return is_valid
            
        except Exception as e:
            logger.error(f"Erro na validação de assinatura: {e}")
            return False
    
    def validate_webhook_request(self, body: bytes, signature_header: str) -> bool:
        """
        Valida requisição completa de webhook
        
        Args:
            body: Body da requisição HTTP
            signature_header: Header X-Hub-Signature-256
            
        Returns:
            True se válida, False caso contrário
        """
        if not signature_header:
            logger.warning("Header de assinatura ausente")
            return False
        
        if not signature_header.startswith('sha256='):
            logger.warning(f"Formato de assinatura inválido: {signature_header}")
            return False
        
        return self.validate_signature(body, signature_header)


def create_validator(webhook_secret: str) -> SignatureValidator:
    """
    Factory function para criar validador
    
    Args:
        webhook_secret: Secret do webhook
        
    Returns:
        Instância do validador
    """
    return SignatureValidator(webhook_secret)


# Exemplo de uso
if __name__ == "__main__":
    # Teste do validador
    secret = "meu_webhook_secret_super_seguro"
    validator = SignatureValidator(secret)
    
    # Teste com payload de exemplo
    test_payload = '{"test": "data"}'
    signature = validator.generate_signature(test_payload)
    
    print(f"Payload: {test_payload}")
    print(f"Assinatura: {signature}")
    print(f"Validação: {validator.validate_signature(test_payload, signature)}")
    
    # Teste com assinatura inválida
    invalid_signature = "sha256=invalid_hash"
    print(f"Validação inválida: {validator.validate_signature(test_payload, invalid_signature)}")
