import threading
import queue
import random
import time
import logging
from datetime import datetime, timedelta
from typing import Optional, Callable
from .models import Alert, TipoAlerta, Prioridade

logger = logging.getLogger(__name__)

class AlertManager:
    def __init__(self, max_size: int = 1000):
        self.alert_queue = queue.PriorityQueue(maxsize=max_size)
        self.processed_count = 0
        self.lock = threading.Lock()
        self.emergency_callback = None
        self.running = False
        self.processor_thread = None
        self._counter = 0
        self._counter_lock = threading.Lock()
        logger.info("AlertManager inicializado com fila de prioridade thread-safe")

    def register_emergency_callback(self, callback: Callable[[Alert], None]):
        self.emergency_callback = callback
        logger.info("Callback de emergência registrado")

    def add_alert(self, alert: Alert) -> bool:
        try:
            if not isinstance(alert, (Alert,)):
                raise TypeError("O objeto deve ser do tipo Alert")
            with self._counter_lock:
                self._counter += 1
                counter = self._counter
            priority_tuple = (
                alert.prioridade.value,
                alert.timestamp.timestamp(),
                counter,
                alert
            )
            self.alert_queue.put(priority_tuple)
            logger.info(f"Alerta adicionado à fila: {alert.id}")
            return True
        except queue.Full:
            logger.error("Fila de alertas cheia - alerta descartado")
            return False

    def get_next_alert(self, timeout: Optional[float] = None) -> Optional[Alert]:
        try:
            priority_tuple = self.alert_queue.get(timeout=timeout)
            alert = priority_tuple[3]
            logger.debug(f"Alerta recuperado da fila: {alert.id}")
            return alert
        except queue.Empty:
            logger.debug("Nenhum alerta disponível na fila")
            return None
        except Exception as e:
            logger.error(f"Erro ao recuperar alerta: {e}")
            return None

    def process_alert(self, alert: Alert) -> bool:
        with self.lock:
            self.processed_count += 1
        logger.info(f"Processando alerta #{self.processed_count}: {alert}")
        if alert.prioridade == Prioridade.CRITICO and self.emergency_callback:
            try:
                self.emergency_callback(alert)
                logger.warning(f"NOTIFICACAO DE EMERGENCIA disparada para alerta {alert.id}")
            except Exception as e:
                logger.error(f"Erro na notificacao de emergencia: {e}")
        time.sleep(0.1)
        logger.info(f"Alerta {alert.id} processado com sucesso")
        return True

    def start_processing(self):
        if self.running:
            logger.warning("Processador já está em execução")
            return
        self.running = True
        self.processor_thread = threading.Thread(target=self._process_loop, daemon=True)
        self.processor_thread.start()
        logger.info("Processador de alertas iniciado")

    def stop_processing(self):
        self.running = False
        if self.processor_thread:
            self.processor_thread.join(timeout=5)
        logger.info("Processador de alertas parado")

    def _process_loop(self):
        logger.info("Iniciando loop de processamento")
        while self.running:
            alert = self.get_next_alert(timeout=1.0)
            if alert:
                self.process_alert(alert)
        logger.info("Loop de processamento finalizado")

    def get_queue_size(self) -> int:
        return self.alert_queue.qsize()

    def get_processed_count(self) -> int:
        return self.processed_count

    def clear_queue(self):
        with self.alert_queue.mutex:
            self.alert_queue.queue.clear()
        logger.info("Fila de alertas limpa")


def generate_random_alert(alert_id: str) -> Alert:
    tipos = list(TipoAlerta)
    prioridades = list(Prioridade)
    timestamp = datetime.now() - timedelta(
        hours=random.randint(0, 24),
        minutes=random.randint(0, 59),
        seconds=random.randint(0, 59)
    )
    tipo = random.choice(tipos)
    prioridade = random.choice(prioridades)
    if tipo == TipoAlerta.MOVIMENTACAO:
        mensagens = [
            "Movimentacao detectada na area restrita Zona A",
            "Presenca nao autorizada na entrada principal",
            "Movimento suspeito no perimetro sul",
            "Vestigios de intrusao detectados no setor B"
        ]
    else:
        mensagens = [
            "Anomalia termica detectada no equipamento CR-4",
            "Temperatura acima do limite normal no servidor room",
            "Alerta de superaquecimento na unidade de refrigeracao",
            "Leituras de calor incomuns no setor de armazenamento"
        ]
    mensagem = random.choice(mensagens)
    return Alert(
        id=alert_id,
        timestamp=timestamp,
        tipo=tipo,
        prioridade=prioridade,
        mensagem=mensagem
    )