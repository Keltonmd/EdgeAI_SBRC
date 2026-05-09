# Título projeto
Avaliação de Inferência em Edge AI sob Restrições Embarcadas em um Sistema Robótico Simulado Baseado na Internet das Coisas Robóticas

**Resumo:**
Este trabalho avalia inferência Edge AI na Internet das Coisas Robóticas (IoRT). Três CNNs foram embarcadas em um ESP32-S3 de forma interligada a um cenário industrial simulado via MQTT no CoppeliaSim. Constatou-se uma grave discrepância entre estimativas teóricas de memória vis-à-vis sua alocação real: a MobileNetV2 consumiu 204\% mais arena que a conversão acusava em placa, falhando junto da pré-treinada V3 nos ensaios embarcados práticos. Apenas a CNN autoral operou com fluidez sistêmica efetiva e 100\% de acerto sob 53,87~ms consumindo enxutos 38,4~KB estáticos, isolando predições fidedignas no chão de fábrica simulado.

# Estrutura do readme.md
Apresenta a organização deste repositório e README:
1. Título do projeto
2. Estrutura do readme.md e do Repositório
3. Selos Considerados
4. Vídeo de Demonstração
5. Informações básicas
6. Dependências
7. Preocupações com segurança
8. Instalação
9. Teste mínimo
10. Experimentos
11. Análise dos Resultados
12. LICENSE

**Estrutura do Repositório:**
```
EdgeAI_SBRC/
├── cenario/          # Cena CoppeliaSim com todos os robôs e sensores (.ttt)
├── controller/       # Scripts Python de controle e orquestração via ZMQ e MQTT
├── dataset/          # [Não versionado] Diretório com particionamentos RGB 32x32
├── esp32/            # Projeto de Firmware C/C++ ESP-IDF (TensorFlow Lite Micro)
├── modelos/          # Modelos Keras exportados e conversões para TFLite (.cc)
├── resultados/       # Métricas coletadas, scripts de plotagem e logs gerados
├── tflm_code/        # Framework base TensorFlow Lite C++ pré-compilado para MCU
└── treinamento/      # Scripts/Notebooks (.ipynb) de treinamento dos modelos
```

# Selos Considerados
Os selos considerados neste processo de avaliação pelo Comitê Técnico de Artefatos (CTA) são:
- **Disponíveis (SeloD)**
- **Funcionais (SeloF)**
- **Sustentáveis (SeloS)**
- **Reprodutíveis (SeloR)**

# Vídeo de Demonstração
O vídeo abaixo apresenta o sistema completo em operação: o cenário industrial simulado no CoppeliaSim, a placa ESP32-S3 realizando inferência Edge AI em tempo real e as métricas de latência e classificação sendo coletadas.

