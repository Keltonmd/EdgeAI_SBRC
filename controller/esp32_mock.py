"""
esp32_mock.py — Simulação software do firmware embarcado ESP32-S3
=================================================================
Replica fielmente o comportamento do firmware C++ (esp32/main/main_functions.cc),
permitindo validar o sistema completo sem hardware físico.

Protocolo idêntico ao da placa real:
  ENTRADA  → tópico /esp/classificar
             payload binário: [8 bytes int64 LE timestamp_μs] + [3072 bytes int8 imagem 32x32 RGB]

  SAÍDA 1  → tópico /esp/resultado
             {"resultado": <int>, "timestamp_envio": <float_unix>}

  SAÍDA 2  → tópico /esp/metricas
             {"id_publicador": "esp32", "modelo": "CNN_32x32_v1",
              "timestamp_envio": <float_unix>, "timestamp_recebido": <float_unix>,
              "latencia_ms": <float>, "tempo_inferencia_ms": <float>,
              "resultado": <int>}

  ENCERRAMENTO → /colaboracao/fim  (mesmo tópico que a placa observa)

Diferenças intencionais em relação à placa física:
  • Usa tflite-runtime (CPU) em vez de TFLite Micro (Xtensa LX7 @ 240 MHz)
    → tempo de inferência será diferente; o campo tempo_inferencia_ms reflete
      o tempo real do mock, não do ESP32
  • timestamp_recebido usa time.time() (Unix epoch) em vez de esp_timer_get_time()
    (μs desde o boot) — isso mantém a compatibilidade com logger_esp.py e
    gerar_resultados.py, que já corrigem esse campo
  • Não há limitação de memória (sem arena de 64 KB)

Dependências:
    pip install tflite-runtime paho-mqtt python-dotenv

Uso:
    # Com arquivo .env na raiz do repositório (recomendado):
    cp .env.example .env   # edite com suas credenciais
    python3 controller/esp32_mock.py

    # Ou com variáveis de ambiente diretamente:
    MQTT_USER=usuario MQTT_PASSWORD=senha python3 controller/esp32_mock.py
"""

import json
import os
import struct
import time
import numpy as np
import paho.mqtt.client as mqtt

# Carrega variáveis de ambiente de um .env se presente
try:
    from dotenv import load_dotenv
    load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))
except ImportError:
    pass  # python-dotenv opcional; variáveis de ambiente também funcionam

# ==========================================================================
# CONFIGURAÇÃO (via .env ou variáveis de ambiente)
# ==========================================================================
MQTT_BROKER   = os.environ.get("MQTT_BROKER",   "localhost")
MQTT_PORT     = int(os.environ.get("MQTT_PORT",  "1883"))
MQTT_USER     = os.environ.get("MQTT_USER",     "SEU_USUARIO")
MQTT_PASSWORD = os.environ.get("MQTT_PASSWORD", "SUA_SENHA")

# Caminho do modelo TFLite — relativo à raiz do repositório
_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
MODEL_PATH = os.environ.get(
    "MODEL_PATH",
    os.path.join(_ROOT, "modelos", "modelo_Inteira.tflite")
)

# Tópicos MQTT — idênticos ao firmware C++
TOPICO_CLASSIFICAR = "/esp/classificar"
TOPICO_RESULTADO   = "/esp/resultado"
TOPICO_METRICAS    = "/esp/metricas"
TOPICO_FIM         = "/colaboracao/fim"

# Identificação do mock (igual ao campo do firmware)
ID_PUBLICADOR = "esp32"
NOME_MODELO   = "CNN_32x32_v1"

# Tamanho esperado do payload de imagem (igual ao firmware: kImageSize)
K_IMAGE_SIZE  = 32 * 32 * 3   # 3072 bytes

# ==========================================================================
# INICIALIZAÇÃO DO TFLITE (equivalente a inicializar_tflm() no C++)
# ==========================================================================
try:
    import tflite_runtime.interpreter as tflite
    Interpreter = tflite.Interpreter
except ImportError:
    # Fallback para tensorflow completo se tflite-runtime não estiver instalado
    import tensorflow as tf
    Interpreter = tf.lite.Interpreter

print(f"[MOCK] Carregando modelo: {MODEL_PATH}")
interpreter = Interpreter(model_path=MODEL_PATH)
interpreter.allocate_tensors()

input_details  = interpreter.get_input_details()[0]
output_details = interpreter.get_output_details()[0]

# Parâmetros de quantização (equivalente a tfInputScale, tfInputZeroPoint no C++)
input_scale      = input_details['quantization'][0]
input_zero_point = input_details['quantization'][1]
input_dtype      = input_details['dtype']   # np.int8 para modelo _Inteira

print(f"[MOCK] Modelo carregado. Input dtype={input_dtype.__name__}, "
      f"scale={input_scale}, zero_point={input_zero_point}")
print(f"[MOCK] Pronto. Aguardando imagens em {TOPICO_CLASSIFICAR} ...")

# ==========================================================================
# INFERÊNCIA (equivalente a predicao() no C++)
# ==========================================================================
running = True

def predicao(imagem_int8: np.ndarray) -> tuple[int, float]:
    """
    Executa inferência e retorna (classe_predita, tempo_inferencia_ms).
    Replica exatamente a função predicao() do firmware:
      1. Copia dados para o tensor de entrada (memcpy equivalente)
      2. Invoke()
      3. Argmax na saída int8
    """
    # Molda para o shape esperado pelo modelo: [1, 32, 32, 3]
    entrada = imagem_int8.reshape(input_details['shape'])

    interpreter.set_tensor(input_details['index'], entrada)

    # Mede tempo de inferência — equivalente a esp_timer_get_time() antes/depois
    t_inicio = time.perf_counter()
    interpreter.invoke()
    t_fim = time.perf_counter()

    tempo_inferencia_ms = (t_fim - t_inicio) * 1000.0

    saida = interpreter.get_tensor(output_details['index'])[0]  # shape [num_classes]

    # Argmax em int8 — idêntico ao loop do firmware
    classe = int(np.argmax(saida))

    print(f"[MOCK] Classe={classe}  tempo_inferência={tempo_inferencia_ms:.3f} ms")
    return classe, tempo_inferencia_ms


