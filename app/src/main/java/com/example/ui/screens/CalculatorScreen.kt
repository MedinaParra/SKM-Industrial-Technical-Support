package com.example.ui.screens

import androidx.compose.animation.*
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.LazyRow
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.geometry.Size
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.StrokeCap
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.ui.viewmodel.BearingViewModel

@Composable
fun CalculatorScreen(
    viewModel: BearingViewModel,
    onNavigateToTab: (Int) -> Unit
) {
    var selectedCalcTab by remember { mutableStateOf(0) } // 0 = Calado, 1 = Ajustes, 2 = Lubricación

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(MaterialTheme.colorScheme.background)
    ) {
        // Tab selector
        TabRow(selectedTabIndex = selectedCalcTab) {
            Tab(
                selected = selectedCalcTab == 0,
                onClick = { selectedCalcTab = 0 },
                text = { Text("Juego & Calado", fontWeight = FontWeight.Bold, fontSize = 12.sp) },
                icon = { Icon(Icons.Default.CompassCalibration, contentDescription = "Calado") }
            )
            Tab(
                selected = selectedCalcTab == 1,
                onClick = { selectedCalcTab = 1 },
                text = { Text("Ajustes Eje", fontWeight = FontWeight.Bold, fontSize = 12.sp) },
                icon = { Icon(Icons.Default.LineWeight, contentDescription = "Ajustes") }
            )
            Tab(
                selected = selectedCalcTab == 2,
                onClick = { selectedCalcTab = 2 },
                text = { Text("Lubricación", fontWeight = FontWeight.Bold, fontSize = 12.sp) },
                icon = { Icon(Icons.Default.Opacity, contentDescription = "Lubricación") }
            )
        }

        when (selectedCalcTab) {
            0 -> CaladoCalculatorTab(viewModel, onNavigateToTab)
            1 -> FitsCalculatorTab(viewModel)
            2 -> LubricationCalculatorTab(viewModel)
        }
    }
}

