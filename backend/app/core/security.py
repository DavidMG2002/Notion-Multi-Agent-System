"""
Sistema de guardrails y moderación de contenido
"""
import hashlib
import logging
import re
from typing import Dict, List
from app.models.security_models import RiskLevel, ModerationResult
from app.config import Config

# Configurar logging de seguridad
security_logger = logging.getLogger('security')

class ContentGuardrails:
    """Sistema de guardrails y moderación de contenido"""
    
    def __init__(self):
        self.prohibited_words = {
            # Violencia explícita
            'matar', 'asesinar', 'violencia', 'atacar', 'golpear', 'lastimar',
            'herir', 'dañar', 'agredir', 'pelear', 'guerra', 'arma', 'pistola',
            'cuchillo', 'bomba', 'explotar', 'destruir', 'quemar', 'torturar',
            
            # Contenido tóxico/discriminatorio  
            'odio', 'discriminar', 'racismo', 'xenofobia', 'homofobia',
            'machismo', 'feminazi', 'terrorista', 'nazi', 'fascista',
            
            # Autolesión/suicidio
            'suicidio', 'matarse', 'autolesión', 'cortarse', 'overdosis',
            'veneno', 'ahorcarse', 'saltar', 'morir',
            
            # Actividades ilegales
            'drogas', 'marihuana', 'cocaína', 'heroína', 'traficar',
            'robar', 'hackear', 'piratear', 'falsificar', 'estafar',
            
            # Palabras ofensivas comunes
            'idiota', 'estúpido', 'imbécil', 'pendejo', 'cabrón', 'puta',
            'mierda', 'joder', 'coño'
        }
        
        # Patrones peligrosos (regex)
        self.dangerous_patterns = [
            r'\b(como|cómo)\s+(matar|asesinar|hacer\s+daño)',
            r'\b(quiero|voy\s+a)\s+(matar|lastimar|herir)',
            r'\bme\s+(quiero|voy\s+a)\s+(matar|suicidar)',
            r'\b(hacer|crear|fabricar)\s+(bomba|arma|veneno)',
            r'\b(odio\s+a|matar\s+a)\s+(todos|negros|judíos|gays)',
            r'\b(instrucciones|tutorial|guía)\s+para\s+(matar|dañar)',
            r'\bjailbreak\b|ignore\s+previous|override\s+safety',
        ]
        
        # Contextos permitidos (excepciones)
        self.allowed_contexts = {
            'educativo', 'histórico', 'académico', 'informativo', 
            'prevención', 'salud mental', 'seguridad', 'ficción'
        }
        
        # Contador de intentos sospechosos
        self.suspicious_attempts: Dict[str, int] = {}
    
    def moderate_content(self, content: str, user_id: str = "anonymous") -> ModerationResult:
        """Modera el contenido y devuelve resultado detallado"""
        
        if not content or not isinstance(content, str):
            return ModerationResult(
                is_safe=True, 
                risk_level=RiskLevel.SAFE, 
                flagged_words=[], 
                flagged_patterns=[],
                reason="Contenido vacío o inválido"
            )
        
        content_lower = content.lower().strip()
        
        # Detectar palabras prohibidas
        flagged_words = self._detect_prohibited_words(content_lower)
        
        # Detectar patrones peligrosos
        flagged_patterns = self._detect_dangerous_patterns(content_lower)
        
        # Evaluar contexto
        context_safe = self._evaluate_context(content_lower)
        
        # Calcular nivel de riesgo
        risk_level = self._calculate_risk_level(flagged_words, flagged_patterns, context_safe)
        
        # Determinar si es seguro
        is_safe = risk_level in [RiskLevel.SAFE, RiskLevel.LOW_RISK]
        
        # Sanitizar si es necesario
        sanitized_content = None
        if risk_level == RiskLevel.LOW_RISK:
            sanitized_content = self._sanitize_content(content, flagged_words)
        
        # Logging de seguridad
        if not is_safe:
            self._log_security_event(user_id, content[:100], flagged_words, flagged_patterns, risk_level)
        
        # Tracking de intentos sospechosos
        self._track_suspicious_activity(user_id, risk_level)
        
        # Generar razón
        reason = self._generate_reason(flagged_words, flagged_patterns, risk_level, context_safe)
        
        return ModerationResult(
            is_safe=is_safe,
            risk_level=risk_level,
            flagged_words=flagged_words,
            flagged_patterns=flagged_patterns,
            reason=reason,
            sanitized_content=sanitized_content
        )
    
    def _detect_prohibited_words(self, content: str) -> List[str]:
        """Detecta palabras prohibidas en el contenido"""
        return [word for word in self.prohibited_words if word in content]
    
    def _detect_dangerous_patterns(self, content: str) -> List[str]:
        """Detecta patrones peligrosos usando regex"""
        flagged = []
        for pattern in self.dangerous_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                flagged.append(pattern)
        return flagged
    
    def _evaluate_context(self, content: str) -> bool:
        """Evalúa si el contexto es educativo/seguro"""
        context_indicators = sum(1 for ctx in self.allowed_contexts if ctx in content)
        return context_indicators >= 1
    
    def _calculate_risk_level(self, flagged_words: List[str], flagged_patterns: List[str], context_safe: bool) -> RiskLevel:
        """Calcula el nivel de riesgo del contenido"""
        
        if not flagged_words and not flagged_patterns:
            return RiskLevel.SAFE
        
        if context_safe and len(flagged_words) <= 2 and not flagged_patterns:
            return RiskLevel.LOW_RISK
        
        if len(flagged_words) <= 3 and not flagged_patterns:
            return RiskLevel.LOW_RISK
        
        if flagged_patterns:
            return RiskLevel.HIGH_RISK if len(flagged_patterns) >= 2 else RiskLevel.MEDIUM_RISK
        
        if len(flagged_words) >= 5:
            return RiskLevel.HIGH_RISK
        
        return RiskLevel.MEDIUM_RISK
    
    def _sanitize_content(self, content: str, flagged_words: List[str]) -> str:
        """Sanitiza el contenido reemplazando palabras problemáticas"""
        sanitized = content
        
        replacements = {
            'matar': 'confrontar',
            'odio': 'desagrado',
            'estúpido': 'poco inteligente',
            'idiota': 'persona imprudente',
            'mierda': '[censurado]',
            'joder': '[censurado]',
        }
        
        for word in flagged_words:
            if word in replacements:
                sanitized = sanitized.replace(word, replacements[word])
            else:
                sanitized = sanitized.replace(word, '[censurado]')
        
        return sanitized
    
    def _log_security_event(self, user_id: str, content: str, flagged_words: List[str], 
                           flagged_patterns: List[str], risk_level: RiskLevel):
        """Registra eventos de seguridad"""
        user_hash = hashlib.sha256(user_id.encode()).hexdigest()[:8]
        
        security_logger.warning(
            f"CONTENT_BLOCKED - User: {user_hash}, Risk: {risk_level.value}, "
            f"Words: {len(flagged_words)}, Patterns: {len(flagged_patterns)}, "
            f"Content: {content[:50]}..."
        )
    
    def _track_suspicious_activity(self, user_id: str, risk_level: RiskLevel):
        """Rastrea actividad sospechosa por usuario"""
        if risk_level in [RiskLevel.MEDIUM_RISK, RiskLevel.HIGH_RISK]:
            if user_id not in self.suspicious_attempts:
                self.suspicious_attempts[user_id] = 0
            self.suspicious_attempts[user_id] += 1
            
            if self.suspicious_attempts[user_id] >= Config.MAX_SUSPICIOUS_ATTEMPTS:
                security_logger.critical(f"USER_BLOCKED - Multiple suspicious attempts: {user_id}")
    
    def _generate_reason(self, flagged_words: List[str], flagged_patterns: List[str], 
                        risk_level: RiskLevel, context_safe: bool) -> str:
        """Genera explicación del resultado de moderación"""
        
        if risk_level == RiskLevel.SAFE:
            return "Contenido seguro y apropiado."
        
        reasons = []
        
        if flagged_words:
            reasons.append(f"Detectadas {len(flagged_words)} palabras problemáticas")
        
        if flagged_patterns:
            reasons.append(f"Detectados {len(flagged_patterns)} patrones peligrosos")
        
        if not context_safe:
            reasons.append("Contexto potencialmente problemático")
        
        return "; ".join(reasons)
    
    def is_user_blocked(self, user_id: str) -> bool:
        """Verifica si un usuario está bloqueado"""
        return self.suspicious_attempts.get(user_id, 0) >= Config.MAX_SUSPICIOUS_ATTEMPTS
    
    def get_safety_stats(self) -> Dict:
        """Obtiene estadísticas de seguridad"""
        return {
            "prohibited_words_count": len(self.prohibited_words),
            "dangerous_patterns_count": len(self.dangerous_patterns),
            "users_with_attempts": len(self.suspicious_attempts),
            "blocked_users": sum(1 for count in self.suspicious_attempts.values() 
                               if count >= Config.MAX_SUSPICIOUS_ATTEMPTS)
        }