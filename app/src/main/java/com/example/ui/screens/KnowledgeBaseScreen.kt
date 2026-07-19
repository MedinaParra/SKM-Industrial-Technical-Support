package com.example.ui.screens

import android.content.Intent
import android.net.Uri
import androidx.compose.animation.*
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.LazyRow
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.CornerRadius
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.geometry.Size
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Path
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.data.model.BearingSpec
import com.example.data.model.HousingSpec
import com.example.ui.viewmodel.BearingViewModel

@Composable
fun KnowledgeBaseScreen(
    viewModel: BearingViewModel,
    onNavigateToTab: (Int) -> Unit
) {
    var selectedTab by remember { mutableStateOf(0) } // 0 = Rodamientos, 1 = Soportes, 2 = Manual Poleas, 3 = Guía SKF
    
    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(MaterialTheme.colorScheme.background)
    ) {
        // Scrollable Tab Row for adaptive layout
        ScrollableTabRow(
            selectedTabIndex = selectedTab,
            edgePadding = 16.dp,
            containerColor = MaterialTheme.colorScheme.surface,
            contentColor = MaterialTheme.colorScheme.primary
        ) {
            Tab(
                selected = selectedTab == 0,
                onClick = { selectedTab = 0 },
                text = { Text("Catálogo Rodamientos", fontWeight = FontWeight.Bold, fontSize = 12.sp) },
                icon = { Icon(Icons.Default.PrecisionManufacturing, contentDescription = "Rodamientos", modifier = Modifier.size(18.dp)) }
            )
            Tab(
                selected = selectedTab == 1,
                onClick = { selectedTab = 1 },
                text = { Text("Soportes y Cotas", fontWeight = FontWeight.Bold, fontSize = 12.sp) },
                icon = { Icon(Icons.Default.ViewInAr, contentDescription = "Soportes", modifier = Modifier.size(18.dp)) }
            )
            Tab(
                selected = selectedTab == 2,
                onClick = { selectedTab = 2 },
                text = { Text("Manual Poleas SKM", fontWeight = FontWeight.Bold, fontSize = 12.sp) },
                icon = { Icon(Icons.Default.MenuBook, contentDescription = "Manual Poleas", modifier = Modifier.size(18.dp)) }
            )
            Tab(
                selected = selectedTab == 3,
                onClick = { selectedTab = 3 },
                text = { Text("Mantenimiento SKF", fontWeight = FontWeight.Bold, fontSize = 12.sp) },
                icon = { Icon(Icons.Default.Build, contentDescription = "Guía SKF", modifier = Modifier.size(18.dp)) }
            )
        }

        when (selectedTab) {
            0 -> BearingsTabScreen(viewModel, onNavigateToTab)
            1 -> HousingsTabScreen(viewModel, onNavigateToTab)
            2 -> SkmPulleyManualScreen()
            3 -> SkfBearingManualScreen()
        }
    }
}

