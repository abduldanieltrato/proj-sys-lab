# lab/utils/pdf_generator.py
import os
import io
from datetime import datetime
from django.conf import settings
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont

# =====================================================================
# CONFIGURAÇÕES
# =====================================================================
LOGO_PATH = os.path.join(settings.BASE_DIR, "lab/static/img/logo.png")
WATERMARK_PATH = os.path.join(settings.BASE_DIR, "lab/static/img/watermark.png")

pdfmetrics.registerFont(UnicodeCIDFont("HeiseiKakuGo-W5"))  # Suporte UTF-8

# =====================================================================#
# FUNÇÕES DE LAYOUT FIXO											   #
# =====================================================================#
def draw_header(canvas_obj, width, height):
    """Cabeçalho institucional"""
    try:
        canvas_obj.drawImage(LOGO_PATH, 1.5*cm, height - 2*cm, width=3*cm, preserveAspectRatio=True, mask='auto')
    except Exception:
        pass
    canvas_obj.setFont("HeiseiKakuGo-W5", 14)
    canvas_obj.drawCentredString(width / 2, height - 1.5*cm, "Hospital Provincial de Pemba")
    canvas_obj.setFont("HeiseiKakuGo-W5", 11)
    canvas_obj.drawCentredString(width / 2, height - 3*cm, "Laboratório de Análises Clínicas")
    canvas_obj.setStrokeColor(colors.black)
    canvas_obj.line(1.5*cm, height - 3.2*cm, width - 1.5*cm, height - 3.2*cm)

def draw_footer(canvas_obj, width, height):
    """Rodapé"""
    canvas_obj.setFont("HeiseiKakuGo-W5", 8)
    rodape = f"Gerado automaticamente por SYS-LAB em {datetime.now().strftime('%d/%m/%Y %H:%M')}"
    canvas_obj.drawRightString(width - 1*cm, 1*cm, rodape)

def draw_watermark(canvas_obj, width, height):
    """Marca d'água centralizada"""
    try:
        canvas_obj.saveState()
        canvas_obj.translate(width / 2, height / 2)
        canvas_obj.rotate(30)
        canvas_obj.setFillAlpha(0.08)
        canvas_obj.drawImage(WATERMARK_PATH, -8*cm, -8*cm, width=16*cm, height=16*cm, preserveAspectRatio=True, mask='auto')
        canvas_obj.restoreState()
    except Exception:
        pass

# =====================================================================
# FUNÇÕES PRINCIPAIS
# =====================================================================
def gerar_pdf_requisicao(requisicao):
    """Gera PDF da requisição de análises"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=1.5*cm, rightMargin=1.5*cm, topMargin=4.5*cm, bottomMargin=1.5*cm)

    story = []
    styles = getSampleStyleSheet()
    style_normal = styles["Normal"]
    style_title = styles["Heading1"]

    # Título
    story.append(Paragraph("REQUISIÇÃO DE ANÁLISES CLÍNICAS", style_title))
    story.append(Spacer(1, 0.5*cm))

    # Dados do paciente
    paciente = requisicao.paciente
    dados = [
        ["Nome do Paciente:", str(paciente)],
        ["Idade:", f"{paciente.idade or '—'} anos"],
        ["Sexo:", paciente.genero or "—"],
        ["Número de Identificação:", paciente.numero_id],
        ["Proveniência:", paciente.proveniencia or 'N/D']
    ]
    tabela_dados = Table(dados, colWidths=[5*cm, 10*cm])
    tabela_dados.setStyle(TableStyle([
        ("BOX", (0,0), (-1,-1), 0.5, colors.grey),
        ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
        ("BACKGROUND", (0,0), (-1,0), colors.lightgrey)
    ]))
    story.append(tabela_dados)
    story.append(Spacer(1, 0.7*cm))

    # Exames
    story.append(Paragraph("<b>Exames Solicitados:</b>", style_normal))
    exames = [[exame.nome] for exame in requisicao.exames_list]
    if not exames:
        exames = [["Nenhum exame registrado."]]
    tabela_exames = Table(exames, colWidths=[15*cm])
    tabela_exames.setStyle(TableStyle([
        ("BOX", (0,0), (-1,-1), 0.5, colors.grey),
        ("GRID", (0,0), (-1,-1), 0.25, colors.grey)
    ]))
    story.append(tabela_exames)

    def layout(canvas_obj, doc_obj):
        width, height = A4
        draw_watermark(canvas_obj, width, height)
        draw_header(canvas_obj, width, height)
        draw_footer(canvas_obj, width, height)

    doc.build(story, onFirstPage=layout, onLaterPages=layout)
    pdf = buffer.getvalue()
    buffer.close()
    return pdf

def gerar_pdf_resultados(requisicao):
    """Gera PDF com resultados laboratoriais"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=3*cm, rightMargin=2*cm, topMargin=4.5*cm, bottomMargin=2*cm)

    styles = getSampleStyleSheet()
    style_normal = styles["Normal"]
    style_title = styles["Heading1"]

    story = []
    story.append(Paragraph("RESULTADOS DE ANÁLISES CLÍNICAS", style_title))
    story.append(Spacer(1, 0.5*cm))

    # Dados do paciente
    paciente = requisicao.paciente
    idade = f"{paciente.idade} anos" if paciente.idade else "—"
    genero = paciente.genero or "—"
    data_analise = getattr(requisicao, 'created_at', None)
    data_analise_str = data_analise.strftime("%d/%m/%Y") if data_analise else "—"

    dados_paciente = [
        ["Nome do Paciente:", paciente.nome],
        ["Idade:", idade],
        ["Sexo:", genero],
        ["Data de Análise:", data_analise_str]
    ]
    tabela_dados = Table(dados_paciente, colWidths=[5*cm, 10*cm])
    tabela_dados.setStyle(TableStyle([
        ("BOX", (0,0), (-1,-1), 0.5, colors.grey),
        ("GRID", (0,0), (-1,-1), 0.25, colors.grey),
        ("BACKGROUND", (0,0), (-1,0), colors.lightgrey)
    ]))
    story.append(tabela_dados)
    story.append(Spacer(1, 0.7*cm))

    # Resultados
    story.append(Paragraph("<b>Resultados Obtidos:</b>", style_normal))
    def safe(val):
        return val if val else "—"

    resultados_data = [["Exame", "Resultado", "Unidade", "Referência"]] + [
        [
            safe(res.exame.nome),
            safe(res.valor),
            safe(res.unidade),
            safe(res.valor_referencia)
        ] for res in requisicao.resultados.all()
    ]
    tabela_resultados = Table(resultados_data, colWidths=[3*cm, 8*cm, 2.5*cm, 2.5*cm])
    tabela_resultados.setStyle(TableStyle([
        ("BOX", (0,0), (-1,-1), 0.5, colors.grey),
        ("GRID", (0,0), (-1,-1), 0.25, colors.grey),
        ("BACKGROUND", (0,0), (-1,0), colors.lightgrey)
    ]))
    story.append(tabela_resultados)

    def layout(canvas_obj, doc_obj):
        width, height = A4
        draw_watermark(canvas_obj, width, height)
        draw_header(canvas_obj, width, height)
        draw_footer(canvas_obj, width, height)

    doc.build(story, onFirstPage=layout, onLaterPages=layout)
    pdf = buffer.getvalue()
    buffer.close()
    return pdf