[![Demonstração do Sistema EdgeAI_SBRC](https://img.youtube.com/vi/R724IeP1t58/maxresdefault.jpg)](https://youtu.be/R724IeP1t58)

> 🎬 **Acesse:** [https://youtu.be/R724IeP1t58](https://youtu.be/R724IeP1t58)

# Informações básicas
Este artefato propõe, implementa e avalia uma arquitetura de comunicação e colaboração baseada em mensageria orientada a eventos para coordenação de robôs heterogêneos em ambiente industrial. A parte física e logística é simulada; na configuração principal do artigo, a IA (computação visual em borda) roda em um microcontrolador real ESP32-S3 conectado via MQTT ao restante do sistema.

> **Execução completa dos experimentos:** para reproduzir integralmente os ensaios do artigo, incluindo firmware embarcado, medições em hardware e validação do fluxo com TFLite Micro, é necessário possuir uma placa ESP32-S3.
>
> **Validação funcional sem hardware:** o repositório também inclui `controller/esp32_mock.py`, que simula a placa real e permite validar o pipeline câmera → classificador → UR10 sem depender do microcontrolador físico.

**Ambiente de Execução Global:**
- **Computador Host:** Sistema Operacional Linux (Ubuntu 20.04+ ou Debian 11+ recomendado). Necessita de ≥ 8GB de RAM para suportar a simulação gráfica, processos do orquestrador Python e o broker de rede de maneira conjunta e estável.
- **Microcontrolador (Edge Device Obrigatório):**
  - MCU: ESP32-S3-WROOM-1-N16R8 (Dual-Core Xtensa LX7 a 240 MHz) ou arquitetura próxima da linha ESP32.
  - SRAM interna: 512 KB
  - Memória Flash: 16 MB
  - PSRAM Externa: 8 MB (opcional ativada apenas para avaliação das arquiteturas MobileNet pesadas apontadas no artigo).
- **Conectividade e Mídia Físicas:** Requer uma conexão de rede sem fio (Wi-Fi 802.11 b/g/n em 2.4GHz ativa) da qual tanto o host quanto a placa participem e um cabo Micro-USB/Type-C para a compilação. 

# Dependências
Para a reprodução da cadeia descrita no artigo, exige-se as seguintes ferramentas e componentes pré-instalados:
- **Simulador 3D:** CoppeliaSim EDU v4.10.0. Responsável pelas físicas cinemáticas. (Versão 4.4+ obrigatoriamente para compatibilidade nativa com *ZMQ Remote API*).
- **Broker MQTT:** Eclipse Mosquitto. Ferramenta de roteamento para arquitetura Pub/Sub.
- **IDE Python:** Interpretador Python 3.10 ou superior. Os pacotes definidos em `controller/requirements.txt` devem estar presentes no VirtualEnv do orquestrador Python. O arquivo já inclui as dependências do controlador e o suporte a `.env`; o mock do ESP32 usa `tflite-runtime` quando disponível e faz fallback para TensorFlow em ambientes compatíveis.
- **Chain de Build C/C++:** Instalação do ESP-IDF (Espressif IoT Development Framework) na versão **v5.2.x**. Pode ser extraída diretamente pela sua Extensão formal de mercado no VS Code ("Espressif IDF").
- **Bibliotecas Lógicas de IA (Embarcado):** Dependência TFLite Micro instalada. Em nosso código-fonte, usa-se a biblioteca modificada `espressif/esp-tflite-micro` na sua revisão `v1.3.5`. Devido à modernidade de nossa implementação Cmake, tal biblioteca já atua nativamente vinculada e manipulada de forma automática pelo manifest `idf_component.yml` dentro de `esp32/main` e não necessita de download manual adicional.

# Preocupações com segurança
Caso a execução do artefato ofereça algum tipo de risco para os avaliadores, este risco deve ser descrito. 
Neste projeto **não há riscos diretos significativos (físicos, químicos ou elétricos)**. As operações físicas mecânicas manipuláveis — garras e robôs móveis omnidirecionais pesados — habitam limites perfeitamente digitais por meio do simulador virtual acadêmico. Por seu turno, o Edge device que executa os gargalos matemáticos de processamento de Visão é mantido por tensão mínima (corrente contínua provinda de barramento USB comum 3.3v~5.0v), abstendo todo risco de surto reverso. Nenhum tipo de payload malicioso contendo shell ou rootkits perigosos é transmitido nos bytes pela fila MQTT.

# Instalação
O processo de inicialização do ecossistema depende das partes comunicantes expostas estarem íntegras.

**1. Clonagem e Configuração do Repositório:**
```bash
git clone https://github.com/Keltonmd/EdgeAI_SBRC.git
cd EdgeAI_SBRC
```

**2. Instalando o CoppeliaSim:**
Dirija-se à [página inicial do Coppelia Robotics](https://www.coppeliarobotics.com/downloads) e baixe o `CoppeliaSim Edu` para Linux (`.tar.xz`). Extraia no diretório de preferência do usuário local:
```bash
mkdir -p ~/Applications
tar -xf CoppeliaSim_Edu_V4_10_0_*.tar.xz -C ~/Applications/
```
Inicie-o por uma janela auxiliar: `~/Applications/CoppeliaSim_*/coppeliaSim.sh`. Ao abrir, vá em Arquivo -> Open Scene -> e navegue até nosso arquivo do artefato em `EdgeAI_SBRC/cenario/cenario_novo.ttt`. **Atenção:** Mantenha aberto e minimizado. Não aperte o botão 'Play'.

**3. Instalando o Broker de Roteamento:**
```bash
sudo apt update && sudo apt install -y mosquitto mosquitto-clients
sudo mosquitto_passwd -c /etc/mosquitto/passwd SEU_USUARIO  # Senha: SUA_SENHA
sudo systemctl restart mosquitto 
```

**4. Preparando o Controller Python (Atores da Cena):**
```bash
cd EdgeAI_SBRC/controller
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Crie o arquivo de configuração do broker na raiz do repositório:

```bash
cd ..
cp .env.example .env
```

Edite `.env` com os dados do seu Mosquitto:

```env
MQTT_BROKER=localhost
MQTT_PORT=1883
MQTT_USER=SEU_USUARIO
MQTT_PASSWORD=SUA_SENHA
```

**5. Compilando o Firmware do microcontrolador (ESP32):**
Configurável rapidamente por intermédio do VS Code. Esta etapa é necessária para os experimentos com hardware real; para a validação com mock, pule para a seção "Teste mínimo".
1. No VS Code, acesse o painel de extensões e instale `ESP-IDF`. Prossiga pela Express config usando ESP-IDF v5.2 ou mais limpo.
2. Acesse a pasta `EdgeAI_SBRC/esp32/` pela IDE e espere o framework de *build* analisar as rotas e injetar o motor Makefile do sistema de plugins cmake C++.
3. Em `main_functions.cc`, substitua os dados fictícios locais:
```cpp
strcpy((char*)wifi_config.sta.ssid,     "SEU_WIFI_AQUI");
strcpy((char*)wifi_config.sta.password, "SUA_SENHA_AQUI");
cfg.broker.address.uri = "mqtt://SEU_BROKER_MQTT_IP:1883"; // Seu host (ifconfig)
```
4. Conecte sua placa à porta serial, selecione `Set Target > esp32s3` na statusbar. 
5. Clique em **Flash** do menu do ESP. O compilador criará dezenas de bibliotecas secundárias de Inteligência. Fim da Instalação do sistema global.

# Teste mínimo

Valida que o pipeline completo de Edge AI funciona — da câmera ao classificador — **sem exigir o hardware físico**. Use a Opção A (mock) para uma validação imediata ou a Opção B se possuir a placa.

## Opção A — Sem hardware (ESP32 Mock) ✅ Recomendado para avaliação

O script `controller/esp32_mock.py` replica fielmente o firmware C++ do ESP32-S3: subscreve em `/esp/classificar`, executa inferência com o modelo `modelos/modelo_Inteira.tflite` (já presente no repositório) e publica nos mesmos tópicos `/esp/resultado` e `/esp/metricas` que a placa real publicaria.

**Pré-requisitos adicionais do mock:**
- Ambiente Python do `controller` já instalado com `pip install -r requirements.txt`
- `python-dotenv` para ler o `.env`
- Runtime de inferência compatível: `tflite-runtime` quando houver wheel para a sua versão do Python, ou TensorFlow/TensorFlow CPU quando o mock usar o fallback automático

**Configuração (uma única vez):**
```bash
# Na raiz do repositório
cp .env.example .env
# Edite .env com o usuário/senha do seu broker Mosquitto
# Opcional: defina MODEL_PATH para escolher outro .tflite
```

**Execução do teste mínimo:**

**Terminal 1** — Broker Mosquitto:
```bash
systemctl status mosquitto  # confirma que está ativo
```

**Terminal 2** — Escuta de validação:
```bash
mosquitto_sub -h localhost -u SEU_USUARIO -P SUA_SENHA -t "/esp/#" -v
```

**Terminal 3** — Inicia o mock:
```bash
cd EdgeAI_SBRC/controller
source .venv/bin/activate
python3 esp32_mock.py
```

**Terminal 4** — Publica uma imagem de teste (simula a câmera):
```bash
python3 - <<'EOF'
import struct, time, paho.mqtt.client as mqtt, numpy as np
c = mqtt.Client()
c.username_pw_set("SEU_USUARIO", "SUA_SENHA")
c.connect("localhost", 1883)
ts = int(time.time() * 1_000_000)
img = np.zeros(32*32*3, dtype=np.int8)          # imagem preta de teste
payload = struct.pack('<q', ts) + img.tobytes()
c.publish("/esp/classificar", payload)
c.disconnect()
print("Imagem de teste enviada.")
EOF
```

**Comportamento esperado no Terminal 2:**
```
/esp/resultado {"resultado": 0, "timestamp_envio": ...}
/esp/metricas  {"id_publicador": "esp32", "modelo": "CNN_32x32_v1", ...}
```

**Comportamento esperado no Terminal 3 (mock):**
```
[MOCK] Conectado ao broker localhost:1883
[MOCK] Subscrito em: /esp/classificar  |  /colaboracao/fim
[MOCK] Latência cam→esp: X.XXX ms
[MOCK] Classe=0  tempo_inferência=X.XXX ms
[MOCK] Publicado → resultado=0, inferência=X.XXX ms
```

---

## Opção B — Com hardware físico (ESP32-S3)

1. Assegure-se de que o Mosquitto esteja ligado: `systemctl status mosquitto`.
2. Abra uma escuta nos tópicos da placa:
```bash
mosquitto_sub -h localhost -u SEU_USUARIO -P SUA_SENHA -t "/esp/#" -v
```
3. Na placa ESP conectada, mantenha ativado o Monitor de Serial via VS-Code (`Ctrl+Shift+P` → `ESP-IDF: Monitor device`).
4. **Comportamento Esperado:** No monitor serial aparecerá "`Conectado ao WiFi!`" e "`MQTT conectado.`". No terminal de escuta, após o envio de uma imagem pela câmera, chegarão mensagens em `/esp/resultado` e `/esp/metricas`.
5. O `controller/main.py` sobe apenas os agentes do simulador e o logger; ele espera receber a classificação da ESP32 real. Se quiser usar o mock, execute `controller/esp32_mock.py` separadamente.



# Experimentos
O artigo tem como cerne evidenciar o funcionamento concorrente e gargalos na aplicação integrada à Inteligência de Borda das Redes Treinadas sob pilhas de fila. As reivindicações validam o determinismo que dita se essa interconexão falha por *timing* e estouros de RAM ou tem êxito sob a restrição física extrema do Espressif ESP32-S3 contra um benchmark estático.

## Reivindicações #1
**Reivindicação:** "A MobileNetV2 consumiu 204% mais arena que a conversão acusava em placa... Apenas a CNN autoral operou com fluidez sistêmica efetiva e consumindo enxutos 38,4 KB estáticos." (Seção 4.3).

Para reproduzir este distanciamento em consumo de recursos de Edge AI (RAM Memory Profile) da matriz TFLite durante instâncias físicas, faremos um acompanhamento da inicialização.

**Processo e Alterações de Modelos:**
1. A arquitetura vem formatada em uso contendo nosso `model_data.cc` (CNN Autoral com compressão INT8 de ~171KB na estática) pré-inclusa e operando unicamente da minúscula SRAM local veloz. O avaliador usará o atalho de monitor serial do ESP `ESP-IDF: Monitor device` com a placa ligada.
2. Observe que há listagens explícitas dos apontamentos de debug internos nativos declarando logs no monitor antes da predição arrancar: `Arena usage: 38400 bytes`. Isso comprova a afirmação de que o limite foi extremamente modesto sob internal memory.
3. Para validar o gargalo catastrófico na classe oposta pesada (MobileNETV2), abra e sobrescreva o script `esp32/main/main_functions.cc` apagando-o e pondo o conteúdo da cópia de backup `esp32/codigos2.txt`. Este código de contingência altera as \textit{Flags} chamando obrigatoriamente do componente sub-módulo *Espressif SPI* as linhas de Heap PSRAM (ex: `heap_caps_malloc(arena_size, MALLOC_CAP_SPIRAM);`), porque na própria SRAM os tamanhos esbarram de forma iminente nos limites, a ponto de travar (kernel panic/throw c++ exception). 
4. No terminal, insira `cp esp32/modelos/v2_Inteira_model.cc esp32/main/model_data.cc`.
5. Recompile o código da placa. Constatará um salto assombroso para estabilizar a rede: consumos superiores na faixa de alocação de `545.4 KB` de \textit{Tensor Arena}. E, conforme alertado na pesquisa referendada no artigo, o próprio modelo sofrerá com degradações numéricas nos resultados ao longo dos ciclos.
**Expectativa de Recursos:** Nenhum script adicional e memória Python para esta parte; o processo se dá primariamente por monitoração USB atada localmente. O tempo aproximado deste setup e gravação dual não excede 5 à 7 minutos de reescrita em Flash Rom. (A CPU de seu desktop alcançará 100% de ocupação enquanto o LLVM re-vincula o objeto CC do tensor ao makefile).


## Reivindicações #2
**Reivindicação:** "A CNN autoral operou com fluidez sistêmica efetiva e 100\% de acerto sob 53,87 ms [...] o processamento contínuo fixo imposto pelo microcontrolador amortece rajadas concorrentes de eventos advindas da simulação." (Seção 4.4).

Verificaremos o ciclo integrado (comunicação M2M, detecção visual mecânica contínua, extração binária e *Jitter/Latência* fixada por roteamento MQTT local da predição).

**Processo de Execução:**
1. Volte ao modelo seguro (CNN Autoral do passo original de instalação) que foi pré-certificado operante sobre os braços robóticos. Certifique-se também que ao final dos ajustes de rede não deixou senhas erradas ou desconectou seu terminal da mesma sub-rede wi-fi do ESP.
2. No seu computador host com o `cenario_novo.ttt` do Coppelia aberto e quieto, inicie todos os agentes simuladores engatilhando o script gerador geral `main.py` do diretório env.
```bash
cd EdgeAI_SBRC/controller
source .venv/bin/activate
python3 main.py
```
3. Este terminal invocará dezenas de `subprocess.Popen`, iniciando o relógio na ferramenta Coppelia com a API de ZMQ paralelamente.
4. **Visão da Simulação e Robôs:** Você verá o braço Franka Panda operar autonomamente, aguardar caixas vindas livremente pela esteira, agarrá-las usando trigonometria computacional inversa (IK solver) e pondo nos omnidirecionais passivos em KUKA youBots. O robô navega de forma autônoma por \textit{waypoints} para apresentar o objeto à zona de visão. No Coppelia, em "Camera Sensor", bytes brutos RGB saltam por rede Wi-Fi ao Mosquitto passando diretamente de Python ao núcleo Xtensa LX7 em C++.
5. O terminal do Host agora estará preenchido pela repetição controlada dos Agentes reportando latências da sua própria via (ex: recebendo \textit{callbacks}). A caixa é sempre guiada a uma zona de aprovação pelo UR10 graças a validação 0, 1 e 2 classificada no Hardware.

**Resultados Esperados:**
A partir de seu encerramento total após os 180 blocos ou de interrupções explícitas manuais do avaliador (`Ctrl+C`), os módulos criam métricas no diretório local. Dentro de `/controller` o documento `resultados_latencia.csv` compilará timestamps e tempos deltas. Analisando as células de médias centrais de tráfego, poderá obter o dado de veracidade afirmado no paper referente ao \textit{delay} de $\sim$53.87 ms isolados pela CNN e em contrapartida, comprovar sua confiabilidade de assertividade não obstrutiva face as altas taxas e \textit{jitters} provindos em nuvem de uma orquestração não-síncrona (como detalhado na tabela 4 do manuscrito).

# Análise dos Resultados

Os dados coletados pelos experimentos estão em `resultados/calcular/`. Os scripts Python nessa pasta processam os CSVs e geram os gráficos e apêndices em PDF presentes no artigo.

> 📄 **Documentação completa** (estrutura de dados, formato dos CSVs, nota sobre relógio do ESP32): [`resultados/calcular/README.md`](resultados/calcular/README.md)

> 🔗 **Dados sem Edge AI (linha de base):** os dados em `resultados/calcular/sem edge ai/` foram coletados no repositório auxiliar [github.com/Keltonmd/Multiagentes](https://github.com/Keltonmd/Multiagentes), que implementa o mesmo cenário robótico sem a adição da câmera e do microcontrolador.

## Pré-requisitos para Análise

```bash
cd resultados/calcular
pip install -r requirements.txt
```

## Passo 1 — Gráficos e CSV de métricas (Com Edge AI)

Gera os 3 gráficos publicados no artigo e um CSV consolidado a partir dos dados coletados no ESP32-S3 e nos agentes robóticos:

```bash
cd "resultados/calcular/com edge ai"
python gerar_resultados.py
```

**Saídas geradas em `resultados/calcular/com edge ai/`:**
| Arquivo | Conteúdo |
|---|---|
| `grafico1_inferencia_modelos.png` | Tempo mediano de inferência: CNN Autoral vs MobileNetV2 vs V3 |
| `grafico2_mediana_latencia.png` | Latência mediana por tópico MQTT (Local / Edison / AWS) |
| `grafico3_jitter.png` | Jitter por tópico MQTT (Local / Edison / AWS) |
| `metricas_topicos_final.csv` | Tabela consolidada de métricas (mediana, jitter, amostras) |

## Passo 2 — Apêndices A, B e C em PDF

Gera as tabelas de métricas consolidadas (mediana e jitter) apresentadas nos apêndices do artigo:

```bash
cd resultados/calcular
python gerar_apendices.py
```

**Saídas geradas em `resultados/calcular/apendices_pdf/`:**
| Arquivo | Conteúdo |
|---|---|
| `apendice_A_sem_edge_ai.pdf` | Latência por tópico — cenário sem Edge AI |
| `apendice_B_com_edge_ai.pdf` | Latência por tópico — cenário com Edge AI |
| `apendice_C_inferencia_esp32.pdf` | Tempo de inferência por modelo no ESP32 |

## Passo 3 — Apêndices D e E (dados brutos) em PDF

Gera tabelas com cada medição individual para auditoria completa dos dados:

```bash
cd resultados/calcular
python gerar_brutos.py
```

**Saídas geradas em `resultados/calcular/apendices_pdf/`:**
| Arquivo | Conteúdo |
|---|---|
| `apendice_D_brutos_sem_edge.pdf` | Medições brutas — cenário sem Edge AI |
| `apendice_E_brutos_com_edge.pdf` | Medições brutas — cenário com Edge AI |

# LICENSE

Este artefato lógico/software, em resguardo a todo seu repositório digital de componentes, roteiros integrativos simulados (exceto logos, componentes padronizados proprietários preexistentes englobados no CoppeliaSim) ou partes explícitas retidas em terceiros via licenciamento condicional — está disponível de código-livre aberto aos preceitos da **MIT License**.

Copyright (c) 2026 Kelton e autores associados (EdgeAI SBRC, IFNMG - C. Januária).

Por favor, verifique o arquivo `LICENSE` original incluso na raiz completa do repositório clonado para consultar cópias integrais dos parágrafos de atribuições contratuais diretas.
