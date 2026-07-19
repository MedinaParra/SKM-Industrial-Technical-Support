package com.example

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.activity.viewModels
import androidx.compose.animation.*
import androidx.compose.animation.core.*
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.PathEffect
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.graphics.drawscope.rotate
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.ui.screens.CalculatorScreen
import com.example.ui.screens.DashboardScreen
import com.example.ui.screens.KnowledgeBaseScreen
import com.example.ui.screens.ReportsScreen
import com.example.ui.theme.MyApplicationTheme
import com.example.ui.viewmodel.BearingViewModel

class MainActivity : ComponentActivity() {
    
    private val viewModel: BearingViewModel by viewModels()

    @OptIn(ExperimentalMaterial3Api::class)
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContent {
            MyApplicationTheme {
                var showSplash by remember { mutableStateOf(true) }
                
                if (showSplash) {
                    SkmSplashScreen(onFinished = { showSplash = false })
                } else {
                    var selectedTab by remember { mutableStateOf(0) }
                    
                    Scaffold(
                    modifier = Modifier.fillMaxSize(),
                    topBar = {
                        Surface(
                            color = MaterialTheme.colorScheme.surface,
                            tonalElevation = 2.dp,
                            modifier = Modifier
                                .fillMaxWidth()
                                .statusBarsPadding()
                        ) {
                            Row(
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .padding(horizontal = 16.dp, vertical = 12.dp),
                                horizontalArrangement = Arrangement.SpaceBetween,
                                verticalAlignment = Alignment.CenterVertically
                            ) {
                                Row(
                                    verticalAlignment = Alignment.CenterVertically,
                                    horizontalArrangement = Arrangement.spacedBy(12.dp)
                                ) {
                                    SkmLogo()
                                    Column {
                                        Text(
                                            text = "SKM Industrial",
                                            fontSize = 16.sp,
                                            fontWeight = FontWeight.Black,
                                            color = MaterialTheme.colorScheme.onSurface
                                        )
                                        Text(
                                            text = "TECHNICAL SUITE",
                                            fontSize = 9.sp,
                                            fontWeight = FontWeight.Bold,
                                            color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.6f),
                                            letterSpacing = 1.2.sp
                                        )
                                    }
                                }
                                Row(
                                    verticalAlignment = Alignment.CenterVertically,
                                    horizontalArrangement = Arrangement.spacedBy(8.dp)
                                ) {
                                    Surface(
                                        color = Color(0xFFDCFCE7),
                                        shape = RoundedCornerShape(100.dp)
                                    ) {
                                        Row(
                                            modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp),
                                            verticalAlignment = Alignment.CenterVertically,
                                            horizontalArrangement = Arrangement.spacedBy(4.dp)
                                        ) {
                                            Icon(
                                                imageVector = Icons.Default.OfflinePin,
                                                contentDescription = "Offline Mode",
                                                tint = Color(0xFF15803D),
                                                modifier = Modifier.size(12.dp)
                                            )
                                            Text(
                                                text = "OFFLINE",
                                                color = Color(0xFF15803D),
                                                fontSize = 9.sp,
                                                fontWeight = FontWeight.Black
                                            )
                                        }
                                    }
                                    Icon(
                                        imageVector = Icons.Default.AccountCircle,
                                        contentDescription = "Perfil",
                                        tint = MaterialTheme.colorScheme.onSurface,
                                        modifier = Modifier.size(28.dp)
                                    )
                                }
                            }
                        }
                    },
                    bottomBar = {
                        NavigationBar(
                            containerColor = MaterialTheme.colorScheme.surface,
                            tonalElevation = 8.dp
                        ) {
                            NavigationBarItem(
                                selected = selectedTab == 0,
                                onClick = { selectedTab = 0 },
                                icon = { Icon(Icons.Default.Dashboard, contentDescription = "Inicio") },
                                label = { Text("Inicio", fontSize = 11.sp, fontWeight = FontWeight.Bold) }
                            )
                            NavigationBarItem(
                                selected = selectedTab == 1,
                                onClick = { selectedTab = 1 },
                                icon = { Icon(Icons.Default.PrecisionManufacturing, contentDescription = "Especificaciones") },
                                label = { Text("Catálogo", fontSize = 11.sp, fontWeight = FontWeight.Bold) }
                            )
                            NavigationBarItem(
                                selected = selectedTab == 2,
                                onClick = { selectedTab = 2 },
                                icon = { Icon(Icons.Default.Calculate, contentDescription = "Calculadora") },
                                label = { Text("Cálculo", fontSize = 11.sp, fontWeight = FontWeight.Bold) }
                            )
                            NavigationBarItem(
                                selected = selectedTab == 3,
                                onClick = { selectedTab = 3 },
                                icon = { Icon(Icons.Default.Assignment, contentDescription = "Reportes") },
                                label = { Text("Reportes", fontSize = 11.sp, fontWeight = FontWeight.Bold) }
                            )
                        }
                    }
                ) { innerPadding ->
                    Box(
                        modifier = Modifier
                            .fillMaxSize()
                            .padding(innerPadding)
                    ) {
                        AnimatedContent(
                            targetState = selectedTab,
                            transitionSpec = {
                                fadeIn() togetherWith fadeOut()
                            },
                            label = "TabTransition"
                        ) { targetTab ->
                            when (targetTab) {
                                0 -> DashboardScreen(
                                    viewModel = viewModel,
                                    onNavigateToTab = { selectedTab = it }
                                )
                                1 -> KnowledgeBaseScreen(
                                    viewModel = viewModel,
                                    onNavigateToTab = { selectedTab = it }
                                )
                                2 -> CalculatorScreen(
                                    viewModel = viewModel,
                                    onNavigateToTab = { selectedTab = it }
                                )
                                3 -> ReportsScreen(
                                    viewModel = viewModel
                                )
                            }
                        }
                    }
                    }
                }
            }
        }
    }
}

