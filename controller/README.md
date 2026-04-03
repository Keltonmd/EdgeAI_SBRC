# 🤖 Controller — Orquestrador de Agentes Robóticos

> Módulo de controle e orquestração do projeto **"Avaliação de Inferência em Edge AI sob Restrições Embarcadas em um Sistema Robótico Simulado Baseado na Internet das Coisas Robóticas"** (SBRC 2026).

Este diretório concentra todos os scripts Python responsáveis por controlar os robôs simulados no **CoppeliaSim**, coordenar a comunicação entre eles via **MQTT** e coletar métricas de latência do sistema.

---

## 📋 Sumário

1. [Visão Geral da Arquitetura](#-visão-geral-da-arquitetura)
2. [Estrutura de Arquivos](#-estrutura-de-arquivos)
3. [Pré-requisitos](#-pré-requisitos)
4. [Instalação](#-instalação)
5. [Configuração do Broker MQTT](#-configuração-do-broker-mqtt)
6. [Como Executar](#-como-executar)
7. [Agentes em Detalhe](#-agentes-em-detalhe)
   - [MqttAgent](#mqttagent---agente-de-comunicação)
   - [CoppeliaBracoAgent](#coppeliabracagent---agente-de-braços-robóticos)
   - [CoppeliaMobileAgent](#coppeliamobileagent---agente-de-robô-móvel)
   - [CoppeliaSensorAgent](#coppeliasensoragent---agente-de-sensores)
8. [Scripts de Robôs](#-scripts-de-robôs)
9. [Fluxo de Comunicação MQTT](#-fluxo-de-comunicação-mqtt)
10. [Coleta de Métricas](#-coleta-de-métricas)
11. [Solução de Problemas](#-solução-de-problemas)

---

## 🏗️ Visão Geral da Arquitetura

O sistema implementa uma **arquitetura multiagente orientada a eventos** em que cada robô opera de forma autônoma e reativa, se comunicando exclusivamente por tópicos MQTT. A cena simulada é executada dentro do **CoppeliaSim**, e cada agente Python se conecta ao simulador através da **ZMQ Remote API**.

```
┌─────────────────────────────────────────────────────┐
│                   CoppeliaSim                       │
│                                                     │
│  [Franka Panda] [UR10] [youBot] [Sensor] [Câmera]   │
└────────────────────┬────────────────────────────────┘
                     │ ZMQ Remote API
         ┌───────────▼────────────┐
         │   Scripts Python       │
         │  (Controller Agents)   │
         └───────────┬────────────┘
                     │ paho-mqtt
         ┌───────────▼────────────┐
         │   Mosquitto Broker     │  ◄──── ESP32-S3
         │   (MQTT PubSub)        │        (Edge AI)
         └────────────────────────┘
```

### Fluxo de Trabalho Resumido

1. O **Sensor da Esteira** detecta um novo bloco e publica no tópico `/bloco/disponivel`.
2. O **Franka Panda** pega o bloco e passa ao **youBot**.
3. O **youBot** transporta o bloco até a zona de visão do UR10.
4. A **Câmera** captura e envia a imagem ao **ESP32** via MQTT para classificação por IA.
5. O **UR10** recebe o resultado da classificação e guarda o bloco na prateleira correta (vermelho ou azul).
6. O **logger** registra todas as métricas de latência da ESP32.

---

## 📁 Estrutura de Arquivos

```
controller/
│
├── main.py                  # Ponto de entrada: Inicia a simulação e sobe todos os agentes
│
├── MqttAgent.py             # Classe base de comunicação MQTT (Pub/Sub + medição de latência)
├── CoppeliaBracoAgent.py    # Controle de braços robóticos com garra (Franka, UR10)
├── CoppeliaMobileAgent.py   # Controle de robôs móveis omnidirecionais (youBot)
├── CoppeliaSensorAgent.py   # Leitura de sensores de proximidade e câmera
│
├── franka.py                # Agente do braço Franka Panda (coleta e entrega de blocos)
├── ur10.py                  # Agente do braço UR10 (classificação e estocagem de blocos)
├── youBot.py                # Agente do robô móvel KUKA youBot (transporte)
├── cam.py                   # Agente da câmera (captura e envio de imagens ao ESP32)
├── sensorEsteira.py         # Agente do sensor de proximidade da esteira
├── logger_esp.py            # Coleta e salva métricas de inferência do ESP32
│
└── requirements.txt         # Dependências Python do projeto
```

---

## 🔧 Pré-requisitos

Antes de usar este módulo, certifique-se de ter os seguintes componentes instalados e configurados:

| Componente | Versão | Descrição |
|---|---|---|
| Python | ≥ 3.10 | Interpretador da linguagem |
| CoppeliaSim (EDU) | ≥ 4.4.0 (recomendado 4.10.0) | Simulador 3D com suporte à ZMQ Remote API |
| Eclipse Mosquitto | Qualquer estável | Broker MQTT local |
| pip | Qualquer | Gerenciador de pacotes Python |

> **⚠️ Aviso:** O CoppeliaSim **deve estar aberto** com a cena `cenario/cenario_novo.ttt` carregada **antes** de executar qualquer script Python. O simulador não deve estar em modo de *play*; o script `main.py` controla isso automaticamente via API.

---

## 📦 Instalação

### 1. Clone o repositório (caso ainda não tenha feito)

```bash
git clone https://github.com/Keltonmd/EdgeBoxAI.git EdgeAI_SBRC
cd EdgeAI_SBRC/controller
```

### 2. Crie e ative um ambiente virtual Python

**Recomendado** para isolar as dependências do projeto:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

> No Windows (se aplicável): `.venv\Scripts\activate`

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

As dependências instaladas serão:

| Pacote | Versão | Finalidade |
|---|---|---|
| `coppeliasim_zmqremoteapi_client` | 2.0.4 | Comunicação com o CoppeliaSim via ZMQ |
| `paho-mqtt` | 2.1.0 | Cliente MQTT para comunicação Pub/Sub |
| `numpy` | 2.3.1 | Computação numérica (vetores, ângulos) |
| `opencv-python` | 4.13.0.92 | Captura e pré-processamento de imagens |
| `pandas` | 3.0.2 | Manipulação e exportação de métricas CSV |
| `openpyxl` | 3.1.5 | Suporte a arquivos Excel (utilizado pelo pandas) |
| `pyzmq` | 27.0.0 | Sockets ZMQ (dependência do cliente CoppeliaSim) |
| `cbor` | 1.0.0 | Serialização binária compacta |

---

## 📡 Configuração do Broker MQTT

### Instalando o Mosquitto

```bash
sudo apt update && sudo apt install -y mosquitto mosquitto-clients
```

### Criando usuário de autenticação

Escolha um nome de usuário e senha e crie-os no Mosquitto:

```bash
# Substitua SEU_USUARIO pela credencial que desejar
sudo mosquitto_passwd -c /etc/mosquitto/passwd SEU_USUARIO
# Digite e confirme a senha quando solicitado
```

### Habilitando autenticação no Mosquitto

Edite (ou crie) o arquivo de configuração `/etc/mosquitto/conf.d/local.conf`:

```bash
sudo nano /etc/mosquitto/conf.d/local.conf
```

Adicione o conteúdo:

```conf
allow_anonymous false
password_file /etc/mosquitto/passwd
listener 1883
```

### Reiniciando o serviço

```bash
sudo systemctl restart mosquitto
sudo systemctl enable mosquitto   # Opcional: para iniciar automaticamente no boot
```

### Verificando se está ativo

```bash
sudo systemctl status mosquitto
```

Você deve ver `Active: active (running)`.

### Configurando as credenciais nos scripts

Após criar o usuário no Mosquitto, configure as mesmas credenciais nos scripts Python. Há **dois arquivos** com um bloco de configuração bem visível no topo:

**`MqttAgent.py`** — utilizado por todos os agentes de robô:
```python
# ==============================================================
# CONFIGURAÇÃO — Ajuste antes de executar
# ==============================================================
MQTT_BROKER   = "localhost"   # IP ou hostname do broker Mosquitto
MQTT_PORT     = 1883
MQTT_USER     = "SEU_USUARIO" # Usuário criado no Mosquitto
MQTT_PASSWORD = "SUA_SENHA"   # Senha correspondente
# ==============================================================
```

**`logger_esp.py`** — logger de métricas do ESP32:
```python
# ==============================================================
# CONFIGURAÇÃO — Ajuste antes de executar
# ==============================================================
MQTT_BROKER   = "localhost"   # IP ou hostname do broker Mosquitto
MQTT_PORT     = 1883
MQTT_USER     = "SEU_USUARIO" # Usuário criado no Mosquitto
MQTT_PASSWORD = "SUA_SENHA"   # Senha correspondente
# ==============================================================
```

> **Dica:** Se o broker estiver em outra máquina da rede, substitua `"localhost"` pelo IP do host (ex: `"192.168.1.100"`).

---

## ▶️ Como Executar

### Passo 1 — Abra o CoppeliaSim com a cena

```bash
~/Applications/CoppeliaSim_Edu_V4_*/coppeliaSim.sh
```

Dentro do CoppeliaSim: `Arquivo → Open Scene → cenario/cenario_novo.ttt`

> **Não pressione o botão Play!** O `main.py` inicia a simulação automaticamente.

### Passo 2 — (Opcional) Conecte o ESP32

Se quiser rodar o experimento completo com a classificação real na borda, conecte o ESP32 ao Wi-Fi e certifique-se de que ele aponta para o broker MQTT correto. Consulte o diretório `esp32/` para instruções de firmware.

### Passo 3 — Execute o orquestrador

Com o ambiente virtual ativado:

```bash
cd EdgeAI_SBRC/controller
source .venv/bin/activate
python3 main.py
```

O `main.py` irá:
1. Conectar ao CoppeliaSim via ZMQ e **iniciar a simulação** automaticamente.
2. Subir cada agente como um subprocesso independente (com 1 segundo de intervalo entre cada).
3. Aguardar todos os processos finalizarem.
4. Parar a simulação ao final.

### Monitorando os tópicos MQTT em tempo real

Em um terminal separado, você pode monitorar todas as mensagens trocadas entre os agentes:

```bash
mosquitto_sub -h localhost -u SEU_USUARIO -P SUA_SENHA -t "#" -v
```

---

## 🔍 Agentes em Detalhe

### `MqttAgent` — Agente de Comunicação

**Arquivo:** `MqttAgent.py`

Classe base utilizada por **todos os agentes de robô** para comunicação MQTT. Oferece:

- **Pub/Sub com QoS configurável**
- **Medição automática de latência** (em ms) entre publicação e recebimento
- **Exportação de métricas** para CSV ao finalizar

#### Principais Métodos

| Método | Descrição |
|---|---|
| `publicar(canal, msg, qos)` | Publica um dicionário JSON em um tópico, injetando automaticamente `timestamp_envio` e `id_publicador` |
| `publicar_bytes(canal, msg, qos)` | Publica payload binário bruto (usado pela câmera para imagens) |
| `salvar_resultados()` | Salva as métricas de latência coletadas em `resultados_<id_agente>.csv` |
| `desconectar()` | Salva métricas, para o loop MQTT e desconecta do broker |

#### Tópicos Monitorados

| Tópico | Ação |
|---|---|
| `/entregador/coletaDisponivel` | Sinaliza que há bloco disponível para coleta |
| `/bloco/disponivel` | Ativa `espera_bloco` com o nome do cubo |
| `/entregador/pontoRecebimento` | Sinaliza que o destino de entrega está livre |
| `/entregador/encomendaDisponibilizada` | Ativa `iniciar_entrega` |
| `/entregador/encomendaColetada` | Ativa `iniciar_coleta` |
| `/colaboracao/fim` | Encerra a colaboração (`finalizado = True`) |
| `/cam/capture` | Ativa captura de imagem |
| `/esp/resultado` | Recebe resultado da classificação da ESP32 |

---

### `CoppeliaBracoAgent` — Agente de Braços Robóticos

**Arquivo:** `CoppeliaBracoAgent.py`

Classe de controle para braços robóticos com garra (Franka Panda e UR10). Conecta-se ao CoppeliaSim via ZMQ e oferece controle cinemático de alto nível.

#### Principais Métodos

| Método | Descrição |
|---|---|
| `abrirGarra()` | Abre a garra ROBOTIQ85 usando IK solver |
| `fecharGarra()` | Fecha a garra para agarrar objetos |
| `descerBraco(z_final, velocidade, intervalo)` | Move o target do braço para baixo até `z_final` |
| `subirBraco(z_final, velocidade, intervalo)` | Move o target do braço para cima até `z_final` |
| `mover_para_posicao_xyz(posicoes, velocidade, intervalo)` | Move o target suavemente para uma posição 3D |
| `rotacionar_para_posicao_xyz(ang_final, espera, velocidade, intervalo)` | Rotaciona e reposiciona o braço simultaneamente |
| `alinharComObjeto(obj_path)` | Alinha o target horizontalmente com um objeto na cena |
| `getPosicoesRack(path, quant)` | Retorna lista de posições disponíveis em uma prateleira |
| `corrigirCaixa(caixa, posicao_correta)` | Corrige a posição de uma caixa após o soltar |

#### Como Instanciar

```python
from CoppeliaBracoAgent import CoppeliaBracoAgent

# Passa o caminho do robô na hierarquia da cena CoppeliaSim
agent = CoppeliaBracoAgent("/Franka")
```

---

### `CoppeliaMobileAgent` — Agente de Robô Móvel

**Arquivo:** `CoppeliaMobileAgent.py`

Classe de controle para o robô móvel omnidirecional KUKA youBot. Implementa navegação autônoma no plano 2D com controle de orientação.

#### Principais Métodos

| Método | Descrição |
|---|---|
| `setVelocidade(vel)` | Define a mesma velocidade para todas as rodas |
| `virarRobo(vel1, vel2)` | Diferencia velocidades para rotação: `vel1>0, vel2<0` vira à direita |
| `moverRobo(alvo)` | Navega autonomamente até um ponto 2D `[x, y]` com controle proporcional |
| `orientarRobo(anguloAlvo)` | Rotaciona o robô para um ângulo alvo (graus) |
| `getPos(path)` | Retorna a posição 3D de um objeto na cena |

#### Como Instanciar

```python
from CoppeliaMobileAgent import CoppeliaMobileAgent
import numpy as np

# Lista com os paths das juntas das rodas no CoppeliaSim
nomes = ['/rollingJoint_rr', '/rollingJoint_rl', '/rollingJoint_fr', '/rollingJoint_fl']
agent = CoppeliaMobileAgent("/youBot", nomes)

# Mover para uma posição XY
agent.moverRobo(np.array([1.5, -0.3]))
agent.orientarRobo(90)  # Orientar para 90 graus
```

---

### `CoppeliaSensorAgent` — Agente de Sensores

**Arquivo:** `CoppeliaSensorAgent.py`

Classe para leitura de sensores de proximidade e câmera no CoppeliaSim.

#### Principais Métodos

| Método | Descrição |
|---|---|
| `leitura()` | Lê o sensor de proximidade e retorna `True` se detectou objeto |
| `lerIMG()` | Captura frame da câmera (`visionSensor`) e retorna `(img_bytes, resolution)` |
| `desenpacotarIMG(img, resolution)` | Converte os bytes brutos em array NumPy RGB `(H, W, 3)` com flip vertical |

#### Como Instanciar

```python
from CoppeliaSensorAgent import CoppeliaSensorAgent

# Sensor de proximidade
sensor_prox = CoppeliaSensorAgent("/proximitySensor")
if sensor_prox.leitura():
    print("Objeto detectado!")

# Câmera
camera = CoppeliaSensorAgent("/visionSensor")
img_bytes, resolution = camera.lerIMG()
img_array = camera.desenpacotarIMG(img_bytes, resolution)
```

---

## 🤖 Scripts de Robôs

### `franka.py` — Braço Franka Panda

**Papel:** Coletar blocos da esteira e entregá-los ao youBot.

**Tópicos escutados:**
- `/bloco/disponivel` (QoS 1) — Sinal de novo bloco na esteira
- `/entregador/pontoRecebimento` — youBot chegou para receber
- `/colaboracao/fim` — Encerrar operação

**Tópicos publicados:**
- `/entregador/encomendaDisponibilizada` — Bloco colocado no youBot

**Fluxo interno:**
```
[Espera bloco] → pegarBloco() → [Espera youBot] → entregarBloco() → [loop]
```

---

### `ur10.py` — Braço Universal Robots UR10

**Papel:** Coletar blocos do youBot, solicitar classificação por câmera/ESP32 e estocá-los na prateleira correta.

**Tópicos escutados:**
- `/entregador/coletaDisponivel` — youBot chegou com o bloco
- `/esp/resultado` — Resultado da classificação (0 = Azul, 1 = Vermelho)

**Tópicos publicados:**
- `/entregador/encomendaColetada` — Bloco retirado do youBot
- `/cam/capture` — Solicita captura de imagem
- `/colaboracao/fim` (QoS 1) — Todas as prateleiras preenchidas

**Lógica de estocagem:**
- Resultado `0` → Prateleira Azul (fallback: Vermelha)
- Resultado `1` → Prateleira Vermelha (fallback: Azul)

---

### `youBot.py` — Robô Móvel KUKA youBot

**Papel:** Transportar blocos entre o Franka Panda e o UR10.

**Tópicos escutados:**
- `/entregador/encomendaDisponibilizada` — Franka colocou bloco no youBot → `iniciar_entrega`
- `/entregador/encomendaColetada` — UR10 retirou bloco → `iniciar_coleta`
- `/colaboracao/fim` — Encerrar operação

**Tópicos publicados:**
- `/entregador/pontoRecebimento` — Chegou à zona de entrega (Franka)
- `/entregador/coletaDisponivel` — Chegou à zona de coleta (UR10)

**Posições-chave na cena:**
- `/entrega_caixa` — Zona de entrega (sob o Franka)
- `/recebe_caixa` — Zona de recebimento (sob o UR10)

---

### `cam.py` — Agente de Câmera

**Papel:** Capturar frames do `visionSensor` e enviá-los ao ESP32 para classificação.

**Tópicos escutados:**
- `/cam/capture` — Solicitar captura
- `/colaboracao/fim` — Encerrar

**Tópicos publicados:**
- `/esp/classificar` (payload binário) — Imagem 32×32 INT8 + timestamp de 8 bytes

**Formato do payload enviado ao ESP32:**
```
[8 bytes: timestamp em microssegundos (little-endian)] + [3072 bytes: imagem 32x32 RGB int8]
```

**Pré-processamento da imagem:**
1. Redimensionar para 32×32 pixels
2. Converter para `int8` via `(pixel - 128)` (normalização centrada em zero)

---

### `sensorEsteira.py` — Sensor de Proximidade

**Papel:** Detectar blocos na esteira e publicar disponibilidade.

**Tópicos escutados:**
- `/colaboracao/fim` — Encerrar

**Tópicos publicados:**
- `/bloco/disponivel` (QoS 1) — Com payload `{"cubo": "/cubo_N"}` onde N é o número sequencial do bloco

**Comportamento:**
- Faz polling a cada 100ms
- Ao detectar novo bloco, aguarda **3 segundos** (para estabilização) antes de publicar
- Evita publicações duplicadas com controle de estado `ultimoEstado`

---

### `logger_esp.py` — Logger de Métricas da ESP32

**Papel:** Coletar e salvar métricas de inferência enviadas pelo ESP32.

**Tópicos escutados:**
- `/esp/metricas` — Métricas de cada inferência
- `/colaboracao/fim` — Encerrar e salvar

**Arquivo gerado:** `metricas_esp.csv`

**Colunas do CSV:**

| Coluna | Descrição |
|---|---|
| `timestamp_logger` | Timestamp do recebimento pelo logger (Unix) |
| `id_publicador` | Identificador do ESP32 |
| `modelo` | Nome do modelo de IA utilizado |
| `timestamp_envio` | Timestamp de envio da imagem (µs) |
| `timestamp_recebido` | Timestamp de recebimento e inferência (µs) |
| `latencia_ms` | Latência total de comunicação (ms) |
| `tempo_inferencia_ms` | Tempo de inferência da CNN (ms) |
| `resultado` | Classe predita (0=Azul, 1=Vermelho) |

---

## 📊 Fluxo de Comunicação MQTT

O diagrama abaixo mostra a sequência completa de mensagens entre os agentes:

```
Sensor        Franka         youBot         Câmera         UR10          ESP32
  │              │               │              │             │              │
  │─/bloco/disponivel──────────►│              │             │              │
  │              │               │              │             │              │
  │        pegarBloco()          │              │             │              │
  │              │               │              │             │              │
  │◄─────/entregador/pontoRecebimento──────────│             │              │
  │              │               │              │             │              │
  │        entregarBloco()       │              │             │              │
  │              │               │              │             │              │
  │       /entregador/encomendaDisponibilizada►│             │              │
  │              │               │              │             │              │
  │              │         entregar()           │             │              │
  │              │               │              │             │              │
  │              │   /entregador/coletaDisponivel────────────►│             │
  │              │               │              │             │              │
  │              │               │              │      pegarBloco()          │
  │              │               │              │             │              │
  │              │◄──────/entregador/encomendaColetada────────│             │
  │              │               │              │             │              │
  │              │         receber()            │             │              │
  │              │               │              │             │              │
  │              │               │              |             |              |
  │              │               │              │             │              │
  │              │               │        <───────/cam/capture│              │
  │              │               │              │             │              │
  │              │               │       capturar()           │              │
  │              │               │              │─/esp/classificar──────────►│
  │              │               │              │             │              │
  │              │               │              │           ◄───/esp/resultado
  │              │               │              │             │              │
  │              │               │              │      guardarBloco()        │
  │              │               │              │             │              │
  [loop até todas as posições da prateleira estarem ocupadas]
  │              │               │              │             │              │
 <──────────────────────────────────────────────────/colaboracao/fim (QoS 1)──►
  │              │               │              │             │              │
[Todos os agentes finalizam e salvam seus CSVs de latência]
```

---

## 📈 Coleta de Métricas

Ao final de cada execução, os seguintes arquivos CSV são gerados no diretório `controller/`:

| Arquivo | Gerado por | Conteúdo |
|---|---|---|
| `resultados_Franka.csv` | `franka.py` | Latências MQTT do braço Franka |
| `resultados_UR10.csv` | `ur10.py` | Latências MQTT do braço UR10 |
| `resultados_youBot.csv` | `youBot.py` | Latências MQTT do youBot |
| `resultados_Cam.csv` | `cam.py` | Latências MQTT da câmera |
| `resultados_sensor.csv` | `sensorEsteira.py` | Latências do sensor de proximidade |
| `metricas_esp.csv` | `logger_esp.py` | Métricas de inferência da ESP32 |

### Estrutura dos CSVs de latência dos robôs

| Coluna | Descrição |
|---|---|
| `Robo_Publicador` | ID do agente que publicou |
| `Robo_Assinante` | ID do agente que recebeu |
| `Topico` | Tópico MQTT da mensagem |
| `Latencia_ms` | Diferença entre timestamp de envio e recebimento (ms) |

> **Nota:** Os CSVs são **acumulativos** — novas execuções *adicionam* linhas ao arquivo existente. Para métricas de uma execução limpa, delete os arquivos antes de cada rodada.

---

## 🛠️ Solução de Problemas

### ❌ `ConnectionRefusedError` ao conectar ao broker MQTT

**Causa:** O Mosquitto não está em execução ou a porta está errada.

```bash
# Verificar status
sudo systemctl status mosquitto

# Reiniciar se necessário
sudo systemctl restart mosquitto
```

---

### ❌ `RuntimeError: Could not connect to remote API server` (ZMQ)

**Causa:** O CoppeliaSim não está aberto ou a cena não foi carregada.

**Solução:**
1. Abra o CoppeliaSim
2. Carregue a cena: `Arquivo → Open Scene → cenario/cenario_novo.ttt`
3. **Não pressione Play**
4. Execute `python3 main.py` novamente

---

### ❌ `[MQTT] Aviso: tópico não tratado: <tópico>`

**Causa:** Uma mensagem foi recebida em um tópico não mapeado no `topic_map` do `MqttAgent`.

**Solução:** Se necessário, adicione o tópico e seu handler correspondente no dicionário `topic_map` em `MqttAgent.py`.

---

### ❌ Robô não se move / fica parado

**Causa:** O agente está aguardando uma mensagem MQTT que ainda não chegou.

**Diagnóstico:**
```bash
# Monitore todos os tópicos em tempo real
mosquitto_sub -h localhost -u SEU_USUARIO -P SUA_SENHA -t "#" -v
```

Verifique se os tópicos esperados estão sendo publicados na sequência correta.

---

### ❌ `Authentication failed` ao conectar ao broker

**Causa:** Usuário ou senha incorretos no Mosquitto.

**Solução:** Recrie o usuário:
```bash
sudo mosquitto_passwd /etc/mosquitto/passwd SEU_USUARIO
# Digite a nova senha
sudo systemctl restart mosquitto
```

---

### ❌ Endereço do broker não encontrado

**Causa:** O valor de `MQTT_BROKER` nos scripts não aponta para o endereço correto do broker na sua rede.

**Solução:** Edite o bloco de configuração no topo de `MqttAgent.py` e `logger_esp.py`:

```python
# Altere para "localhost" se o broker estiver na mesma máquina,
# ou informe o IP da máquina onde o Mosquitto está rodando:
MQTT_BROKER = "192.168.1.100"  # exemplo
```

---

## 📄 Licença

Este módulo faz parte do projeto **EdgeAI SBRC** e está licenciado sob a **MIT License**.

Consulte o arquivo [`LICENSE`](../LICENSE) na raiz do repositório para os termos completos.

---

*Desenvolvido no contexto do artigo submetido ao SBRC 2026 — IFNMG Campus Januária.*