# ==========================================================================
# CALLBACK MQTT (equivalente a on_message() no C++)
# ==========================================================================
def on_message(client, userdata, msg):
    global running

    # ----- /colaboracao/fim -----
    if msg.topic == TOPICO_FIM:
        print("[MOCK] Sinal de finalização recebido. Encerrando...")
        running = False
        return

    # ----- /esp/classificar -----
    if msg.topic != TOPICO_CLASSIFICAR:
        return

    payload = msg.payload
    esperado = 8 + K_IMAGE_SIZE   # sizeof(int64_t) + kImageSize

    if len(payload) != esperado:
        print(f"[MOCK] Tamanho inválido: {len(payload)} bytes (esperado {esperado})")
        return

    # ── Extrai timestamp_envio (int64, μs, little-endian) ──
    # No firmware: memcpy(&timestamp_envio, data, sizeof(int64_t))
    timestamp_envio_us = struct.unpack_from('<q', payload, 0)[0]

    # Converte μs → Unix epoch float (cam.py usa int(time.time() * 1_000_000))
    timestamp_envio_unix = timestamp_envio_us / 1_000_000.0

    # ── Extrai imagem int8 ──
    # No firmware: const int8_t* imagem = (const int8_t*)(data + sizeof(int64_t))
    imagem_bytes = payload[8:]
    imagem_int8  = np.frombuffer(imagem_bytes, dtype=np.int8).copy()

    # ── timestamp_recebido ──
    # No firmware: esp_timer_get_time() retorna μs desde o boot (não Unix epoch)
    # No mock: usamos time.time() (Unix epoch) para compatibilidade com logger_esp.py
    timestamp_recebido_unix = time.time()

    # ── Latência câmera → esp (equivalente ao printf do firmware) ──
    latencia_ms = (timestamp_recebido_unix - timestamp_envio_unix) * 1000.0
    print(f"[MOCK] Latência cam→esp: {latencia_ms:.3f} ms")

    # ── Inferência ──
    resultado, tempo_inferencia_ms = predicao(imagem_int8)

    # ==========================================================================
    # Publica /esp/resultado
    # Formato idêntico ao sprintf do firmware:
    #   {"resultado":%d,"timestamp_envio":%.6f}
    # ==========================================================================
    json_resposta = json.dumps({
        "resultado":        resultado,
        "timestamp_envio":  round(timestamp_envio_unix, 6)
    })
    client.publish(TOPICO_RESULTADO, json_resposta, qos=0)

    # ==========================================================================
    # Publica /esp/metricas
    # Formato idêntico ao sprintf do firmware (todos os campos)
    # ==========================================================================
    json_metricas = json.dumps({
        "id_publicador":        ID_PUBLICADOR,
        "modelo":               NOME_MODELO,
        "timestamp_envio":      round(timestamp_envio_unix,    6),
        "timestamp_recebido":   round(timestamp_recebido_unix, 6),
        "latencia_ms":          round(latencia_ms,             3),
        "tempo_inferencia_ms":  round(tempo_inferencia_ms,     3),
        "resultado":            resultado
    })
    client.publish(TOPICO_METRICAS, json_metricas, qos=0)

    print(f"[MOCK] Publicado → resultado={resultado}, "
          f"inferência={tempo_inferencia_ms:.3f} ms")


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f"[MOCK] Conectado ao broker {MQTT_BROKER}:{MQTT_PORT}")
        # Subscreve nos mesmos tópicos que o firmware C++ (MQTT_EVENT_CONNECTED)
        client.subscribe(TOPICO_CLASSIFICAR, qos=0)
        client.subscribe(TOPICO_FIM,         qos=0)
        print(f"[MOCK] Subscrito em: {TOPICO_CLASSIFICAR}  |  {TOPICO_FIM}")
    else:
        print(f"[MOCK] Falha na conexão MQTT (rc={rc})")


def on_disconnect(client, userdata, rc):
    print(f"[MOCK] Desconectado do broker (rc={rc})")


# ==========================================================================
# INICIALIZAÇÃO MQTT (equivalente a setup() → esp_mqtt_client_init() no C++)
# ==========================================================================
mqtt_client = mqtt.Client()
mqtt_client.username_pw_set(MQTT_USER, MQTT_PASSWORD)
mqtt_client.on_connect    = on_connect
mqtt_client.on_message    = on_message
mqtt_client.on_disconnect = on_disconnect

print(f"[MOCK] Conectando a {MQTT_BROKER}:{MQTT_PORT} ...")
mqtt_client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)
mqtt_client.loop_start()

# ==========================================================================
# LOOP PRINCIPAL (equivalente ao loop() + vTaskDelay() no C++)
# ==========================================================================
try:
    while running:
        time.sleep(0.01)   # ~10 ms — equivalente ao vTaskDelay(10/portTICK_PERIOD_MS)
except KeyboardInterrupt:
    print("\n[MOCK] Interrupção manual (Ctrl+C).")

# Equivalente a esp_mqtt_client_stop() + esp_mqtt_client_destroy()
mqtt_client.loop_stop()
mqtt_client.disconnect()
print("[MOCK] Encerrado.")
