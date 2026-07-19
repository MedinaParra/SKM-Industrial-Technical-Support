package com.example.util

import android.content.Context
import android.graphics.Canvas
import android.graphics.Color
import android.graphics.Paint
import android.graphics.Typeface
import android.graphics.pdf.PdfDocument
import com.example.data.model.MountingReport
import java.io.File
import java.io.FileOutputStream

object PdfGenerator {

    fun generateMountingReportPdf(context: Context, report: MountingReport): File {
        val pdfDocument = PdfDocument()
        
        // Page specification (Letter size: 612 x 792 points)
        val pageInfo = PdfDocument.PageInfo.Builder(612, 792, 1).create()
        val page = pdfDocument.startPage(pageInfo)
        val canvas: Canvas = page.canvas

        // Paints for drawing
        val titlePaint = Paint().apply {
            color = Color.parseColor("#1E3A8A") // SKM Navy Blue
            textSize = 22f
            typeface = Typeface.create(Typeface.DEFAULT, Typeface.BOLD)
        }

        val subtitlePaint = Paint().apply {
            color = Color.parseColor("#475569") // Gray
            textSize = 10f
            typeface = Typeface.create(Typeface.DEFAULT, Typeface.ITALIC)
        }

        val headerPaint = Paint().apply {
            color = Color.parseColor("#0F172A") // Slate Dark
            textSize = 14f
            typeface = Typeface.create(Typeface.DEFAULT, Typeface.BOLD)
        }

        val bodyPaint = Paint().apply {
            color = Color.parseColor("#334155")
            textSize = 11f
            typeface = Typeface.create(Typeface.DEFAULT, Typeface.NORMAL)
        }

        val boldBodyPaint = Paint().apply {
            color = Color.parseColor("#0F172A")
            textSize = 11f
            typeface = Typeface.create(Typeface.DEFAULT, Typeface.BOLD)
        }

        val valuePaint = Paint().apply {
            color = Color.parseColor("#1E40AF") // Accent Blue
            textSize = 11f
            typeface = Typeface.create(Typeface.DEFAULT, Typeface.BOLD)
        }

        val footerPaint = Paint().apply {
            color = Color.parseColor("#64748B")
            textSize = 9f
            typeface = Typeface.create(Typeface.DEFAULT, Typeface.NORMAL)
        }

        val borderPaint = Paint().apply {
            color = Color.parseColor("#CBD5E1") // Light gray border
            style = Paint.Style.STROKE
            strokeWidth = 1f
        }

        val dividerPaint = Paint().apply {
            color = Color.parseColor("#94A3B8")
            style = Paint.Style.STROKE
            strokeWidth = 1.5f
        }

        val successBoxPaint = Paint().apply {
            color = Color.parseColor("#DCFCE7") // Light Green
            style = Paint.Style.FILL
        }

        val successBorderPaint = Paint().apply {
            color = Color.parseColor("#16A34A") // Green
            style = Paint.Style.STROKE
            strokeWidth = 1.5f
        }

        val warningBoxPaint = Paint().apply {
            color = Color.parseColor("#FEE2E2") // Light Red
            style = Paint.Style.FILL
        }

        val warningBorderPaint = Paint().apply {
            color = Color.parseColor("#DC2626") // Red
            style = Paint.Style.STROKE
            strokeWidth = 1.5f
        }

        // Draw Header Border
        canvas.drawRect(30f, 30f, 582f, 762f, borderPaint)

        // Title and Logo Area
        canvas.drawText("SKM INDUSTRIAL", 45f, 65f, titlePaint)
        canvas.drawText("REPORTE TÉCNICO: MONTAJE DE RODAMIENTO", 45f, 85f, headerPaint)
        canvas.drawText("Sistemas de Transmisión de Potencia y Montajes Críticos", 45f, 100f, subtitlePaint)

        // Draw top thick divider
        canvas.drawLine(45f, 110f, 567f, 110f, dividerPaint)

        // General Information Section
        var y = 135f
        canvas.drawText("INFORMACIÓN GENERAL", 45f, y, headerPaint)
        canvas.drawLine(45f, y + 5, 220f, y + 5, borderPaint)

        y += 25f
        canvas.drawText("Cliente:", 45f, y, bodyPaint)
        canvas.drawText(report.clientName, 150f, y, boldBodyPaint)
        canvas.drawText("Fecha:", 340f, y, bodyPaint)
        canvas.drawText(report.date, 440f, y, boldBodyPaint)

        y += 20f
        canvas.drawText("Equipo / Tag:", 45f, y, bodyPaint)
        canvas.drawText(report.machineTag, 150f, y, boldBodyPaint)
        canvas.drawText("Técnico:", 340f, y, bodyPaint)
        canvas.drawText(report.technicianName, 440f, y, boldBodyPaint)

        // Bearing Specifications Section
        y += 35f
        canvas.drawText("ESPECIFICACIONES DEL RODAMIENTO", 45f, y, headerPaint)
        canvas.drawLine(45f, y + 5, 300f, y + 5, borderPaint)

        y += 25f
        canvas.drawText("Designación:", 45f, y, bodyPaint)
        canvas.drawText(report.bearingDesignation, 150f, y, boldBodyPaint)
        canvas.drawText("Marca:", 340f, y, bodyPaint)
        canvas.drawText(report.brand, 440f, y, boldBodyPaint)

        y += 20f
        canvas.drawText("Manguito de Fijación:", 45f, y, bodyPaint)
        canvas.drawText(report.sleeveType, 150f, y, boldBodyPaint)

        // Clearance and Mounting Specs
        y += 40f
        canvas.drawText("MEDICIONES Y TOLERANCIAS", 45f, y, headerPaint)
        canvas.drawLine(45f, y + 5, 230f, y + 5, dividerPaint)

        // Table background for values
        y += 15f
        canvas.drawRect(45f, y, 567f, y + 160f, borderPaint)
        
        // Horizontal lines inside table
        for (i in 1..4) {
            canvas.drawLine(45f, y + (i * 32f), 567f, y + (i * 32f), borderPaint)
        }
        // Vertical lines inside table
        canvas.drawLine(280f, y, 280f, y + 160f, borderPaint)

        val tableYStart = y
        // Table Content
        val rowHeight = 32f
        var rowY = tableYStart + 20f

        // Row 1: Initial Radial Clearance
        canvas.drawText("Juego Radial Inicial (Antes de Montar)", 55f, rowY, bodyPaint)
        canvas.drawText("${report.initialClearanceMm} mm", 290f, rowY, valuePaint)

        // Row 2: Target Reduction
        rowY += rowHeight
        canvas.drawText("Reducción de Juego Requerida (Manual)", 55f, rowY, bodyPaint)
        canvas.drawText("${report.targetReductionMinMm} - ${report.targetReductionMaxMm} mm", 290f, rowY, valuePaint)

        // Row 3: Final Measured Clearance
        rowY += rowHeight
        canvas.drawText("Juego Radial Final Medido", 55f, rowY, bodyPaint)
        canvas.drawText("${report.finalClearanceMm} mm", 290f, rowY, valuePaint)

        // Row 4: Actual Reduction Achieved
        rowY += rowHeight
        canvas.drawText("Reducción Real Lograda", 55f, rowY, bodyPaint)
        val diffPaint = Paint(valuePaint).apply {
            color = if (report.clearanceReductionMm >= report.targetReductionMinMm && 
                        report.clearanceReductionMm <= report.targetReductionMaxMm) {
                Color.parseColor("#16A34A") // Green
            } else {
                Color.parseColor("#DC2626") // Red
            }
        }
        canvas.drawText("${report.clearanceReductionMm} mm", 290f, rowY, diffPaint)

        // Row 5: Drive-Up and Tightening Angle
        rowY += rowHeight
        canvas.drawText("Calado Axial Recomendado / Ángulo", 55f, rowY, bodyPaint)
        canvas.drawText("${report.axialDriveUpMm} mm / ${report.lockNutAngleDegrees}°", 290f, rowY, valuePaint)

        // Status Card
        y += 185f
        val statusText = "ESTADO DEL MONTAJE: ${report.status.uppercase()}"
        if (report.status == "Aprobado") {
            canvas.drawRect(45f, y, 567f, y + 35f, successBoxPaint)
            canvas.drawRect(45f, y, 567f, y + 35f, successBorderPaint)
            
            val approvedTextPaint = Paint().apply {
                color = Color.parseColor("#15803D")
                textSize = 12f
                typeface = Typeface.create(Typeface.DEFAULT, Typeface.BOLD)
            }
            canvas.drawText(statusText, 60f, y + 22f, approvedTextPaint)
        } else {
            canvas.drawRect(45f, y, 567f, y + 35f, warningBoxPaint)
            canvas.drawRect(45f, y, 567f, y + 35f, warningBorderPaint)
            
            val failedTextPaint = Paint().apply {
                color = Color.parseColor("#B91C1C")
                textSize = 12f
                typeface = Typeface.create(Typeface.DEFAULT, Typeface.BOLD)
            }
            canvas.drawText(statusText, 60f, y + 22f, failedTextPaint)
        }

        // Notes Section
        y += 60f
        canvas.drawText("NOTAS / OBSERVACIONES TÉCNICAS", 45f, y, headerPaint)
        canvas.drawLine(45f, y + 5, 270f, y + 5, borderPaint)

        y += 20f
        val noteLines = report.notes.chunked(70)
        for (line in noteLines) {
            canvas.drawText(line, 45f, y, bodyPaint)
            y += 18f
        }

        // Signature Blocks at the bottom
        y = 690f
        canvas.drawLine(45f, y, 220f, y, borderPaint)
        canvas.drawText("Firma del Técnico", 75f, y + 15f, bodyPaint)
        canvas.drawText(report.technicianName, 65f, y + 30f, subtitlePaint)

        canvas.drawLine(390f, y, 565f, y, borderPaint)
        canvas.drawText("Aprobación SKM Supervisión", 400f, y + 15f, bodyPaint)

        // Footer
        canvas.drawText("SKM Industrial - Manual SKF de Montaje de Rodamientos 2026. Generado en Modo Offline.", 110f, 750f, footerPaint)

        pdfDocument.finishPage(page)

        // Save PDF to Context File
        val pdfDir = File(context.cacheDir, "reports")
        if (!pdfDir.exists()) {
            pdfDir.mkdirs()
        }
        val file = File(pdfDir, "SKM_Reporte_Montaje_${System.currentTimeMillis()}.pdf")
        val fileOutputStream = FileOutputStream(file)
        pdfDocument.writeTo(fileOutputStream)
        pdfDocument.close()
        fileOutputStream.close()

        return file
    }
}