@Composable
fun BearingsTabScreen(
    viewModel: BearingViewModel,
    onNavigateToTab: (Int) -> Unit
) {
    val query by viewModel.bearingSearchQuery.collectAsState()
    val selectedBrand by viewModel.selectedBrandFilter.collectAsState()
    val bearingsList by viewModel.bearingsList.collectAsState()
    val selectedBearing by viewModel.selectedBearing.collectAsState()

    val context = LocalContext.current

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp)
    ) {
        // Search & Filter Card
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(8.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            TextField(
                value = query,
                onValueChange = { viewModel.bearingSearchQuery.value = it },
                placeholder = { Text("Buscar rodamiento (e.g., 22215 EK)", fontSize = 13.sp) },
                leadingIcon = { Icon(Icons.Default.Search, contentDescription = "Buscar") },
                singleLine = true,
                modifier = Modifier.weight(1f),
                colors = TextFieldDefaults.colors(
                    focusedContainerColor = MaterialTheme.colorScheme.surface,
                    unfocusedContainerColor = MaterialTheme.colorScheme.surface
                ),
                shape = RoundedCornerShape(10.dp)
            )
        }

        // Brand Filter Selection Chips
        LazyRow(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            val brands = listOf("Todas", "SKF", "FAG", "Timken", "DODGE", "NSK")
            items(brands) { brand ->
                val isSelected = selectedBrand == brand
                FilterChip(
                    selected = isSelected,
                    onClick = { viewModel.selectedBrandFilter.value = brand },
                    label = { Text(brand, fontSize = 12.sp, fontWeight = FontWeight.Bold) },
                    colors = FilterChipDefaults.filterChipColors(
                        selectedContainerColor = MaterialTheme.colorScheme.primary,
                        selectedLabelColor = Color.White
                    )
                )
            }
        }

        // Bearing List and details
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .weight(1f),
            horizontalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            // Main list
            LazyColumn(
                modifier = Modifier
                    .weight(1f)
                    .fillMaxHeight(),
                verticalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                if (bearingsList.isEmpty()) {
                    item {
                        Box(
                            modifier = Modifier
                                .fillMaxWidth()
                                .padding(24.dp),
                            contentAlignment = Alignment.Center
                        ) {
                            Text("No se encontraron rodamientos.", color = Color.Gray, fontSize = 13.sp)
                        }
                    }
                } else {
                    items(bearingsList) { bearing ->
                        val isSelected = selectedBearing?.id == bearing.id
                        Card(
                            onClick = { viewModel.selectedBearing.value = bearing },
                            modifier = Modifier.fillMaxWidth(),
                            colors = CardDefaults.cardColors(
                                containerColor = if (isSelected) MaterialTheme.colorScheme.primaryContainer else MaterialTheme.colorScheme.surface
                            ),
                            border = if (isSelected) BorderStroke(1.5.dp, MaterialTheme.colorScheme.primary) else null
                        ) {
                            Row(
                                modifier = Modifier
                                    .padding(12.dp)
                                    .fillMaxWidth(),
                                horizontalArrangement = Arrangement.SpaceBetween,
                                verticalAlignment = Alignment.CenterVertically
                            ) {
                                Column(verticalArrangement = Arrangement.spacedBy(2.dp)) {
                                    Row(horizontalArrangement = Arrangement.spacedBy(6.dp), verticalAlignment = Alignment.CenterVertically) {
                                        Text(
                                            text = bearing.designation,
                                            fontWeight = FontWeight.Bold,
                                            fontSize = 15.sp,
                                            color = MaterialTheme.colorScheme.onSurface
                                        )
                                        Surface(
                                            color = MaterialTheme.colorScheme.secondary,
                                            shape = RoundedCornerShape(4.dp)
                                        ) {
                                            Text(
                                                text = bearing.brand,
                                                color = MaterialTheme.colorScheme.primary,
                                                fontSize = 9.sp,
                                                fontWeight = FontWeight.Bold,
                                                modifier = Modifier.padding(horizontal = 4.dp, vertical = 2.dp)
                                            )
                                        }
                                    }
                                    Text(
                                        text = bearing.type,
                                        fontSize = 11.sp,
                                        color = Color.Gray
                                    )
                                }
                                Text(
                                    text = "d = ${bearing.boreDiameterMm.toInt()} mm",
                                    fontSize = 13.sp,
                                    fontWeight = FontWeight.Bold,
                                    color = MaterialTheme.colorScheme.primary
                                )
                            }
                        }
                    }
                }
            }

            // Expanded Detail View Pane (for Tablet/Horizontal) or Modal Detail
        }

        // If a bearing is selected, show details at the bottom or as a beautiful floating panel
        selectedBearing?.let { bearing ->
            Card(
                modifier = Modifier
                    .fillMaxWidth()
                    .wrapContentHeight(),
                colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface),
                shape = RoundedCornerShape(16.dp),
                border = BorderStroke(1.dp, Color(0xFFE2E8F0))
            ) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Column {
                            Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                                Text(
                                    text = "Especificaciones: ${bearing.designation}",
                                    fontSize = 16.sp,
                                    fontWeight = FontWeight.Black,
                                    color = MaterialTheme.colorScheme.primary
                                )
                                Surface(
                                    color = MaterialTheme.colorScheme.primary,
                                    shape = RoundedCornerShape(4.dp)
                                ) {
                                    Text(
                                        text = bearing.brand,
                                        color = Color.White,
                                        fontSize = 10.sp,
                                        fontWeight = FontWeight.Bold,
                                        modifier = Modifier.padding(horizontal = 6.dp, vertical = 3.dp)
                                    )
                                }
                            }
                            Text("Rodamiento de Rodillos Cónicos / Oscilantes", fontSize = 11.sp, color = Color.Gray)
                        }
                        IconButton(onClick = { viewModel.selectedBearing.value = null }) {
                            Icon(Icons.Default.Close, contentDescription = "Cerrar")
                        }
                    }

                    HorizontalDivider(modifier = Modifier.padding(vertical = 10.dp))

                    // Physical dimensions layout
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.spacedBy(16.dp)
                    ) {
                        DimensionItem(label = "Eje d", value = "${bearing.boreDiameterMm.toInt()} mm", modifier = Modifier.weight(1f))
                        DimensionItem(label = "Exterior D", value = "${bearing.outerDiameterMm.toInt()} mm", modifier = Modifier.weight(1f))
                        DimensionItem(label = "Ancho B", value = "${bearing.widthMm.toInt()} mm", modifier = Modifier.weight(1f))
                    }

                    Spacer(modifier = Modifier.height(12.dp))

                    // Loads & Limits
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.spacedBy(16.dp)
                    ) {
                        DimensionItem(label = "C. Dinámica", value = "${bearing.dynamicLoadKn} kN", modifier = Modifier.weight(1f))
                        DimensionItem(label = "C. Estática", value = "${bearing.staticLoadKn} kN", modifier = Modifier.weight(1f))
                        DimensionItem(label = "Vel. Límite", value = "${bearing.limitingSpeedRpm.toInt()} RPM", modifier = Modifier.weight(1f))
                    }

                    Spacer(modifier = Modifier.height(14.dp))

                    // Mounting Tolerances Header
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Icon(Icons.Default.CompassCalibration, contentDescription = "Tolerancia", tint = MaterialTheme.colorScheme.primary, modifier = Modifier.size(16.dp))
                        Spacer(modifier = Modifier.width(6.dp))
                        Text("Tolerancias de Montaje SKF (Cono 1:12)", fontSize = 13.sp, fontWeight = FontWeight.Bold, color = MaterialTheme.colorScheme.onSurface)
                    }

                    Spacer(modifier = Modifier.height(6.dp))

                    // Recommended reduction range
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Text("Reducción de Juego Radial:", fontSize = 12.sp, color = Color.Gray)
                        Text(
                            text = "${bearing.recommendedReductionMin} - ${bearing.recommendedReductionMax} mm",
                            fontSize = 13.sp,
                            fontWeight = FontWeight.Bold,
                            color = MaterialTheme.colorScheme.primary
                        )
                    }
                    Spacer(modifier = Modifier.height(4.dp))
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Text("Calado Axial Recomendado (s):", fontSize = 12.sp, color = Color.Gray)
                        Text(
                            text = "${bearing.axialDriveUp1To12Min} - ${bearing.axialDriveUp1To12Max} mm",
                            fontSize = 13.sp,
                            fontWeight = FontWeight.Bold,
                            color = MaterialTheme.colorScheme.secondary
                        )
                    }

                    Spacer(modifier = Modifier.height(14.dp))

                    // Navigation Actions
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        Button(
                            onClick = {
                                // Prefill inputs in calculator!
                                viewModel.calcNominalBore.value = bearing.boreDiameterMm.toString()
                                viewModel.calcInitialClearance.value = bearing.clearanceMinC3.toString() // Use C3 as standard industry baseline
                                viewModel.calcFinalClearance.value = (bearing.clearanceMinC3 - bearing.recommendedReductionMin).toString()
                                onNavigateToTab(2) // Navigate to Calculator tab!
                            },
                            modifier = Modifier.weight(1.2f)
                        ) {
                            Icon(Icons.Default.Calculate, contentDescription = "Calcular")
                            Spacer(modifier = Modifier.width(6.dp))
                            Text("Ir a Calculadora", fontSize = 12.sp)
                        }

                        OutlinedButton(
                            onClick = {
                                if (bearing.cadUrl.isNotEmpty()) {
                                    val intent = Intent(Intent.ACTION_VIEW, Uri.parse(bearing.cadUrl))
                                    context.startActivity(intent)
                                }
                            },
                            modifier = Modifier.weight(1f)
                        ) {
                            Icon(Icons.Default.CloudDownload, contentDescription = "CAD 3D")
                            Spacer(modifier = Modifier.width(6.dp))
                            Text("CAD 3D", fontSize = 12.sp)
                        }
                    }
                }
            }
        }
    }
}

