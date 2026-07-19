package com.example.ui.screens

import android.content.Context
import android.content.Intent
import android.net.Uri
import android.widget.Toast
import androidx.compose.animation.*
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.core.content.FileProvider
import com.example.data.model.MountingReport
import com.example.ui.viewmodel.BearingViewModel
import java.io.File

@Composable
fun ReportsScreen(viewModel: BearingViewModel) {
    val reports by viewModel.reportsList.collectAsState()
    val generatedPdf by viewModel.generatedPdfFile.collectAsState()

    var showCreateDialog by remember { mutableStateOf(false) }

    val context = LocalContext.current

    // Observe when a new PDF is generated, and open it
    LaunchedEffect(generatedPdf) {
        generatedPdf?.let { file ->
            Toast.makeText(context, "Reporte generado con éxito en PDF", Toast.LENGTH_LONG).show()
            openPdfFile(context, file)
            viewModel.generatedPdfFile.value = null // reset trigger
        }
    }

    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(MaterialTheme.colorScheme.background)
    ) {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Column {
                    Text(
                        text = "Historial de Reportes",
                        fontSize = 18.sp,
                        fontWeight = FontWeight.Black,
                        color = MaterialTheme.colorScheme.onBackground
                    )
                    Text(
                        text = "Reportes técnicos oficiales exportados",
                        fontSize = 11.sp,
                        color = Color.Gray
                    )
                }

                Button(
                    onClick = { showCreateDialog = true },
                    colors = ButtonDefaults.buttonColors(containerColor = MaterialTheme.colorScheme.primary)
                ) {
                    Icon(Icons.Default.Add, contentDescription = "Generar")
                    Spacer(modifier = Modifier.width(4.dp))
                    Text("Nuevo Reporte")
                }
            }

            // Reports history list
            LazyColumn(
                modifier = Modifier
                    .fillMaxWidth()
                    .weight(1f),
                verticalArrangement = Arrangement.spacedBy(10.dp)
            ) {
                if (reports.isEmpty()) {
                    item {
                        Column(
                            modifier = Modifier
                                .fillMaxWidth()
                                .padding(vertical = 48.dp),
                            horizontalAlignment = Alignment.CenterHorizontally,
                            verticalArrangement = Arrangement.spacedBy(8.dp)
                        ) {
                            Icon(
                                imageVector = Icons.Default.Description,
                                contentDescription = "No reports",
                                tint = Color.LightGray,
                                modifier = Modifier.size(48.dp)
                            )
                            Text(
                                text = "No hay reportes de montaje guardados.",
                                fontSize = 13.sp,
                                color = Color.Gray
                            )
                            Text(
                                text = "Presione 'Nuevo Reporte' para generar uno.",
                                fontSize = 11.sp,
                                color = Color.Gray
                            )
                        }
                    }
                } else {
                    items(reports) { report ->
                        ReportItemCard(
                            report = report,
                            onOpenClick = {
                                // Re-generate the PDF for this report item on click to open
                                val pdfFile = com.example.util.PdfGenerator.generateMountingReportPdf(context, report)
                                openPdfFile(context, pdfFile)
                            },
                            onDeleteClick = {
                                viewModel.deleteReport(report)
                                Toast.makeText(context, "Reporte eliminado", Toast.LENGTH_SHORT).show()
                            }
                        )
                    }
                }
            }
        }

        // Create Report Dialog Form
        if (showCreateDialog) {
            var client by remember { mutableStateOf("") }
            var machineTag by remember { mutableStateOf("") }
            var technician by remember { mutableStateOf("") }
            var notes by remember { mutableStateOf("") }

            AlertDialog(
                onDismissRequest = { showCreateDialog = false },
                title = { Text("Generar Reporte de Montaje", fontWeight = FontWeight.Bold, fontSize = 16.sp) },
                text = {
                    Column(
                        modifier = Modifier
                            .fillMaxWidth()
                            .wrapContentHeight(),
                        verticalArrangement = Arrangement.spacedBy(10.dp)
                    ) {
                        Text(
                            text = "Se incluirán las mediciones activas de la calculadora de calado radial.",
                            fontSize = 11.sp,
                            color = MaterialTheme.colorScheme.primary,
                            fontWeight = FontWeight.Bold
                        )
                        OutlinedTextField(
                            value = client,
                            onValueChange = { client = it },
                            label = { Text("Nombre del Cliente") },
                            placeholder = { Text("e.g. Minera Candelaria") },
                            modifier = Modifier.fillMaxWidth()
                        )
                        OutlinedTextField(
                            value = machineTag,
                            onValueChange = { machineTag = it },
                            label = { Text("Equipo / Tag de Máquina") },
                            placeholder = { Text("e.g. Molino SAG-01") },
                            modifier = Modifier.fillMaxWidth()
                        )
                        OutlinedTextField(
                            value = technician,
                            onValueChange = { technician = it },
                            label = { Text("Técnico Responsable") },
                            placeholder = { Text("e.g. Ing. Juan Pérez") },
                            modifier = Modifier.fillMaxWidth()
                        )
                        OutlinedTextField(
                            value = notes,
                            onValueChange = { notes = it },
                            label = { Text("Notas / Observaciones de Montaje") },
                            placeholder = { Text("Opcional: detalles del proceso") },
                            modifier = Modifier.fillMaxWidth(),
                            maxLines = 3
                        )
                    }
                },
                confirmButton = {
                    Button(
                        onClick = {
                            viewModel.createReport(client, machineTag, technician, notes)
                            showCreateDialog = false
                        }
                    ) {
                        Text("Generar PDF")
                    }
                },
                dismissButton = {
                    TextButton(onClick = { showCreateDialog = false }) {
                        Text("Cancelar")
                    }
                }
            )
        }
    }
}

