"""
Módulo de geração de PDFs institucionais para SYS-LAB
Autor: Trato
Versão: 1.8 (sem linhas verticais em todas as tabelas, fontes com fallback automático)
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

from lab.models import Paciente
from PIL import Image

logger = logging.getLogger(__name__)

# ================= PATHS =================
LOGO_PATH = os.path.join(settings.BASE_DIR, "lab", "static", "img", "logo.png")
WATERMARK_PATH = LOGO_PATH

# ================= FONTES =================
try:
    pdfmetrics.registerFont(TTFont("Roboto", "/usr/share/fonts/truetype/roboto/Roboto-Regular.ttf"))
    pdfmetrics.registerFont(TTFont("Roboto-Bold", "/usr/share/fonts/truetype/roboto/Roboto-Bold.ttf"))
    DEFAULT_FONT = "Roboto"
    DEFAULT_FONT_BOLD = "Roboto-Bold"
except Exception as e:
    logger.warning("Falha ao registrar Roboto, usando Courier como fallback: %s", e)
    DEFAULT_FONT = "Courier"
    DEFAULT_FONT_BOLD = "Courier-Bold"

# ================= HEADER =================
def draw_header(canvas, doc):
    canvas.saveState()
    canvas.setFont(DEFAULT_FONT_BOLD, 14)

    if os.path.exists(LOGO_PATH):
        try:
            with Image.open(LOGO_PATH) as img:
                if img.mode == "RGBA":
                    img = img.convert("RGB")
                buf = io.BytesIO()
                img.save(buf, format="PNG")
                buf.seek(0)
                canvas.drawImage(ImageReader(buf), 35, A4[1] - 135,
                                 width=100, height=100, preserveAspectRatio=True, mask='auto')
        except Exception as e:
            logger.warning("Erro ao carregar logo: %s", e)
    else:
        canvas.setFont(DEFAULT_FONT, 10)
        canvas.drawString(35, A4[1] - 90, "LOGO INDISPONÍVEL")

    canvas.setFont(DEFAULT_FONT_BOLD, 14)
    canvas.drawString(140, A4[1] - 60, "HOSPITAL PROVINCIAL DE PEMBA")
    canvas.setFont(DEFAULT_FONT, 11)
    canvas.drawString(140, A4[1] - 78, "Laboratório de Análises Clínicas")
    canvas.setFont(DEFAULT_FONT, 9)
    canvas.drawString(140, A4[1] - 95, "Bairro Cimento, Cidade de Pemba - Cabo Delgado")
    canvas.drawString(140, A4[1] - 110, "Tel: +258 84 773 5374 | +258 86 128 4041 | info@lab-pemba-mz.com")

    canvas.setStrokeColor(colors.black)
    canvas.setLineWidth(1)
    canvas.line(0 * cm, A4[1] - 120, A4[0] - 0 * cm, A4[1] - 120)
    canvas.restoreState()

# ================= FOOTER =================
def draw_footer(canvas, doc):
    canvas.saveState()
    canvas.setFont(DEFAULT_FONT, 8)
    footer_text = f"Gerado automaticamente por analinklab em {datetime.now().strftime('%d/%m/%Y %H:%M')}"
    canvas.drawRightString(A4[0] - 2 * cm, 1.5 * cm, footer_text)
    canvas.restoreState()

# ================= WATERMARK =================
def draw_watermark(canvas, doc):
    try:
        canvas.saveState()
        try:
            canvas.setFillAlpha(0.08)
        except Exception:
            pass

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

        wm_width, wm_height = 4 * cm, 8 * cm
        spacing_x, spacing_y = 1.0 * cm, 2.0 * cm

        y = -wm_height
        while y < height + wm_height:
            x = -wm_width
            while x < width + wm_width:
                canvas.saveState()
                cx, cy = x + wm_width / 2, y + wm_height / 2
                canvas.translate(cx, cy)
                canvas.rotate(90)
                canvas.drawImage(
                    watermark, -wm_width/2, -wm_height/2,
                    width=wm_width, height=wm_height,
                    preserveAspectRatio=True, mask='auto'
                )
                canvas.restoreState()
                x += wm_width + spacing_x
            y += wm_height + spacing_y
        canvas.restoreState()
    except Exception as e:
        logger.warning("Erro ao desenhar watermark: %s", e)

# ================= ASSINATURAS =================
def draw_signatures(canvas, doc, usuario=None):
    canvas.saveState()
    y = 2 * cm
    width_total = A4[0] - 1 * cm - 1 * cm
    width_line = (width_total - 3 * cm) / 2

    x1_start, x1_end = 3 * cm, 3 * cm + width_line
    x2_start, x2_end = x1_end + 2 * cm, x1_end + 2 * cm + width_line

    canvas.setLineWidth(1)
    canvas.line(x1_start, y, x1_end, y)
    canvas.line(x2_start, y, x2_end, y)

    tecnico_nome = "Técnico de Laboratório"
    if usuario:
        nomes = []
        if getattr(usuario, "first_name", None):
            nomes.append(usuario.first_name.strip())
        if getattr(usuario, "last_name", None):
            nomes.append(usuario.last_name.strip())
        if getattr(usuario, "outros_nomes", None):
            nomes.extend([n.strip() for n in usuario.outros_nomes.split() if n.strip()])
        if nomes:
            tecnico_nome = " ".join(nomes)

    canvas.setFont(DEFAULT_FONT, 10)
    canvas.drawCentredString((x1_start + x1_end)/2, y - 12, tecnico_nome)
    canvas.drawCentredString((x2_start + x2_end)/2, y - 12, "Responsavel do Laboratório")
    canvas.restoreState()

# ================= LAYOUT UNIFICADO =================
def layout(canvas, doc, usuario=None):
    draw_watermark(canvas, doc)
    draw_header(canvas, doc)
    draw_footer(canvas, doc)
    draw_signatures(canvas, doc, usuario)

# ================= ESTILO DE TABELAS =================
def estilo_tabela_horizontal():
    return TableStyle([
        ("FONTNAME", (0,0), (-1,-1), DEFAULT_FONT),
        ("FONTSIZE", (0,0), (-1,-1), 9),
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("LINEABOVE", (0,0), (-1,0), 0.5, colors.black),
        ("LINEBELOW", (0,-1), (-1,-1), 0.5, colors.black),
        ("LINEBELOW", (0,0), (-1,-1), 0.25, colors.black),
        ("BACKGROUND", (0,0), (-1,0), colors.lightgrey)
    ])

# ================= PDF DE REQUISIÇÃO =================
def gerar_pdf_requisicao(requisicao):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            leftMargin=2*cm, rightMargin=0.5*cm,
                            topMargin=2*cm, bottomMargin=0.5*cm)

    story = []
    heading_style = ParagraphStyle("Heading1", fontName=DEFAULT_FONT_BOLD, fontSize=10, leading=12)
    story.append(Paragraph("REQUISIÇÃO DE ANÁLISES CLÍNICAS", heading_style))
    story.append(Spacer(0, 3*cm))

    paciente = requisicao.paciente
    idade = getattr(paciente, "idade_display", lambda: "—")()

    dados = [
        ["nome do paciente:", paciente.nome],
        ["idade:", idade],
        ["gênero:", paciente.genero or "—"],
        ["N. B.I./Passaporte/Doc:", paciente.numero_id or "—"],
        ["Proveniência:", getattr(Paciente.proveniencia, "proveniencia", "N/D")]
    ]
    tabela = Table(dados, colWidths=[4*cm, 12*cm])
    tabela.setStyle(estilo_tabela_horizontal())
    story.append(tabela)
    story.append(Spacer(2, 2*cm))

    exames = [[e.nome] for e in getattr(requisicao, "exames_list", requisicao.exames.all())] or [["Nenhum exame registrado."]]
    tabela_exames = Table(exames, colWidths=[15*cm])
    tabela_exames.setStyle(estilo_tabela_horizontal())
    story.append(tabela_exames)

    tecnico_user = getattr(requisicao, "analista", None)
    doc.build(story, onFirstPage=lambda c,d: layout(c,d,tecnico_user),
              onLaterPages=lambda c,d: layout(c,d,tecnico_user))

    pdf_bytes = buffer.getvalue()
    buffer.close()
    filename = f"Req-{paciente.nid}-{paciente.nome.replace(' ', '_')}.pdf"
    return pdf_bytes, filename

# ================= PDF DE RESULTADOS =================
def gerar_pdf_resultados(requisicao):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            leftMargin=2*cm, rightMargin=2*cm,
                            topMargin=3*cm, bottomMargin=2*cm)

    story = []
    heading_style = ParagraphStyle("Heading1", fontName=DEFAULT_FONT_BOLD, fontSize=12, leading=14)
    story.append(Paragraph("RESULTADOS DE ANÁLISES CLÍNICAS", heading_style))
    story.append(Spacer(1, 0.5*cm))

    paciente = requisicao.paciente
    idade = getattr(paciente, "idade_display", lambda: "—")()
    data_analise = getattr(requisicao, "created_at", None)
    data_str = data_analise.strftime("%d/%m/%Y") if data_analise else "—"

    dados_paciente = [
        ["nome do paciente:", paciente.nome],
        ["idade:", idade],
        ["gênero:", paciente.genero or "—"],
        ["data da análise:", data_str]
    ]
    tabela_dados = Table(dados_paciente, colWidths=[6*cm, 12*cm])
    tabela_dados.setStyle(estilo_tabela_horizontal())
    story.append(tabela_dados)
    story.append(Spacer(2, 0.5*cm))

    resultados_data = [["exame", "resultado", "unidade", "referência"]]
    resultados_qs = getattr(requisicao, "resultados", None)
    if resultados_qs:
        for r in resultados_qs.all():
            resultados_data.append([
                getattr(r.exame, "nome", "—"),
                getattr(r, "resultado", "—"),
                getattr(r, "unidade", getattr(r.exame, "unidade", "—")),
                getattr(r, "valor_referencia", getattr(r.exame, "valor_ref", "—"))
            ])

    tabela_resultados = Table(resultados_data, colWidths=[5*cm, 5*cm, 2.5*cm, 2.5*cm])
    tabela_resultados.setStyle(estilo_tabela_horizontal())
    story.append(tabela_resultados)

    tecnico_user = getattr(requisicao, "analista", None)
    doc.build(story, onFirstPage=lambda c,d: layout(c,d,tecnico_user),
              onLaterPages=lambda c,d: layout(c,d,tecnico_user))

    pdf_bytes = buffer.getvalue()
    buffer.close()
    filename = f"Res-{paciente.nid}-{paciente.nome.replace(' ', '_')}.pdf"
    return pdf_bytes, filename