@Composable
fun HousingsTabScreen(
    viewModel: BearingViewModel,
    onNavigateToTab: (Int) -> Unit
) {
    val query by viewModel.housingSearchQuery.collectAsState()
    val selectedBrand by viewModel.selectedHousingBrandFilter.collectAsState()
    val housingsList by viewModel.housingsList.collectAsState()
    val selectedHousing by viewModel.selectedHousing.collectAsState()

    val context = LocalContext.current

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp)
    ) {
        // Search & Filter
        TextField(
            value = query,
            onValueChange = { viewModel.housingSearchQuery.value = it },
            placeholder = { Text("Buscar soporte (e.g., SNL 515)", fontSize = 13.sp) },
            leadingIcon = { Icon(Icons.Default.Search, contentDescription = "Buscar") },
            singleLine = true,
            modifier = Modifier.fillMaxWidth(),
            colors = TextFieldDefaults.colors(
                focusedContainerColor = MaterialTheme.colorScheme.surface,
                unfocusedContainerColor = MaterialTheme.colorScheme.surface
            ),
            shape = RoundedCornerShape(10.dp)
        )

        // Brand Selector for Housings
        LazyRow(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            val brands = listOf("Todas", "SKF", "FAG", "DODGE", "NSK")
            items(brands) { brand ->
                val isSelected = selectedBrand == brand
                FilterChip(
                    selected = isSelected,
                    onClick = { viewModel.selectedHousingBrandFilter.value = brand },
                    label = { Text(brand, fontSize = 12.sp, fontWeight = FontWeight.Bold) },
                    colors = FilterChipDefaults.filterChipColors(
                        selectedContainerColor = MaterialTheme.colorScheme.primary,
                        selectedLabelColor = Color.White
                    )
                )
            }
        }

        // List
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .weight(1f),
            horizontalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            LazyColumn(
                modifier = Modifier
                    .weight(1f)
                    .fillMaxHeight(),
                verticalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                if (housingsList.isEmpty()) {
                    item {
                        Box(
                            modifier = Modifier
                                .fillMaxWidth()
                                .padding(24.dp),
                            contentAlignment = Alignment.Center
                        ) {
                            Text("No se encontraron soportes.", color = Color.Gray, fontSize = 13.sp)
                        }
                    }
                } else {
                    items(housingsList) { housing ->
                        val isSelected = selectedHousing?.designation == housing.designation
                        Card(
                            onClick = { viewModel.selectedHousing.value = housing },
                            modifier = Modifier.fillMaxWidth(),
                            colors = CardDefaults.cardColors(
                                containerColor = if (isSelected) MaterialTheme.colorScheme.primaryContainer else MaterialTheme.colorScheme.surface
                            ),
                            border = if (isSelected) BorderStroke(1.5.dp, MaterialTheme.colorScheme.primary) else null
                        ) {
                            Column(modifier = Modifier.padding(12.dp)) {
                                Row(
                                    modifier = Modifier.fillMaxWidth(),
                                    horizontalArrangement = Arrangement.SpaceBetween,
                                    verticalAlignment = Alignment.CenterVertically
                                ) {
                                    Row(horizontalArrangement = Arrangement.spacedBy(6.dp), verticalAlignment = Alignment.CenterVertically) {
                                        Text(
                                            text = housing.designation,
                                            fontWeight = FontWeight.Bold,
                                            fontSize = 15.sp,
                                            color = MaterialTheme.colorScheme.onSurface
                                        )
                                        Surface(
                                            color = MaterialTheme.colorScheme.secondary,
                                            shape = RoundedCornerShape(4.dp)
                                        ) {
                                            Text(
                                                text = housing.brand,
                                                color = Color.White,
                                                fontSize = 9.sp,
                                                fontWeight = FontWeight.Bold,
                                                modifier = Modifier.padding(horizontal = 4.dp, vertical = 2.dp)
                                            )
                                        }
                                    }
                                    Text(
                                        text = "${housing.weightKg} kg",
                                        fontSize = 11.sp,
                                        color = Color.Gray
                                    )
                                }
                                Spacer(modifier = Modifier.height(4.dp))
                                Text(
                                    text = "Comp: ${housing.compatibleBearingsCsv}",
                                    fontSize = 11.sp,
                                    color = Color.Gray,
                                    maxLines = 1,
                                    overflow = TextOverflow.Ellipsis
                                )
                            }
                        }
                    }
                }
            }
        }

        // Selected housing details with Canvas diagram!
        selectedHousing?.let { housing ->
            Card(
                modifier = Modifier
                    .fillMaxWidth()
                    .wrapContentHeight(),
                colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface),
                shape = RoundedCornerShape(16.dp),
                border = BorderStroke(1.dp, Color(0xFFE2E8F0))
            ) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                            Text(
                                text = "Soporte: ${housing.designation}",
                                fontSize = 16.sp,
                                fontWeight = FontWeight.Black,
                                color = MaterialTheme.colorScheme.primary
                            )
                            Surface(
                                color = Color(0xFF1E3A8A),
                                shape = RoundedCornerShape(4.dp)
                            ) {
                                textBrand(brand = housing.brand)
                            }
                        }
                        IconButton(onClick = { viewModel.selectedHousing.value = null }) {
                            Icon(Icons.Default.Close, contentDescription = "Cerrar")
                        }
                    }

                    HorizontalDivider(modifier = Modifier.padding(vertical = 8.dp))

                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.spacedBy(16.dp)
                    ) {
                        // Canvas drawing on the left side (Plummer Block 2D diagram with dimensions)
                        Box(
                            modifier = Modifier
                                .weight(1f)
                                .height(140.dp)
                                .background(Color(0xFFF8FAFC), shape = RoundedCornerShape(10.dp))
                                .border(1.dp, Color(0xFFE2E8F0), shape = RoundedCornerShape(10.dp)),
                            contentAlignment = Alignment.Center
                        ) {
                            Canvas(modifier = Modifier.fillMaxSize().padding(10.dp)) {
                                val w = size.width
                                val h = size.height

                                // Draw Plummer Block Housing base
                                val basePath = Path().apply {
                                    // Left flange
                                    moveTo(w * 0.15f, h * 0.85f)
                                    lineTo(w * 0.25f, h * 0.85f)
                                    // Left vertical rise
                                    lineTo(w * 0.28f, h * 0.55f)
                                    // Upper arc dome of housing
                                    cubicTo(
                                        w * 0.35f, h * 0.25f,
                                        w * 0.65f, h * 0.25f,
                                        w * 0.72f, h * 0.55f
                                    )
                                    // Right rise down
                                    lineTo(w * 0.75f, h * 0.85f)
                                    // Right flange
                                    lineTo(w * 0.85f, h * 0.85f)
                                    // Down base
                                    lineTo(w * 0.85f, h * 0.92f)
                                    lineTo(w * 0.15f, h * 0.92f)
                                    close()
                                }
                                drawPath(
                                    path = basePath,
                                    color = Color(0xFF475569),
                                    style = Stroke(width = 4f)
                                )

                                // Draw shaft hole
                                drawCircle(
                                    color = Color(0xFF94A3B8),
                                    radius = 16f,
                                    center = Offset(w * 0.5f, h * 0.58f),
                                    style = Stroke(width = 3.5f)
                                )

                                // Drawing dimensions lines (L cota - Total length)
                                val dimensionColor = Color(0xFF0284C7)
                                drawLine(
                                    color = dimensionColor,
                                    start = Offset(w * 0.15f, h * 0.97f),
                                    end = Offset(w * 0.85f, h * 0.97f),
                                    strokeWidth = 2f
                                )
                                // Arrows
                                drawLine(color = dimensionColor, start = Offset(w * 0.15f, h * 0.97f), end = Offset(w * 0.19f, h * 0.94f), strokeWidth = 2f)
                                drawLine(color = dimensionColor, start = Offset(w * 0.15f, h * 0.97f), end = Offset(w * 0.19f, h * 1.00f), strokeWidth = 2f)
                                drawLine(color = dimensionColor, start = Offset(w * 0.85f, h * 0.97f), end = Offset(w * 0.81f, h * 0.94f), strokeWidth = 2f)
                                drawLine(color = dimensionColor, start = Offset(w * 0.85f, h * 0.97f), end = Offset(w * 0.81f, h * 1.00f), strokeWidth = 2f)

                                // Cota L Text overlay
                                // Height Cota (H - Height to Center)
                                drawLine(
                                    color = dimensionColor,
                                    start = Offset(w * 0.5f, h * 0.58f),
                                    end = Offset(w * 0.5f, h * 0.92f),
                                    strokeWidth = 1.5f
                                )
                            }
                            // Text overlays
                            Text("Cota L = ${housing.L_mm.toInt()} mm", fontSize = 9.sp, fontWeight = FontWeight.Bold, color = Color(0xFF0284C7), modifier = Modifier.align(Alignment.BottomCenter).padding(bottom = 6.dp))
                            Text("H = ${housing.H_mm.toInt()}", fontSize = 9.sp, fontWeight = FontWeight.Bold, color = Color(0xFF0284C7), modifier = Modifier.align(Alignment.Center).padding(top = 18.dp))
                        }

                        // Right side text dimensions
                        Column(
                            modifier = Modifier.weight(1.1f),
                            verticalArrangement = Arrangement.spacedBy(4.dp)
                        ) {
                            Text("Cotas Principales", fontSize = 12.sp, fontWeight = FontWeight.Bold, color = MaterialTheme.colorScheme.onSurface)
                            CotaRow(label = "Ancho (W):", value = "${housing.W_mm.toInt()} mm")
                            CotaRow(label = "Altura Centro (H):", value = "${housing.H_mm.toInt()} mm")
                            CotaRow(label = "Altura Total (H1):", value = "${housing.H1_mm.toInt()} mm")
                            CotaRow(label = "Dist. Pernos:", value = "${housing.boltDistanceMm.toInt()} mm")
                            CotaRow(label = "Peso Total:", value = "${housing.weightKg} kg")
                        }
                    }

                    Spacer(modifier = Modifier.height(10.dp))

                    // Compatible bearings list
                    Surface(
                        color = MaterialTheme.colorScheme.primaryContainer.copy(alpha = 0.2f),
                        shape = RoundedCornerShape(8.dp),
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        Column(modifier = Modifier.padding(10.dp), verticalArrangement = Arrangement.spacedBy(4.dp)) {
                            Text(
                                text = "Rodamientos Compatibles:",
                                fontSize = 11.sp,
                                fontWeight = FontWeight.Bold,
                                color = MaterialTheme.colorScheme.primary
                            )
                            Text(
                                text = housing.compatibleBearingsCsv,
                                fontSize = 12.sp,
                                color = MaterialTheme.colorScheme.onPrimaryContainer,
                                fontWeight = FontWeight.Medium
                            )
                            Spacer(modifier = Modifier.height(2.dp))
                            Text(
                                text = "Manguitos Recomendados: ${housing.compatibleSleevesCsv}",
                                fontSize = 11.sp,
                                color = Color.Gray,
                                fontWeight = FontWeight.Bold
                            )
                        }
                    }

                    Spacer(modifier = Modifier.height(10.dp))

                    // CAD Download Row
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        Button(
                            onClick = {
                                if (housing.cadUrl.isNotEmpty()) {
                                    val intent = Intent(Intent.ACTION_VIEW, Uri.parse(housing.cadUrl))
                                    context.startActivity(intent)
                                }
                            },
                            modifier = Modifier.weight(1f)
                        ) {
                            Icon(Icons.Default.CloudDownload, contentDescription = "Descargar CAD")
                            Spacer(modifier = Modifier.width(8.dp))
                            Text("Enlace CAD 3D de Soporte")
                        }
                    }
                }
            }
        }
    }
}

