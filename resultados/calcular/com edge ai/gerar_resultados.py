"""
gerar_resultados.py — Script principal de análise dos resultados "Com Edge AI"
===============================================================================
Gera os 3 gráficos e o CSV de métricas consolidadas a partir dos dados coletados
nos experimentos com CNN embarcada no ESP32-S3.

Estrutura esperada de dados (relativa a este script):
    com edge ai/
    ├── cnn_autoral/
    │   ├── local/    → resultados_*.csv  +  metricas_esp.csv
    │   ├── edison/   → resultados_*.csv  +  metricas_esp.csv
    │   └── aws/      → resultados_*.csv  +  metricas_esp.csv
    ├── v2/
    │   └── metricas_esp.csv              (apenas inferência, sem agentes)
    └── v3/
        └── metricas_esp.csv              (apenas inferência, sem agentes)

Saídas geradas (nesta mesma pasta):
    grafico1_inferencia_modelos.png  — Tempo mediano de inferência: V2 vs V3 vs Autoral
    grafico2_mediana_latencia.png    — Mediana de latência por tópico (Local/Edison/AWS)
    grafico3_jitter.png              — Jitter por tópico (Local/Edison/AWS)
    metricas_topicos_final.csv       — Tabela consolidada de métricas

Nota sobre relógio do ESP32:
    O campo `latencia_ms` bruto do metricas_esp.csv é inválido (diferença entre
    timestamp Unix do host e millis() do ESP desde o boot). A latência real do
    tópico /esp/classificar é calculada como:
        latencia_real_ms = (timestamp_logger - timestamp_envio) * 1000
    onde timestamp_logger e timestamp_envio são ambos timestamps Unix do host.

Uso:
    cd "resultados/calcular/com edge ai"
    pip install -r requirements.txt
    python gerar_resultados.py
"""

import pandas as pd
import os
import matplotlib
matplotlib.use('Agg')   # Renderização sem display (servidores/CI)
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import seaborn as sns
import numpy as np
import glob

sns.set(style="whitegrid")
base_dir = os.path.abspath(os.path.dirname(__file__))


# =============================================================================
# FUNÇÕES AUXILIARES
# =============================================================================

def combinar_resultados(pasta: str, ambiente: str) -> pd.DataFrame:
    """Combina todos os resultados_*.csv de uma pasta, retornando
    colunas [Topico, Latencia_ms, Ambiente]."""
    dfs = []
    for arquivo in glob.glob(os.path.join(pasta, 'resultados_*.csv')):
        try:
            df = pd.read_csv(arquivo)
            if 'Topico' in df.columns and 'Latencia_ms' in df.columns:
                df['Ambiente'] = ambiente
                dfs.append(df[['Topico', 'Latencia_ms', 'Ambiente']])
        except Exception as e:
            print(f"  ⚠ Erro ao ler {arquivo}: {e}")
    return pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()


def calcular_offset_relogio(pasta: str):
    """Calcula o offset mediano entre relógio Unix (host) e millis() do ESP.
    Retorna o valor em segundos ou None se o arquivo não existir."""
    caminho = os.path.join(pasta, 'metricas_esp.csv')
    if not os.path.exists(caminho):
        return None
    df = pd.read_csv(caminho)
    offsets = df['timestamp_envio'] - df['timestamp_recebido']
    return float(np.median(offsets))


def extrair_latencia_classificar(pasta: str, ambiente: str) -> pd.DataFrame:
    """Extrai a latência do tópico /esp/classificar a partir do metricas_esp.csv.

    Latência correta = (timestamp_logger − timestamp_envio) × 1000 ms.
    Ambos os timestamps são Unix epoch, gerados no host Python, portanto
    não há problema de dessincronização de relógio.
    """
    caminho = os.path.join(pasta, 'metricas_esp.csv')
    if not os.path.exists(caminho):
        return pd.DataFrame()
    df = pd.read_csv(caminho)
    latencias = (df['timestamp_logger'] - df['timestamp_envio']) * 1000.0
    return pd.DataFrame({
        'Topico': '/esp/classificar',
        'Latencia_ms': latencias,
        'Ambiente': ambiente
    })


# =============================================================================
# GRÁFICO 1 — Tempo mediano de inferência: V2 vs V3 vs CNN Autoral
# =============================================================================
print("\n=== [1/3] Tempo Mediano de Inferência por Modelo ===")

modelos_esp = {
    'MobileNet V2': os.path.join(base_dir, 'v2', 'metricas_esp.csv'),
    'MobileNet V3': os.path.join(base_dir, 'v3', 'metricas_esp.csv'),
    'CNN Autoral':  os.path.join(base_dir, 'cnn_autoral', 'local', 'metricas_esp.csv'),
}

dados_inferencia = []
for nome, caminho in modelos_esp.items():
    if not os.path.exists(caminho):
        print(f"  ⚠ Arquivo não encontrado: {caminho}")
        continue
    df = pd.read_csv(caminho)
    col = 'tempo_inferencia_ms'
    if col not in df.columns:
        print(f"  ⚠ Coluna '{col}' ausente em {caminho}")
        continue
    dados_inferencia.append({
        'Modelo': nome,
        'Mediana Inferência (ms)': round(float(np.median(df[col])), 2),
        'N': len(df)
    })

