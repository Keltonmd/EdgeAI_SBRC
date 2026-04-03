# Título projeto
Avaliação de Inferência em Edge AI sob Restrições Embarcadas em um Sistema Robótico Simulado Baseado na Internet das Coisas Robóticas

**Resumo:**
Este trabalho avalia inferência Edge AI na Internet das Coisas Robóticas (IoRT). Três CNNs foram embarcadas em um ESP32-S3 de forma interligada a um cenário industrial simulado via MQTT no CoppeliaSim. Constatou-se uma grave discrepância entre estimativas teóricas de memória vis-à-vis sua alocação real: a MobileNetV2 consumiu 204% mais arena que a conversão acusava em placa, falhando junto da pré-treinada V3 nos ensaios embarcados práticos. Apenas a CNN autoral operou com fluidez sistêmica efetiva e 100% de acerto sob 53,87 ms consumindo enxutos 38,4 KB estáticos, isolando predições fidedignas no chão de fábrica simulado.

# Estrutura do readme.md
Apresenta a organização deste repositório e README:
1. Título do projeto
2. Estrutura do readme.md e do Repositório
3. Selos Considerados
4. Informações básicas
5. Dependências
6. Preocupações com segurança
7. Instalação
8. Teste mínimo
9. Experimentos
10. LICENSE

**Estrutura do Repositório:**
```
EdgeAI_SBRC/
├── cenario/          # Cena CoppeliaSim com todos os robôs e sensores (.ttt)
├── controller/       # Scripts Python de controle e orquestração via ZMQ e MQTT
├── esp32/            # Projeto de Firmware C/C++ ESP-IDF (TensorFlow Lite Micro)
├── modelos/          # Modelos Keras exportados e conversões para TFLite (.cc)
├── Dataset/          # [Não versionado] Diretório com particionamentos RGB 32x32
└── Treinamento/      # Scripts/Notebooks (.ipynb) de treinamento dos modelos
```

# Selos Considerados
Os selos considerados neste processo de avaliação pelo Comitê Técnico de Artefatos (CTA) são:
- **Disponíveis (SeloD)**
- **Funcionais (SeloF)**
- **Sustentáveis (SeloS)**
- **Reprodutíveis (SeloR)**

# Informações básicas
Este artefato propõe, implementa e avalia uma arquitetura de comunicação e colaboração baseada em mensageria orientada a eventos para coordenação de robôs heterogêneos em ambiente industrial. A parte física e logística é simulada; entretanto, a IA (computação visual em borda) roda de forma totalmente desconectada em um microcontrolador real operando via internet.

> **⚠️ REQUISITO FÍSICO OBRIGATÓRIO (RESTRIÇÃO DE HARDWARE):** 
> Para a execução completa, reprodução dos experimentos e validação dos selos de funcionalidade, é **estritamente necessário possuir fisicamente uma placa de desenvolvimento ESP32-S3**. Sem este componente físico de hardware, é impossível efetuar as chamadas das Redes Neurais via TFLite Micro, impossibilitando com que os robôs do simulador tomem decisões, visto que as predições ocorrem de forma isolada do Host.

**Ambiente de Execução Global:**
- **Computador Host:** Sistema Operacional Linux (Ubuntu 20.04+ ou Debian 11+ recomendado). Necessita de ≥ 8GB de RAM para suportar a simulação gráfica, processos do orquestrador Python e o broker de rede de maneira conjunta e estável.
- **Microcontrolador (Edge Device Obrigatório):**
  - MCU: ESP32-S3-WROOM-1-N16R8 (Dual-Core Xtensa LX7 a 240 MHz) ou arquitetura próxima da linha ESP32.
  - SRAM interna: 512 KB
  - Memória Flash: 16 MB
  - PSRAM Externa: 8 MB (opcional ativada apenas para avaliação das arquiteturas MobileNet pesadas apontadas no artigo).
- **Conectividade e Mídia Físicas:** Requer uma conexão de rede sem fio (Wi-Fi 802.11 b/g/n em 2.4GHz ativa) da qual ambos o host e a placa participem e um cabo Micro-USB/Type-C para a compilação. 

