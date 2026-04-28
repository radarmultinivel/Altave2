import logging
import threading
import time
import random
from datetime import datetime
from alerts.models import Alert, TipoAlerta, Prioridade
from alerts.manager import AlertManager, generate_random_alert


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('altave_alerts.log', encoding='utf-8')
        ]
    )


def emergency_notification_callback(alert: Alert):
    print(f"\n[NOTIFICACAO DE EMERGENCIA]")
    print(f"Alerta Critico ID: {alert.id}")
    print(f"Tipo: {alert.tipo.value}")
    print(f"Mensagem: {alert.mensagem}")
    print(f"Timestamp: {alert.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)


def simulate_sensors(manager: AlertManager, duration: int = 30):
    def sensor_worker(sensor_id: int):
        start_time = time.time()
        alert_count = 0
        while time.time() - start_time < duration:
            alert_id = f"SENSOR_{sensor_id}_{int(time.time()*1000)}"
            alert = generate_random_alert(alert_id)
            if manager.add_alert(alert):
                alert_count += 1
                logging.info(f"Sensor {sensor_id} enviou alerta {alert_id}")
            time.sleep(random.uniform(0.5, 2.0))
        logging.info(f"Sensor {sensor_id} finalizou. {alert_count} alertas enviados.")
    sensors = []
    for i in range(5):
        thread = threading.Thread(target=sensor_worker, args=(i+1,), daemon=True)
        thread.start()
        sensors.append(thread)
    time.sleep(duration)
    for sensor in sensors:
        sensor.join(timeout=2.0)
    logging.info("Simulacao de sensores finalizada")


def run_test_simulation():
    print("INICIANDO SIMULACAO DE TESTE COM 10 ALERTAS ALEATORIOS")
    print("=" * 60)
    manager = AlertManager()
    manager.register_emergency_callback(emergency_notification_callback)
    manager.start_processing()
    test_alerts = []
    for i in range(10):
        alert_id = f"TEST_{i+1:03d}"
        alert = generate_random_alert(alert_id)
        test_alerts.append(alert)
        manager.add_alert(alert)
        print(f"Alerta {alert_id} adicionado: {alert.tipo.value} | {alert.prioridade.name}")
        time.sleep(0.2)
    print(f"\nFila de alertas: {manager.get_queue_size()} alertas aguardando")
    print("Processamento em andamento...")
    time.sleep(15)
    manager.stop_processing()
    print(f"\nRESULTADOS DA SIMULACAO:")
    print(f"Alertas processados: {manager.get_processed_count()}")
    print(f"Alertas restantes na fila: {manager.get_queue_size()}")
    critical_processed = sum(1 for alert in test_alerts if alert.prioridade == Prioridade.CRITICO)
    print(f"Alertas criticos gerados: {critical_processed}")


def run_continuous_simulation():
    print("INICIANDO SIMULACAO CONTINUA DE FLUXO DE DADOS")
    print("=" * 60)
    manager = AlertManager()
    manager.register_emergency_callback(emergency_notification_callback)
    manager.start_processing()
    print("Iniciando sensores...")
    simulate_sensors(manager, duration=20)
    for i in range(10):
        time.sleep(2)
        print(f"Status: Processados={manager.get_processed_count()}, "
              f"Fila={manager.get_queue_size()}")
    manager.stop_processing()
    print(f"\nRESULTADOS FINAIS:")
    print(f"Total de alertas processados: {manager.get_processed_count()}")


def main():
    setup_logging()
    logger = logging.getLogger(__name__)
    print("Sistema ALTAVE - Gerenciador de Alertas de Missao Critica")
    print("Desenvolvido por L. A. Leandro")
    print("Data: 2026-04-27 21:15:00")
    print("=" * 60)
    try:
        run_test_simulation()
        print("\n" + "="*60)
        response = input("\nDeseja executar simulacao continua? (s/n): ").strip().lower()
        if response == 's':
            run_continuous_simulation()
        print("\nSistema ALTAVE finalizado com sucesso!")
    except KeyboardInterrupt:
        logger.info("Interrupcao do usuario recebida")
        print("\nSistema interrompido pelo usuario")
    except Exception as e:
        logger.error(f"Erro na execucao: {e}")
        print(f"\nErro: {e}")


if __name__ == "__main__":
    main()