@Composable
fun CotaRow(label: String, value: String) {
    Row(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.SpaceBetween,
        verticalAlignment = Alignment.CenterVertically
    ) {
        Text(label, fontSize = 11.sp, color = Color.Gray)
        Text(value, fontSize = 12.sp, fontWeight = FontWeight.Bold, color = MaterialTheme.colorScheme.onSurface)
    }
}

@Composable
fun DimensionItem(label: String, value: String, modifier: Modifier = Modifier) {
    Surface(
        color = Color(0xFFF1F5F9),
        shape = RoundedCornerShape(8.dp),
        modifier = modifier
    ) {
        Column(
            modifier = Modifier.padding(8.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Text(label, fontSize = 10.sp, color = Color.Gray, fontWeight = FontWeight.Bold)
            Spacer(modifier = Modifier.height(2.dp))
            Text(value, fontSize = 13.sp, fontWeight = FontWeight.Black, color = Color(0xFF0F172A))
        }
    }
}

@Composable
fun textBrand(brand: String) {
    Text(
        text = brand,
        color = Color.White,
        fontSize = 10.sp,
        fontWeight = FontWeight.Bold,
        modifier = Modifier.padding(horizontal = 6.dp, vertical = 3.dp)
    )
}

// ==========================================
// SKM PULLEY TECHNICAL MANUAL SCREEN
// ==========================================

@Composable
fun SkmPulleyManualScreen() {
    var searchQuery by remember { mutableStateOf("") }
    var selectedSection by remember { mutableStateOf("Todo") }
    
    val sections = listOf("Todo", "Prólogo", "Introducción", "Aplicaciones", "Anatomía", "Aceptación")
    
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp)
    ) {
        // Search Input
        TextField(
            value = searchQuery,
            onValueChange = { searchQuery = it },
            placeholder = { Text("Buscar en el manual de poleas...", fontSize = 13.sp) },
            leadingIcon = { Icon(Icons.Default.Search, contentDescription = "Buscar") },
            trailingIcon = {
                if (searchQuery.isNotEmpty()) {
                    IconButton(onClick = { searchQuery = "" }) {
                        Icon(Icons.Default.Close, contentDescription = "Limpiar")
                    }
                }
            },
            singleLine = true,
            modifier = Modifier.fillMaxWidth(),
            colors = TextFieldDefaults.colors(
                focusedContainerColor = MaterialTheme.colorScheme.surface,
                unfocusedContainerColor = MaterialTheme.colorScheme.surface
            ),
            shape = RoundedCornerShape(10.dp)
        )
        
        // Horizontal Section Selector
        LazyRow(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            items(sections) { section ->
                val isSelected = selectedSection == section
                FilterChip(
                    selected = isSelected,
                    onClick = { selectedSection = section },
                    label = { Text(section, fontSize = 11.sp, fontWeight = FontWeight.Bold) },
                    colors = FilterChipDefaults.filterChipColors(
                        selectedContainerColor = MaterialTheme.colorScheme.primary,
                        selectedLabelColor = Color.White
                    )
                )
            }
        }
        
        // Manual Content
        LazyColumn(
            modifier = Modifier
                .weight(1f)
                .fillMaxWidth(),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            // Section 1: Prólogo
            if ((selectedSection == "Todo" || selectedSection == "Prólogo") && 
                (searchQuery.isEmpty() || "prólogo".contains(searchQuery, true) || "mecánico".contains(searchQuery, true) || "espera".contains(searchQuery, true))) {
                item {
                    ManualSectionCard(
                        title = "PRÓLOGO — A Ti, Mecánico",
                        subtitle = "«La mina no espera.» — Dicho habitual en mantenimiento"
                    ) {
                        Text(
                            text = "Si estás leyendo estas líneas, probablemente ya sabes lo que se siente tener las manos manchadas de grasa a las siete de la mañana. Sabes lo que pesa un tortímetro después de la tercera ronda de torque. Conoces el sonido que hace una eslinga cuando toma tensión, y has sentido en la nuca el calor de un machón a cuatrocientos grados. Eso no se aprende en un libro. Se aprende estando ahí.",
                            fontSize = 13.sp,
                            lineHeight = 18.sp,
                            color = MaterialTheme.colorScheme.onSurface
                        )
                        
                        Spacer(modifier = Modifier.height(10.dp))
                        
                        ConceptCard(
                            title = "CONCEPTO CLAVE: El trabajo invisible",
                            text = "En la minería, nadie habla de las poleas cuando funcionan bien. Tu trabajo es invisible cuando está bien hecho, pero es la mayor demostración de competencia. Cada polea reparada en Antofagasta llega a faenas a 3.000 metros de altitud en el desierto, soportando de -5°C a +35°C de forma continua, 24 horas, 365 días. Si una polea falla, la cinta para, y la mina entera se detiene."
                        )
                    }
                }
            }
            
            // Section 2: Introducción
            if ((selectedSection == "Todo" || selectedSection == "Introducción") && 
                (searchQuery.isEmpty() || "introducción".contains(searchQuery, true) || "estándar".contains(searchQuery, true) || "competencia".contains(searchQuery, true) || "cema".contains(searchQuery, true))) {
                item {
                    ManualSectionCard(
                        title = "1. Introducción al Transporte por Correas",
                        subtitle = "Basado en Estándar MECoE-R&W-EST-009 y Base Técnica LIC-022"
                    ) {
                        Text(
                            text = "Las poleas son componentes ultra críticos en el transporte de mineral a granel de BHP Chile. Una falla de polea provoca detenciones con costos que superan los cientos de miles de dólares por hora en Minera Escondida y Minera Spence.",
                            fontSize = 13.sp,
                            lineHeight = 18.sp,
                            color = MaterialTheme.colorScheme.onSurface
                        )
                        
                        Spacer(modifier = Modifier.height(10.dp))
                        
                        Text(
                            text = "Niveles de Competencia Técnica del Mecánico:",
                            fontSize = 12.sp,
                            fontWeight = FontWeight.Bold,
                            color = MaterialTheme.colorScheme.primary
                        )
                        
                        Spacer(modifier = Modifier.height(6.dp))
                        
                        Column(verticalArrangement = Arrangement.spacedBy(6.dp)) {
                            BulletItem("Nivel 1 (Mecánico Asistente):", "Desarme, limpieza, preparación de superficies y registro fotográfico. Opera bajo supervisión directa.")
                            BulletItem("Nivel 2 (Mecánico Especialista):", "Desarme y armado completo, metrología básica, aplicación de adhesivos y revestimientos, y calado de rodamientos.")
                            BulletItem("Nivel 3 (Mecánico Senior):", "Lidera la reparación. Interpreta ensayos no destructivos (END), supervisa el calado de rodamientos, valida el balanceo dinámico en banco de pruebas y genera informes técnicos.")
                        }
                        
                        Spacer(modifier = Modifier.height(10.dp))
                        
                        TechNoteCard(
                            text = "El estándar ANSI/CEMA B105.1 es la normativa fundamental de diseño. El límite de deflexión máxima admisible en el eje es de 0,002 pulgadas por pulgada de longitud total."
                        )
                    }
                }
            }
            
            // Section 3: Aplicaciones
            if ((selectedSection == "Todo" || selectedSection == "Aplicaciones") && 
                (searchQuery.isEmpty() || "aplicaciones".contains(searchQuery, true) || "revestimiento".contains(searchQuery, true) || "chancado".contains(searchQuery, true) || "cerámico".contains(searchQuery, true) || "diamantado".contains(searchQuery, true))) {
                item {
                    ManualSectionCard(
                        title = "2. Áreas de Aplicación Minera (BHP)",
                        subtitle = "Condiciones operacionales y estándares de revestimiento"
                    ) {
                        Text(
                            text = "Cada área de la planta minera tiene condiciones operativas diferentes que determinan el tipo de polea y revestimiento requerido para optimizar la vida útil:",
                            fontSize = 13.sp,
                            lineHeight = 18.sp,
                            color = MaterialTheme.colorScheme.onSurface
                        )
                        
                        Spacer(modifier = Modifier.height(10.dp))
                        
                        Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                            BulletItem("Chancado y Alimentación:", "Impacto severo de mineral grueso (hasta 400mm). Alta vibración. Exige revestimiento de Caucho Diamantado de 65±5 Shore A en motrices para tracción, y caucho liso en no motrices.")
                            BulletItem("Concentradoras y Pulpas:", "Ambiente húmedo y altamente corrosivo. El mineral es fino con agua. Requiere control riguroso de corrosión en ejes/descansos.")
                            BulletItem("Apilamiento y Ripios (Lixiviación):", "El ambiente más agresivo. Soluciones ácidas y partículas angulares altamente abrasivas. Requiere obligatoriamente Caucho Cerámico al 30% o Cerámico al 100% en todas las poleas.")
                        }
                        
                        Spacer(modifier = Modifier.height(10.dp))
                        
                        WarningCard(
                            title = "PRECAUCIÓN: Desgaste en Apilamientos",
                            text = "Las poleas en ripios y apilamiento tienen una vida útil significativamente menor. Durante la evaluación técnica, preste atención extrema al mapeo de espesores del manto por ultrasonido (ASTM E787), ya que el desgaste ácido carcome el acero por debajo del revestimiento sin ser visible a simple vista."
                        )
                    }
                }
            }
            
            // Section 4: Anatomía
            if ((selectedSection == "Todo" || selectedSection == "Anatomía") && 
                (searchQuery.isEmpty() || "anatomía".contains(searchQuery, true) || "componentes".contains(searchQuery, true) || "eje".contains(searchQuery, true) || "soldadura".contains(searchQuery, true) || "manto".contains(searchQuery, true) || "obturadores".contains(searchQuery, true))) {
                item {
                    ManualSectionCard(
                        title = "3. Anatomía de la Polea & Componentes",
                        subtitle = "Análisis de tolerancias y prohibiciones críticas"
                    ) {
                        Column(verticalArrangement = Arrangement.spacedBy(10.dp)) {
                            Text(
                                text = "Una polea técnica de SKM se compone de elementos diseñados para soportar esfuerzos mecánicos masivos bajo condiciones severas:",
                                fontSize = 13.sp,
                                lineHeight = 18.sp
                            )
                            
                            // Eje
                            Text("A. Eje de Transmisión", fontWeight = FontWeight.Bold, fontSize = 13.sp, color = MaterialTheme.colorScheme.primary)
                            Text("• Material: Acero aleado de alta resistencia SAE 4340 templado y revenido (Dureza: 270-320 HB).\n• Tolerancias: h9 en zona de rodamientos (0,8 Ra acabado fino), h8 en zona de manguitos de expansión (1,6 Ra).\n• Prohibición Absoluta: ESTÁ PROHIBIDO realizar aporte de soldadura en ejes. La soldadura debilita la metalurgia creando zonas de fragilidad propensas a fisuras por fatiga. El único proceso permitido es el metalizado y exclusivamente en la zona de obturadores.", fontSize = 12.sp, lineHeight = 17.sp)
                            
                            // Manto
                            Text("B. Manto y Tapas Laterales", fontWeight = FontWeight.Bold, fontSize = 13.sp, color = MaterialTheme.colorScheme.primary)
                            Text("• Material: Acero estructural ASTM A572 Grado 50 cilindrado en una sola pieza (NUNCA construido en partes o parcheado).\n• Diseño de Tapa: Unión tapa-cilindrado obligatoriamente tipo T-Shape Button. Diseños planos o de soldadura directa sin centrador son motivo de baja inmediata de la polea.\n• Alivio de tensiones: Obligatorio en horno antes del mecanizado final para eliminar tensiones residuales de soldadura.\n• Prohibición: NUNCA soldar masas de balanceo sobre las tapas laterales. Deben instalarse mecánicamente en la cara frontal mediante pernos.", fontSize = 12.sp, lineHeight = 17.sp)
                            
                            // Descansos
                            Text("C. Descansos (Chumaceras Bipartidas) y Obturadores", fontWeight = FontWeight.Bold, fontSize = 13.sp, color = MaterialTheme.colorScheme.primary)
                            Text("• Alojamiento: Tolerancia G7 para rodamientos ≤500mm y F7 para >500mm.\n• Obturadores: Modelo de laberinto vertical. Se prohíbe el uso de sellos de aluminio debido a que el roce metal-metal genera polvo conductor y abrasivo para los rodamientos. Cambiar siempre O-rings y V-rings.", fontSize = 12.sp, lineHeight = 17.sp)
                        }
                    }
                }
            }
            
            // Section 5: Aceptación
            if ((selectedSection == "Todo" || selectedSection == "Aceptación") && 
                (searchQuery.isEmpty() || "aceptación".contains(searchQuery, true) || "banco".contains(searchQuery, true) || "pruebas".contains(searchQuery, true) || "límites".contains(searchQuery, true) || "vibración".contains(searchQuery, true) || "euler".contains(searchQuery, true))) {
                item {
                    ManualSectionCard(
                        title = "4. Pruebas en Banco & Criterios de Aceptación",
                        subtitle = "Evaluación final de calidad dinámica (ISO 1940-1)"
                    ) {
                        Text(
                            text = "La transmisión de potencia se basa en la ecuación de Euler-Eytelwein: T1/T2 = e^(μ*θ). Un revestimiento diamantado (μ=0,35) tiene más del doble de capacidad de tracción que un manto de acero desnudo (μ=0,15). La pérdida del revestimiento causa patinaje severo y sobrecalentamiento.",
                            fontSize = 13.sp,
                            lineHeight = 18.sp,
                            color = MaterialTheme.colorScheme.onSurface
                        )
                        
                        Spacer(modifier = Modifier.height(10.dp))
                        
                        Text(
                            text = "Límites Críticos de Aceptación en Banco (Prueba sin carga):",
                            fontSize = 12.sp,
                            fontWeight = FontWeight.Bold,
                            color = MaterialTheme.colorScheme.primary
                        )
                        
                        Spacer(modifier = Modifier.height(8.dp))
                        
                        Column(verticalArrangement = Arrangement.spacedBy(4.dp)) {
                            SpecRow("Velocidad de Vibración:", "< 1.0 mm/s RMS (Vertical, Horiz, Axial)")
                            SpecRow("Temperatura de Descansos:", "≤ 35°C (durante la prueba)")
                            SpecRow("TIR sobre Cilindrado:", "Máximo 0,75 mm")
                            SpecRow("TIR sobre Revestimiento Caucho:", "Máximo 1,5 mm")
                            SpecRow("TIR sobre Revestimiento Cerámico:", "Máximo 1,5 mm")
                            SpecRow("Diámetro exterior vs Eje:", "TIR máximo 1,5 mm")
                            SpecRow("Runout de Machón:", "Máximo 0,1 mm por cada 100mm de radio")
                            SpecRow("Torque Transmisible hacia Polea:", "Fricción residual ≤ 2,7 Nm")
                        }
                    }
                }
            }
        }
    }
}

