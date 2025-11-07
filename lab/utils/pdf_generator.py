"""
Módulo de geração de PDFs institucionais para AnaBioLink
Autor: Trato (ajustado)
Versão: 3.1.1 (estilos de tabela ajustados)
Descrição: Mantém comportamento anterior; altera apenas o desenho de linhas
           nas tabelas de resultados: linhas horizontais somente entre exames,
           e rótulos (Valor / Unidade / Valor referência) apresentados
           junto ao cabeçalho do exame.
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
                # posicione a imagem no canto superior esquerdo
                canvas.drawImage(ImageReader(buf), 20, A4[1] - 130,
                                 width=125, height=90, preserveAspectRatio=True, mask='auto')
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

    # linha de separação robusta
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
    # espaço entre assinaturas
    width_line = (width_total - 4 * cm) / 2

    x1 = 3 * cm
    x2 = 3 * cm + width_line + 2 * cm + width_line

    canvas.setLineWidth(1)
    canvas.line(x1, y, x1 + width_line, y)
    canvas.line(x1 + width_line + 2 * cm, y, x2, y)

    tecnico_nome = "Técnico de Laboratório"
    if usuario:
        nomes = [usuario.first_name, usuario.last_name]
        tecnico_nome = " ".join(filter(None, nomes)).strip() or tecnico_nome

    canvas.setFont(FONT, 10)
    canvas.drawCentredString(x1 + width_line / 2, y - 12, tecnico_nome)
    canvas.drawCentredString(x1 + width_line + 2 * cm + width_line / 2, y - 12, "Responsável do Laboratório")
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

                # Transparência (ReportLab recente suporta setFillAlpha)
                try:
                    canvas.setFillAlpha(0.06)
                except Exception:
                    # alguns backends antigos podem não suportar setFillAlpha; ignore se falhar
                    pass

                # Desenhar múltiplas instâncias
                y = 0
                while y < A4[1]:
                    x = 0
                    while x < A4[0]:
                        canvas.drawImage(watermark, x, y, width=w, height=h, mask='auto', preserveAspectRatio=True)
                        x += step_x
                    y += step_y

                try:
                    canvas.setFillAlpha(1.0)
                except Exception:
                    pass
        else:
            logger.warning("Marca d'água não encontrada em %s", WATERMARK_PATH)
    except Exception as e:
        logger.warning("Falha ao aplicar marca d'água: %s", e)
    finally:
        canvas.restoreState()


# ==================== LAYOUT PADRÃO ====================
def layout(canvas, doc, usuario=None):
    # Ordem: watermark por baixo, depois header, footer e assinaturas
    # watermark desenhada primeiro para ficar atrás (dependendo do backend)
    draw_watermark(canvas, doc)
    draw_header(canvas, doc)
    draw_footer(canvas, doc)
    draw_signatures(canvas, doc, usuario)


# ==================== ESTILO DE TABELAS ====================
def estilo_tabela_base_cmds():
    """
    Retorna lista de comandos (tuplas) compatível com TableStyle.
    Não adiciona linhas verticais nem linhas horizontais padrão — somente tipografia e paddings.
    """
    return [
        ("FONTNAME", (0, 0), (-1, -1), FONT),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]


# ==================== PDF DE REQUISIÇÃO ====================
def gerar_pdf_requisicao(requisicao, pos_x=1 * cm, pos_y=None):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            leftMargin=3 * cm, rightMargin=1 * cm,
                            topMargin=4 * cm, bottomMargin=1 * cm)

    story = []

    style = ParagraphStyle("Heading1", fontName=FONT_BOLD, fontSize=10)
    story.append(Spacer(1, 1 * cm if not pos_y else pos_y))
    story.append(Paragraph("REQUISIÇÃO DE ANÁLISES CLÍNICAS", style))
    story.append(Spacer(2, 0.5 * cm))

    paciente = requisicao.paciente
    idade = getattr(paciente, "idade_display", lambda: "—")()

    dados = [
        ["Nome do Paciente:", paciente.nome],
        ["Idade:", idade],
        ["Gênero:", paciente.genero or "—"],
        ["Documento:", paciente.numero_id or "—"],
        ["Proveniência:", getattr(paciente, "proveniencia", "N/D")]
    ]
    tabela = Table(dados, colWidths=[4 * cm, 12 * cm], hAlign='LEFT')
    tabela.setStyle(TableStyle(estilo_tabela_base_cmds()))
    story.append(tabela)
    story.append(Spacer(1, 0.5 * cm))
    story.append(Paragraph("Exames Requisitados", style))
    story.append(Spacer(1, 0.5 * cm))

    exames = [[e.nome] for e in getattr(requisicao, "exames_list", requisicao.exames.all())] or [["Nenhum exame registrado."]]
    tabela_exames = Table(exames, colWidths=[16 * cm], hAlign='LEFT')
    tabela_exames.setStyle(TableStyle(estilo_tabela_base_cmds()))
    story.append(tabela_exames)

    usuario = getattr(requisicao, "analista", None)
    doc.build(story, onFirstPage=lambda c, d: layout(c, d, usuario),
              onLaterPages=lambda c, d: layout(c, d, usuario))

    pdf_bytes = buffer.getvalue()
    buffer.close()
    filename = f"AnaBioLink_Req-{paciente.numero_id}-{paciente.nome.replace(' ', '_')}.pdf"
    return pdf_bytes, filename


# ==================== PDF DE RESULTADOS ====================
def gerar_pdf_resultados(requisicao, pos_x=2 * cm, pos_y=None):
    """
    Gera PDF de resultados agrupando por exame.
    Alterações principais:
    - Para cada exame adiciona um cabeçalho com o NOME DO EXAME (à esquerda) e 
      os rótulos (Valor | Unidade | Valor referência) na mesma linha (colunas à direita).
    - Desenha linha horizontal acima do cabeçalho do exame e abaixo do bloco do exame.
    - Não desenha linhas entre os parâmetros do mesmo exame.
    """
    import itertools

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            leftMargin=3 * cm, rightMargin=1 * cm,
                            topMargin=4 * cm, bottomMargin=1 * cm)

    story = []
    story.append(Spacer(1, 1 * cm if not pos_y else pos_y))
    style = ParagraphStyle("Heading1", fontName=FONT_BOLD, fontSize=12)
    story.append(Paragraph("RESULTADOS DE ANÁLISES", style))
    story.append(Spacer(1, 0.5 * cm))

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
    tabela_dados = Table(dados, colWidths=[6 * cm, 12 * cm], hAlign='LEFT')
    tabela_dados.setStyle(TableStyle(estilo_tabela_base_cmds()))
    story.append(tabela_dados)
    story.append(Spacer(1, 0.5 * cm))

    # -----------------------------------------------------------
    # Construção dos resultados agrupados por exame
    # -----------------------------------------------------------
    resultados_data = []
    style_cmds = estilo_tabela_base_cmds()
    # larguras apropriadas: campo, valor, unidade, valor_referencia
    col_widths = [6 * cm, 4 * cm, 2 * cm, 4 * cm]

    resultados_qs = getattr(requisicao, "resultados", None)
    if not resultados_qs:
        resultados_data = [["Nenhum resultado disponível."]]
        tabela_resultados = Table(resultados_data, colWidths=[16 * cm], hAlign='LEFT')
        tabela_resultados.setStyle(TableStyle(style_cmds))
        story.append(tabela_resultados)
    else:
        resultados_list = list(resultados_qs.all().select_related('exame_campo', 'exame_campo__exame'))
        resultados_list.sort(key=lambda r: (
            getattr(r.exame_campo.exame, "nome", ""),
            getattr(r.exame_campo, "ordem", 0)
        ))

        # iterar agrupado por exame
        for exame_nome, group in itertools.groupby(resultados_list, key=lambda r: getattr(r.exame_campo.exame, "nome", "—")):
            # índice da linha onde o cabeçalho do exame será inserido
            row_index = len(resultados_data)

            # CABEÇALHO: uma linha com [NOME_EXAME, "Valor", "Unidade", "Valor referência"]
            # O nome do exame ficará na coluna 0; as labels das colunas na 1,2,3
            resultados_data.append([exame_nome or "—", "Valor", "Unidade", "Valor referência"])

            # estilo para o cabeçalho: fundo claro, negrito a linha inteira e fontsize um pouco maior
            style_cmds.append(("BACKGROUND", (0, row_index), (-1, row_index), colors.HexColor("#F2F7FF")))
            style_cmds.append(("FONTNAME", (0, row_index), (-1, row_index), FONT_BOLD))
            style_cmds.append(("FONTSIZE", (0, row_index), (-1, row_index), 10))
            style_cmds.append(("LEFTPADDING", (0, row_index), (0, row_index), 6))
            style_cmds.append(("BOTTOMPADDING", (0, row_index), (-1, row_index), 6))
            # linha horizontal acima do cabeçalho do exame
            style_cmds.append(("LINEABOVE", (0, row_index), (-1, row_index), 0.7, colors.HexColor("#333333")))

            # agora adiciona os parâmetros (sem linhas entre eles)
            start_block_index = len(resultados_data)
            for r in group:
                exame_campo = getattr(r, "exame_campo", None)
                exame_nome_campo = getattr(exame_campo, "nome_campo", "—")
                unidade = r.unidade or getattr(exame_campo, "unidade", "—")
                valor_ref = r.valor_referencia or getattr(exame_campo, "valor_referencia", "—")
                valor = r.resultado or "—"
                resultados_data.append([exame_nome_campo, valor, unidade, valor_ref])

            # índice do final do bloco do exame (última linha pertencente a este exame)
            last_block_index = len(resultados_data) - 1
            # desenhar linha horizontal abaixo do bloco do exame para separar do próximo exame
            style_cmds.append(("LINEBELOW", (0, last_block_index), (-1, last_block_index), 0.5, colors.HexColor("#333333")))
            # pequeno espaçamento em baixo do bloco para melhorar leitura
            style_cmds.append(("BOTTOMPADDING", (0, last_block_index), (-1, last_block_index), 8))

        # criar a tabela final com os comandos acumulados
        tabela_resultados = Table(resultados_data, colWidths=col_widths, hAlign='LEFT')
        tabela_resultados.setStyle(TableStyle(style_cmds))
        story.append(tabela_resultados)

    # -----------------------------------------------------------
    # Finaliza documento mantendo header/footer/watermark via layout existente
    # -----------------------------------------------------------
    usuario = getattr(requisicao, "analista", None)
    doc.build(story, onFirstPage=lambda c, d: layout(c, d, usuario),
              onLaterPages=lambda c, d: layout(c, d, usuario))

    pdf_bytes = buffer.getvalue()
    buffer.close()
    filename = f"AnaBioLink_Res-{paciente.numero_id}-{paciente.nome.replace(' ', '_')}.pdf"
    return pdf_bytes, filename