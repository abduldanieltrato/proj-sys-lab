"""
Módulo de geração de PDFs institucionais para AnaBioLink
Autor: Trato
Versão: 3.1 (layout híbrido: design AnaBioLink + margens institucionais precisas)
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
                canvas.drawImage(ImageReader(buf), 20, A4[1] - 130,
                                 width=125, height=190, preserveAspectRatio=True, mask='auto')
        except Exception as e:
            logger.warning("Erro ao carregar logo: %s", e)
    else:
        canvas.setFont(FONT, 10)
        canvas.drawString(35, A4[1] - 90, "LOGO INDISPONÍVEL")

    canvas.setFont(FONT_BOLD, 14)
    canvas.drawString(150, A4[1] - 60, "AnaBioLink - Sistema de Gestão Laboratorial")
    canvas.setFont(FONT, 11)
    canvas.drawString(150, A4[1] - 78, "Laboratório de Análises Clínicas e Diagnóstico")
    canvas.setFont(FONT, 9)
    canvas.drawString(150, A4[1] - 95, "Pemba - Cabo Delgado, Moçambique")
    canvas.drawString(150, A4[1] - 110, "Tel: +258 84 773 5374 | Email: suporte@anabiolink.mz")

    canvas.setStrokeColor(colors.darkblue)
    canvas.setLineWidth(5)
    canvas.line(0 * cm, A4[1] - 120, A4[0] - 0 * cm, A4[1] - 120)
    canvas.restoreState()


# ==================== RODAPÉ ====================
def draw_footer(canvas, doc):
    canvas.saveState()
    canvas.setFont(FONT, 8)
    footer_text = f"Gerado automaticamente por AnaBioLink em {datetime.now().strftime('%d/%m/%Y %H:%M')}"
    canvas.drawRightString(A4[0] - 1 * cm, 0.7 * cm, footer_text)
    canvas.restoreState()


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


# ==================== MARCA D'ÁGUA ====================
def draw_watermark(canvas, doc):
    canvas.saveState()
    try:
        if os.path.exists(WATERMARK_PATH):
            with Image.open(WATERMARK_PATH) as img:
                if img.mode == "RGBA":
                    img = img.convert("RGB")
                buf = io.BytesIO()
                img.save(buf, format="PNG")
                buf.seek(0)
                watermark = ImageReader(buf)

                # Tamanho da marca d’água (em pontos)
                w, h = 120, 170

                # Espaçamento entre as marcas
                step_x, step_y = w + 40, h + 50

                # Transparência
                canvas.setFillAlpha(0.08)

                # Desenhar múltiplas instâncias
                y = 0
                while y < A4[1]:
                    x = 0
                    while x < A4[0]:
                        canvas.drawImage(watermark, x, y, width=w, height=h, mask='auto', preserveAspectRatio=True)
                        x += step_x
                    y += step_y

                canvas.setFillAlpha(1.0)
        else:
            logger.warning("Marca d'água não encontrada em %s", WATERMARK_PATH)
    except Exception as e:
        logger.warning("Falha ao aplicar marca d'água: %s", e)
    finally:
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
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#E0E0E0"))
    ])


# ==================== PDF DE REQUISIÇÃO ====================
def gerar_pdf_requisicao(requisicao, pos_x=1*cm, pos_y=None):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            leftMargin=3*cm, rightMargin=1*cm,
                            topMargin=4*cm, bottomMargin=1*cm)

    story = []

    style = ParagraphStyle("Heading1", fontName=FONT_BOLD, fontSize=10)
    story.append(Spacer(1, 1*cm if not pos_y else pos_y))
    story.append(Paragraph("REQUISIÇÃO DE ANÁLISES CLÍNICAS", style))
    story.append(Spacer(2, 0.5*cm))

    paciente = requisicao.paciente
    idade = getattr(paciente, "idade_display", lambda: "—")()

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
    story.append(Paragraph("Exames Requisitados", style))
    story.append(Spacer(1, 0.5*cm))

    exames = [[e.nome] for e in getattr(requisicao, "exames_list", requisicao.exames.all())] or [["Nenhum exame registrado."]]
    tabela_exames = Table(exames, colWidths=[16*cm], hAlign='LEFT')
    tabela_exames.setStyle(estilo_tabela_sem_verticais())
    story.append(tabela_exames)

    usuario = getattr(requisicao, "analista", None)
    doc.build(story, onFirstPage=lambda c,d: layout(c,d,usuario),
              onLaterPages=lambda c,d: layout(c,d,usuario))

    pdf_bytes = buffer.getvalue()
    buffer.close()
    filename = f"AnaBioLink_Req-{paciente.numero_id}-{paciente.nome.replace(' ', '_')}.pdf"
    return pdf_bytes, filename


# ==================== PDF DE RESULTADOS ====================
def gerar_pdf_resultados(requisicao, pos_x=2*cm, pos_y=None):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            leftMargin=3*cm, rightMargin=1*cm,
                            topMargin=4*cm, bottomMargin=1*cm)

    story = []
    story.append(Spacer(1, 1*cm if not pos_y else pos_y))
    style = ParagraphStyle("Heading1", fontName=FONT_BOLD, fontSize=12)
    story.append(Paragraph("RESULTADOS DE ANÁLISES CLÍNICAS", style))
    story.append(Spacer(1, 0.5*cm))

    paciente = requisicao.paciente
    idade = getattr(paciente, "idade_display", lambda: "—")()
    data_analise = getattr(requisicao, "created_at", None)
    data_str = data_analise.strftime("%d/%m/%Y") if data_analise else "—"

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

    resultados_data = [["Exame", "Resultado", "Unidade", "Referência"]]
    resultados_qs = getattr(requisicao, "resultados", None)
    if resultados_qs:
        for r in resultados_qs.all():
            exame_nome = getattr(r.exame_campo, "nome_campo", "—")
            unidade = r.unidade or getattr(r.exame_campo, "unidade", "—")
            valor_ref = r.valor_referencia or getattr(r.exame_campo, "valor_referencia", "—")
            resultados_data.append([
                exame_nome,
                r.resultado or "—",
                unidade,
                valor_ref
            ])

    tabela_resultados = Table(resultados_data, colWidths=[5*cm, 5*cm, 2.5*cm, 2.5*cm], hAlign='LEFT')
    tabela_resultados.setStyle(estilo_tabela_sem_verticais())
    story.append(tabela_resultados)

    usuario = getattr(requisicao, "analista", None)
    doc.build(story, onFirstPage=lambda c,d: layout(c,d,usuario),
              onLaterPages=lambda c,d: layout(c,d,usuario))

    pdf_bytes = buffer.getvalue()
    buffer.close()
    filename = f"AnaBioLink_Res-{paciente.numero_id}-{paciente.nome.replace(' ', '_')}.pdf"
    return pdf_bytes, filename
