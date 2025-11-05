"""
Módulo de geração de PDFs institucionais para SYS-LAB
Autor: Trato
Versão: 3.0 (controle absoluto de posição de tabelas, linhas horizontais apenas)
"""

import os
import io
import logging
from datetime import datetime
from django.conf import settings
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader
from PIL import Image
from lab.models import Paciente

logger = logging.getLogger(__name__)

# ==================== PATHS ====================
LOGO_PATH = os.path.join(settings.BASE_DIR, "lab", "static", "img", "logo.png")
WATERMARK_PATH = LOGO_PATH

# ==================== FONTES ====================
try:
    pdfmetrics.registerFont(TTFont("Roboto", "/usr/share/fonts/truetype/roboto/Roboto-Regular.ttf"))
    pdfmetrics.registerFont(TTFont("Roboto-Bold", "/usr/share/fonts/truetype/roboto/Roboto-Bold.ttf"))
    FONT = "Roboto"
    FONT_BOLD = "Roboto-Bold"
except Exception as e:
    logger.warning("Falha ao registrar Roboto, usando Courier como fallback: %s", e)
    FONT = "Courier"
    FONT_BOLD = "Courier-Bold"

# ==================== CABEÇALHO ====================
def draw_header(canvas, doc):
    canvas.saveState()
    if os.path.exists(LOGO_PATH):
        try:
            with Image.open(LOGO_PATH) as img:
                if img.mode == "RGBA":
                    img = img.convert("RGB")
                buf = io.BytesIO()
                img.save(buf, format="PNG")
                buf.seek(0)
                canvas.drawImage(ImageReader(buf), 15, A4[1] - 130,
                                 width=150, height=190, preserveAspectRatio=True, mask='auto')
        except Exception as e:
            logger.warning("Erro ao carregar logo: %s", e)
    else:
        canvas.setFont(FONT, 10)
        canvas.drawString(35, A4[1] - 90, "LOGO INDISPONÍVEL")

    canvas.setFont(FONT_BOLD, 14)
    canvas.drawString(140, A4[1] - 60, "HOSPITAL PROVINCIAL DE PEMBA")
    canvas.setFont(FONT, 11)
    canvas.drawString(140, A4[1] - 78, "Laboratório de Análises Clínicas")
    canvas.setFont(FONT, 9)
    canvas.drawString(140, A4[1] - 95, "Bairro Cimento, Cidade de Pemba - Cabo Delgado")
    canvas.drawString(140, A4[1] - 110, "Tel: +258 84 773 5374 | +258 86 128 4041 | info@lab-pemba-mz.com")

    canvas.setStrokeColor(colors.black)
    canvas.setLineWidth(1)
    canvas.line(0 * cm, A4[1] - 120, A4[0] - 0 * cm, A4[1] - 120)
    canvas.restoreState()

# ==================== RODAPÉ ====================
def draw_footer(canvas, doc):
    canvas.saveState()
    canvas.setFont(FONT, 8)
    footer_text = f"Gerado automaticamente por analinklab em {datetime.now().strftime('%d/%m/%Y %H:%M')}"
    canvas.drawRightString(A4[0] - 1 * cm, 0.7 * cm, footer_text)
    canvas.restoreState()

# ==================== WATERMARK ====================
def draw_watermark(canvas, doc):
    try:
        if not os.path.exists(WATERMARK_PATH):
            return

        with Image.open(WATERMARK_PATH) as img:
            if img.mode == "RGBA":
                img = img.convert("RGB")
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            buf.seek(0)
            watermark = ImageReader(buf)

        canvas.saveState()
        try:
            canvas.setFillAlpha(0.08)
        except Exception:
            pass

        wm_width, wm_height = 6 * cm, 8 * cm
        spacing_x, spacing_y = 1 * cm, 2 * cm
        width, height = doc.pagesize

        y = -wm_height
        while y < height + wm_height:
            x = -wm_width
            while x < width + wm_width:
                canvas.saveState()
                canvas.translate(x + wm_width / 2, y + wm_height / 2)
                canvas.rotate(90)
                canvas.drawImage(watermark, -wm_width/2, -wm_height/2,
                                 width=wm_width, height=wm_height,
                                 preserveAspectRatio=True, mask='auto')
                canvas.restoreState()
                x += wm_width + spacing_x
            y += wm_height + spacing_y

        canvas.restoreState()
    except Exception as e:
        logger.warning("Erro ao desenhar watermark: %s", e)

# ==================== ASSINATURAS ====================
def draw_signatures(canvas, doc, usuario=None):
    canvas.saveState()
    y = 2 * cm
    width_total = A4[0] - 2 * cm
    width_line = (width_total - 4 * cm) / 2

    x1, x2 = 3 * cm, 3 * cm + width_line + 2 * cm + width_line

    canvas.setLineWidth(1)
    canvas.line(3 * cm, y, 3 * cm + width_line, y)
    canvas.line(3 * cm + width_line + 2 * cm, y, x2, y)

    tecnico_nome = "Técnico de Laboratório"
    if usuario:
        nomes = [usuario.first_name, usuario.last_name]
        tecnico_nome = " ".join(filter(None, nomes)).strip() or tecnico_nome

    canvas.setFont(FONT, 10)
    canvas.drawCentredString((3 * cm + 3 * cm + width_line) / 2, y - 12, tecnico_nome)
    canvas.drawCentredString((3 * cm + width_line + 2 * cm + x2) / 2, y - 12, "Responsável do Laboratório")
    canvas.restoreState()

