# Cenário de Simulação (CoppeliaSim)

Este diretório contém o ambiente virtual simulado utilizado no projeto EdgeAI_SBRC para a avaliação do sistema robótico interconectado via protocolos de Internet das Coisas Robóticas (IoRT).

## Conteúdo

* **`cenario_novo.ttt`**: Arquivo de cena do simulador CoppeliaSim. Este ambiente inclui todos os artefatos físicos reproduzidos digitalmente:
  * Braços robóticos (ex: Franka Panda, UR10)
  * Robôs móveis omnidirecionais (ex: KUKA youBots)
  * Esteiras, caixas e sensores de visão (câmeras)
  * Todo o conjunto de regras cinemáticas necessárias

## Instalação do CoppeliaSim

Para executar a simulação, é estritamente necessário ter o **CoppeliaSim Edu** instalado em seu sistema (a versão recomendada e testada no projeto é a **v4.10.0** ou superior, pois ela garante a estabilidade necessária e possui suporte nativo atualizado à API *ZMQ Remote*, que interconecta o simulador ao controlador Python).

Siga os passos detalhados abaixo para instalar e rodar o simulador em um ambiente Linux (requisito base do projeto - Ubuntu 20.04+ ou Debian 11+):

1. **Acesso ao portal:** Navegue até a página de downloads no site oficial da fabricante (Coppelia Robotics): [https://www.coppeliarobotics.com/downloads](https://www.coppeliarobotics.com/downloads).
2. **Download do pacote:** Localize a seção destinada à licença **Edu** (voltada para ambientes acadêmicos) e baixe o pacote correspondente ao seu sistema operacional Linux (geralmente Ubuntu). O pacote estará compactado no formato `.tar.xz` (pesando entre 300MB e 500MB). Exemplo de arquivo: `CoppeliaSim_Edu_V4_10_0_Ubuntu20_04.tar.xz`.
3. **Preparo do diretório:** Abra um terminal em sua máquina. Recomenda-se criar um diretório amigável para alocar suas aplicações pessoais na sua pasta local (Home do usuário), evitando problemas com permissões de administrador:
   ```bash
   mkdir -p ~/Applications
   ```
4. **Extração dos binários:** Utilize a ferramenta nativa `tar` para extrair os arquivos baixados diretamente para o novo diretório de aplicações. (O comando abaixo procura o instalador na pasta Downloads. Ajuste o caminho se necessário):
   ```bash
   tar -xf ~/Downloads/CoppeliaSim_Edu_V4_10_0_*.tar.xz -C ~/Applications/
   ```
5. **Inicialização do software:** No Linux, o CoppeliaSim não requer a instalação padrão de pacotes via gerenciador (como `apt`). Ele é disponibilizado na forma *portable* e executado apenas executando um *launcher* `.sh`. Para abri-lo pelo terminal sempre que for utilizar o projeto, chame o arquivo principal:
   ```bash
   ~/Applications/CoppeliaSim_Edu_V4_10_0_*/coppeliaSim.sh
   ```
   > **Nota Importante:** É comum que, durante as primeiras inicializações via linha de comando, o software demore um pouco para levantar a interface 3D por conta do acoplamento dinâmico à biblioteca gráfica *OpenGL* ou *Vulkan*. **Não feche o terminal** de onde o executável foi chamado, caso contrário o simulador será imediatamente encerrado.

## Como Utilizar

Este cenário é projetado para operar em conjunto com a orquestração em Python (`controller/`) e o dispositivo físico de borda (ESP32-S3), mas ele não deve ser iniciado manualmente dando *Play* no simulador.

1. Inicie o CoppeliaSim Edu de acordo com os passos de instalação acima.
2. Vá em `File > Open Scene...` e carregue o arquivo `cenario_novo.ttt`.
3. **Atenção:** Mantenha o simulador aberto e minimizado. **Não aperte o botão de *Play***. O controle de tempo da simulação, *steps* e a movimentação dos robôs são comandados remotamente pelos scripts orquestradores presentes na pasta `controller/`.

## Requisitos de Execução

- **Simulador:** CoppeliaSim EDU (v4.10.0 recomendada).
- **RAM do Host:** O computador host necessita de pelo menos 8GB de RAM para suportar a simulação gráfica, processos do orquestrador Python e o broker MQTT em paralelo.
