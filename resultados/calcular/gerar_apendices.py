"""
gerar_apendices.py — Gera os Apêndices A (sem Edge AI) e B+C (com Edge AI) em PDF
====================================================================================
Apêndice A: tabela de latência mediana e jitter por tópico para cada ambiente,
            usando os dados do repositório Multiagentes (sem Edge AI).
Apêndice B: mesma tabela, porém com os dados com Edge AI (CNN Autoral).
Apêndice C: tabela de tempo de inferência ESP por modelo (Autoral vs V2 vs V3).

Estrutura de dados esperada (caminhos relativos a este script):
    sem edge ai/
    ├── Local/
    │   ├── resultados_Franka.csv
    │   ├── resultados_youBot.csv
    │   ├── resultados_UR10.csv
    │   └── resultados_sensor.csv
    ├── Edison/
    │   ├── resultados_Franka_Edison.csv
    │   ├── resultados_youBot_Edison.csv
    │   ├── resultados_UR10_Edison.csv
    │   └── resultados_sensor_Edison.csv
    └── Nuvem/
        ├── resultados_FrankaNuvem.csv
        ├── resultados_youBotNuvem.csv
        ├── resultados_UR10Nuvem.csv
        └── resultados_sensorNuvem.csv

    com edge ai/
    ├── cnn_autoral/{local,edison,aws}/   resultados_*.csv + metricas_esp.csv
    ├── v2/metricas_esp.csv
    └── v3/metricas_esp.csv

Saídas (em apendices_pdf/):
    apendice_A_sem_edge_ai.pdf
    apendice_B_com_edge_ai.pdf
    apendice_C_inferencia_esp32.pdf

Uso:
    cd "resultados/calcular"
    pip install -r requirements.txt
    python gerar_apendices.py
"""

import os
import glob
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

base = os.path.abspath(os.path.dirname(__file__))
OUT_DIR = os.path.join(base, 'apendices_pdf')
os.makedirs(OUT_DIR, exist_ok=True)

SEM_EDGE = os.path.join(base, 'sem edge ai')
COM_EDGE = os.path.join(base, 'com edge ai')


# =============================================================================
# UTILITÁRIOS
# =============================================================================

def parse_float(val):
    if isinstance(val, str):
        return float(val.replace(',', '.'))
    return float(val)


def fmt(val, decimals=2):
    try:
        return f"{float(val):.{decimals}f}".replace('.', ',')
    except Exception:
        return str(val)


def get_col(df, candidates):
    for c in candidates:
        if c in df.columns:
            return c
    return None


def create_pdf_table(df, filepath, is_landscape=False):
    """Salva um DataFrame como tabela PDF via matplotlib."""
    if df.empty:
        print(f"  ⚠ DataFrame vazio — pulando {os.path.basename(filepath)}")
        return

    max_nl = max(
        (df[c].astype(str).str.count('\n').max() for c in df.columns
         if df[c].dtype == object),
        default=0
    )
    fig_h = max_nl * 0.4 + len(df) * 0.5 + 2
    fig_w = 14 if is_landscape else 11

    fig, ax = plt.subplots(figsize=(fig_w, fig_h))
    ax.axis('off')

    # Wrap tópico se necessário
    disp = df.copy()
    if 'Tópico' in disp.columns:
        import textwrap
        disp['Tópico'] = disp['Tópico'].apply(
            lambda x: '\n'.join(textwrap.wrap(str(x), 28)))

    table = ax.table(cellText=disp.values, colLabels=disp.columns,
                     cellLoc='center', loc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 1.8)

    for (row, col), cell in table.get_celld().items():
        cell.set_edgecolor('black')
        if row == 0:
            cell.set_text_props(weight='bold')
            cell.set_facecolor('#f0f0f0')
            cell.set_linewidth(1.5)
        else:
            cell.set_linewidth(0.5)

    plt.text(0.5, -0.03, "Fonte: elaborada pelo autor (2026).",
             ha='center', va='top', transform=ax.transAxes, fontsize=9)
    plt.tight_layout()
    plt.savefig(filepath, format='pdf', bbox_inches='tight', dpi=300)
    plt.close()
    print(f"  ✓ Gerado: {os.path.basename(filepath)}")


# =============================================================================
# APÊNDICE A — Sem Edge AI
# =============================================================================
print("\n=== Gerando Apêndice A (Sem Edge AI) ===")

# Mapeamento: (nome_exibição, arquivo_Local, arquivo_Edison, arquivo_Nuvem)
TOPICOS_SEM = [
    ('/bloco/disponivel',
     'resultados_sensor.csv', 'resultados_sensor_Edison.csv', 'resultados_sensorNuvem.csv'),
    ('/entregador/coletaDisponivel',
     'resultados_Franka.csv', 'resultados_Franka_Edison.csv', 'resultados_FrankaNuvem.csv'),
    ('/entregador/pontoRecebimento',
     'resultados_youBot.csv', 'resultados_youBot_Edison.csv', 'resultados_youBotNuvem.csv'),
    ('/entregador/encomendaColetada',
     'resultados_youBot.csv', 'resultados_youBot_Edison.csv', 'resultados_youBotNuvem.csv'),
    ('/entregador/encomendaDisponibilizada',
     'resultados_youBot.csv', 'resultados_youBot_Edison.csv', 'resultados_youBotNuvem.csv'),
    ('/colaboracao/fim',
     'resultados_UR10.csv', 'resultados_UR10_Edison.csv', 'resultados_UR10Nuvem.csv'),
]

envs_sem = {
    'Local':  ('Local',  0),
    'Edison': ('Edison', 1),
    'AWS':    ('Nuvem',  2),
}

