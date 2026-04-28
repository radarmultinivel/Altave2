# ALTAVE Alerts - Sistema de Gerenciamento de Alertas de Missao Critica

## Ideia
Sistema para gerenciamento de alertas de missao critica, priorizando alertas criticos, com fila thread-safe, processamento ordenado e suporte a multiplos sensores simulados.

## Requisitos
- Python 3.7 ou superior
- Bibliotecas padrao do Python (sem dependencias externas)

## Especificacoes Tecnicas

### Estrutura do Projeto
```
altave_alerts/
|-- main.py              # Ponto de entrada, simulacao e informacoes do desenvolvedor
|-- test_alerts.py       # Testes de prioridade e thread-safety
|-- requirements.txt     # Vazio (sem dependencias externas)
|-- alerts/
|   |-- __init__.py      # Exporta classes principais
|   |-- models.py        # Definicao de Alert, TipoAlerta, Prioridade
|   |-- manager.py       # AlertManager, geracao de alertas e logica de fila
```

### Classes Principais

#### Alert (dataclass)
- Atributos: id (str), timestamp (datetime), tipo (TipoAlerta), prioridade (Prioridade), mensagem (str)
- Validacao em `__post_init__`: tipos corretos e strings nao vazias
- Ordenacao via `__lt__`: compara prioridade, depois timestamp

#### TipoAlerta (Enum)
- MOVIMENTACAO: "Movimentacao"
- CALOR: "Calor"

#### Prioridade (Enum)
- CRITICO = 1 (mais alto)
- MEDIO = 2
- BAIXO = 3

#### AlertManager
- Fila `queue.PriorityQueue` thread-safe
- Metodos:
  - `add_alert(alert)`: adiciona alerta com tupla (prioridade, timestamp, contador, alerta)
  - `get_next_alert(timeout)`: recupera proximo alerta
  - `process_alert(alert)`: processa alerta, dispara callback se critico
  - `start_processing()`: inicia thread de processamento
  - `stop_processing()`: para thread
  - `register_emergency_callback(callback)`: define funcao para alertas criticos
- Contador thread-safe para desempate de alertas com mesma prioridade e timestamp

### Fluxograma de Funcionamento

```
[SENSOR] --gera alerta--> [AlertManager.add_alert]
                               |
                               v
                        [PriorityQueue]
                               |
                               v
                    [Thread de Processamento]
                               |
                               v
                        [AlertManager.process_alert]
                               |
                +--------------+--------------+
                |                             |
         prioridade == CRITICO?         prioridade != CRITICO
                |                             |
                v                             v
         [emergency_callback]           [log processamento]
                |                             |
                +--------------+--------------+
                               |
                               v
                        [proximo alerta]
```

## Instrucoes de Execucao
1. Navegue ate o diretorio do projeto:
   ```bash
   cd altave_alerts
   ```
2. Executar simulacao principal:
   ```bash
   python main.py
   ```
   O sistema exibira:
   - Nome do sistema, desenvolvedor e data
   - Simulacao com 10 alertas aleatorios
   - Pergunta se deseja simulacao continua
3. Executar testes de validacao:
   ```bash
   python test_alerts.py
   ```
   Testes verificam:
   - Ordem de prioridade (criticos primeiro)
   - Thread-safety com multiplos sensores

## Exemplos de Saida

### main.py
```
Sistema ALTAVE - Gerenciador de Alertas de Missao Critica
Desenvolvido por L. A. Leandro
Data: 2026-04-27 21:15:00
============================================================
INICIANDO SIMULACAO DE TESTE COM 10 ALERTAS ALEATORIOS
...
```

### test_alerts.py
```
SISTEMA ALTAVE - TESTES DE VALIDACAO
======================================================================
TESTE DE PRIORIDADE - ALTAVE ALERTS
...
[SUCESSO] Todos os alertas CRITICOS foram processados antes dos outros!
======================================================================
TESTE DE THREAD-SAFETY
...
[SUCESSO] Nenhuma excecao de concorrencia detectada!
======================================================================
RESUMO DOS TESTES
Teste de Prioridade: PASSOU
Teste de Thread-Safety: PASSOU
======================================================================
```

## Logging
- Logs sao gravados em `altave_alerts.log` com formato de data, nome, nivel e mensagem.
- Nivel de log: INFO (configuravel em `setup_logging`).

## Consideracoes Finais
- Sistema expandivel para novos tipos de alertas e sensores.
- Uso de fila de prioridade garante O(log n) para insercao e remocao.
- Thread-safety garantida por mecanismos nativos do Python.