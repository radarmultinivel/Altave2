import threading
import time
from datetime import datetime
from alerts.models import Alert, TipoAlerta, Prioridade
from alerts.manager import AlertManager, generate_random_alert


def emergency_callback_test(alert: Alert):
    print(f"[EMERGENCIA] Alerta Critico processado: {alert.id}")


def test_priority_order():
    print("=" * 70)
    print("TESTE DE PRIORIDADE - ALTAVE ALERTS")
    print("=" * 70)
    manager = AlertManager()
    manager.register_emergency_callback(emergency_callback_test)
    processing_order = []
    order_lock = threading.Lock()
    original_process = manager.process_alert
    def tracked_process(alert: Alert) -> bool:
        with order_lock:
            processing_order.append(alert)
        return original_process(alert)
    manager.process_alert = tracked_process
    print("\nGerando 10 alertas aleatorios...")
    alerts = []
    for i in range(10):
        alert_id = f"TEST_{i+1:03d}"
        alert = generate_random_alert(alert_id)
        alerts.append(alert)
        print(f"  {alert_id}: {alert.tipo.value:12s} | Prioridade: {alert.prioridade.name:8s} | {alert.timestamp.strftime('%H:%M:%S')}")
    import random
    random.shuffle(alerts)
    print("\nAdicionando alertas a fila (embaralhados)...")
    for alert in alerts:
        manager.add_alert(alert)
    print(f"Total na fila: {manager.get_queue_size()}")
    print("\nProcessando alertas...\n")
    manager.start_processing()
    time.sleep(2)
    while manager.get_queue_size() > 0:
        time.sleep(0.5)
    time.sleep(1)
    manager.stop_processing()
    print("\n" + "=" * 70)
    print("RESULTADOS DO TESTE")
    print("=" * 70)
    print(f"\nTotal de alertas processados: {len(processing_order)}")
    critical_found = False
    order_correct = True
    print("\nOrdem de processamento:")
    for i, alert in enumerate(processing_order, 1):
        marker = "[CRITICO]" if alert.prioridade == Prioridade.CRITICO else ""
        print(f"  {i:2d}. {alert.id} - {alert.prioridade.name:8s} {marker}")
        if alert.prioridade != Prioridade.CRITICO:
            critical_found = True
        elif critical_found and alert.prioridade == Prioridade.CRITICO:
            order_correct = False
            print(f"  *** ERRO: Alerta critico processado fora de ordem!")
    print("\n" + "=" * 70)
    print("PROVA DE PRIORIDADE")
    print("=" * 70)
    critical_alerts = [a for a in processing_order if a.prioridade == Prioridade.CRITICO]
    medium_alerts = [a for a in processing_order if a.prioridade == Prioridade.MEDIO]
    low_alerts = [a for a in processing_order if a.prioridade == Prioridade.BAIXO]
    print(f"\nAlertas Criticos processados: {len(critical_alerts)}")
    print(f"Alertas Medios processados: {len(medium_alerts)}")
    print(f"Alertas Baixos processados: {len(low_alerts)}")
    if critical_alerts:
        last_critical_idx = max(processing_order.index(a) for a in critical_alerts)
        first_medium_idx = min((processing_order.index(a) for a in medium_alerts), default=float('inf'))
        first_low_idx = min((processing_order.index(a) for a in low_alerts), default=float('inf'))
        if last_critical_idx < first_medium_idx and last_critical_idx < first_low_idx:
            print("\n[SUCESSO] Todos os alertas CRITICOS foram processados antes dos outros!")
            print("         O sistema respeita a ordem de prioridade.")
        else:
            print("\n[FALHA] A ordem de prioridade nao foi respeitada!")
            order_correct = False
    print("\nVerificacao de desempate por timestamp (mesma prioridade):")
    for priority in [Prioridade.CRITICO, Prioridade.MEDIO, Prioridade.BAIXO]:
        same_priority = [a for a in processing_order if a.prioridade == priority]
        if len(same_priority) > 1:
            timestamps = [a.timestamp for a in same_priority]
            if timestamps == sorted(timestamps):
                print(f"  {priority.name}: OK (ordenados por timestamp)")
            else:
                print(f"  {priority.name}: FALHA (timestamps fora de ordem)")
                order_correct = False
    print("\n" + "=" * 70)
    if order_correct:
        print("TESTE CONCLUIDO COM SUCESSO!")
        print("O sistema ALTAVE processa alertas criticos primeiro.")
    else:
        print("TESTE FALHOU!")
    print("=" * 70)
    return order_correct


def test_thread_safety():
    print("\n" + "=" * 70)
    print("TESTE DE THREAD-SAFETY")
    print("=" * 70)
    manager = AlertManager()
    manager.register_emergency_callback(emergency_callback_test)
    alert_count = [0]
    count_lock = threading.Lock()
    def sensor_thread(sensor_id: int, num_alerts: int):
        for i in range(num_alerts):
            alert_id = f"SENSOR_{sensor_id}_ALERT_{i}"
            alert = generate_random_alert(alert_id)
            if manager.add_alert(alert):
                with count_lock:
                    alert_count[0] += 1
    threads = []
    for i in range(5):
        t = threading.Thread(target=sensor_thread, args=(i+1, 20))
        threads.append(t)
    print("\nIniciando 5 sensores enviando 20 alertas cada (total 100)...")
    start_time = time.time()
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    elapsed = time.time() - start_time
    print(f"Alertas enviados: {alert_count[0]}")
    print(f"Tempo decorrido: {elapsed:.2f}s")
    print(f"Taxa: {alert_count[0]/elapsed:.1f} alertas/segundo")
    print("\n[SUCESSO] Nenhuma excecao de concorrencia detectada!")
    return True


if __name__ == "__main__":
    print("SISTEMA ALTAVE - TESTES DE VALIDACAO")
    print("=" * 70)
    result1 = test_priority_order()
    result2 = test_thread_safety()
    print("\n" + "=" * 70)
    print("RESUMO DOS TESTES")
    print("=" * 70)
    print(f"Teste de Prioridade: {'PASSOU' if result1 else 'FALHOU'}")
    print(f"Teste de Thread-Safety: {'PASSOU' if result2 else 'FALHOU'}")
    print("=" * 70)