# Dependências
Para a reprodução da cadeia descrita no artigo, exige-se as seguintes ferramentas e componentes pré-instalados:
- **Simulador 3D:** CoppeliaSim EDU v4.10.0. Responsável pelas físicas cinemáticas. (Versão 4.4+ obrigatoriamente para compatibilidade nativa com *ZMQ Remote API*).
- **Broker MQTT:** Eclipse Mosquitto. Ferramenta de roteamento para arquitetura Pub/Sub.
- **IDE Python:** Interpretador Python 3.10 ou superior. Os pacotes estritos listados em `controller/requirements.txt` devem estar presentes no VirtualEnv (`cbor==1.0.0`, `coppeliasim-zmqremoteapi-client==2.0.4`, `numpy==2.3.1`, `pandas`, `openpyxl`, `paho-mqtt==2.1.0`, `pyzmq==27.0.0`).
- **Chain de Build C/C++:** Instalação do ESP-IDF (Espressif IoT Development Framework) na versão **v5.2.x**. Pode ser extraída diretamente pela sua Extensão formal de mercado no VS Code ("Espressif IDF").
- **Bibliotecas Lógicas de IA (Embarcado):** Dependência TFLite Micro instalada. Em nosso código-fonte, usa-se a biblioteca modificada `espressif/esp-tflite-micro` na sua revisão `v1.3.5`. Devido à modernidade de nossa implementação Cmake, tal biblioteca já atua nativamente atracada e manipulada de forma automática pelo manifest `idf_component.yml` dentro de `esp32/main` e não necessita download reverso manual.

# Preocupações com segurança
Caso a execução do artefato ofereça algum tipo de risco para os avaliadores, este risco deve ser descrito. 
Neste projeto **não há riscos diretos significativos (físicos, químicos ou elétricos)**. As operações físicas mecânicas manipuláveis — garras e robôs móveis omnidirecionais pesados — habitam limites perfeitamente digitais por viés do simulador virtual acadêmico. Por seu turno, o Edge device que executa os gargalos matemáticos de processamento de Visão é mantido por tensão mínima (corrente contínua provinda de barramento USB comum 3.3v~5.0v), abstendo todo risco de surto reverso. Nenhum tipo de payload malicioso contendo shell ou rootkits perigosos é transmitido nos bytes pela fila MQTT.

# Instalação
O processo de inicialização do ecossistema depende das partes comunicantes expostas estarem íntegras.

**1. Clonagem e Configuração do Repositório:**
```bash
git clone https://github.com/Keltonmd/EdgeBoxAI.git EdgeAI_SBRC
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
sudo mosquitto_passwd -c /etc/mosquitto/passwd kelton  # Senha: Projeto2025
sudo systemctl restart mosquitto 
```

