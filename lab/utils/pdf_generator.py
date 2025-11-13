# lab/utils/pdf_generator.py
import os
import io
import logging
from datetime import datetime
from django.conf import settings
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import (
	SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
	KeepTogether
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas as rl_canvas
from PIL import Image

logger = logging.getLogger(__name__)

# ---------------- Caminhos ----------------
LOGO_PATH = os.path.join(settings.BASE_DIR, "lab", "static", "img", "logo.png")

# ---------------- Fontes ----------------
try:
	pdfmetrics.registerFont(TTFont("Times-Roman", "/usr/share/fonts/truetype/msttcorefonts/Times_New_Roman.ttf"))
	pdfmetrics.registerFont(TTFont("Times-Bold", "/usr/share/fonts/truetype/msttcorefonts/Times_New_Roman_Bold.ttf"))
	FONT = "Times-Roman"
	FONT_BOLD = "Times-Bold"
except Exception as e:
	logger.warning("Falha ao registrar Times New Roman, usando Courier: %s", e)
	FONT = "Courier"
	FONT_BOLD = "Courier-Bold"


# ---------------- Canvas com numeração ----------------
from reportlab.pdfgen import canvas as rl_canvas

class NumberedCanvas(rl_canvas.Canvas):
    """
    Implementação robusta: armazena o estado de cada página em showPage()
    e, no save(), redesenha cada página adicionando o footer com 'Página X de Y'.
    Esta versão evita duplicação quando usada como canvasmaker.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        # guarda o estado actual da página (dicionário das attrs do canvas)
        self._saved_page_states.append(dict(self.__dict__))
        # inicia uma nova página internamente (não chama novamente draw/footer)
        self._startPage()

    def save(self):
        # número total de páginas
        num_pages = len(self._saved_page_states)
        # redesenha cada página a partir dos estados guardados, desenhando o footer
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self._draw_footer(num_pages)
            # usar o método da classe base para finalizar esta página no arquivo final
            rl_canvas.Canvas.showPage(self)
        # finalmente salva o PDF
        rl_canvas.Canvas.save(self)

    def _draw_footer(self, total_pages):
        try:
            self.setFont(FONT, 8)
        except Exception:
            self.setFont("Helvetica", 8)
        page_num = self._pageNumber
        footer_text = f"Gerado automaticamente por AnaBioLink em {datetime.now().strftime('%d/%m/%Y %H:%M')}"
        right = A4[0] - 1 * cm
        self.drawRightString(right, 0.7 * cm, f"{footer_text} — Página {page_num} de {total_pages}")


# ---------------- Header ----------------
def _safe_image_reader(path):
	if not os.path.exists(path):
		return None
	try:
		with Image.open(path) as img:
			img = img.convert("RGB")
			buf = io.BytesIO()
			img.save(buf, format="JPEG", quality=90)
			buf.seek(0)
			return ImageReader(buf)
	except Exception as e:
		logger.warning("Erro ao abrir imagem %s: %s", path, e)
		return None


def draw_header(canvas_obj, doc):
	canvas_obj.saveState()
	logo = _safe_image_reader(LOGO_PATH)
	if logo:
		try:
			canvas_obj.drawImage(logo, 20, A4[1] - 130, width=125, height=90, preserveAspectRatio=True)
		except Exception as e:
			logger.warning("Erro ao desenhar logo no header: %s", e)
	else:
		canvas_obj.setFont(FONT, 10)
		canvas_obj.drawString(35, A4[1] - 90, "LOGO INDISPONÍVEL")

	canvas_obj.setFont(FONT_BOLD, 14)
	canvas_obj.drawString(150, A4[1] - 60, "AnaBioLink - Sistema de Gestão Laboratorial")
	canvas_obj.setFont(FONT, 11)
	canvas_obj.drawString(150, A4[1] - 78, "Laboratório de Análises Clínicas e Diagnóstico")
	canvas_obj.setFont(FONT, 9)
	canvas_obj.drawString(150, A4[1] - 95, "Pemba - Cabo Delgado, Moçambique")
	canvas_obj.drawString(150, A4[1] - 110, "Tel: +258 84 773 5374 | Email: suporte@anabiolink.mz")
	canvas_obj.setStrokeColor(colors.darkblue)
	canvas_obj.setLineWidth(5)
	canvas_obj.line(0 * cm, A4[1] - 120, A4[0], A4[1] - 120)
	canvas_obj.restoreState()


# ---------------- Assinaturas ----------------
def draw_signatures(canvas_obj, doc, usuario=None):
	canvas_obj.saveState()
	y = 2.5 * cm  # margem inferior aumentada
	width_total = A4[0] - 2 * cm
	width_line = (width_total - 4 * cm) / 2
	x1 = 3 * cm
	x2 = 3 * cm + width_line + 2 * cm + width_line
	canvas_obj.setLineWidth(1)
	canvas_obj.line(x1, y, x1 + width_line, y)
	canvas_obj.line(x1 + width_line + 2 * cm, y, x2, y)
	tecnico_nome = "Técnico de Laboratório"
	if usuario:
		nomes = [getattr(usuario, "first_name", ""), getattr(usuario, "last_name", "")]
		tecnico_nome = " ".join(filter(None, nomes)).strip() or tecnico_nome
	canvas_obj.setFont(FONT, 10)
	canvas_obj.drawCentredString(x1 + width_line / 2, y - 12, tecnico_nome)
	canvas_obj.drawCentredString(x1 + width_line + 2 * cm + width_line / 2, y - 12, "Responsável do Laboratório")
	canvas_obj.restoreState()


# ---------------- Callback de Página ----------------
def _on_page(canvas_obj, doc, usuario=None):
	canvas_obj.saveState()
	draw_header(canvas_obj, doc)
	draw_signatures(canvas_obj, doc, usuario)
	canvas_obj.restoreState()


# ---------------- Funções Auxiliares ----------------
def _cell_paragraph(text):
	cell_style = ParagraphStyle("cell_style", fontName=FONT, fontSize=9, leading=11)
	return Paragraph(str(text), cell_style)


# ---------------- PDF: REQUISIÇÃO ----------------
def gerar_pdf_requisicao(requisicao):
	import reportlab.lib.pagesizes as pagesizes
	buffer = io.BytesIO()
	page_width, _ = pagesizes.A4
	left_margin, right_margin = 3 * cm, 1 * cm
	usable_width = page_width - left_margin - right_margin

	doc = SimpleDocTemplate(
		buffer, pagesize=pagesizes.A4,
		leftMargin=left_margin, rightMargin=right_margin,
		topMargin=4 * cm, bottomMargin=3.5 * cm  # espaço extra p/ assinaturas
	)

	story = []
	style_title = ParagraphStyle("Heading1", fontName=FONT_BOLD, fontSize=10)
	story.append(Spacer(1, 1 * cm))
	story.append(Paragraph("REQUISIÇÃO DE EXAMES", style_title))
	story.append(Spacer(1, 0.5 * cm))

	paciente = requisicao.paciente
	idade = getattr(paciente, "idade", lambda: "—")()
	dados = [
		[Paragraph("Nome do Paciente:", style_title), Paragraph(paciente.nome, style_title)],
		[Paragraph("Idade:", style_title), Paragraph(idade, style_title)],
		[Paragraph("Gênero:", style_title), Paragraph(paciente.genero or "—", style_title)],
		[Paragraph("Documento:", style_title), Paragraph(paciente.numero_id or "—", style_title)],
		[Paragraph("Proveniência:", style_title), Paragraph(getattr(paciente, "proveniencia", "N/D"), style_title)],
		[Paragraph("Data de Criação:", style_title), Paragraph(requisicao.created_at.strftime("%d/%m/%Y %H:%M"), style_title)],
	]
	tabela = Table(dados, colWidths=[usable_width * 0.25, usable_width * 0.75], hAlign="LEFT")
	tabela.setStyle(TableStyle([
		("FONTNAME", (0, 0), (-1, -1), FONT),
		("FONTSIZE", (0, 0), (-1, -1), 9),
	]))
	story.append(tabela)
	story.append(Spacer(1, 0.5 * cm))

	story.append(Paragraph("Exames Requisitados", style_title))
	story.append(Spacer(1, 0.3 * cm))
	exames = requisicao.exames.all()
	exames_data = [[_cell_paragraph(e.nome)] for e in exames] if exames.exists() else [[_cell_paragraph("Nenhum exame registrado.")]]
	tabela_exames = Table(exames_data, colWidths=[usable_width], hAlign="LEFT")
	story.append(KeepTogether(tabela_exames))

	doc.build(
		story,
		onFirstPage=lambda c, d: _on_page(c, d, getattr(requisicao, "analista", None)),
		onLaterPages=lambda c, d: _on_page(c, d, getattr(requisicao, "analista", None)),
		canvasmaker=NumberedCanvas
	)

	pdf_bytes = buffer.getvalue()
	buffer.close()
	filename = f"AnaBioLink_Requisicao_{requisicao.id_custom}_{requisicao.paciente.nome}.pdf"
	return pdf_bytes, filename


# ---------------- PDF: RESULTADOS ----------------
def gerar_pdf_resultados(requisicao, apenas_validados=False):
	import reportlab.lib.pagesizes as pagesizes
	buffer = io.BytesIO()
	page_width, _ = pagesizes.A4
	left_margin, right_margin = 3 * cm, 1 * cm
	usable_width = page_width - left_margin - right_margin

	doc = SimpleDocTemplate(
		buffer, pagesize=pagesizes.A4,
		leftMargin=left_margin, rightMargin=right_margin,
		topMargin=4.5 * cm, bottomMargin=2 * cm  # margem corrigida
	)

	elements = []
	styles = getSampleStyleSheet()
	style_title = ParagraphStyle("Heading3", fontName=FONT_BOLD, fontSize=12)
	style_subtitle = ParagraphStyle("Heading4", fontName=FONT_BOLD, fontSize=10)
	style_normal = ParagraphStyle("Normal", fontName=FONT, fontSize=9)
	cell_style = ParagraphStyle("cell_style", fontName=FONT, fontSize=9, leading=11)

	elements.append(Paragraph("RESULTADOS DE ANÁLISES", style_title))
	elements.append(Spacer(1, 10))
	elements.append(Paragraph(f"Nome de Paciente: {requisicao.paciente.nome}", style_normal))
	elements.append(Paragraph(f"Idade: {requisicao.paciente.idade()}", style_normal))
	elements.append(Paragraph(f"Gênero: {requisicao.paciente.genero}", style_normal))
	elements.append(Paragraph(f"Documento: {requisicao.paciente.numero_id}", style_normal))
	elements.append(Paragraph(f"Proveniência: {requisicao.paciente.proveniencia}", style_normal))
	elements.append(Spacer(1, 8))
	elements.append(Paragraph(f"Ordem da Requisição: {requisicao.id_custom}", style_normal))
	elements.append(Paragraph(f"Data dos Resultados: {requisicao.created_at.strftime('%d/%m/%Y %H:%M')}", style_normal))
	elements.append(Spacer(1, 16))

	resultados_qs = getattr(requisicao, "resultados", None) or getattr(requisicao, "resultadoitem_set", None)
	if not resultados_qs:
		elements.append(Paragraph("Nenhum resultado disponível para esta requisição.", style_normal))
	else:
		qs = resultados_qs.select_related("exame_campo__exame")
		if apenas_validados:
			qs = qs.filter(validado=True)
		exames_agrupados = {}
		for r in qs:
			exame = r.exame_campo.exame
			exames_agrupados.setdefault(exame.nome, []).append(r)
		if not exames_agrupados:
			elements.append(Paragraph("Nenhum resultado validado encontrado.", style_normal))
		else:
			for exame_nome, resultados in exames_agrupados.items():
				elements.append(Paragraph(exame_nome, style_subtitle))
				elements.append(Spacer(1, 6))
				data = [[
					Paragraph("Indicador", cell_style),
					Paragraph("Resultado", cell_style),
					Paragraph("Unidade", cell_style),
					Paragraph("Valor de Ref.", cell_style)
				]]
				for r in resultados:
					valor = getattr(r, "resultado", None)
					if valor in (None, ""):
						for attr in ("valor_texto", "valor_numerico", "valor_percentagem", "valor_escolha"):
							v = getattr(r, attr, None)
							if v not in (None, ""):
								valor = v
								break
					data.append([
						Paragraph(r.exame_campo.nome_campo, cell_style),
						Paragraph(str(f'{valor} {r.exame_campo.unidade}') if valor not in (None, "") else "-", cell_style),
						Paragraph(r.exame_campo.unidade or "-", cell_style),
						Paragraph(r.exame_campo.valor_referencia or "-", cell_style),
					])
				table = Table(data, colWidths=[usable_width * 0.35, usable_width * 0.35, usable_width * 0.15, usable_width * 0.15], hAlign="LEFT")
				table.setStyle(TableStyle([
					("FONTNAME", (0, 0), (-1, 0), FONT_BOLD),
					("ALIGN", (1, 1), (-1, -1), "LEFT"),
				]))
				elements.append(table)
				elements.append(Spacer(1, 12))

	doc.build(
		elements,
		onFirstPage=lambda c, d: _on_page(c, d, getattr(requisicao, "analista", None)),
		onLaterPages=lambda c, d: _on_page(c, d, getattr(requisicao, "analista", None)),
		canvasmaker=NumberedCanvas
	)

	pdf = buffer.getvalue()
	buffer.close()
	filename = f"AnaBioLink_Resultados_{requisicao.id_custom}_{requisicao.paciente.nome}.pdf"
	return pdf, filename
