"""
lab.utils.pdf_generator
-----------------------

Gerador de PDFs para o sistema AnaBioLink.

Este módulo expõe duas funções principais:
- gerar_pdf_requisicao(requisicao) -> (bytes, filename)
- gerar_pdf_resultados(requisicao, apenas_validados=False) -> (bytes, filename)

Design goals:
- Manter compatibilidade com o código existente (não altera modelos).
- Usar Times New Roman quando disponível; fallback para Courier.
- Estilos consistentes, cabeçalho/rodapé padronizados e docstrings profissionais.
"""

import os
import io
import logging
from datetime import datetime
from typing import Optional, Tuple

from django.conf import settings
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (
	SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas as rl_canvas
from reportlab.lib.enums import TA_LEFT, TA_RIGHT
from PIL import Image

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configurações de fontes e caminhos
# ---------------------------------------------------------------------------
LOGO_PATH = os.path.join(settings.BASE_DIR, "lab", "static", "img", "logo.png")

try:
	# tenta registrar Times New Roman (regular + bold)
	pdfmetrics.registerFont(TTFont("Times-Roman", "/usr/share/fonts/truetype/msttcorefonts/Times_New_Roman.ttf"))
	pdfmetrics.registerFont(TTFont("Times-Bold", "/usr/share/fonts/truetype/msttcorefonts/Times_New_Roman_Bold.ttf"))
	FONT = "Times-Roman"
	FONT_BOLD = "Times-Bold"
except Exception as e:
	# fallback para ambientes que não têm msttcorefonts instaladas
	logger.warning("Falha ao registrar Times New Roman; usando Courier. Erro: %s", e)
	FONT = "Courier"
	FONT_BOLD = "Courier-Bold"


# ---------------------------------------------------------------------------
# Canvas customizado
# ---------------------------------------------------------------------------
class NumberedCanvas(rl_canvas.Canvas):
	"""
	Canvas customizado que salva estados de página, desenha rodapé com data/hora
	e numeração "Página X de Y" ao salvar o documento.
	"""

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self._saved_page_states = []

	def showPage(self) -> None:
		"""Armazena o estado atual da página e inicia uma nova."""
		self._saved_page_states.append(dict(self.__dict__))
		self._startPage()

	def save(self) -> None:
		"""Desenha rodapé em todas as páginas salvas e efetiva o save final."""
		num_pages = len(self._saved_page_states)
		for state in self._saved_page_states:
			self.__dict__.update(state)
			self._draw_footer(num_pages)
			rl_canvas.Canvas.showPage(self)
		rl_canvas.Canvas.save(self)

	def _draw_footer(self, total_pages: int) -> None:
		"""Desenha o rodapé com data/hora de geração e numeração de páginas."""
		try:
			self.setFont(FONT, 8)
		except Exception:
			# fallback muito seguro
			self.setFont("Helvetica", 8)

		page_num = self._pageNumber
		footer_text = f"Gerado automaticamente por AnaBioLink em {datetime.now().strftime('%d/%m/%Y às %H:%M')}"
		right = A4[0] - 1 * cm
		self.drawRightString(right, 0.7 * cm, f"{footer_text} — Página {page_num} de {total_pages}")


# ---------------------------------------------------------------------------
# Helpers para imagens e cabeçalho
# ---------------------------------------------------------------------------
def _safe_image_reader(path: str) -> Optional[ImageReader]:
	"""
	Carrega e converte uma imagem para ImageReader.
	Se o ficheiro não existir ou der erro, retorna None.
	"""
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


def draw_header(canvas_obj: rl_canvas.Canvas, doc) -> None:
	"""
	Desenha o cabeçalho do documento: logo, nome do sistema e contactos.
	"""
	canvas_obj.saveState()
	logo = _safe_image_reader(LOGO_PATH)
	if logo:
		try:
			canvas_obj.drawImage(logo, 20, A4[1] - 130, width=125, height=90, preserveAspectRatio=True)
		except Exception as e:
			logger.warning("Erro ao desenhar logo: %s", e)
	else:
		canvas_obj.setFont(FONT, 10)
		canvas_obj.drawString(35, A4[1] - 90, "LOGO INDISPONÍVEL")

	# Títulos e contactos
	canvas_obj.setFont(FONT_BOLD, 14)
	canvas_obj.drawString(150, A4[1] - 60, "AnaBioLink - Sistema de Gestão Laboratorial")
	canvas_obj.setFont(FONT, 11)
	canvas_obj.drawString(150, A4[1] - 78, "Laboratório de Análises Clínicas e Diagnóstico")
	canvas_obj.setFont(FONT, 9)
	canvas_obj.drawString(150, A4[1] - 95, "Pemba - Cabo Delgado, Moçambique")
	canvas_obj.drawString(150, A4[1] - 110, "Tel: +258 84 773 5374 | Email: abdultrato@anabiolink.mz")

	# Linha separadora
	canvas_obj.setStrokeColor(colors.darkblue)
	canvas_obj.setLineWidth(0.5)
	canvas_obj.line(0 * cm, A4[1] - 120, A4[0], A4[1] - 120)
	canvas_obj.restoreState()


def draw_signatures(canvas_obj: rl_canvas.Canvas, doc, usuario=None) -> None:
	"""
	Desenha as linhas de assinatura na parte inferior do PDF.
	Se um 'usuario' é passado, exibe o nome do técnico; senão usa rótulo genérico.
	"""
	canvas_obj.saveState()
	y = 1 * cm
	width_total = A4[0] - 2 * cm
	width_line = (width_total - 4 * cm) / 2
	x1 = 1 * cm
	x2 = 3 * cm + width_line + 2 * cm + width_line

	canvas_obj.setStrokeColor(colors.darkblue)
	canvas_obj.setLineWidth(0.3)
	canvas_obj.line(x1, y, x1 + width_line, y)
	

	tecnico_nome = "Técnico de Laboratório"
	if usuario:
		nomes = [getattr(usuario, "first_name", ""), getattr(usuario, "last_name", "")]
		tecnico_nome = " ".join(filter(None, nomes)).strip() or tecnico_nome

	canvas_obj.setFont(FONT, 10)
	canvas_obj.drawCentredString(x1 + width_line / 2, y - 12, f'Assinatura de {tecnico_nome}')
	canvas_obj.drawCentredString(x1 + width_line + 2 * cm + width_line / 2, y - 12, " ")
	canvas_obj.restoreState()


def _on_page(canvas_obj: rl_canvas.Canvas, doc, usuario=None) -> None:
	"""
	Callback usado por SimpleDocTemplate para desenhar header/signatures em cada página.
	"""
	canvas_obj.saveState()
	draw_header(canvas_obj, doc)
	draw_signatures(canvas_obj, doc, usuario)
	canvas_obj.restoreState()


# ---------------------------------------------------------------------------
# Estilos reutilizáveis
# ---------------------------------------------------------------------------
bold_style = ParagraphStyle(name="Bold", fontName=FONT_BOLD, fontSize=9, leading=11, alignment=TA_LEFT)
cell_style = ParagraphStyle(name="Cell", fontName=FONT, fontSize=9, leading=11, alignment=TA_LEFT)


def _cell_paragraph(text: str, bold: bool = False) -> Paragraph:
	"""
	Retorna um Paragraph formatado para uso em células de tabela.
	:params text: string do conteúdo
	:params bold: se True aplica fonte em negrito
	"""
	style = bold_style if bold else cell_style
	return Paragraph(str(text), style)


# ---------------------------------------------------------------------------
# Geração de PDF: Requisição
# ---------------------------------------------------------------------------
def gerar_pdf_requisicao(requisicao) -> Tuple[bytes, str]:
	"""
	Gera o PDF da requisição de exames.

	:param requisicao: instância de RequisicaoAnalise
	:returns: tuple (pdf_bytes, filename)
	"""
	import reportlab.lib.pagesizes as pagesizes

	buffer = io.BytesIO()
	page_width, _ = pagesizes.A4
	left_margin, right_margin = 1 * cm, 1 * cm
	usable_width = page_width - left_margin - right_margin

	doc = SimpleDocTemplate(
		buffer,
		pagesize=pagesizes.A4,
		leftMargin=left_margin,
		rightMargin=right_margin,
		topMargin=4 * cm,
		bottomMargin=2 * cm
	)

	story = []

	# Título
	style_title = ParagraphStyle("HeadingReq", fontName=FONT_BOLD, fontSize=10)
	story.append(Spacer(0.5, 0.5 * cm))
	story.append(Paragraph("REQUISIÇÃO DE EXAMES", style_title))
	story.append(Spacer(0.3, 0.3 * cm))
	

	# Paciente e metadados
	paciente = requisicao.paciente
	idade = getattr(paciente, "idade", lambda: "—")()
	analista = requisicao.analista

	style_left = ParagraphStyle("req_left", fontName=FONT, fontSize=8, leading=10)
	style_right = ParagraphStyle("req_right", fontName=FONT, fontSize=8, leading=10, alignment=TA_RIGHT)

	left_lines = [
		f"Nome do Paciente: {paciente.nome}",
		f"Idade: {idade}",
		f"Gênero: {paciente.genero or '—'}",
		f"Documento: {paciente.numero_id or '—'}",
		f"Proveniência: {getattr(paciente, 'proveniencia', '—')}"
	]

	if analista:
		nome_real = getattr(analista, 'get_full_name', lambda: '')()
		apelido = getattr(analista, 'apelido', '')
		tecnico_texto = f"{nome_real} ({apelido})" if apelido else nome_real
	else:
		tecnico_texto = "—"

	right_lines = [
		f"Ordem da Requisição: {requisicao.id_custom}",
		f"Data da Criação: {requisicao.created_at.strftime('%d/%m/%Y %H:%M')}",
		f"Analista: {tecnico_texto or '—'}"
	]

	left_para = Paragraph("<br/>".join(left_lines), style_left)
	right_para = Paragraph("<br/>".join(right_lines), style_right)

	req_table = Table([[left_para, right_para]], colWidths=[usable_width * 0.62, usable_width * 0.38], hAlign="LEFT")
	req_table.setStyle(TableStyle([
		("VALIGN", (0, 0), (-1, -1), "TOP"),
		("FONTNAME", (0, 0), (-1, -1), FONT),
		("FONTSIZE", (0, 0), (-1, -1), 8),
		("LEFTPADDING", (0, 0), (-1, -1), 0),
		("RIGHTPADDING", (0, 0), (-1, -1), 0),
	]))
	story.append(req_table)
	story.append(Spacer(1, 0.5 * cm))

	# Exames requisitados (com negrito)
	story.append(Paragraph("Exames Requisitados", style_title))
	story.append(Spacer(1, 0.3 * cm))

	exames = requisicao.exames.all()
	exames_data = [
		[_cell_paragraph(f"Nome do Exame: &nbsp;&nbsp;&nbsp&nbsp;&nbsp;&nbsp;{e.codigo.upper()}&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{e.nome.capitalize()}&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{e.metodo.capitalize()}&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;")]
		for e in exames
	] if exames.exists() else [[_cell_paragraph("Nenhum exame registrado.", bold=True)]]

	tabela_exames = Table(exames_data, colWidths=[usable_width], hAlign="LEFT")
	tabela_exames.setStyle(TableStyle([
		("LEFTPADDING", (0, 0), (-1, -1), 2),
		("RIGHTPADDING", (0, 0), (-1, -1), 2),
	]))
	story.append(KeepTogether(tabela_exames))

	# Finaliza doc
	doc.build(
		story,
		onFirstPage=lambda c, d: _on_page(c, d, analista),
		onLaterPages=lambda c, d: _on_page(c, d, analista),
		canvasmaker=NumberedCanvas
	)

	pdf_bytes = buffer.getvalue()
	buffer.close()
	filename = f"AnaBioLink_Requisicao_{requisicao.id_custom}_{requisicao.paciente.nome}.pdf"
	return pdf_bytes, filename


# ---------------------------------------------------------------------------
# Geração de PDF: Resultados
# ---------------------------------------------------------------------------
def gerar_pdf_resultados(requisicao, apenas_validados: bool = False) -> Tuple[bytes, str]:
	"""
	Gera o PDF com os resultados dos exames de uma requisição.

	:param requisicao: instância de RequisicaoAnalise
	:param apenas_validados: se True inclui apenas resultados validados
	:return: tuple (pdf_bytes, filename)
	"""
	import reportlab.lib.pagesizes as pagesizes

	buffer = io.BytesIO()
	page_width, _ = pagesizes.A4
	left_margin, right_margin = 3 * cm, 1 * cm
	usable_width = page_width - left_margin - right_margin

	doc = SimpleDocTemplate(
		buffer,
		pagesize=pagesizes.A4,
		leftMargin=left_margin,
		rightMargin=right_margin,
		topMargin=4.5 * cm,
		bottomMargin=2 * cm
	)

	elements = []

	# Título principal
	style_title = ParagraphStyle("HeadingRes", fontName=FONT_BOLD, fontSize=12)
	elements.append(Paragraph("RESULTADOS DE ANÁLISES", style_title))
	elements.append(Spacer(1, 10))

	# Informações do paciente / meta
	style_left = ParagraphStyle("patient_left", fontName=FONT, fontSize=9, leading=12)
	style_right = ParagraphStyle("patient_right", fontName=FONT, fontSize=9, leading=12, alignment=TA_RIGHT)

	left_lines = [
		f"Nome de Paciente: {requisicao.paciente.nome}",
		f"Idade: {requisicao.paciente.idade()}",
		f"Gênero: {requisicao.paciente.genero or '—'}",
		f"Documento: {requisicao.paciente.numero_id or '—'}",
		f"Proveniência: {getattr(requisicao.paciente, 'proveniencia', '—')}"
	]

	analista = requisicao.analista
	if analista:
		nome_real = getattr(analista, 'get_full_name', lambda: '')()
		apelido = getattr(analista, 'apelido', '')
		tecnico_texto = f"{nome_real} ({apelido})" if apelido else nome_real
	else:
		tecnico_texto = "—"

	right_lines = [
		f"Ordem da Requisição: {requisicao.id_custom}",
		f"Data dos Resultados: {requisicao.created_at.strftime('%d/%m/%Y %H:%M')}",
		f"Técnico de Laboratório: {tecnico_texto or '—'}"
	]

	left_para = Paragraph("<br/>".join(left_lines), style_left)
	right_para = Paragraph("<br/>".join(right_lines), style_right)

	patient_table = Table([[left_para, right_para]], colWidths=[usable_width * 0.62, usable_width * 0.38], hAlign="LEFT")
	patient_table.setStyle(TableStyle([
		("VALIGN", (0, 0), (-1, -1), "TOP"),
		("FONTNAME", (0, 0), (-1, -1), FONT),
		("FONTSIZE", (0, 0), (-1, -1), 9),
		("LEFTPADDING", (0, 0), (-1, -1), 0),
		("RIGHTPADDING", (0, 0), (-1, -1), 0),
	]))
	elements.append(patient_table)
	elements.append(Spacer(1, 12))

	# Queryset de resultados (compatibilidade com diferentes nomes de relação)
	resultados_qs = getattr(requisicao, "resultados", None) or getattr(requisicao, "resultadoitem_set", None)
	if not resultados_qs:
		elements.append(Paragraph("Nenhum resultado disponível para esta requisição.", cell_style))
	else:
		qs = resultados_qs.select_related("exame_campo__exame")
		if apenas_validados:
			qs = qs.filter(validado=True)

		# Agrupa por exame (exame.nome)
		exames_agrupados = {}
		for r in qs:
			exame = r.exame_campo.exame
			exames_agrupados.setdefault(exame.nome, []).append(r)

		# Para cada exame, cria uma tabela com resultados
		for exame_nome, resultados in exames_agrupados.items():
			# Título do exame
			elements.append(Paragraph(exame_nome, bold_style))
			elements.append(Spacer(1, 6))

			# Cabeçalho da tabela de resultados (em negrito)
			data = [[
				_cell_paragraph(resultados[0].exame_campo.exame.metodo, bold=True),
				_cell_paragraph("Resultado", bold=True),
				_cell_paragraph("Unidade", bold=True),
				_cell_paragraph("Valor de Ref.", bold=True)
			]]

			# Linhas com resultados
			for r in resultados:
				valor = getattr(r, "resultado", None)
				if valor in (None, ""):
					for attr in ("valor_texto", "valor_numerico", "valor_percentagem", "valor_escolha"):
						v = getattr(r, attr, None)
						if v not in (None, ""):
							valor = v
							break

				data.append([
					_cell_paragraph(r.exame_campo.nome_campo),
					_cell_paragraph(f"{valor} {r.exame_campo.unidade}" if valor not in (None, "") else "-"),
					_cell_paragraph(r.exame_campo.unidade or "-"),
					_cell_paragraph(r.exame_campo.valor_referencia or "-"),
				])

			# Tabela de resultados
			table = Table(
				data,
				colWidths=[usable_width * 0.35, usable_width * 0.35, usable_width * 0.15, usable_width * 0.15],
				hAlign="LEFT"
			)
			table.setStyle(TableStyle([
				("FONTNAME", (0, 0), (-1, 0), FONT_BOLD),  # cabeçalho em negrito
				("ALIGN", (1, 1), (-1, -1), "LEFT"),
				("LEFTPADDING", (0, 0), (-1, -1), 2),
				("RIGHTPADDING", (0, 0), (-1, -1), 2),
			]))
			elements.append(table)
			elements.append(Spacer(1, 12))

	# Finaliza documento
	doc.build(
		elements,
		onFirstPage=lambda c, d: _on_page(c, d, analista),
		onLaterPages=lambda c, d: _on_page(c, d, analista),
		canvasmaker=NumberedCanvas
	)

	pdf = buffer.getvalue()
	buffer.close()
	filename = f"AnaBioLink_Resultados_{requisicao.id_custom}_{requisicao.paciente.nome}.pdf"
	return pdf, filename
