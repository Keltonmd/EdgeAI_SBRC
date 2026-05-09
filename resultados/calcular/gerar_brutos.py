"""
gerar_brutos.py — Gera os Apêndices D e E com dados brutos linha a linha em PDF
=================================================================================
Apêndice D: cada medição individual de latência do cenário Sem Edge AI.
Apêndice E: cada medição individual de latência do cenário Com Edge AI (CNN Autoral).

Uso:
    cd "resultados/calcular"
    pip install -r requirements.txt
    python gerar_brutos.py
"""

import csv
import os
import glob
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

base = os.path.abspath(os.path.dirname(__file__))
OUT_DIR = os.path.join(base, 'apendices_pdf')
os.makedirs(OUT_DIR, exist_ok=True)


def fmt(v, decimals=2):
    try:
        return f"{float(v):.{decimals}f}".replace('.', ',')
    except Exception:
        return str(v)


def draw_table_pdf(pdf_path, col_labels, col_widths, rows,
                   col_aligns=None, fontsize=8, rows_per_page=45):
    """Escreve uma tabela paginada em PDF via matplotlib."""
    fig_w = sum(col_widths) + 0.5
    row_h = 0.22
    header_h = 0.4
    margin_h = 0.8
    if col_aligns is None:
        col_aligns = ['center'] * len(col_labels)

    chunks = [rows[i:i + rows_per_page]
              for i in range(0, max(len(rows), 1), rows_per_page)]

    with PdfPages(pdf_path) as pdf:
        for chunk in chunks:
            n_rows = len(chunk)
            fig_h = max(header_h + n_rows * row_h + margin_h, 3.0)
            fig, ax = plt.subplots(figsize=(fig_w, fig_h))
            ax.axis('off')

            table = ax.table(
                cellText=[list(r) for r in chunk],
                colLabels=col_labels,
                colWidths=[w / fig_w for w in col_widths],
                loc='center', cellLoc='center'
            )
            table.auto_set_font_size(False)
            table.set_fontsize(fontsize)
            table.scale(1, 1.4)

            for j in range(len(col_labels)):
                cell = table[0, j]
                cell.set_facecolor('#1F3864')
                cell.set_text_props(color='white', fontweight='bold')

            for i, row_data in enumerate(chunk):
                fc = '#E8EDF5' if i % 2 == 0 else 'white'
                for j in range(len(row_data)):
                    cell = table[i + 1, j]
                    cell.set_facecolor(fc)
                    cell.set_text_props(ha=col_aligns[j])

            plt.tight_layout(rect=[0, 0.02, 1, 1.0])
            pdf.savefig(fig, bbox_inches='tight')
            plt.close(fig)

    print(f"  ✓ {os.path.basename(pdf_path)} ({len(rows)} linhas)")


def process_raw_data(data_dir: str, pdf_name: str):
    """Lê todos os resultados_*.csv recursivamente em data_dir e gera um PDF."""
    files = glob.glob(os.path.join(data_dir, '**', '*.csv'), recursive=True)
    rows = []

    for fpath in sorted(files):
        basename = os.path.basename(fpath)
        # Ignora arquivos que não são de agentes
        if any(skip in basename for skip in ('metricas', 'processamento',
                                              'resumo', 'metricas_topicos')):
            continue
        if 'resultados_' not in basename:
            continue

        # Infere ambiente pela pasta
        parts = fpath.replace('\\', '/').split('/')
        if any(p in ('Local', 'local') for p in parts):
            env = 'Local'
        elif any(p in ('Edison', 'edison') for p in parts):
            env = 'Edison'
        elif any(p in ('Nuvem', 'aws', 'AWS') for p in parts):
            env = 'Nuvem/AWS'
        else:
            env = 'Outro'

        try:
            with open(fpath, newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for r in reader:
                    if 'Latencia_ms' not in r or 'Topico' not in r:
                        continue
                    try:
                        lat_val = float(r['Latencia_ms'])
                        if abs(lat_val) > 10_000:   # outlier
                            continue
                    except (ValueError, TypeError):
                        continue
                    rows.append({
                        'Ambiente': env,
                        'Topico': r['Topico'],
                        'Pub': r.get('Robo_Publicador', ''),
                        'Sub': r.get('Robo_Assinante', ''),
                        'Latencia': lat_val
                    })
        except Exception as e:
            print(f"  ⚠ {fpath}: {e}")

    order = {'Local': 0, 'Edison': 1, 'Nuvem/AWS': 2, 'Outro': 3}
    rows.sort(key=lambda r: (order.get(r['Ambiente'], 9), r['Topico']))

    table_rows = [[r['Ambiente'], r['Topico'], r['Pub'], r['Sub'],
                   fmt(r['Latencia'])] for r in rows]

    draw_table_pdf(
        pdf_path=os.path.join(OUT_DIR, pdf_name),
        col_labels=['Ambiente', 'Tópico', 'Pub.', 'Sub.', 'Lat. (ms)'],
        col_widths=[1.2, 3.5, 1.2, 1.2, 1.2],
        col_aligns=['center', 'left', 'center', 'center', 'center'],
        rows=table_rows
    )


if __name__ == '__main__':
    print('\n=== Gerando Apêndice D (dados brutos — Sem Edge AI) ===')
    process_raw_data(os.path.join(base, 'sem edge ai'),
                     'apendice_D_brutos_sem_edge.pdf')

    print('\n=== Gerando Apêndice E (dados brutos — Com Edge AI / CNN Autoral) ===')
    process_raw_data(os.path.join(base, 'com edge ai', 'cnn_autoral'),
                     'apendice_E_brutos_com_edge.pdf')

    print(f'\n✅ PDFs brutos gerados em: {OUT_DIR}\n')