// ==========================================
// SKF BEARING MAINTENANCE MANUAL SCREEN
// ==========================================

@Composable
fun SkfBearingManualScreen() {
    var searchQuery by remember { mutableStateOf("") }
    var selectedSection by remember { mutableStateOf("Todo") }
    
    val sections = listOf("Todo", "Conceptos", "Almacenamiento", "Montaje", "Lubricación", "Inspección")
    
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp)
    ) {
        // Search Input
        TextField(
            value = searchQuery,
            onValueChange = { searchQuery = it },
            placeholder = { Text("Buscar en la guía SKF de rodamientos...", fontSize = 13.sp) },
            leadingIcon = { Icon(Icons.Default.Search, contentDescription = "Buscar") },
            trailingIcon = {
                if (searchQuery.isNotEmpty()) {
                    IconButton(onClick = { searchQuery = "" }) {
                        Icon(Icons.Default.Close, contentDescription = "Limpiar")
                    }
                }
            },
            singleLine = true,
            modifier = Modifier.fillMaxWidth(),
            colors = TextFieldDefaults.colors(
                focusedContainerColor = MaterialTheme.colorScheme.surface,
                unfocusedContainerColor = MaterialTheme.colorScheme.surface
            ),
            shape = RoundedCornerShape(10.dp)
        )
        
        // Horizontal Section Selector
        LazyRow(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            items(sections) { section ->
                val isSelected = selectedSection == section
                FilterChip(
                    selected = isSelected,
                    onClick = { selectedSection = section },
                    label = { Text(section, fontSize = 11.sp, fontWeight = FontWeight.Bold) },
                    colors = FilterChipDefaults.filterChipColors(
                        selectedContainerColor = MaterialTheme.colorScheme.primary,
                        selectedLabelColor = Color.White
                    )
                )
            }
        }
        
        // Manual Content
        LazyColumn(
            modifier = Modifier
                .weight(1f)
                .fillMaxWidth(),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            // Section 1: Conceptos
            if ((selectedSection == "Todo" || selectedSection == "Conceptos") && 
                (searchQuery.isEmpty() || "conceptos".contains(searchQuery, true) || "terminología".contains(searchQuery, true) || "juego".contains(searchQuery, true) || "sufijo".contains(searchQuery, true))) {
                item {
                    ManualSectionCard(
                        title = "1. Nociones Básicas y Terminología SKF",
                        subtitle = "Estructura de diseño y designaciones de rodamientos"
                    ) {
                        Text(
                            text = "Un rodamiento es un elemento de precisión para soportar cargas y reducir fricción. Se compone de aro interior, aro exterior, elementos rodantes, jaula y tapados (sellos/placas de protección).",
                            fontSize = 13.sp,
                            lineHeight = 18.sp,
                            color = MaterialTheme.colorScheme.onSurface
                        )
                        
                        Spacer(modifier = Modifier.height(10.dp))
                        
                        Text(
                            text = "Sufijos de Designación Comunes:",
                            fontSize = 12.sp,
                            fontWeight = FontWeight.Bold,
                            color = MaterialTheme.colorScheme.primary
                        )
                        
                        Spacer(modifier = Modifier.height(6.dp))
                        
                        Column(verticalArrangement = Arrangement.spacedBy(4.dp)) {
                            SpecRow("Z, 2Z:", "Placa de protección de chapa de acero. No rozante.")
                            SpecRow("RS, 2RS:", "Sello rozante de caucho acrilonitrilo-butadieno (NBR).")
                            SpecRow("RSH, 2RSH:", "Sello rozante reforzado con chapa de acero (alta resistencia).")
                            SpecRow("RSL, 2RSL:", "Sello de baja fricción, excelente rendimiento térmico.")
                            SpecRow("V:", "Completamente lleno de rodillos (sin jaula). Mayor capacidad de carga.")
                        }
                        
                        Spacer(modifier = Modifier.height(10.dp))
                        
                        ConceptCard(
                            title = "Juego Interno del Rodamiento",
                            text = "El juego interno es la distancia radial o axial que permite al aro exterior moverse respecto al interior. El juego inicial (antes de montar) siempre es mayor que el juego de funcionamiento (montado). Esto se debe a que la interferencia de los ajustes comprime el aro interior, y el calor expande los componentes. Los rodamientos de rodillos esféricos exigen mantener juego residual controlado tras el montaje."
                        )
                    }
                }
            }
            
            // Section 2: Almacenamiento
            if ((selectedSection == "Todo" || selectedSection == "Almacenamiento") && 
                (searchQuery.isEmpty() || "almacenamiento".contains(searchQuery, true) || "humedad".contains(searchQuery, true) || "vida útil".contains(searchQuery, true) || "conservación".contains(searchQuery, true))) {
                item {
                    ManualSectionCard(
                        title = "2. Almacenamiento y Conservación de Rodamientos",
                        subtitle = "Prácticas para evitar la corrosión y deformación"
                    ) {
                        Text(
                            text = "Las condiciones incorrectas de almacenamiento degradan la grasa y oxidan las pistas de rodadura. Siga las siguientes pautas estrictas de SKF:",
                            fontSize = 13.sp,
                            lineHeight = 18.sp,
                            color = MaterialTheme.colorScheme.onSurface
                        )
                        
                        Spacer(modifier = Modifier.height(10.dp))
                        
                        Column(verticalArrangement = Arrangement.spacedBy(6.dp)) {
                            BulletItem("Posición horizontal:", "Almacenar siempre horizontalmente. Evita deformaciones y marcas por vibración en caminos de rodadura.")
                            BulletItem("Humedad relativa límite:", "Controlar y limitar la humedad relativa según la temperatura:\n• 75% máximo a 20°C\n• 60% máximo a 22°C\n• 50% máximo a 25°C")
                            BulletItem("Embalaje original intacto:", "No abrir el embalaje original del fabricante hasta el momento exacto de la instalación para evitar contaminación por polvo o humedad.")
                            BulletItem("Rotar máquinas en reserva:", "Las máquinas o poleas almacenadas en reserva deben rotarse periódicamente a mano para redistribuir la grasa en los rodamientos y evitar falso Brinell.")
                        }
                        
                        Spacer(modifier = Modifier.height(10.dp))
                        
                        SpecRow("Vida útil (Abiertos):", "5 años máximo en almacenamiento (con compuesto antioxidante).")
                        SpecRow("Vida útil (Sellados):", "3 años máximo. La grasa se degrada por el paso del tiempo.")
                    }
                }
            }
            
            // Section 3: Montaje
            if ((selectedSection == "Todo" || selectedSection == "Montaje") && 
                (searchQuery.isEmpty() || "montaje".contains(searchQuery, true) || "caliente".contains(searchQuery, true) || "frío".contains(searchQuery, true) || "calentador".contains(searchQuery, true) || "inducción".contains(searchQuery, true))) {
                item {
                    ManualSectionCard(
                        title = "3. Montaje en Frío y en Caliente SKF",
                        subtitle = "Técnicas mecánicas y térmicas aprobadas"
                    ) {
                        Text(
                            text = "El montaje correcto garantiza que el rodamiento no sufra daños estructurales antes de entrar en servicio. El calor se usa para dilatar el aro interior y facilitar el deslizamiento sobre el eje.",
                            fontSize = 13.sp,
                            lineHeight = 18.sp,
                            color = MaterialTheme.colorScheme.onSurface
                        )
                        
                        Spacer(modifier = Modifier.height(10.dp))
                        
                        Text("A. Montaje en Frío (Ajuste Mecánico o Hidráulico):", fontWeight = FontWeight.Bold, fontSize = 13.sp, color = MaterialTheme.colorScheme.primary)
                        Text("• Adecuado para diámetros pequeños. Utilizar herramientas que apliquen la fuerza de forma uniforme sobre el aro que se monta con interferencia (nunca transmitir fuerza de montaje a través de los elementos rodantes).\n• SKF Drive-up: Utiliza una tuerca hidráulica y un reloj comparador para medir el calado axial exacto del rodamiento cónico.\n• Inyección de aceite: Excelente para rodamientos medianos y grandes. Se inyecta aceite a alta presión en los conductos del eje para expandir radialmente el aro interior, facilitando el deslizamiento.", fontSize = 12.sp, lineHeight = 17.sp)
                        
                        Spacer(modifier = Modifier.height(8.dp))
                        
                        Text("B. Montaje en Caliente (Dilatación Térmica):", fontWeight = FontWeight.Bold, fontSize = 13.sp, color = MaterialTheme.colorScheme.primary)
                        Text("• Calentador de Inducción SKF: El método más seguro y limpio. Calienta el aro de manera uniforme. Magnetiza el rodamiento, por lo que es obligatorio desmagnetizarlo al final del ciclo para evitar que atraiga limallas abrasivas.\n• Placas eléctricas: Útiles para rodamientos pequeños. Colocar un aro distanciador; los rodamientos sellados nunca deben tocar directamente la placa.", fontSize = 12.sp, lineHeight = 17.sp)
                        
                        Spacer(modifier = Modifier.height(10.dp))
                        
                        WarningCard(
                            title = "PROHIBICIÓN: ¡NUNCA usar llama directa!",
                            text = "Está prohibido calentar un rodamiento con soplete o llama directa. La llama directa ablanda el acero templado, destruyendo el tratamiento térmico, y sobrecalienta localmente el rodamiento, inutilizándolo."
                        )
                    }
                }
            }
            
            // Section 4: Lubricación
            if ((selectedSection == "Todo" || selectedSection == "Lubricación") && 
                (searchQuery.isEmpty() || "lubricación".contains(searchQuery, true) || "grasa".contains(searchQuery, true) || "cantidad".contains(searchQuery, true) || "reposición".contains(searchQuery, true) || "compatibilidad".contains(searchQuery, true))) {
                item {
                    ManualSectionCard(
                        title = "4. Guía de Lubricación y Grasas",
                        subtitle = "Aditivos, llenado y compatibilidad entre espesantes"
                    ) {
                        Text(
                            text = "Aproximadamente el 36% de las fallas de rodamientos se deben a una lubricación inadecuada. La grasa se compone de aceite base (70-95%), espesante (5-30%) y aditivos (antioxidantes, EP para presiones extremas, AW antidesgaste).",
                            fontSize = 13.sp,
                            lineHeight = 18.sp,
                            color = MaterialTheme.colorScheme.onSurface
                        )
                        
                        Spacer(modifier = Modifier.height(10.dp))
                        
                        Text(
                            text = "Cantidad de Grasa Recomendada:",
                            fontSize = 12.sp,
                            fontWeight = FontWeight.Bold,
                            color = MaterialTheme.colorScheme.primary
                        )
                        Spacer(modifier = Modifier.height(4.dp))
                        Text(
                            text = "• Rodamiento: Llenar al 100% de grasa para asegurar que los rodillos queden lubricados desde el primer giro.\n• Espacio libre en el descanso/soporte: Llenar entre 30% y 50% de la cavidad libre para evitar calentamiento por agitación de grasa (para ambientes con mucho polvo o humedad extrema, se puede llenar hasta el 90%).",
                            fontSize = 12.sp,
                            lineHeight = 17.sp
                        )
                        
                        Spacer(modifier = Modifier.height(10.dp))
                        
                        Text(
                            text = "Fórmula de Reposición de Grasa (Gp en gramos):",
                            fontSize = 12.sp,
                            fontWeight = FontWeight.Bold,
                            color = MaterialTheme.colorScheme.primary
                        )
                        Spacer(modifier = Modifier.height(4.dp))
                        SpecRow("Reposición lateral:", "Gp = 0,005 * D * B")
                        SpecRow("Reposición central (ranura W33):", "Gp = 0,002 * D * B")
                        Text("(Donde D es el diámetro exterior en mm y B es el ancho en mm)", fontSize = 11.sp, color = Color.Gray)
                        
                        Spacer(modifier = Modifier.height(10.dp))
                        
                        WarningCard(
                            title = "PRECAUCIÓN: Incompatibilidad de Grasas",
                            text = "¡NUNCA mezcle grasas incompatibles! Espesantes incompatibles (como litio y poliurea) provocan que la mezcla se licúe, perdiendo consistencia rápidamente y fugándose del soporte, destruyendo la lubricación. Si se cambia de grasa, se debe remover y limpiar al 100% el rodamiento antes de aplicar la nueva."
                        )
                    }
                }
            }
            
            // Section 5: Inspección
            if ((selectedSection == "Todo" || selectedSection == "Inspección") && 
                (searchQuery.isEmpty() || "inspección".contains(searchQuery, true) || "ruido".contains(searchQuery, true) || "vibración".contains(searchQuery, true) || "temperatura".contains(searchQuery, true))) {
                item {
                    ManualSectionCard(
                        title = "5. Inspección, Ruido y Vibración",
                        subtitle = "Monitoreo de condición proactivo en rodamiento"
                    ) {
                        Text(
                            text = "El monitoreo de condición permite detectar fallas antes de que ocurra una avería catastrófica. Las tres variables principales son Ruido, Temperatura y Vibración:",
                            fontSize = 13.sp,
                            lineHeight = 18.sp,
                            color = MaterialTheme.colorScheme.onSurface
                        )
                        
                        Spacer(modifier = Modifier.height(10.dp))
                        
                        Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                            BulletItem("Inspección de Ruido:", "Utilizar estetoscopio. Un rodamiento sano produce un 'ronroneo' suave y continuo. Ruidos estridentes, chirridos o golpes intermitentes indican falta de grasa, juego insuficiente o mella en la pista de rodadura.")
                            BulletItem("Inspección de Temperatura:", "Mapear con termómetros. Por lo general, el soporte exterior suele estar 5°C más frío que el aro exterior del rodamiento, y 10°C más frío que el aro interior.")
                            BulletItem("Monitoreo de Vibración:", "Las frecuencias bajas (0-2 kHz) del espectro indican desalineación, soltura de pernos o desbalanceo; frecuencias altas (2-50 kHz) o muy altas (>50 kHz) revelan microfisuras y descascarillado temprano en pistas.")
                        }
                    }
                }
            }
        }
    }
}