if dados_inferencia:
    df_inf = pd.DataFrame(dados_inferencia)
    print(df_inf.to_string(index=False))

    fig, ax = plt.subplots(figsize=(8, 5))
    sns.barplot(data=df_inf, x='Modelo', y='Mediana Inferência (ms)',
                hue='Modelo', legend=False, palette='coolwarm', ax=ax)
    ax.set_title('Tempo Mediano de Inferência por Modelo (Edge AI)', fontsize=14)
    ax.set_ylabel('Tempo de Inferência (ms)')
    ax.yaxis.set_major_formatter(ticker.FormatStrFormatter('%.0f'))
    for i, row in df_inf.iterrows():
        ax.text(i, row['Mediana Inferência (ms)'] + 2,
                f"{row['Mediana Inferência (ms)']} ms",
                ha='center', fontsize=11, fontweight='bold')
    plt.tight_layout()
    out1 = os.path.join(base_dir, 'grafico1_inferencia_modelos.png')
    plt.savefig(out1, dpi=300)
    plt.close()
    print(f"  ✓ Salvo: {os.path.basename(out1)}")
else:
    print("  ✗ Nenhum dado de inferência disponível para o Gráfico 1.")


# =============================================================================
# GRÁFICOS 2 e 3 — Latência e Jitter por Tópico (Local / Edison / AWS)
# =============================================================================
print("\n=== [2/3] Latência e Jitter por Tópico (CNN Autoral) ===")

cenarios = {
    'Local':  os.path.join(base_dir, 'cnn_autoral', 'local'),
    'Edison': os.path.join(base_dir, 'cnn_autoral', 'edison'),
    'AWS':    os.path.join(base_dir, 'cnn_autoral', 'aws'),
}

partes = []
for ambiente, pasta in cenarios.items():
    if not os.path.isdir(pasta):
        print(f"  ⚠ Pasta não encontrada: {pasta}")
        continue

    # -- Tópicos dos agentes (resultados_*.csv) --
    df_res = combinar_resultados(pasta, ambiente)
    if not df_res.empty:
        # Corrige a latência do tópico /esp/resultado (dessincronização de relógio)
        offset = calcular_offset_relogio(pasta)
        if offset is not None:
            mask = df_res['Topico'] == '/esp/resultado'
            df_res.loc[mask, 'Latencia_ms'] -= offset * 1000.0
            print(f"  {ambiente}: offset de relógio = {offset:.2f}s "
                  f"→ corrigindo {mask.sum()} medições de /esp/resultado")
        partes.append(df_res)

    # -- Tópico /esp/classificar (metricas_esp.csv) --
    df_class = extrair_latencia_classificar(pasta, ambiente)
    if not df_class.empty:
        partes.append(df_class)

if not partes:
    print("  ✗ Nenhum dado de tópicos disponível. "
          "Verifique se as pastas cnn_autoral/local|edison|aws contêm os CSVs.")
else:
    df_geral = pd.concat(partes, ignore_index=True)

    # Remove outliers absurdos (> 10 000 ms) antes de calcular estatísticas
    df_geral = df_geral[df_geral['Latencia_ms'].abs() < 10_000]

    metricas = (
        df_geral.groupby(['Ambiente', 'Topico'])['Latencia_ms']
        .agg(Latencia_Mediana_ms='median', Jitter_ms='std', Amostras='count')
        .reset_index()
    )
    metricas['Latencia_Mediana_ms'] = metricas['Latencia_Mediana_ms'].round(2)
    metricas['Jitter_ms'] = metricas['Jitter_ms'].round(2)
    metricas['Ambiente'] = pd.Categorical(
        metricas['Ambiente'], categories=['Local', 'Edison', 'AWS'], ordered=True
    )
    metricas = metricas.sort_values(['Topico', 'Ambiente'])

    print("\nMétricas consolidadas:")
    print(metricas.to_string(index=False))

    csv_out = os.path.join(base_dir, 'metricas_topicos_final.csv')
    metricas.to_csv(csv_out, index=False)
    print(f"\n  ✓ CSV salvo: {os.path.basename(csv_out)}")

    # --- Gráfico 2: Mediana da Latência ---
    fig, ax = plt.subplots(figsize=(16, 7))
    sns.barplot(data=metricas, x='Topico', y='Latencia_Mediana_ms',
                hue='Ambiente', palette='Set2', ax=ax)
    ax.set_title('Mediana da Latência por Tópico e Cenário (CNN Autoral)', fontsize=14)
    ax.set_ylabel('Latência Mediana (ms)')
    ax.set_xlabel('Tópico MQTT')
    ax.yaxis.set_major_formatter(ticker.FormatStrFormatter('%.0f'))
    plt.xticks(rotation=45, ha='right')
    plt.legend(title='Cenário')
    plt.tight_layout()
    out2 = os.path.join(base_dir, 'grafico2_mediana_latencia.png')
    plt.savefig(out2, dpi=300)
    plt.close()
    print(f"  ✓ Salvo: {os.path.basename(out2)}")

    # --- Gráfico 3: Jitter ---
    fig, ax = plt.subplots(figsize=(16, 7))
    sns.barplot(data=metricas, x='Topico', y='Jitter_ms',
                hue='Ambiente', palette='Set2', ax=ax)
    ax.set_title('Jitter por Tópico e Cenário (CNN Autoral)', fontsize=14)
    ax.set_ylabel('Jitter (ms)')
    ax.set_xlabel('Tópico MQTT')
    ax.yaxis.set_major_formatter(ticker.FormatStrFormatter('%.0f'))
    plt.xticks(rotation=45, ha='right')
    plt.legend(title='Cenário')
    plt.tight_layout()
    out3 = os.path.join(base_dir, 'grafico3_jitter.png')
    plt.savefig(out3, dpi=300)
    plt.close()
    print(f"  ✓ Salvo: {os.path.basename(out3)}")

print("\n✅ Análise concluída com sucesso!\n")