rows_a = []
for topico, f_local, f_edison, f_nuvem in TOPICOS_SEM:
    for env_label, (pasta, _) in envs_sem.items():
        fname = {'Local': f_local, 'Edison': f_edison, 'AWS': f_nuvem}[env_label]
        fpath = os.path.join(SEM_EDGE, pasta, fname)
        if not os.path.exists(fpath):
            continue
        try:
            df = pd.read_csv(fpath)
            tc = get_col(df, ['Topico', 'Tópico'])
            lc = get_col(df, ['Latencia_ms'])
            if tc is None or lc is None:
                continue
            sub = df[df[tc] == topico][lc].apply(parse_float)
            if sub.empty:
                continue
            rows_a.append([env_label, topico,
                           fmt(sub.median()), fmt(sub.std()), len(sub)])
        except Exception as e:
            print(f"  ⚠ {fpath}: {e}")

df_a = pd.DataFrame(rows_a, columns=['Ambiente', 'Tópico',
                                      'Lat. Mediana (ms)', 'Jitter (ms)', 'Amostras'])
create_pdf_table(df_a, os.path.join(OUT_DIR, 'apendice_A_sem_edge_ai.pdf'),
                 is_landscape=True)


# =============================================================================
# APÊNDICE B — Com Edge AI (CNN Autoral)
# =============================================================================
print("\n=== Gerando Apêndice B (Com Edge AI — CNN Autoral) ===")

envs_com = {
    'Local':  os.path.join(COM_EDGE, 'cnn_autoral', 'local'),
    'Edison': os.path.join(COM_EDGE, 'cnn_autoral', 'edison'),
    'AWS':    os.path.join(COM_EDGE, 'cnn_autoral', 'aws'),
}

rows_b = []

for env_label, pasta in envs_com.items():
    if not os.path.isdir(pasta):
        print(f"  ⚠ Pasta não encontrada: {pasta}")
        continue

    # Calcular offset de relógio para corrigir /esp/resultado
    metricas_path = os.path.join(pasta, 'metricas_esp.csv')
    offset_ms = 0.0
    if os.path.exists(metricas_path):
        df_esp = pd.read_csv(metricas_path)
        offset_ms = float(np.median(df_esp['timestamp_envio'] - df_esp['timestamp_recebido'])) * 1000.0

    # Tópicos dos agentes
    for csv_file in glob.glob(os.path.join(pasta, 'resultados_*.csv')):
        try:
            df = pd.read_csv(csv_file)
            tc = get_col(df, ['Topico', 'Tópico'])
            lc = get_col(df, ['Latencia_ms'])
            if tc is None or lc is None:
                continue
            for topico, sub_df in df.groupby(tc):
                lats = sub_df[lc].apply(parse_float)
                # Corrige /esp/resultado
                if topico == '/esp/resultado' and offset_ms != 0:
                    lats = lats - offset_ms
                lats = lats[lats.abs() < 10_000]   # remove outliers
                if lats.empty:
                    continue
                rows_b.append([env_label, topico,
                               fmt(lats.median()), fmt(lats.std()), len(lats)])
        except Exception as e:
            print(f"  ⚠ {csv_file}: {e}")

    # /esp/classificar via metricas_esp.csv
    if os.path.exists(metricas_path):
        df_esp = pd.read_csv(metricas_path)
        lats_class = (df_esp['timestamp_logger'] - df_esp['timestamp_envio']) * 1000.0
        lats_class = lats_class[lats_class.abs() < 10_000]
        if not lats_class.empty:
            rows_b.append([env_label, '/esp/classificar',
                           fmt(lats_class.median()), fmt(lats_class.std()),
                           len(lats_class)])

df_b = pd.DataFrame(rows_b, columns=['Ambiente', 'Tópico',
                                      'Lat. Mediana (ms)', 'Jitter (ms)', 'Amostras'])
df_b['_ord'] = pd.Categorical(df_b['Ambiente'],
                               categories=['Local', 'Edison', 'AWS'], ordered=True)
df_b = df_b.sort_values(['Tópico', '_ord']).drop('_ord', axis=1).reset_index(drop=True)
create_pdf_table(df_b, os.path.join(OUT_DIR, 'apendice_B_com_edge_ai.pdf'),
                 is_landscape=True)


# =============================================================================
# APÊNDICE C — Tempo de Inferência por Modelo no ESP32
# =============================================================================
print("\n=== Gerando Apêndice C (Inferência ESP32 por Modelo) ===")

modelos_c = [
    ('CNN Autoral',    os.path.join(COM_EDGE, 'cnn_autoral', 'local', 'metricas_esp.csv')),
    ('MobileNet V2',   os.path.join(COM_EDGE, 'v2', 'metricas_esp.csv')),
    ('MobileNet V3',   os.path.join(COM_EDGE, 'v3', 'metricas_esp.csv')),
]

rows_c = []
for nome, fpath in modelos_c:
    if not os.path.exists(fpath):
        print(f"  ⚠ Não encontrado: {fpath}")
        continue
    df = pd.read_csv(fpath)
    col = 'tempo_inferencia_ms'
    if col not in df.columns:
        print(f"  ⚠ Coluna '{col}' ausente em {fpath}")
        continue
    infs = df[col].dropna().apply(parse_float)
    rows_c.append([nome, fmt(infs.median()), fmt(infs.std()), len(infs)])

df_c = pd.DataFrame(rows_c, columns=['Arquitetura', 'Tempo Mediano (ms)',
                                      'Desvio Padrão (ms)', 'Amostras'])
create_pdf_table(df_c, os.path.join(OUT_DIR, 'apendice_C_inferencia_esp32.pdf'))

print("\n✅ Todos os apêndices foram gerados em:", OUT_DIR, "\n")