@Composable
fun CaladoCalculatorTab(
    viewModel: BearingViewModel,
    onNavigateToTab: (Int) -> Unit
) {
    val selectedBearing by viewModel.selectedBearing.collectAsState()
    val calcNominalBore by viewModel.calcNominalBore.collectAsState()
    val calcSleeveType by viewModel.calcSleeveType.collectAsState()
    val calcInitialClearance by viewModel.calcInitialClearance.collectAsState()
    val calcFinalClearance by viewModel.calcFinalClearance.collectAsState()

    // Calculated fields
    val bore = calcNominalBore.toDoubleOrNull() ?: 75.0
    val initial = calcInitialClearance.toDoubleOrNull() ?: 0.060
    val final = calcFinalClearance.toDoubleOrNull() ?: 0.025

    val actualReduction = initial - final

    // Fetch recommendations based on whether a real bearing is selected
    val recRedMin = selectedBearing?.recommendedReductionMin ?: viewModel.calculateEstimatedReductionMin(bore)
    val recRedMax = selectedBearing?.recommendedReductionMax ?: viewModel.calculateEstimatedReductionMax(bore)
    val driveUp = selectedBearing?.axialDriveUp1To12Min ?: viewModel.calculateEstimatedAxialDriveUp(bore)
    val lockAngle = selectedBearing?.minLockingAngleDegrees ?: viewModel.calculateEstimatedLockNutAngle(bore)

    val isApproved = actualReduction in recRedMin..recRedMax

    LazyColumn(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        // Warning/Banner
        item {
            Card(
                colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.primaryContainer.copy(alpha = 0.2f))
            ) {
                Row(
                    modifier = Modifier.padding(12.dp),
                    horizontalArrangement = Arrangement.spacedBy(8.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Icon(Icons.Default.Info, contentDescription = "Instrucciones", tint = MaterialTheme.colorScheme.primary)
                    Text(
                        text = "Ingrese dimensiones manuales o seleccione un rodamiento del Catálogo para pre-cargar especificaciones oficiales SKF.",
                        fontSize = 11.sp,
                        color = MaterialTheme.colorScheme.onPrimaryContainer
                    )
                }
            }
        }

        // Selected Bearing info
        item {
            selectedBearing?.let { bearing ->
                Card(
                    colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.primaryContainer),
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Row(
                        modifier = Modifier
                            .padding(12.dp)
                            .fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Column {
                            Text("Rodamiento Activo:", fontSize = 11.sp, fontWeight = FontWeight.Bold)
                            Text("${bearing.designation} (${bearing.brand})", fontSize = 14.sp, fontWeight = FontWeight.Black)
                        }
                        OutlinedButton(
                            onClick = { viewModel.selectedBearing.value = null },
                            colors = ButtonDefaults.outlinedButtonColors(contentColor = MaterialTheme.colorScheme.onPrimaryContainer)
                        ) {
                            Text("Liberar", fontSize = 11.sp)
                        }
                    }
                }
            }
        }

        // Inputs Section
        item {
            Card(
                colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface),
                modifier = Modifier.fillMaxWidth()
            ) {
                Column(modifier = Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(12.dp)) {
                    Text("Parámetros de Medición", fontSize = 14.sp, fontWeight = FontWeight.Bold)

                    if (selectedBearing == null) {
                        TextField(
                            value = calcNominalBore,
                            onValueChange = { viewModel.calcNominalBore.value = it },
                            label = { Text("Diámetro Nominal de Eje (d - mm)") },
                            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
                            modifier = Modifier.fillMaxWidth()
                        )
                    }

                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.spacedBy(12.dp)
                    ) {
                        TextField(
                            value = calcInitialClearance,
                            onValueChange = { viewModel.calcInitialClearance.value = it },
                            label = { Text("Juego Inicial (mm)") },
                            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
                            modifier = Modifier.weight(1f)
                        )
                        TextField(
                            value = calcFinalClearance,
                            onValueChange = { viewModel.calcFinalClearance.value = it },
                            label = { Text("Juego Final (mm)") },
                            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
                            modifier = Modifier.weight(1f)
                        )
                    }
                }
            }
        }

        // Results Section (Interactive Gauge + Text)
        item {
            Card(
                colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface),
                modifier = Modifier.fillMaxWidth()
            ) {
                Column(
                    modifier = Modifier.padding(16.dp),
                    horizontalAlignment = Alignment.CenterHorizontally,
                    verticalArrangement = Arrangement.spacedBy(12.dp)
                ) {
                    Text(
                        text = "Análisis de Calado SKF",
                        fontSize = 14.sp,
                        fontWeight = FontWeight.Bold,
                        modifier = Modifier.fillMaxWidth()
                    )

                    // Interactive gauge drawn in Canvas representing actual clearance reduction
                    Box(
                        modifier = Modifier
                            .size(150.dp)
                            .background(Color.Transparent),
                        contentAlignment = Alignment.Center
                    ) {
                        Canvas(modifier = Modifier.fillMaxSize()) {
                            val w = size.width
                            val h = size.height
                            val center = Offset(w / 2, h / 2)
                            val radius = w / 2 - 12f

                            // Draw arc background (180 degrees sweep from left to right)
                            drawArc(
                                color = Color(0xFFE2E8F0),
                                startAngle = 180f,
                                sweepAngle = 180f,
                                useCenter = false,
                                style = Stroke(width = 16f, cap = StrokeCap.Round)
                            )

                            // Target Arc (Green zone representing acceptable reduction range)
                            val totalSpan = 180f
                            val maxReductionValue = recRedMax * 2.0 // gauge scale max
                            
                            val startAngle = 180f + ((recRedMin / maxReductionValue) * totalSpan).toFloat()
                            val sweepAngle = (((recRedMax - recRedMin) / maxReductionValue) * totalSpan).toFloat()

                            drawArc(
                                color = Color(0x6016A34A),
                                startAngle = startAngle,
                                sweepAngle = sweepAngle,
                                useCenter = false,
                                style = Stroke(width = 16f, cap = StrokeCap.Round)
                            )

                            // Actual Needle pointing to achieved reduction
                            val needlePercent = (actualReduction / maxReductionValue).coerceIn(0.0, 1.0)
                            val needleAngle = 180f + (needlePercent * totalSpan).toFloat()
                            val needleRad = Math.toRadians(needleAngle.toDouble())
                            val endX = center.x + (radius - 10) * Math.cos(needleRad).toFloat()
                            val endY = center.y + (radius - 10) * Math.sin(needleRad).toFloat()

                            // Draw needle pin
                            drawCircle(color = Color(0xFF1E293B), radius = 10f, center = center)
                            drawLine(
                                color = if (isApproved) Color(0xFF16A34A) else Color(0xFFDC2626),
                                start = center,
                                end = Offset(endX, endY),
                                strokeWidth = 5f,
                                cap = StrokeCap.Round
                            )
                        }

                        Column(
                            modifier = Modifier.padding(top = 40.dp),
                            horizontalAlignment = Alignment.CenterHorizontally
                        ) {
                            Text(
                                text = String.format("%.3f mm", actualReduction),
                                fontSize = 18.sp,
                                fontWeight = FontWeight.Black,
                                color = if (isApproved) Color(0xFF15803D) else Color(0xFFB91C1C)
                            )
                            Text(
                                text = "Reducción Real",
                                fontSize = 10.sp,
                                color = Color.Gray,
                                fontWeight = FontWeight.Bold
                            )
                        }
                    }

                    // Approved / Rejected Banner
                    Surface(
                        color = if (isApproved) Color(0xFFDCFCE7) else Color(0xFFFEE2E2),
                        shape = RoundedCornerShape(8.dp),
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        Text(
                            text = if (isApproved) "MONTAJE CONFORME (Dentro de límites SKF)" else "FUERA DE TOLERANCIA (Verifique el calado)",
                            color = if (isApproved) Color(0xFF15803D) else Color(0xFFB91C1C),
                            fontSize = 11.sp,
                            fontWeight = FontWeight.Bold,
                            textAlign = TextAlign.Center,
                            modifier = Modifier.padding(8.dp)
                        )
                    }

                    // Comparative text fields
                    Column(
                        modifier = Modifier.fillMaxWidth(),
                        verticalArrangement = Arrangement.spacedBy(6.dp)
                    ) {
                        ParamRow(
                            label = "Reducción Requerida (SKF):",
                            valStr = String.format("%.3f - %.3f mm", recRedMin, recRedMax)
                        )
                        ParamRow(
                            label = "Calado Axial Mínimo (s):",
                            valStr = String.format("%.3f mm", driveUp)
                        )
                        ParamRow(
                            label = "Ángulo de Apriete Tuerca:",
                            valStr = String.format("%.0f° aprox.", lockAngle)
                        )
                    }

                    Spacer(modifier = Modifier.height(8.dp))

                    // Build technical PDF report button
                    Button(
                        onClick = { onNavigateToTab(3) }, // Go to Reports tab to generate PDF!
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        Icon(Icons.Default.PictureAsPdf, contentDescription = "PDF")
                        Spacer(modifier = Modifier.width(8.dp))
                        Text("Exportar Reporte a PDF")
                    }
                }
            }
        }
    }
}