**4. Preparando o Controller Python (Atores da Cena):**
```bash
cd EdgeAI_SBRC/controller
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
*(Nota: No arquivo `MqttAgent.py`, certifique-se que o parâmetro padrão no `__init__` onde cita `broker: str == "debian.local"` aponte em fato para `"localhost"` ou o hostname exato da sua máquina atual do teste. O Python não conectará os nós caso não ache o broker).*

**5. Compilando o Firmware do microcontrolador (ESP32):**
Configurável rapidamente por intermédio do VS Code.
1. No VS Code, acesse o painel de extensões e instale `ESP-IDF`. Prossiga pela Express config usando ESP-IDF v5.2 ou mais limpo.
2. Acesse a pasta `EdgeAI_SBRC/esp32/` pela IDE e espere o framework de *build* analisar as rotas e injetar o motor Makefile do sistema de plugins cmake C++.
3. Em `main_functions.cc`, substitua os dados fictícios locais:
```cpp
strcpy((char*)wifi_config.sta.ssid,     "NOME_DA_SUA_REDE");
strcpy((char*)wifi_config.sta.password, "SENHA_DA_SUA_REDE");
cfg.broker.address.uri = "mqtt://192.168.1.XXX:1883"; // Seu host (ifconfig)
```
4. Conecte sua placa à porta serial, selecione `Set Target > esp32s3` na statusbar. 
5. Clique em **Flash** do menu do ESP. O compilador criará dezenas de bibliotecas secundárias de Inteligência. Fim da Instalação do sistema global.

# Teste mínimo
Este passo comprova a comunicação básica e o funcionamento estrito da Edge AI independente da cena, validando o recebimento da mensagem serial e sua emissão após a etapa de Instalação.

1. Assegure-se de que o Moquitto esteja ligado: status systemctl ok.
2. Na janela de comandos principal (computador onde o Python se iniciará), abra uma escuta aos tópicos produzidos por uma possível placa:
```bash
mosquitto_sub -h localhost -u kelton -P Projeto2025 -t "/esp/#" -v
```
3. Na placa ESP conectada, mantenha ativado seu Monitor de Serial via terminal integrado do VS-Code (`Ctrl+Shift+P` -> `ESP-IDF: Monitor device`). 
4. **Comportamento Esperado:** Nas linhas que subirão da placa via USB (serial), uma estampará o elance de sucesso "`I (xxxx) wifi: connected to ap`", seguida de confirmação do nó de fila com "`MQTT: Connected to broker`". Logo em seguida dirá que aguarda imagens. No terminal Host do Mosquitto, verifique se a mensagem retentiva chegou atestando se a porta e IPs passados entre os módulos estão na malha da rede certas, de forma que as comunicações se confirmam sáfias para o fluxo final de grandes experimentos das seções posteriores.

# Experimentos
O artigo tem como cerne evidenciar o funcionamento concorrente e gargalos na aplicação integrada à Inteligência de Borda das Redes Treinadas sob pilhas de fila. As reivindicações validam o determinismo que dita se essa interconexão falha por *timing* e estouros RAM ou tem êxito sob a restrição física extrema do Espressif ESP32-S3 contra um benchmark estático.

## Reivindicações #1
**Reivindicação:** "A MobileNetV2 consumiu 204% mais arena que a conversão acusava em placa... Apenas a CNN autoral operou com fluidez sistêmica efetiva e consumindo enxutos 38,4 KB estáticos." (Seção 4.3).

Para reproduzir este distanciamento em consumo de recursos de Edge AI (RAM Memory Profile) da matriz TFLite durante instâncias físicas, faremos um acompanhamento da inicialização.

**Processo e Alterações de Modelos:**
1. A arquitetura vem formatada em uso contendo nosso `model_data.cc` (CNN Autoral com compressão INT8 de ~171KB na estática) pré-inclusa e operando unicamente da minúscula SRAM local veloz. O avaliador usará o atalho de monitor serial do ESP `ESP-IDF: Monitor device` com a placa ligada.
2. Observe que há listagens explícitas dos apontamentos de debug internos nativos declarando logs no monitor antes da predição arrancar: `Arena usage: 38400 bytes`. Isso aprova a afirmação que o limite foi extremamente modesto sob internal memory.
3. Para validar o gargalo catastrófico na classe oposta pesada (MobileNETV2), abra e sobrescreva o script `esp32/main/main_functions.cc` apagando-o e pondo o conteúdo da cópia de backup `esp32/codigos2.txt`. Este código de contingência altera as \textit{Flags} chamando obrigatoriamente do componente sub-módulo *Espressif SPI* as linhas de Heap PSRAM (ex: `heap_caps_malloc(arena_size, MALLOC_CAP_SPIRAM);`), porque na própria SRAM os tamanhos esbarram de iminente de forma a travar (kernel panic/throw c++ exception). 
4. Na ide, insira `cp esp32/modelos/v2_Inteira_model.cc esp32/main/model_data.cc`.
5. Recompile a placa. Constatará um salto assombroso para estabilizar a rede: consumos superiores na faixa de alocação de `545.4 KB` de \textit{Tensor Arena}. E, conforme alertado na pesquisa referendada no artigo, o próprio modelo sofrerá com degradações numéricas nos resultados ao longo dos ciclos.
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
4. **Visão da Simulação e Robôs:** Você verá o braço Franka Panda operar autonomamente, aguardar caixas vindas livremente pela esteira, agarrá-las usando trigonometria computacional inversa (IK solver) e pondo nos omnidirecionais passivos em KUKA youBots. O robô viaja propostas autônomas por \textit{waypoints} para apresentar à zona de visão. No Coppelia, em "Camera Sensor", bytes brutos RGB saltam por rede Wi-Fi ao Mosquitto passando diretamente de Python ao núcleo Xtensa LX7 em C++.
5. O terminal do Host agora estará poluído pela repetição controlada dos Agentes reportando latências da sua própria via (ex: recebendo \textit{callbacks}). A caixa é sempre guiada a uma zona de aprovação pelo UR10 graças a validação 0, 1 e 2 classificada no Hardware.

**Resultados Esperados:**
A partir de seu encerramento total após os 180 blocos ou de intersecções explícitas manuais do avaliador (`Ctrl+C`), os módulos criam métricas no diretório local. Dentro de `/controller` o documento `resultados_latencia.csv` compilará timestamps e tempos deltas. Analisando as células de médias centrais de tráfego, poderá obter o dado de veracidade afirmado no paper referente ao \textit{delay} de $\sim$53.87 ms isolados pela CNN e em contrapartida, comprovar sua confiabilidade de assertividade não obstrutiva face as altas taxas e \textit{jitters} provindos em nuvem de uma orquestração não-síncrona (como detalhado na tabela 4 do manuscrito).

# LICENSE
Este artefato lógico/software, em resguardo a todo seu repositório digital de componentes, roteiros integrativos simulados (execto logos, componentes padronizados proprietários preexistentes englobados no CoppeliaSim) ou partes explícitas retidas em terceiros via licenciamento condicional — está disponível de código-livre aberto aos preceitos da **MIT License**.

Copyright (c) 2026 Kelton e autores associados (EdgeAI SBRC, IFNMG - C. Januária).

Por favor, verifique o arquivo `LICENSE` original incluso na raiz completa do repositório clonado para consultar cópias integrais dos parágrafos de atribuições contratuais diretas.
