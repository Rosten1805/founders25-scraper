"""Excepciones específicas del pipeline.

Capturar todo con `except Exception` genérico oculta si un fallo fue un
timeout, un 404 o un error de parseo. Aquí cada capa lanza una excepción
específica para que el llamador decida (reintentar, descartar el registro,
abortar la corrida) con conocimiento real de la causa.
"""


class ScraperError(Exception):
    """Base para errores propios del scraper."""


class NonRetryableHTTPError(ScraperError):
    """Respuesta HTTP de error que no tiene sentido reintentar (ej. 404)."""

    def __init__(self, url: str, status_code: int):
        self.url = url
        self.status_code = status_code
        super().__init__(f"HTTP {status_code} no reintentable en {url}")


class CircuitBreakerOpenError(ScraperError):
    """Se alcanzó el máximo de fallos consecutivos — se aborta la corrida.

    Ver /DOCS/onboarding_scraper.md §6 (circuit breaker conceptual).
    """

    def __init__(self, consecutive_failures: int):
        self.consecutive_failures = consecutive_failures
        super().__init__(
            f"Circuit breaker abierto tras {consecutive_failures} fallos consecutivos"
        )


class RequiredFieldMissingError(ScraperError):
    """Un campo requerido del contrato de datos no pudo extraerse/normalizarse.

    Ver /DOCS/data_contract.md §1 y §4 — dispara el descarte del registro,
    no el aborto de la corrida completa.
    """

    def __init__(self, field: str, context: str):
        self.field = field
        self.context = context
        super().__init__(f"Campo requerido '{field}' faltante ({context})")