@Composable
fun FitsCalculatorTab(viewModel: BearingViewModel) {
    val tolNominalSize by viewModel.tolNominalSize.collectAsState()
    val tolFitType by viewModel.tolFitType.collectAsState()

    val fitResult = viewModel.calculateFitTolerances()

    LazyColumn(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        item {
            Card(
                colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface)
            ) {
                Column(modifier = Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(12.dp)) {
                    Text("Ajustes de Eje y Alojamiento (ISO)", fontSize = 14.sp, fontWeight = FontWeight.Bold)

                    TextField(
                        value = tolNominalSize,
                        onValueChange = { viewModel.tolNominalSize.value = it },
                        label = { Text("Diámetro Nominal (mm)") },
                        keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
                        modifier = Modifier.fillMaxWidth()
                    )

                    Text("Clasificación de Ajuste (Técnico)", fontSize = 12.sp, fontWeight = FontWeight.Bold)
                    val fitTypes = listOf(
                        "Eje m5 (Carga Pesada/Rotativo)",
                        "Eje k6 (Carga Normal)",
                        "Eje g6 (Desplazamiento Fácil)",
                        "Alojamiento H7 (Estándar)",
                        "Alojamiento J7"
                    )
                    
                    Column(verticalArrangement = Arrangement.spacedBy(4.dp)) {
                        fitTypes.forEach { type ->
                            val isSelected = tolFitType == type
                            Surface(
                                color = if (isSelected) MaterialTheme.colorScheme.primaryContainer else Color(0xFFF1F5F9),
                                shape = RoundedCornerShape(8.dp),
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .clickable { viewModel.tolFitType.value = type }
                            ) {
                                Row(
                                    modifier = Modifier.padding(10.dp),
                                    verticalAlignment = Alignment.CenterVertically
                                ) {
                                    RadioButton(selected = isSelected, onClick = { viewModel.tolFitType.value = type })
                                    Spacer(modifier = Modifier.width(8.dp))
                                    Text(type, fontSize = 12.sp, fontWeight = FontWeight.Medium)
                                }
                            }
                        }
                    }
                }
            }
        }

        // Tolerance results
        item {
            Card(
                colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface),
                modifier = Modifier.fillMaxWidth()
            ) {
                Column(modifier = Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(10.dp)) {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Icon(Icons.Default.OfflineBolt, contentDescription = "Fit Result", tint = MaterialTheme.colorScheme.primary)
                        Spacer(modifier = Modifier.width(8.dp))
                        Text("Ajuste ISO: ${fitResult.fitClass}", fontSize = 15.sp, fontWeight = FontWeight.Bold)
                    }

                    Text(
                        text = fitResult.description,
                        fontSize = 12.sp,
                        color = Color.Gray
                    )

                    HorizontalDivider()

                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.spacedBy(16.dp)
                    ) {
                        Column(modifier = Modifier.weight(1f)) {
                            Text("Desviación Superior", fontSize = 11.sp, color = Color.Gray)
                            Text("+${fitResult.upperDevMicrons} µm", fontSize = 16.sp, fontWeight = FontWeight.Black, color = MaterialTheme.colorScheme.primary)
                        }
                        Column(modifier = Modifier.weight(1f)) {
                            Text("Desviación Inferior", fontSize = 11.sp, color = Color.Gray)
                            Text(
                                text = if (fitResult.lowerDevMicrons >= 0) "+${fitResult.lowerDevMicrons} µm" else "${fitResult.lowerDevMicrons} µm",
                                fontSize = 16.sp,
                                fontWeight = FontWeight.Black,
                                color = MaterialTheme.colorScheme.secondary
                            )
                        }
                    }

                    HorizontalDivider()

                    Column(verticalArrangement = Arrangement.spacedBy(4.dp)) {
                        Text("Recomendación de Lubricación:", fontSize = 11.sp, color = Color.Gray, fontWeight = FontWeight.Bold)
                        Text(fitResult.recommendedLube, fontSize = 12.sp, color = MaterialTheme.colorScheme.onSurface, fontWeight = FontWeight.Medium)
                    }
                }
            }
        }
    }
}