@Composable
fun SkmLogo(modifier: Modifier = Modifier) {
    Image(
        painter = painterResource(R.drawable.skm_logo_symbol),
        contentDescription = "Logo SKM Industrial",
        contentScale = ContentScale.Fit,
        modifier = modifier.size(40.dp)
    )
}

@Composable
fun SkmLogoSymbol(
    modifier: Modifier = Modifier,
    rotationAngle: Float = 0f,
    gearRotationAngle: Float = 0f
) {
    Canvas(modifier = modifier) {
        val w = size.width
        val h = size.height
        val cx = w / 2f
        val cy = h / 2f
        val r = w / 2f

        // 1. Outer solid black/dark corporate circle
        drawCircle(
            color = Color(0xFF1E293B),
            radius = r * 0.95f,
            center = Offset(cx, cy),
            style = Stroke(width = r * 0.05f)
        )

        // 2. White background filled inside
        drawCircle(
            color = Color.White,
            radius = r * 0.92f,
            center = Offset(cx, cy)
        )

        // We rotate the inner dashed ring and crescent to satisfy the "circle spinning" request
        rotate(rotationAngle, pivot = Offset(cx, cy)) {
            // 3. Dashed black concentric line inside
            val dashLength = r * 0.06f
            val dashGap = r * 0.06f
            drawCircle(
                color = Color(0xFF1E293B),
                radius = r * 0.83f,
                center = Offset(cx, cy),
                style = Stroke(
                    width = r * 0.015f,
                    pathEffect = PathEffect.dashPathEffect(
                        floatArrayOf(dashLength, dashGap),
                        0f
                    )
                )
            )

            // 4. Large Orange Crescent Shape
            // We draw a filled orange circle
            drawCircle(
                color = Color(0xFFEF8321), // Official SKM Orange
                radius = r * 0.72f,
                center = Offset(cx, cy)
            )

            // Overlay a white circle slightly offset to the left to carve out the crescent
            drawCircle(
                color = Color.White,
                radius = r * 0.65f,
                center = Offset(cx - r * 0.22f, cy)
            )

            // 5. Inner Orange Circle centered at the bite of the crescent
            drawCircle(
                color = Color(0xFFEF8321),
                radius = r * 0.35f,
                center = Offset(cx - r * 0.22f, cy)
            )
        }

        // 6. Central Black Gear (cog wheel) - we rotate it on its own pivot inside!
        rotate(rotationAngle, pivot = Offset(cx, cy)) {
            val gearCx = cx - r * 0.22f
            val gearCy = cy
            
            // Draw gear background black center
            rotate(gearRotationAngle, pivot = Offset(gearCx, gearCy)) {
                val gearR = r * 0.20f
                drawCircle(
                    color = Color(0xFF1E293B),
                    radius = gearR,
                    center = Offset(gearCx, gearCy)
                )

                // Gear teeth
                val toothCount = 8
                val toothWidth = gearR * 0.45f
                val toothHeight = gearR * 0.35f
                for (i in 0 until toothCount) {
                    val angleDeg = i * (360f / toothCount)
                    rotate(angleDeg, pivot = Offset(gearCx, gearCy)) {
                        drawRect(
                            color = Color(0xFF1E293B),
                            topLeft = Offset(gearCx - toothWidth / 2f, gearCy - gearR - toothHeight),
                            size = androidx.compose.ui.geometry.Size(toothWidth, toothHeight * 1.6f)
                        )
                    }
                }
            }

            // Central White circle inside the gear
            val gearCxInner = cx - r * 0.22f
            drawCircle(
                color = Color.White,
                radius = r * 0.09f,
                center = Offset(gearCxInner, gearCy)
            )
        }
    }
}

