import logging
import time

from sqlalchemy import text

from src.db.database import db


logger = logging.getLogger(__name__)


def verify_database_connection(app, retries=5, delay=2):
    with app.app_context():
        for attempt in range(1, retries + 1):
            try:
                db.session.execute(text("SELECT 1"))
                logger.info("Banco conectado com sucesso! ✅")
                return True

            except Exception as e:
                logger.error("Falha ao conectar ao banco 🚨")
                logger.error(
                    "Tentativa %s/%s",
                    attempt,
                    retries,
                )

                reason = str(e).splitlines()[0]
                logger.error(
                    "Motivo: %s — %s",
                    e.__class__.__name__,
                    reason,
                )

                if attempt < retries:
                    logger.warning(
                        "Aguardando %ss antes de tentar novamente...",
                        delay,
                    )
                    time.sleep(delay)
                else:
                    logger.critical("Não foi possivel conectar")
                    logger.info("Verifique:")
                    logger.info(" - Se o PostgreSQL está rodando")
                    logger.info(" - Se a porta está correta")
                    logger.info(" - Se as variáveis de ambiente estão certas")
                    raise e
