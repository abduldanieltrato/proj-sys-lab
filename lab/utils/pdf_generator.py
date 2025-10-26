# lab/utils/pdf_generator.py
"""
Gerador de PDFs institucionais (requisição e resultados).
- Cabeçalho com logotipo (Times New Roman).
- Marca d'água repetida horizontalmente (rotacionada 90°).
- Tabelas com suporte a textos longos (Paragraph).
- Assinaturas e docstrings explicativas.
"""

import os
import io
from datetime import datetime
from django.conf import settings
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader
from PIL import Image

# --------------------------
# CONFIGURAÇÕES
# --------------------------
LOGO_PATH = os.path.join(settings.BASE_DIR, "lab/static/img/logo_fix.png")
WATERMARK_PATH = os.path.join(settings.BASE_DIR, "lab/static/img/watermark.png")

# Registre a fonte Times (ajuste o caminho conforme seu sistema)
# Se essas fontes não existirem no sistema, comente ou aponte para um .ttf válido.
try:
    pdfmetrics.registerFont(TTFont("Times-Roman", "/usr/share/fonts/truetype/msttcorefonts/Times_New_Roman.ttf"))
    pdfmetrics.registerFont(TTFont("Times-Bold", "/usr/share/fonts/truetype/msttcorefonts/Times_New_Roman_Bold.ttf"))
except Exception:
    # fallback: ReportLab já inclui "Times-Roman" sem registro em alguns ambientes
    pass

# Debug path (opcional)
print("LOGO_PATH:", LOGO_PATH, os.path.exists(LOGO_PATH))
print("WATERMARK_PATH:", WATERMARK_PATH, os.path.exists(WATERMARK_PATH))


# --------------------------
# LAYOUT: HEADER / FOOTER / WATERMARK
# --------------------------

def draw_header(canvas, doc):
    """
    Desenha o cabeçalho institucional com logotipo e textos.
    Recebe (canvas, doc) — compatível com ReportLab onPage callbacks.
    """
    canvas.saveState()
    canvas.setFont("Times-Bold", 12)

    # Desenha logo (usa Pillow para compatibilidade)
    if os.path.exists(LOGO_PATH):
        try:
            with Image.open(LOGO_PATH) as img:
                if img.mode == "RGBA":
                    img = img.convert("RGB")
                buf = io.BytesIO()
                img.save(buf, format="PNG")
                buf.seek(0)
                # posição e tamanho (ajuste se desejar)
                logo_x = 35
                logo_y = A4[1] - 135  # A4[1] é a altura em pontos
                canvas.drawImage(ImageReader(buf), logo_x, logo_y, width=100, height=100, preserveAspectRatio=True, mask='auto')
        except Exception as e:
            print("Erro ao carregar logo:", e)

    # Texto institucional (Times)
    canvas.setFont("Times-Bold", 14)
    canvas.drawString(140, A4[1] - 60, "HOSPITAL PROVINCIAL DE PEMBA")
    canvas.setFont("Times-Roman", 11)
    canvas.drawString(140, A4[1] - 78, "Laboratório de Análises Clínicas")
    canvas.setFont("Times-Roman", 9)
    canvas.drawString(140, A4[1] - 95, "Bairro Cimento, Cidade de Pemba - Cabo Delgado")
    canvas.drawString(140, A4[1] - 110, "Tel: +258 84 773 5374 | +258 86 128 4041 | info@lab-pemba-mz.com")

    # Linha de separação
    canvas.setStrokeColor(colors.black)
    canvas.setLineWidth(10)
    canvas.line(0.0*cm, A4[1] - 135, A4[1] - 4*cm, A4[1] - 135)

    canvas.restoreState()


def draw_footer(canvas, doc):
    """
    Desenha o rodapé com data/hora. Recebe (canvas, doc).
    """
    canvas.saveState()
    canvas.setFont("Times-Roman", 8)
    footer_text = f"Gerado automaticamente por SYS-LAB em {datetime.now().strftime('%d/%m/%Y %H:%M')}"
    canvas.drawRightString(A4[0] - 2*cm, 1.5*cm, footer_text)
    canvas.restoreState()


def draw_watermark(canvas, doc):
    """
    Marca d'água preenchendo toda a página, repetida horizontal e verticalmente.
    Rotacionada 90° para ficar vertical.
    """
    try:
        canvas.saveState()
        try:
            canvas.setFillAlpha(0.1)
        except Exception:
            pass  # fallback para versões antigas

        width, height = doc.pagesize

        if not os.path.exists(WATERMARK_PATH):
            canvas.restoreState()
            return

        with Image.open(WATERMARK_PATH) as img:
            if img.mode == "RGBA":
                img = img.convert("RGB")
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            buf.seek(0)
            watermark = ImageReader(buf)

        # dimensões da marca (ajustar se quiser maior/menor)
        wm_width = 4*cm
        wm_height = 8*cm
        spacing_x = -1.0*cm
        spacing_y = -3.99999999*cm

        # loop vertical
        y = -wm_height
        while y < height + wm_height:
            x = -wm_width
            while x < width + wm_width:
                canvas.saveState()
                cx = x + wm_width/2
                cy = y + wm_height/2
                canvas.translate(cx, cy)
                canvas.rotate(90)
                canvas.drawImage(
                    watermark,
                    -wm_width/2, -wm_height/2,
                    width=wm_width,
                    height=wm_height,
                    preserveAspectRatio=True,
                    mask='auto'
                )
                canvas.restoreState()
                x += wm_width + spacing_x
            y += wm_height + spacing_y

        canvas.restoreState()
    except Exception as e:
        print("Erro ao desenhar watermark:", e)



