import io
from datetime import datetime
from django.http import FileResponse
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet


def gerar_pdf_requisicao(requisicao):
	buffer = io.BytesIO()
	pdf = canvas.Canvas(buffer, pagesize=A4)
	width, height = A4

	pdf.setTitle(f"Requisição {requisicao.id} - {requisicao.paciente.nome}")

	# Cabeçalho
	pdf.setFont("Helvetica-Bold", 14)
	pdf.drawString(2 * cm, 28 * cm, "SYS-LAB - Requisição de Análises")
	pdf.setFont("Helvetica", 10)
	pdf.drawString(2 * cm, 27.3 * cm, f"Data: {requisicao.data_solicitacao.strftime('%d/%m/%Y %H:%M')}")
	pdf.line(2 * cm, 27 * cm, 19 * cm, 27 * cm)

	# Dados do Paciente
	pdf.setFont("Helvetica-Bold", 11)
	pdf.drawString(2 * cm, 26 * cm, "Dados do Paciente:")
	pdf.setFont("Helvetica", 10)
	pdf.drawString(2 * cm, 25.5 * cm, f"Nome: {requisicao.paciente.nome}")
	pdf.drawString(2 * cm, 25.0 * cm, f"Proveniência: {requisicao.paciente.proveniencia}")
	pdf.drawString(2 * cm, 24.5 * cm, f"Número de Identificação: {requisicao.paciente.numero_identificacao}")

	# Exames solicitados
	pdf.setFont("Helvetica-Bold", 11)
	pdf.drawString(2 * cm, 23.5 * cm, "Exames Solicitados:")

	y = 23.0 * cm
	for item in requisicao.itemrequisicao_set.all():
		pdf.setFont("Helvetica", 10)
		pdf.drawString(2.3 * cm, y, f"- {item.exame.nome}")
		y -= 0.5 * cm

	if not requisicao.itemrequisicao_set.exists():
		pdf.drawString(2.3 * cm, y, "Nenhum exame registrado.")

	# Rodapé
	pdf.setFont("Helvetica-Oblique", 8)
	pdf.drawString(2 * cm, 2 * cm, f"Gerado em {datetime.now().strftime('%d/%m/%Y %H:%M')} por SYS-LAB")

	pdf.showPage()
	pdf.save()

	buffer.seek(0)
	return FileResponse(buffer, as_attachment=True, filename=f"requisicao_{requisicao.id}.pdf")

def gerar_pdf_resultados(requisicao):
	buffer = io.BytesIO()
	pdf = canvas.Canvas(buffer, pagesize=A4)
	width, height = A4
	styles = getSampleStyleSheet()

	pdf.setTitle(f"Resultados - {requisicao.paciente.nome}")

	# Cabeçalho
	pdf.setFont("Helvetica-Bold", 14)
	pdf.drawString(2 * cm, 28 * cm, "SYS-LAB - Resultados de Análises")
	pdf.setFont("Helvetica", 10)
	pdf.drawString(2 * cm, 27.3 * cm, f"Data de Validação: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
	pdf.line(2 * cm, 27 * cm, 19 * cm, 27 * cm)

	# Dados do Paciente
	pdf.setFont("Helvetica-Bold", 11)
	pdf.drawString(2 * cm, 26 * cm, "Dados do Paciente:")
	pdf.setFont("Helvetica", 10)
	pdf.drawString(2 * cm, 25.5 * cm, f"Nome: {requisicao.paciente.nome}")
	pdf.drawString(2 * cm, 25.0 * cm, f"Proveniência: {requisicao.paciente.proveniencia}")
	pdf.drawString(2 * cm, 24.5 * cm, f"Número de Identificação: {requisicao.paciente.numero_identificacao}")

	# Tabela de Resultados
	data = [["Exame", "Resultado", "Unidade", "Referência", "Analista", "Validação"]]

	for r in requisicao.resultados.all():
		data.append([
			r.exame.nome,
			r.valor if r.valor else "-",
			r.unidade or "-",
			r.valor_referencia or "-",
			r.validado_por.username if r.validado_por else "-",
			r.data_validacao.strftime('%d/%m/%Y %H:%M') if r.data_validacao else "-"
		])

	table = Table(data, colWidths=[5 * cm, 2.5 * cm, 2 * cm, 2.5 * cm, 3 * cm, 3 * cm])
	table.setStyle(TableStyle([
		('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
		('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
		('FONT', (0, 0), (-1, 0), 'Helvetica-Bold'),
		('FONT', (0, 1), (-1, -1), 'Helvetica'),
		('FONTSIZE', (0, 0), (-1, -1), 9),
	]))

	w, h = table.wrapOn(pdf, width, height)
	table.drawOn(pdf, 2 * cm, 20 * cm - h)

	# Rodapé
	pdf.setFont("Helvetica-Oblique", 8)
	pdf.drawString(2 * cm, 2 * cm, f"Gerado por SYS-LAB em {datetime.now().strftime('%d/%m/%Y %H:%M')}")

	pdf.showPage()
	pdf.save()

	buffer.seek(0)
	return FileResponse(buffer, as_attachment=True, filename=f"resultados_{requisicao.id}.pdf")