@Composable
fun SkmSplashScreen(onFinished: () -> Unit) {
    // Launch delay to automatically exit the splash screen
    LaunchedEffect(Unit) {
        kotlinx.coroutines.delay(2600)
        onFinished()
    }

    // Set up infinite rotation for the emblem
    val infiniteTransition = rememberInfiniteTransition(label = "SplashRotation")
    val rotation by infiniteTransition.animateFloat(
        initialValue = 0f,
        targetValue = 360f,
        animationSpec = infiniteRepeatable(
            animation = tween(4000, easing = LinearEasing),
            repeatMode = RepeatMode.Restart
        ),
        label = "LogoRotation"
    )
    
    val gearRotation by infiniteTransition.animateFloat(
        initialValue = 360f,
        targetValue = 0f,
        animationSpec = infiniteRepeatable(
            animation = tween(2500, easing = LinearEasing),
            repeatMode = RepeatMode.Restart
        ),
        label = "GearRotation"
    )

    // Layout
    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(Color(0xFFF8FAFC)), // Premium bright background
        contentAlignment = Alignment.Center
    ) {
        Column(
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.Center,
            modifier = Modifier.padding(24.dp)
        ) {
            Image(
                painter = painterResource(R.drawable.skm_logo_horizontal),
                contentDescription = "SKM Industrial Ltda.",
                contentScale = ContentScale.Fit,
                modifier = Modifier
                    .fillMaxWidth()
                    .heightIn(max = 220.dp)
            )
            
            Spacer(modifier = Modifier.height(32.dp))
            
            Spacer(modifier = Modifier.height(40.dp))
            
            // Thin elegant orange progress bar
            CircularProgressIndicator(
                modifier = Modifier.size(24.dp),
                color = Color(0xFFEF8321),
                strokeWidth = 2.dp
            )
            
            Spacer(modifier = Modifier.height(16.dp))
            
            Text(
                text = "CARGANDO SUITE TÉCNICA",
                color = Color(0xFF94A3B8),
                fontSize = 10.sp,
                fontWeight = FontWeight.Bold,
                letterSpacing = 1.5.sp
            )
        }
    }
}