# --------------------------
# LAYOUT UNIFICADO (callback)
# --------------------------
def layout(canvas, doc):
    """
    Função passada para onFirstPage / onLaterPages.
    Garante execução na ordem correta: watermark -> header -> footer.
    """
    draw_watermark(canvas, doc)     # Marca D'agua
    draw_header(canvas, doc)        # Cabecalho
    draw_footer(canvas, doc)        # Rodape
    draw_signatures(canvas, doc)    # assinaturas


# --------------------------
# GERADOR: REQUISIÇÃO
# --------------------------
def gerar_pdf_requisicao(requisicao):
    """
    Gera PDF da requisição de análises.
    Retorna bytes do PDF.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        leftMargin=3*cm, rightMargin=2*cm,
        topMargin=5*cm, bottomMargin=2*cm
    )

    story = []
    styles = getSampleStyleSheet()
    # assegura fonte Times nos headings
    try:
        styles["Heading1"].fontName = "Times-Bold"
    except Exception:
        pass

    story.append(Paragraph("REQUISIÇÃO DE ANÁLISES CLÍNICAS", styles["Heading1"]))
    story.append(Spacer(1, 1.5*cm))

    paciente = requisicao.paciente
    dados = [
        ["Nome do Paciente:", str(paciente)],
        ["Idade:", f"{paciente.idade or '—'} anos"],
        ["Sexo:", paciente.genero or "—"],
        ["Número de ID:", paciente.numero_id or "—"],
        ["Proveniência:", paciente.proveniencia or 'N/D']
    ]

    tabela = Table(dados, colWidths=[5*cm, 10*cm])
    tabela.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), "Times-Roman"),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.grey),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey)
    ]))
    story.append(tabela)
    story.append(Spacer(1, 0.7*cm))

    exames = [[e.nome] for e in getattr(requisicao, "exames_list", requisicao.exames.all())] or [["Nenhum exame registrado."]]
    tabela_exames = Table(exames, colWidths=[15*cm])
    tabela_exames.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), "Times-Roman"),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.grey),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.grey)
    ]))
    story.append(tabela_exames)

    doc.build(story, onFirstPage=layout, onLaterPages=layout)
    pdf = buffer.getvalue()
    buffer.close()
    return pdf


# --------------------------
# GERADOR: RESULTADOS
# --------------------------
def gerar_pdf_resultados(requisicao):
    """
    Gera PDF com resultados de análises (usa Paragraph nas células para wrap).
    Retorna bytes do PDF.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        leftMargin=3*cm, rightMargin=2*cm,
        topMargin=5.0*cm, bottomMargin=2*cm
    )

    story = []
    styles = getSampleStyleSheet()
    try:
        styles["Heading1"].fontName = "Times-Bold"
    except Exception:
        pass

    story.append(Paragraph("RESULTADOS DE ANÁLISES CLÍNICAS", styles["Heading1"]))
    story.append(Spacer(1, 0.5*cm))

    paciente = requisicao.paciente
    idade = f"{paciente.idade} anos" if getattr(paciente, "idade", None) else "—"
    genero = paciente.genero or "—"
    data_analise = getattr(requisicao, "created_at", None)
    data_str = data_analise.strftime("%d/%m/%Y") if data_analise else "—"

    dados_paciente = [
        ["Nome do Paciente:", paciente.nome],
        ["Idade:", idade],
        ["Sexo:", genero],
        ["Data de Análise:", data_str]
    ]
    tabela_dados = Table(dados_paciente, colWidths=[5*cm, 10*cm])
    tabela_dados.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), "Times-Roman"),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.grey),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey)
    ]))
    story.append(tabela_dados)
    story.append(Spacer(1, 0.7*cm))

    # tabela de resultados com quebra automática de texto
    resultados_data = [["Exame", "Resultado", "Unidade", "Referência"]]
    text_style = ParagraphStyle("TextWrap", fontName="Times-Roman", fontSize=10, leading=13)

    for r in requisicao.resultados.all():
        resultados_data.append([
            Paragraph(getattr(r.exame, "nome", "—"), text_style),
            Paragraph(r.valor or "—", text_style),
            Paragraph(r.unidade or getattr(r.exame, "unidade", "—"), text_style),
            Paragraph(r.valor_referencia or getattr(r.exame, "valor_ref", "—"), text_style)
        ])

    tabela_resultados = Table(resultados_data, colWidths=[6*cm, 3*cm, 3*cm, 3*cm])
    tabela_resultados.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), "Times-Roman"),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.grey),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey)
    ]))
    story.append(tabela_resultados)

    doc.build(story, onFirstPage=layout, onLaterPages=layout)
    pdf = buffer.getvalue()
    buffer.close()
    return pdf

def draw_signatures(canvas, doc):
    """
    Desenha duas linhas de assinatura no final da página
    lado a lado: Técnico de Laboratório e Chefe do Laboratório
    """
    canvas.saveState()

    # Posição vertical do início das linhas (1.5cm acima da margem inferior)
    y = 3*cm
    width_total = A4[0] - 3*cm - 2*cm  # largura disponível (margens)
    width_line = (width_total - 2*cm) / 2  # espaço entre as linhas

    # Coordenadas das linhas
    x1_start = 3*cm
    x1_end = x1_start + width_line
    x2_start = x1_end + 2*cm
    x2_end = x2_start + width_line

    # Linhas de assinatura
    canvas.setLineWidth(1)
    canvas.line(x1_start, y, x1_end, y)  # Técnico
    canvas.line(x2_start, y, x2_end, y)  # Chefe

    # Textos abaixo das linhas
    canvas.setFont("Times-Roman", 10)
    canvas.drawCentredString((x1_start + x1_end)/2, y - 12, "Técnico de Laboratório")
    canvas.drawCentredString((x2_start + x2_end)/2, y - 12, "Chefe do Laboratório \n Anibal Albino")

    canvas.restoreState()