@Composable
fun LubricationCalculatorTab(viewModel: BearingViewModel) {
    val relubBearingType by viewModel.relubBearingType.collectAsState()
    val relubRpm by viewModel.relubRpm.collectAsState()
    val relubTemp by viewModel.relubTemp.collectAsState()
    val relubBore by viewModel.relubBore.collectAsState()

    val relubResult = viewModel.calculateRelubrication()

    LazyColumn(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        item {
            Card(
                colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface)
            ) {
                Column(modifier = Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(12.dp)) {
                    Text("Calculadora de Intervalo de Grasa", fontSize = 14.sp, fontWeight = FontWeight.Bold)

                    TextField(
                        value = relubBore,
                        onValueChange = { viewModel.relubBore.value = it },
                        label = { Text("Diámetro del Eje (d - mm)") },
                        keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
                        modifier = Modifier.fillMaxWidth()
                    )

                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.spacedBy(12.dp)
                    ) {
                        TextField(
                            value = relubRpm,
                            onValueChange = { viewModel.relubRpm.value = it },
                            label = { Text("Velocidad (RPM)") },
                            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
                            modifier = Modifier.weight(1f)
                        )
                        TextField(
                            value = relubTemp,
                            onValueChange = { viewModel.relubTemp.value = it },
                            label = { Text("Temperatura (°C)") },
                            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
                            modifier = Modifier.weight(1f)
                        )
                    }

                    Text("Tipo de Rodamiento", fontSize = 12.sp, fontWeight = FontWeight.Bold)
                    val bearingTypes = listOf("Rodillos Oscilantes", "Bolas de Ranura Profunda", "Rodillos Cilíndricos")
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        bearingTypes.forEach { type ->
                            val isSelected = relubBearingType == type
                            Surface(
                                color = if (isSelected) MaterialTheme.colorScheme.primaryContainer else Color(0xFFF1F5F9),
                                shape = RoundedCornerShape(8.dp),
                                modifier = Modifier
                                    .weight(1f)
                                    .clickable { viewModel.relubBearingType.value = type }
                            ) {
                                Text(
                                    text = type,
                                    fontSize = 10.sp,
                                    fontWeight = FontWeight.Bold,
                                    textAlign = TextAlign.Center,
                                    modifier = Modifier.padding(horizontal = 4.dp, vertical = 8.dp)
                                )
                            }
                        }
                    }
                }
            }
        }

        // Relubrication quantity and hours results card
        item {
            Card(
                colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface),
                modifier = Modifier.fillMaxWidth()
            ) {
                Column(modifier = Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(12.dp)) {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Icon(Icons.Default.OilBarrel, contentDescription = "Grasa", tint = MaterialTheme.colorScheme.primary)
                        Spacer(modifier = Modifier.width(8.dp))
                        Text("Intervalos de Lubricación", fontSize = 14.sp, fontWeight = FontWeight.Bold)
                    }

                    HorizontalDivider()

                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.spacedBy(16.dp)
                    ) {
                        Column(modifier = Modifier.weight(1f)) {
                            Text("Cantidad de Grasa (Gp)", fontSize = 11.sp, color = Color.Gray)
                            Text("${relubResult.quantityGrams} gramos", fontSize = 16.sp, fontWeight = FontWeight.Black, color = MaterialTheme.colorScheme.primary)
                        }
                        Column(modifier = Modifier.weight(1f)) {
                            Text("Frecuencia Re-lubricación", fontSize = 11.sp, color = Color.Gray)
                            Text("${relubResult.intervalHours} horas", fontSize = 16.sp, fontWeight = FontWeight.Black, color = MaterialTheme.colorScheme.secondary)
                        }
                    }

                    HorizontalDivider()

                    Column(verticalArrangement = Arrangement.spacedBy(4.dp)) {
                        Text("Lubricante Recomendado SKF:", fontSize = 11.sp, color = Color.Gray, fontWeight = FontWeight.Bold)
                        Text(
                            text = relubResult.recommendedGreaseType,
                            fontSize = 12.sp,
                            color = MaterialTheme.colorScheme.onSurface,
                            fontWeight = FontWeight.Bold
                        )
                    }
                }
            }
        }
    }
}

@Composable
fun ParamRow(label: String, valStr: String) {
    Row(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.SpaceBetween,
        verticalAlignment = Alignment.CenterVertically
    ) {
        Text(label, fontSize = 12.sp, color = Color.Gray)
        Text(valStr, fontSize = 13.sp, fontWeight = FontWeight.Bold, color = MaterialTheme.colorScheme.onSurface)
    }
}
