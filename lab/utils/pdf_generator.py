import os, io
from datetime import datetime
from django.conf import settings
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont

LOGO_PATH = os.path.join(settings.BASE_DIR, "lab/static/img/logo.png")
WATERMARK_PATH = os.path.join(settings.BASE_DIR, "lab/static/img/watermark.png")
pdfmetrics.registerFont(UnicodeCIDFont("HeiseiKakuGo-W5"))

# ------------------ Layout ------------------ #
def draw_header(c, width, height):
    try: c.drawImage(LOGO_PATH, 1.5*cm, height-3*cm, width=2.5*cm, preserveAspectRatio=True, mask='auto')
    except: pass
    c.setFont("HeiseiKakuGo-W5", 14)
    c.drawCentredString(width/2, height-2*cm, "Hospital Provincial de Pemba")
    c.setFont("HeiseiKakuGo-W5", 11)
    c.drawCentredString(width/2, height-2.7*cm, "Laboratório de Análises Clínicas")
    c.setStrokeColor(colors.black)
    c.line(1.5*cm, height-3.2*cm, width-1.5*cm, height-3.2*cm)

def draw_footer(c, width, height):
    c.setFont("HeiseiKakuGo-W5", 8)
    c.drawRightString(width-1.5*cm, 1.5*cm, f"Gerado automaticamente por SYS-LAB em {datetime.now().strftime('%d/%m/%Y %H:%M')}")

def draw_watermark(c, width, height):
    try:
        c.saveState()
        c.translate(width/2, height/2)
        c.rotate(30)
        c.setFillAlpha(0.08)
        c.drawImage(WATERMARK_PATH, -8*cm, -8*cm, width=16*cm, height=16*cm, preserveAspectRatio=True, mask='auto')
        c.restoreState()
    except: pass

# ------------------ PDF Requisição ------------------ #
def gerar_pdf_requisicao(requisicao):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=3*cm, rightMargin=2*cm, topMargin=4.5*cm, bottomMargin=2*cm)
    story, styles = [], getSampleStyleSheet()
    story.append(Paragraph("REQUISIÇÃO DE ANÁLISES CLÍNICAS", styles["Heading1"]))
    story.append(Spacer(1, 0.5*cm))
    paciente = requisicao.paciente
    dados = [
        ["Nome do Paciente:", str(paciente)],
        ["Idade:", f"{paciente.idade or '—'} anos"],
        ["Sexo:", paciente.genero or "—"],
        ["Número de ID:", paciente.numero_id],
        ["Proveniência:", paciente.proveniencia or 'N/D']
    ]
    tabela = Table(dados, colWidths=[5*cm, 10*cm])
    tabela.setStyle(TableStyle([
        ("BOX",(0,0),(-1,-1),0.5,colors.grey),
        ("GRID",(0,0),(-1,-1),0.5,colors.grey),
        ("BACKGROUND",(0,0),(-1,0),colors.lightgrey)
    ]))
    story.append(tabela)
    story.append(Spacer(1,0.7*cm))
    exames = [[e.nome] for e in requisicao.exames_list] or [["Nenhum exame registrado."]]
    tabela_exames = Table(exames, colWidths=[15*cm])
    tabela_exames.setStyle(TableStyle([("BOX",(0,0),(-1,-1),0.5,colors.grey),("GRID",(0,0),(-1,-1),0.25,colors.grey)]))
    story.append(tabela_exames)

    def layout(c, doc_obj):
        w,h = A4
        draw_watermark(c,w,h)
        draw_header(c,w,h)
        draw_footer(c,w,h)

    doc.build(story, onFirstPage=layout, onLaterPages=layout)
    pdf = buffer.getvalue()
    buffer.close()
    return pdf

# ------------------ PDF Resultados ------------------ #
def gerar_pdf_resultados(requisicao):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=3*cm, rightMargin=2*cm, topMargin=4.5*cm, bottomMargin=2*cm)
    story, styles = [], getSampleStyleSheet()
    story.append(Paragraph("RESULTADOS DE ANÁLISES CLÍNICAS", styles["Heading1"]))
    story.append(Spacer(1,0.5*cm))
    paciente = requisicao.paciente
    idade = f"{paciente.idade} anos" if paciente.idade else "—"
    genero = paciente.genero or "—"
    data_analise = getattr(requisicao, 'created_at', None)
    data_str = data_analise.strftime("%d/%m/%Y") if data_analise else "—"
    dados_paciente = [
        ["Nome do Paciente:", paciente.nome],
        ["Idade:", idade],
        ["Sexo:", genero],
        ["Data de Análise:", data_str]
    ]
    tabela_dados = Table(dados_paciente, colWidths=[5*cm,10*cm])
    tabela_dados.setStyle(TableStyle([
        ("BOX",(0,0),(-1,-1),0.5,colors.grey),
        ("GRID",(0,0),(-1,-1),0.25,colors.grey),
        ("BACKGROUND",(0,0),(-1,0),colors.lightgrey)
    ]))
    story.append(tabela_dados)
    story.append(Spacer(1,0.7*cm))

    resultados_data = [["Exame","Resultado","Unidade","Referência"]]
    for r in requisicao.resultados.all():
        resultados_data.append([
            r.exame.nome,
            r.valor or "—",
            r.unidade or r.exame.unidade or "—",
            r.valor_referencia or r.exame.valor_ref or "—"
        ])
    tabela_resultados = Table(resultados_data, colWidths=[6*cm,3*cm,3*cm,3*cm])
    tabela_resultados.setStyle(TableStyle([
        ("BOX",(0,0),(-1,-1),0.5,colors.grey),
        ("GRID",(0,0),(-1,-1),0.25,colors.grey),
        ("BACKGROUND",(0,0),(-1,0),colors.lightgrey)
    ]))
    story.append(tabela_resultados)

    def layout(c, doc_obj):
        w,h = A4
        draw_watermark(c,w,h)
        draw_header(c,w,h)
        draw_footer(c,w,h)

    doc.build(story, onFirstPage=layout, onLaterPages=layout)
    pdf = buffer.getvalue()
    buffer.close()
    return pdf