// ==========================================
// DECORATIVE & FORMATTING WIDGETS FOR MANUALS
// ==========================================

@Composable
fun ManualSectionCard(
    title: String,
    subtitle: String,
    content: @Composable () -> Unit
) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface),
        shape = RoundedCornerShape(12.dp),
        border = BorderStroke(1.dp, MaterialTheme.colorScheme.outline)
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Text(
                text = title,
                fontSize = 15.sp,
                fontWeight = FontWeight.Black,
                color = MaterialTheme.colorScheme.primary
            )
            Text(
                text = subtitle,
                fontSize = 11.sp,
                color = Color.Gray,
                fontWeight = FontWeight.Bold,
                modifier = Modifier.padding(bottom = 12.dp)
            )
            
            HorizontalDivider(modifier = Modifier.padding(bottom = 12.dp))
            
            content()
        }
    }
}

@Composable
fun BulletItem(label: String, desc: String) {
    Column {
        Row(
            verticalAlignment = Alignment.Top,
            horizontalArrangement = Arrangement.spacedBy(6.dp),
            modifier = Modifier.padding(start = 4.dp)
        ) {
            Text("•", fontSize = 14.sp, fontWeight = FontWeight.Bold, color = MaterialTheme.colorScheme.primary)
            Text(
                text = label,
                fontSize = 12.sp,
                fontWeight = FontWeight.Black,
                color = MaterialTheme.colorScheme.onSurface
            )
        }
        Text(
            text = desc,
            fontSize = 12.sp,
            color = Color.Gray,
            modifier = Modifier.padding(start = 16.dp, bottom = 4.dp)
        )
    }
}