@Composable
fun ReportItemCard(
    report: MountingReport,
    onOpenClick: () -> Unit,
    onDeleteClick: () -> Unit
) {
    val isApproved = report.status == "Aprobado"
    
    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(16.dp),
        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface),
        border = androidx.compose.foundation.BorderStroke(1.dp, MaterialTheme.colorScheme.outline.copy(alpha = 0.5f)),
        elevation = CardDefaults.cardElevation(defaultElevation = 1.dp)
    ) {
        Column(modifier = Modifier.padding(14.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Column {
                    Text(
                        text = report.bearingDesignation,
                        fontWeight = FontWeight.Black,
                        fontSize = 15.sp,
                        color = MaterialTheme.colorScheme.onSurface
                    )
                    Text(
                        text = "${report.clientName} • ${report.machineTag}",
                        fontSize = 11.sp,
                        color = Color.Gray
                    )
                }

                Surface(
                    color = if (isApproved) Color(0xFFDCFCE7) else Color(0xFFFEE2E2),
                    shape = RoundedCornerShape(6.dp)
                ) {
                    Text(
                        text = report.status,
                        color = if (isApproved) Color(0xFF15803D) else Color(0xFFB91C1C),
                        fontSize = 10.sp,
                        fontWeight = FontWeight.Bold,
                        modifier = Modifier.padding(horizontal = 6.dp, vertical = 3.dp)
                    )
                }
            }

            HorizontalDivider(color = Color(0xFFF1F5F9))

            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Column {
                    Text(
                        text = "Técnico: ${report.technicianName}",
                        fontSize = 11.sp,
                        color = Color.Gray
                    )
                    Text(
                        text = "Fecha: ${report.date}",
                        fontSize = 10.sp,
                        color = Color.LightGray
                    )
                }

                Row(horizontalArrangement = Arrangement.spacedBy(4.dp)) {
                    IconButton(onClick = onDeleteClick) {
                        Icon(Icons.Default.DeleteOutline, contentDescription = "Eliminar", tint = Color.Gray)
                    }
                    Button(
                        onClick = onOpenClick,
                        colors = ButtonDefaults.buttonColors(containerColor = MaterialTheme.colorScheme.secondary)
                    ) {
                        Icon(Icons.Default.OpenInNew, contentDescription = "Abrir")
                        Spacer(modifier = Modifier.width(4.dp))
                        Text("Ver PDF", fontSize = 11.sp)
                    }
                }
            }
        }
    }
}

// Share/View File Intent launch system
private fun openPdfFile(context: Context, file: File) {
    try {
        val authority = "${context.packageName}.fileprovider"
        val uri = FileProvider.getUriForFile(context, authority, file)
        
        val intent = Intent(Intent.ACTION_VIEW).apply {
            setDataAndType(uri, "application/pdf")
            flags = Intent.FLAG_GRANT_READ_URI_PERMISSION or Intent.FLAG_ACTIVITY_CLEAR_TOP
        }
        context.startActivity(Intent.createChooser(intent, "Abrir reporte técnico de montaje"))
    } catch (e: Exception) {
        Toast.makeText(context, "No se encontró un visor de PDF compatible. El archivo se guardó.", Toast.LENGTH_LONG).show()
    }
}
