# Análise de Resultados — `resultados/calcular/`

Esta pasta contém os dados coletados durante os experimentos e os scripts Python
que os processam para gerar os gráficos e tabelas (apêndices) presentes no artigo.

---

## Estrutura de Dados

```
resultados/calcular/
│
├── sem edge ai/                  # Dados do cenário BASE (sem visão computacional)
│   ├── Local/                    # Broker rodando na mesma máquina
│   │   ├── resultados_Franka.csv
│   │   ├── resultados_youBot.csv
│   │   ├── resultados_UR10.csv
│   │   └── resultados_sensor.csv
│   ├── Edison/                   # Broker em Intel Edison (edge server)
│   │   ├── resultados_Franka_Edison.csv
│   │   ├── resultados_youBot_Edison.csv
│   │   ├── resultados_UR10_Edison.csv
│   │   └── resultados_sensor_Edison.csv
│   └── Nuvem/                    # Broker em instância AWS EC2
│       ├── resultados_FrankaNuvem.csv
│       ├── resultados_youBotNuvem.csv
│       ├── resultados_UR10Nuvem.csv
│       └── resultados_sensorNuvem.csv
│
├── com edge ai/                  # Dados e scripts do cenário COM Edge AI (ESP32-S3)
│   ├── cnn_autoral/              # CNN projetada do zero (modelo principal do artigo)
│   │   ├── local/
│   │   │   ├── resultados_Cam.csv
│   │   │   ├── resultados_Franka.csv
│   │   │   ├── resultados_UR10.csv
│   │   │   ├── resultados_youBot.csv
│   │   │   ├── resultados_sensor.csv
│   │   │   └── metricas_esp.csv  ← métricas de inferência do ESP32
│   │   ├── edison/               # mesmos arquivos
│   │   └── aws/                  # mesmos arquivos
│   ├── v2/
│   │   └── metricas_esp.csv      ← inferência MobileNetV2 no ESP32
│   ├── v3/
│   │   └── metricas_esp.csv      ← inferência MobileNetV3 no ESP32
│   └── gerar_resultados.py       # ★ Gráficos e CSV de métricas (executar daqui)
│
├── gerar_apendices.py            # Apêndices A, B e C em PDF
├── gerar_brutos.py               # Apêndices D e E (dados brutos linha a linha) em PDF
├── requirements.txt              # Dependências Python para os scripts
└── apendices_pdf/                # [Gerado automaticamente] PDFs dos apêndices
```

---

## Formato dos CSVs

### `resultados_<Agente>.csv` (tópicos dos robôs)
| Coluna | Tipo | Descrição |
|---|---|---|
| `Robo_Publicador` | str | Agente que publicou a mensagem |
| `Robo_Assinante` | str | Agente que recebeu a mensagem |
| `Topico` | str | Tópico MQTT (ex: `/entregador/coletaDisponivel`) |
| `Latencia_ms` | float | Tempo de entrega da mensagem em milissegundos |

### `metricas_esp.csv` (métricas de inferência do ESP32)
| Coluna | Tipo | Descrição |
|---|---|---|
| `timestamp_logger` | float | Timestamp Unix (host) no momento do recebimento |
| `id_publicador` | str | Identificador do ESP32 |
| `modelo` | str | Nome do modelo TFLite embarcado |
| `timestamp_envio` | float | Timestamp Unix (host) quando a imagem foi enviada |
| `timestamp_recebido` | float | `millis()` do ESP desde o boot (≠ Unix epoch) |
| `latencia_ms` | float | ⚠ **Campo inválido** — diferença entre relógios diferentes |
| `tempo_inferencia_ms` | float | Tempo de inferência medido internamente no ESP32 |
| `resultado` | int | Classe predita (0 = rejeitado, 1 = aprovado) |

> **⚠ Nota sobre `latencia_ms`:** O campo bruto `latencia_ms` no `metricas_esp.csv`
> é calculado pelo ESP32 como `timestamp_recebido - timestamp_envio`, onde
> `timestamp_recebido` é `millis()` (ms desde o boot) e `timestamp_envio` é
> Unix epoch × 1000. A diferença de referencial torna este campo **inválido para
> medir latência de rede**. A latência real do tópico `/esp/classificar` é
> calculada pelos scripts como:
> ```
> latencia_real_ms = (timestamp_logger − timestamp_envio) × 1000
> ```

---

## Sobre o Cenário "Sem Edge AI"

Os dados em `sem edge ai/` foram coletados em um experimento separado, sem a
presença da câmera ou do ESP32, registrando apenas a latência de comunicação
MQTT entre os agentes robóticos. O código fonte desse experimento está disponível
no repositório auxiliar:

> **🔗 Repositório sem Edge AI:** https://github.com/Keltonmd/Multiagentes

Esses dados servem como **linha de base** para comparação com os resultados
obtidos com a adição da visão computacional embarcada.

---

## Como Executar

### 1. Instalar as dependências

```bash
cd resultados/calcular
pip install -r requirements.txt
```

### 2. Gerar gráficos e CSV de métricas (Com Edge AI)

Gera `grafico1_inferencia_modelos.png`, `grafico2_mediana_latencia.png`,
`grafico3_jitter.png` e `metricas_topicos_final.csv` dentro de `com edge ai/`:

```bash
cd "resultados/calcular/com edge ai"
python gerar_resultados.py
```

### 3. Gerar Apêndices A, B e C em PDF

Gera tabelas de métricas consolidadas (mediana e jitter) em `apendices_pdf/`:

```bash
cd resultados/calcular
python gerar_apendices.py
```

### 4. Gerar Apêndices D e E em PDF (dados brutos)

Gera tabelas com cada medição individual em `apendices_pdf/`:

```bash
cd resultados/calcular
python gerar_brutos.py
```

---

## Saídas Geradas

| Arquivo | Script | Descrição |
|---|---|---|
| `com edge ai/grafico1_inferencia_modelos.png` | `gerar_resultados.py` | Tempo mediano de inferência por modelo |
| `com edge ai/grafico2_mediana_latencia.png` | `gerar_resultados.py` | Latência mediana por tópico/cenário |
| `com edge ai/grafico3_jitter.png` | `gerar_resultados.py` | Jitter por tópico/cenário |
| `com edge ai/metricas_topicos_final.csv` | `gerar_resultados.py` | Tabela consolidada de métricas |
| `apendices_pdf/apendice_A_sem_edge_ai.pdf` | `gerar_apendices.py` | Tabela sem Edge AI |
| `apendices_pdf/apendice_B_com_edge_ai.pdf` | `gerar_apendices.py` | Tabela com Edge AI |
| `apendices_pdf/apendice_C_inferencia_esp32.pdf` | `gerar_apendices.py` | Inferência por modelo |
| `apendices_pdf/apendice_D_brutos_sem_edge.pdf` | `gerar_brutos.py` | Dados brutos sem Edge AI |
| `apendices_pdf/apendice_E_brutos_com_edge.pdf` | `gerar_brutos.py` | Dados brutos com Edge AI |