# ==================== LAYOUT PADRÃO ====================
def layout(canvas, doc, usuario=None):
    draw_watermark(canvas, doc)
    draw_header(canvas, doc)
    draw_footer(canvas, doc)
    draw_signatures(canvas, doc, usuario)

# ==================== ESTILO DE TABELAS ====================
def estilo_tabela_sem_verticais():
    return TableStyle([
        ("FONTNAME", (0,0), (-1,-1), FONT),
        ("FONTSIZE", (0,0), (-1,-1), 9),
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("LINEABOVE", (0,0), (-1,0), 0.5, colors.black),
        ("LINEBELOW", (0,-1), (-1,-1), 0.5, colors.black),
        ("LINEBELOW", (0,0), (-1,-1), 0.25, colors.black),
        ("BACKGROUND", (0,0), (-1,0), colors.lightgrey)
    ])

# ==================== PDF DE REQUISIÇÃO ====================
def gerar_pdf_requisicao(requisicao, pos_x=1*cm, pos_y=None):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            leftMargin=3*cm, rightMargin=1*cm,
                            topMargin=4*cm, bottomMargin=1*cm)

    story = []

    # Título
    style = ParagraphStyle("Heading1", fontName=FONT_BOLD, fontSize=10)
    story.append(Spacer(1, 1*cm if not pos_y else pos_y))  # ajuste Y
    story.append(Paragraph("REQUISIÇÃO DE ANÁLISES CLÍNICAS", style))
    story.append(Spacer(2, 0.5*cm))

    paciente = requisicao.paciente
    idade = getattr(paciente, "idade_display", lambda: "—")()

    # Dados do paciente
    dados = [
        ["Nome do Paciente:", paciente.nome],
        ["Idade:", idade],
        ["Gênero:", paciente.genero or "—"],
        ["Documento:", paciente.numero_id or "—"],
        ["Proveniência:", getattr(paciente, "proveniencia", "N/D")]
    ]
    tabela = Table(dados, colWidths=[4*cm, 12*cm], hAlign='LEFT')
    tabela.setStyle(estilo_tabela_sem_verticais())
    story.append(tabela)
    story.append(Spacer(1, 0.5*cm))
    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph("Exames Requisitados", style))
    story.append(Spacer(1, 0.5*cm))

    # Exames
    exames = [[e.nome] for e in getattr(requisicao, "exames_list", requisicao.exames.all())] or [["Nenhum exame registrado."]]
    tabela_exames = Table(exames, colWidths=[16*cm], hAlign='LEFT')
    tabela_exames.setStyle(estilo_tabela_sem_verticais())
    story.append(tabela_exames)

    usuario = getattr(requisicao, "analista", None)
    doc.build(story, onFirstPage=lambda c,d: layout(c,d,usuario),
              onLaterPages=lambda c,d: layout(c,d,usuario))

    pdf_bytes = buffer.getvalue()
    buffer.close()
    filename = f"Req-{paciente.nid}-{paciente.nome.replace(' ', '_')}.pdf"
    return pdf_bytes, filename

# ==================== PDF DE RESULTADOS ====================
def gerar_pdf_resultados(requisicao, pos_x=2*cm, pos_y=None):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            leftMargin=0.5*cm, rightMargin=0.5*cm,
                            topMargin=3*cm, bottomMargin=2*cm)

    story = []
    story.append(Spacer(1, 1*cm if not pos_y else pos_y))  # ajuste Y
    style = ParagraphStyle("Heading1", fontName=FONT_BOLD, fontSize=12)
    story.append(Paragraph("RESULTADOS DE ANÁLISES CLÍNICAS", style))
    story.append(Spacer(1, 0.5*cm))

    paciente = requisicao.paciente
    idade = getattr(paciente, "idade_display", lambda: "—")()
    data_analise = getattr(requisicao, "created_at", None)
    data_str = data_analise.strftime("%d/%m/%Y") if data_analise else "—"

    # Dados do paciente
    dados = [
        ["Nome do Paciente:", paciente.nome],
        ["Idade:", idade],
        ["Gênero:", paciente.genero or "—"],
        ["Data da Análise:", data_str],
    ]
    tabela_dados = Table(dados, colWidths=[6*cm, 12*cm], hAlign='LEFT')
    tabela_dados.setStyle(estilo_tabela_sem_verticais())
    story.append(tabela_dados)
    story.append(Spacer(1, 0.5*cm))

    # Resultados
    resultados_data = [["Exame", "Resultado", "Unidade", "Referência"]]
    resultados_qs = getattr(requisicao, "resultados", None)
    if resultados_qs:
        for r in resultados_qs.all():
            resultados_data.append([
                getattr(r.exame, "nome", "—"),
                getattr(r, "resultado", "—"),
                getattr(r, "unidade", getattr(r.exame, "unidade", "—")),
                getattr(r, "valor_referencia", getattr(r.exame, "valor_ref", "—"))
            ])
    tabela_resultados = Table(resultados_data, colWidths=[5*cm, 5*cm, 2.5*cm, 2.5*cm], hAlign='LEFT')
    tabela_resultados.setStyle(estilo_tabela_sem_verticais())
    story.append(tabela_resultados)

    usuario = getattr(requisicao, "analista", None)
    doc.build(story, onFirstPage=lambda c,d: layout(c,d,usuario),
              onLaterPages=lambda c,d: layout(c,d,usuario))

    pdf_bytes = buffer.getvalue()
    buffer.close()
    filename = f"Res-{paciente.nid}-{paciente.nome.replace(' ', '_')}.pdf"
    return pdf_bytes, filename
