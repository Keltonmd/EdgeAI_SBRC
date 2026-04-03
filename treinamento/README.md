# 🧠 CNN EdgeAI — Treinamento de Modelos para Classificação de Cores

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1oBZcstCkrvkj5GFwm9B4oe0iajFY_G-V?usp=sharing)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)](https://www.python.org/)
[![TensorFlow](https://img.shields.io/badge/TensorFlow-2.x-orange?logo=tensorflow)](https://www.tensorflow.org/)
[![TFLite](https://img.shields.io/badge/TFLite-Edge%20Deployment-green)](https://www.tensorflow.org/lite)
[![Dataset](https://img.shields.io/badge/Dataset-Kaggle-20beff?logo=kaggle)](https://www.kaggle.com/datasets/keltonmartins/colors-red-and-blue)

> Módulo de treinamento do projeto **"Avaliação de Inferência em Edge AI sob Restrições Embarcadas em um Sistema Robótico Simulado Baseado na Internet das Coisas Robóticas"** (SBRC 2026).

Este diretório contém o notebook de treinamento e avaliação de redes neurais convolucionais (CNNs) para a tarefa de **classificação de cores** (Azul, Vermelho e Background), com foco em implantação em dispositivos de **borda (Edge AI)**. O modelo final é exportado para o formato `.tflite` para ser executado de forma eficiente em hardware embarcado.

---

## 📋 Sumário

1. [Descrição](#-descrição)
2. [Estrutura do Notebook](#️-estrutura-do-notebook)
3. [Arquiteturas dos Modelos](#-arquiteturas-dos-modelos)
4. [Dataset](#-dataset)
5. [Dependências](#️-dependências)
6. [Como Usar](#-como-usar)
7. [Saídas Geradas](#-saídas-geradas)
8. [Parâmetros de Treinamento](#️-parâmetros-de-treinamento)
9. [Pipeline de Conversão para TFLite](#-pipeline-de-conversão-para-tflite)
10. [Contexto do Projeto](#-contexto-do-projeto)
11. [Licença](#-licença)

---

## 📋 Descrição

O notebook `CNN_Lite_final.ipynb` realiza um **estudo comparativo** entre três arquiteturas de CNN:

| Modelo | Tipo | Parâmetros |
|---|---|---|
| **MobileNetV3 Small** | Transfer Learning (ImageNet) | ~2.5M |
| **MobileNetV2** | Transfer Learning (ImageNet) | ~2.3M |
| **CNN Customizada** | Do zero  | Custom |

O melhor modelo é convertido para o formato **TensorFlow Lite (TFLite)** para ser embarcado no sistema de Edge AI descrito no artigo.

---

## 🗂️ Estrutura do Notebook

```
CNN_Lite_final.ipynb
│
├── 📦 1. Aquisição e Configuração de Dados
│   ├── Download do dataset via kagglehub
│   ├── Organização das classes em diretórios
│   └── Split: 70% treino / 15% validação / 15% teste
│
├── 🔬 2. Treinamento dos Modelos
│   ├── MobileNet V3 Small (Transfer Learning)
│   ├── MobileNet V2 (Transfer Learning)
│   └── CNN Customizada 
│
├── 📊 3. Avaliação e Métricas
│   ├── Curvas de Accuracy e Loss
│   └── Matrizes de Confusão (por modelo)
│
└── 🚀 4. Conversão para Edge AI
    ├── Carregamento do melhor modelo (.keras)
    └── Exportação para TFLite (.tflite)
```

---

## 🏗️ Arquiteturas dos Modelos

### MobileNet V3 Small & MobileNet V2 (Transfer Learning)
```
Base MobileNet (pesos ImageNet, congelados na Fase 1)
  └── GlobalAveragePooling2D
      └── Dense(32, LeakyReLU(0.01)) + L2
          └── Dropout(0.4)
              └── Dense(3, softmax)  ← saída
```

**Estratégia de treinamento em 2 fases:**
- **Fase 1:** Base congelada → 50 épocas, Adam (lr=1e-3)
- **Fase 2:** Fine-tuning completo → 50 épocas, Adam (lr=1e-5)

### CNN Customizada 
```
Input (32x32x3)
  └── [Block 1] Conv2D(32) → Conv2D(32) → MaxPool → Dropout(0.2)
      └── [Block 2] Conv2D(64) → Conv2D(64) → MaxPool → Dropout(0.3)
          └── [Block 3] Conv2D(128) → MaxPool → Dropout(0.4)
              └── Flatten → Dense(128) → Dropout(0.5) → Dense(3, softmax)
```
**Treinamento:** 100 épocas, Adam (lr=1e-3)

---

## 📊 Dataset

- **Nome:** `colors-red-and-blue`
- **Fonte:** [Kaggle — keltonmartins/colors-red-and-blue](https://www.kaggle.com/datasets/keltonmartins/colors-red-and-blue)
- **Classes:**
  - `0` — Azul (Blue)
  - `1` — Vermelho (Red)
  - `2` — Background
- **Resolução de entrada:** `32 × 32` pixels
- **Divisão dos dados:**
  - 🟢 Treino: **70%**
  - 🔵 Validação: **15%**
  - 🔴 Teste: **15%**

---

## 🛠️ Dependências

| Biblioteca | Uso |
|---|---|
| `tensorflow` / `keras` | Treinamento e conversão dos modelos |
| `opencv-python` (cv2) | Leitura e pré-processamento de imagens |
| `numpy` | Manipulação de arrays |
| `matplotlib` | Plotagem de curvas de treinamento |
| `seaborn` | Visualização de matrizes de confusão |
| `scikit-learn` | Divisão e embaralhamento do dataset |
| `kagglehub` | Download automático do dataset |

### Instalação

```bash
pip install tensorflow opencv-python numpy matplotlib seaborn scikit-learn kagglehub
```

> **Recomendado:** Execute no Google Colab para acesso a GPU gratuita.

---

## 🚀 Como Usar

### Opção 1: Google Colab (Recomendado)

1. Acesse o notebook diretamente pelo badge no topo deste README.
2. Certifique-se de usar uma sessão com **GPU** ativada:
   - `Ambiente de execução` → `Alterar tipo de ambiente de execução` → `GPU`
3. Configure sua credencial do Kaggle para download do dataset:
   - Crie um token em [kaggle.com/settings](https://www.kaggle.com/settings)
   - Faça upload do arquivo `kaggle.json` quando solicitado
4. Execute todas as células em ordem (`Ctrl+F9` ou `Runtime > Run All`).

### Opção 2: Localmente (Jupyter)

```bash
# Clone o repositório principal
git clone https://github.com/Keltonmd/EdgeAI_SBRC.git
cd EdgeAI_SBRC/treinamento

# Instale as dependências
pip install tensorflow opencv-python numpy matplotlib seaborn scikit-learn kagglehub jupyter

# Configure o Kaggle
mkdir ~/.kaggle
cp kaggle.json ~/.kaggle/
chmod 600 ~/.kaggle/kaggle.json

# Abra o notebook
jupyter notebook CNN_Lite_final.ipynb
```

---

## 📁 Saídas Geradas

Após a execução completa do notebook, os seguintes arquivos são gerados:

| Arquivo | Descrição |
|---|---|
| `modeloV3.keras` | Melhor modelo MobileNetV3 Small salvo via `ModelCheckpoint` |
| `modeloV2.keras` | Melhor modelo MobileNetV2 salvo via `ModelCheckpoint` |
| `modelo_base.keras` | Melhor modelo CNN Customizada salvo via `ModelCheckpoint` |
| `modelo.tflite` | **Modelo final convertido para Edge AI (TFLite)** |

---

## ⚙️ Parâmetros de Treinamento

| Parâmetro | MobileNets | CNN Customizada |
|---|---|---|
| Batch Size | 16 | 16 |
| Épocas (Fase 1) | 50 | — |
| Épocas (Fase 2 / Total) | 50 | 100 |
| Otimizador | Adam | Adam |
| Learning Rate (inicial) | 1e-3 | 1e-3 |
| Learning Rate (fine-tune) | 1e-5 | — |
| Regularização | L2 | Dropout |

---

## 🔄 Pipeline de Conversão para TFLite

Após o treinamento, o modelo com melhor desempenho é convertido para implantação em edge:

```python
# Carregar o melhor modelo
model = tf.keras.models.load_model('modeloV3.keras')

# Converter para TFLite
converter = tf.lite.TFLiteConverter.from_keras_model(model)
tflite_model = converter.convert()

# Salvar o arquivo
with open('modelo.tflite', 'wb') as f:
    f.write(tflite_model)
```

O arquivo `modelo.tflite` é posteriormente implantado no dispositivo de borda descrito na arquitetura do sistema (veja o repositório principal).

---

## 📚 Contexto do Projeto

Este notebook faz parte do projeto **EdgeAI SBRC**, que propõe uma arquitetura de visão computacional embarcada para classificação em tempo real usando:

- **ESP32-S3** (ou microcontrolador equivalente) como dispositivo de borda
- **TensorFlow Lite Micro** para inferência eficiente
- **MQTT** para comunicação dos resultados

Para mais detalhes sobre a arquitetura completa do sistema, consulte o [README principal do projeto](../README.md).

---

## 📄 Licença

Este módulo faz parte do projeto **EdgeAI SBRC** e está licenciado sob a **MIT License**.

Consulte o arquivo [`LICENSE`](../LICENSE) na raiz do repositório para os termos completos.

---

*Desenvolvido no contexto do artigo submetido ao SBRC 2026 — IFNMG Campus Januária.*