@Composable
fun ConceptCard(title: String, text: String) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = Color(0xFFFEF3C7)), // M3 Gold tint
        shape = RoundedCornerShape(8.dp),
        border = BorderStroke(1.dp, Color(0xFFF59E0B))
    ) {
        Row(
            modifier = Modifier.padding(12.dp),
            horizontalArrangement = Arrangement.spacedBy(10.dp),
            verticalAlignment = Alignment.Top
        ) {
            Icon(
                imageVector = Icons.Default.Lightbulb,
                contentDescription = "Concepto Clave",
                tint = Color(0xFFD97706),
                modifier = Modifier.size(20.dp)
            )
            Column(verticalArrangement = Arrangement.spacedBy(2.dp)) {
                Text(
                    text = title,
                    fontSize = 12.sp,
                    fontWeight = FontWeight.Black,
                    color = Color(0xFF92400E)
                )
                Text(
                    text = text,
                    fontSize = 11.sp,
                    lineHeight = 15.sp,
                    color = Color(0xFF78350F)
                )
            }
        }
    }
}

@Composable
fun WarningCard(title: String, text: String) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = Color(0xFFFEE2E2)), // M3 soft red/orange tint
        shape = RoundedCornerShape(8.dp),
        border = BorderStroke(1.dp, Color(0xFFF87171))
    ) {
        Row(
            modifier = Modifier.padding(12.dp),
            horizontalArrangement = Arrangement.spacedBy(10.dp),
            verticalAlignment = Alignment.Top
        ) {
            Icon(
                imageVector = Icons.Default.Warning,
                contentDescription = "Precaución",
                tint = Color(0xFFDC2626),
                modifier = Modifier.size(20.dp)
            )
            Column(verticalArrangement = Arrangement.spacedBy(2.dp)) {
                Text(
                    text = title,
                    fontSize = 12.sp,
                    fontWeight = FontWeight.Black,
                    color = Color(0xFF991B1B)
                )
                Text(
                    text = text,
                    fontSize = 11.sp,
                    lineHeight = 15.sp,
                    color = Color(0xFF7F1D1D)
                )
            }
        }
    }
}

@Composable
fun TechNoteCard(text: String) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = Color(0xFFEFF6FF)), // Soft blue tint
        shape = RoundedCornerShape(8.dp),
        border = BorderStroke(1.dp, Color(0xFF60A5FA))
    ) {
        Row(
            modifier = Modifier.padding(12.dp),
            horizontalArrangement = Arrangement.spacedBy(10.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Icon(
                imageVector = Icons.Default.Info,
                contentDescription = "Nota Técnica",
                tint = Color(0xFF2563EB),
                modifier = Modifier.size(18.dp)
            )
            Text(
                text = text,
                fontSize = 11.sp,
                lineHeight = 15.sp,
                color = Color(0xFF1E40AF),
                modifier = Modifier.weight(1f)
            )
        }
    }
}

@Composable
fun SpecRow(label: String, value: String) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 2.dp),
        horizontalArrangement = Arrangement.SpaceBetween,
        verticalAlignment = Alignment.CenterVertically
    ) {
        Text(label, fontSize = 12.sp, color = Color.Gray, fontWeight = FontWeight.Medium)
        Text(value, fontSize = 12.sp, fontWeight = FontWeight.Bold, color = MaterialTheme.colorScheme.onSurface)
    }
}
