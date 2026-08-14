"""Cliente HTTP con rate limiting, retries con backoff y circuit breaker.

Evita el anti-patrón de timeout único sin reintentos, sin delay entre
requests y sin distinción de tipo de error: aquí se clasifica cada fallo,
se reintenta solo lo reintentable, se espera entre requests por cortesía y
se aborta la corrida si hay demasiados fallos consecutivos seguidos.

Política respaldada por /DOCS/onboarding_scraper.md §6.
"""

from __future__ import annotations

import logging
import random
import time
import uuid

import requests

from scraper import config
from scraper.exceptions import CircuitBreakerOpenError, NonRetryableHTTPError

logger = logging.getLogger("scraper.http_client")


class HttpClient:
    """Envoltorio sobre requests.Session con políticas de cortesía y resiliencia."""

    def __init__(
        self,
        user_agent: str = config.USER_AGENT,
        timeout: tuple[int, int] = config.REQUEST_TIMEOUT,
        delay_range: tuple[float, float] = (config.DELAY_MIN, config.DELAY_MAX),
        max_retries: int = config.MAX_RETRIES,
    ):
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": user_agent})
        self.timeout = timeout
        self.delay_range = delay_range
        self.max_retries = max_retries
        self._consecutive_failures = 0

    def _politeness_delay(self) -> None:
        base = random.uniform(*self.delay_range)
        jitter = random.uniform(-config.JITTER, config.JITTER)
        time.sleep(max(0.0, base + jitter))

    def get(self, url: str) -> requests.Response:
        """GET con reintentos exponenciales y clasificación de errores.

        - Errores de red/timeout y 5xx/429 -> reintentables (backoff exponencial + jitter).
        - 4xx (salvo 429) -> NO reintentable, se propaga de inmediato.
        - Tras `max_retries` intentos fallidos, o si el circuit breaker está
          abierto, se propaga la última excepción.
        """
        if self._consecutive_failures >= config.CIRCUIT_BREAKER_MAX_CONSECUTIVE_FAILURES:
            raise CircuitBreakerOpenError(self._consecutive_failures)

        request_id = uuid.uuid4().hex[:8]
        last_exc: Exception | None = None

        for attempt in range(1, self.max_retries + 1):
            self._politeness_delay()
            start = time.monotonic()
            try:
                response = self.session.get(url, timeout=self.timeout)
                duration_ms = int((time.monotonic() - start) * 1000)

                if response.status_code in config.RETRYABLE_STATUS_CODES:
                    logger.warning(
                        "request_id=%s url=%s status=%s attempt=%d/%d duration_ms=%d "
                        "reason=retryable_status",
                        request_id, url, response.status_code, attempt, self.max_retries,
                        duration_ms,
                    )
                    last_exc = requests.exceptions.HTTPError(
                        f"HTTP {response.status_code}", response=response
                    )
                    self._sleep_backoff(attempt)
                    continue

                if response.status_code >= 400:
                    logger.error(
                        "request_id=%s url=%s status=%s attempt=%d duration_ms=%d "
                        "reason=non_retryable_status",
                        request_id, url, response.status_code, attempt, duration_ms,
                    )
                    self._consecutive_failures += 1
                    raise NonRetryableHTTPError(url, response.status_code)

                logger.info(
                    "request_id=%s url=%s status=%s attempt=%d duration_ms=%d",
                    request_id, url, response.status_code, attempt, duration_ms,
                )
                self._consecutive_failures = 0
                # books.toscrape.com declara UTF-8 en un <meta> HTML, no en la
                # cabecera HTTP Content-Type. requests solo detecta encoding
                # desde la cabecera HTTP; sin ella cae a ISO-8859-1 por RFC
                # 2616 y corrompe cualquier caracter no-ASCII (£, comillas
                # tipográficas, tildes) al leer .text. Se fuerza UTF-8, que es
                # el encoding real y verificado del sitio (ver
                # /DOCS/onboarding_scraper.md).
                response.encoding = "utf-8"
                return response

            except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as exc:
                duration_ms = int((time.monotonic() - start) * 1000)
                logger.warning(
                    "request_id=%s url=%s attempt=%d/%d duration_ms=%d "
                    "reason=%s error=%s",
                    request_id, url, attempt, self.max_retries, duration_ms,
                    type(exc).__name__, exc,
                )
                last_exc = exc
                self._sleep_backoff(attempt)

        self._consecutive_failures += 1
        logger.error(
            "request_id=%s url=%s exhausted_retries=%d consecutive_failures=%d",
            request_id, url, self.max_retries, self._consecutive_failures,
        )
        assert last_exc is not None
        raise last_exc

    @staticmethod
    def _sleep_backoff(attempt: int) -> None:
        backoff = config.BACKOFF_BASE_SECONDS ** attempt
        jitter = random.uniform(0, 1)
        time.sleep(backoff + jitter)

    def close(self) -> None:
        self.session.close()

    def __enter__(self) -> "HttpClient":
        return self

    def __exit__(self, *exc_info) -> None:
        self.close()
