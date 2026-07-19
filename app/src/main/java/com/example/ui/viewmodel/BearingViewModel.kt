package com.example.ui.viewmodel

import android.app.Application
import android.content.Context
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.example.data.api.GeminiApiClient
import com.example.data.local.BearingDatabase
import com.example.data.model.BearingSpec
import com.example.data.model.HousingSpec
import com.example.data.model.MountingReport
import com.example.data.repository.BearingRepository
import com.example.util.PdfGenerator
import kotlinx.coroutines.flow.*
import kotlinx.coroutines.launch
import java.io.File
import java.text.SimpleDateFormat
import java.util.*

class BearingViewModel(application: Application) : AndroidViewModel(application) {

    private val repository: BearingRepository

    // Search & Filter UI States
    val bearingSearchQuery = MutableStateFlow("")
    val housingSearchQuery = MutableStateFlow("")

    val selectedBrandFilter = MutableStateFlow("Todas") // "Todas", "SKF", "FAG", "Timken", "DODGE", "NSK"
    val selectedHousingBrandFilter = MutableStateFlow("Todas") // "Todas", "SKF", "FAG", "DODGE", "NSK"

    // Live Lists
    val bearingsList: StateFlow<List<BearingSpec>>
    val housingsList: StateFlow<List<HousingSpec>>
    val reportsList: StateFlow<List<MountingReport>>

    // Selected items
    val selectedBearing = MutableStateFlow<BearingSpec?>(null)
    val selectedHousing = MutableStateFlow<HousingSpec?>(null)

    // Seeding/Loading State
    val isDbSeeding = MutableStateFlow(true)

    // PDF Exporting state
    val generatedPdfFile = MutableStateFlow<File?>(null)

    // Chat AI State
    val chatHistory = MutableStateFlow<List<Pair<String, String>>>(emptyList()) // Pair of (sender, text)
    val isAiLoading = MutableStateFlow(false)

    // Dynamic Calculator inputs
    val calcNominalBore = MutableStateFlow("75") // mm
    val calcSleeveType = MutableStateFlow("Cono 1:12 (H)") // "Cono 1:12 (H)" or "Cono 1:30 (K)"
    val calcInitialClearance = MutableStateFlow("0.060") // mm
    val calcFinalClearance = MutableStateFlow("0.025") // mm
    val calcClearanceClass = MutableStateFlow("Normal") // "C2", "Normal", "C3", "C4"

    // Dynamic Tolerances inputs
    val tolNominalSize = MutableStateFlow("50.0") // mm
    val tolFitType = MutableStateFlow("Eje m5 (Carga Pesada/Rotativo)") 
    // "Eje m5 (Carga Pesada/Rotativo)", "Eje k6 (Carga Normal)", "Eje g6 (Desplazamiento Fácil)", "Alojamiento H7 (Estándar)", "Alojamiento J7"

    // Dynamic Relubrication inputs
    val relubBearingType = MutableStateFlow("Rodillos Oscilantes") // "Rodillos Oscilantes", "Bolas de Ranura Profunda", "Rodillos Cilíndricos"
    val relubRpm = MutableStateFlow("1500")
    val relubTemp = MutableStateFlow("70") // °C
    val relubBore = MutableStateFlow("75") // mm

    init {
        val database = BearingDatabase.getDatabase(application)
        repository = BearingRepository(database.bearingDao())

        // Seed data
        viewModelScope.launch {
            repository.seedDatabaseIfEmpty()
            isDbSeeding.value = false
        }

        // Connect Search & Filter for Bearings
        bearingsList = combine(
            bearingSearchQuery,
            selectedBrandFilter
        ) { query, brand ->
            Pair(query, brand)
        }.flatMapLatest { (query, brand) ->
            val flow = if (query.isEmpty()) repository.allBearings else repository.searchBearings(query)
            flow.map { list ->
                if (brand == "Todas") list else list.filter { it.brand.equals(brand, ignoreCase = true) }
            }
        }.stateIn(viewModelScope, SharingStarted.WhileSubscribed(5000), emptyList())

        // Connect Search & Filter for Housings
        housingsList = combine(
            housingSearchQuery,
            selectedHousingBrandFilter
        ) { query, brand ->
            Pair(query, brand)
        }.flatMapLatest { (query, brand) ->
            val flow = if (query.isEmpty()) repository.allHousings else repository.searchHousings(query)
            flow.map { list ->
                if (brand == "Todas") list else list.filter { it.brand.equals(brand, ignoreCase = true) }
            }
        }.stateIn(viewModelScope, SharingStarted.WhileSubscribed(5000), emptyList())

        reportsList = repository.allReports.stateIn(viewModelScope, SharingStarted.WhileSubscribed(5000), emptyList())
    }

    // AI Helper method
    fun askAi(question: String) {
        if (question.isBlank()) return
        val currentHistory = chatHistory.value.toMutableList()
        currentHistory.add("user" to question)
        chatHistory.value = currentHistory
        
        isAiLoading.value = true
        viewModelScope.launch {
            val answer = GeminiApiClient.askAssistant(question, selectedBearing.value)
            val updatedHistory = chatHistory.value.toMutableList()
            updatedHistory.add("ai" to answer)
            chatHistory.value = updatedHistory
            isAiLoading.value = false
        }
    }

    fun clearChat() {
        chatHistory.value = emptyList()
    }

    // PDF Report Generator trigger
    fun createReport(
        client: String,
        machineTag: String,
        technician: String,
        notes: String
    ) {
        viewModelScope.launch {
            val bearing = selectedBearing.value
            val initial = calcInitialClearance.value.toDoubleOrNull() ?: 0.060
            val final = calcFinalClearance.value.toDoubleOrNull() ?: 0.025
            
            // Calculate actual values
            val actualReduction = initial - final
            
            val bearingDesignation = bearing?.designation ?: "Personalizado (d = ${calcNominalBore.value} mm)"
            val brand = bearing?.brand ?: "SKM"
            val sleeve = if (bearing != null) "H" else calcSleeveType.value

            // Recommended values from database or calculations
            val recRedMin = bearing?.recommendedReductionMin ?: calculateEstimatedReductionMin(calcNominalBore.value.toDoubleOrNull() ?: 75.0)
            val recRedMax = bearing?.recommendedReductionMax ?: calculateEstimatedReductionMax(calcNominalBore.value.toDoubleOrNull() ?: 75.0)
            val axialDriveUp = bearing?.axialDriveUp1To12Min ?: calculateEstimatedAxialDriveUp(calcNominalBore.value.toDoubleOrNull() ?: 75.0)
            
            val lockAngle = bearing?.minLockingAngleDegrees ?: calculateEstimatedLockNutAngle(calcNominalBore.value.toDoubleOrNull() ?: 75.0)

            val status = if (actualReduction in recRedMin..recRedMax) "Aprobado" else "Fuera de Tolerancia"

            val dateFormat = SimpleDateFormat("yyyy-MM-dd HH:mm", Locale.getDefault())
            val currentDate = dateFormat.format(Date())

            val report = MountingReport(
                clientName = client.ifEmpty { "SKM Industrial S.A." },
                machineTag = machineTag.ifEmpty { "Bomba de Pulpa MP-104" },
                technicianName = technician.ifEmpty { "Técnico Especialista SKM" },
                date = currentDate,
                bearingDesignation = bearingDesignation,
                brand = brand,
                sleeveType = sleeve,
                initialClearanceMm = initial,
                targetReductionMinMm = recRedMin,
                targetReductionMaxMm = recRedMax,
                finalClearanceMm = final,
                clearanceReductionMm = actualReduction,
                axialDriveUpMm = axialDriveUp,
                lockNutAngleDegrees = lockAngle,
                status = status,
                notes = notes.ifEmpty { "Montaje realizado de acuerdo al manual SKF utilizando galgas de precisión. Eje verificado y lubricación inicial aplicada." }
            )

            val reportId = repository.insertReport(report)
            val generatedFile = PdfGenerator.generateMountingReportPdf(getApplication(), report.copy(id = reportId))
            generatedPdfFile.value = generatedFile
        }
    }

    fun deleteReport(report: MountingReport) {
        viewModelScope.launch {
            repository.deleteReport(report)
        }
    }

    // Helper functions to estimate recommended values if custom size entered
    fun calculateEstimatedReductionMin(bore: Double): Double {
        return when {
            bore <= 40 -> 0.020
            bore <= 50 -> 0.025
            bore <= 65 -> 0.030
            bore <= 80 -> 0.035
            bore <= 100 -> 0.045
            bore <= 120 -> 0.050
            bore <= 140 -> 0.060
            else -> 0.070
        }
    }

    fun calculateEstimatedReductionMax(bore: Double): Double {
        return calculateEstimatedReductionMin(bore) + 0.005
    }

    fun calculateEstimatedAxialDriveUp(bore: Double): Double {
        return when {
            bore <= 40 -> 0.30
            bore <= 50 -> 0.35
            bore <= 65 -> 0.40
            bore <= 80 -> 0.45
            bore <= 100 -> 0.50
            bore <= 120 -> 0.65
            bore <= 140 -> 0.75
            else -> 0.90
        }
    }

    fun calculateEstimatedLockNutAngle(bore: Double): Double {
        return when {
            bore <= 50 -> 100.0
            bore <= 80 -> 120.0
            bore <= 120 -> 140.0
            else -> 160.0
        }
    }

    // Shaft Fit Calculations
    fun calculateFitTolerances(): FitResult {
        val size = tolNominalSize.value.toDoubleOrNull() ?: 50.0
        val type = tolFitType.value
        
        // Return structured tolerances recommendations (in microns)
        return when {
            type.contains("m5") -> FitResult(
                fitClass = "m5",
                description = "Interferencia / Carga Pesada o de Choque en Eje Giratorio",
                upperDevMicrons = 20.0,
                lowerDevMicrons = 9.0,
                recommendedLube = "Grasa de alta viscosidad EP2 o Aceite sintético"
            )
            type.contains("k6") -> FitResult(
                fitClass = "k6",
                description = "Interferencia Leve / Carga Normal o Rotativa en Eje",
                upperDevMicrons = 18.0,
                lowerDevMicrons = 2.0,
                recommendedLube = "Grasa Multipropósito NLGI 2"
            )
            type.contains("g6") -> FitResult(
                fitClass = "g6",
                description = "Juego / Desplazamiento Fácil o Ajuste de Transición",
                upperDevMicrons = -9.0,
                lowerDevMicrons = -25.0,
                recommendedLube = "Lubricación con película de grasa fina antidesgaste"
            )
            type.contains("H7") -> FitResult(
                fitClass = "H7",
                description = "Alojamiento Estándar (Ajuste Deslizante)",
                upperDevMicrons = 25.0,
                lowerDevMicrons = 0.0,
                recommendedLube = "Grasa sellante de cavidad para prevenir corrosión"
            )
            type.contains("J7") -> FitResult(
                fitClass = "J7",
                description = "Alojamiento Ajustado (Transición Media)",
                upperDevMicrons = 12.0,
                lowerDevMicrons = -13.0,
                recommendedLube = "Grasa sellante anticorrosión"
            )
            else -> FitResult("m5", "Ajuste por Defecto", 20.0, 9.0, "Grasa EP2")
        }
    }

    // Relubrication calculations
    fun calculateRelubrication(): RelubResult {
        val d = relubBore.value.toDoubleOrNull() ?: 75.0
        val rpm = relubRpm.value.toDoubleOrNull() ?: 1500.0
        val temp = relubTemp.value.toDoubleOrNull() ?: 70.0
        val type = relubBearingType.value

        // Standard SKF formula:
        // Quantity of grease (Gp) = d * B * 0.005 (grams)
        // Let's estimate a typical width B as ~0.4 * d
        val estimatedWidth = d * 0.4
        val quantityGrams = Math.round(d * estimatedWidth * 0.005 * 10.0) / 10.0

        // Estimated frequency Tf (hours) using SKF charts:
        // Tf = K * (14,000,000 / (rpm * sqrt(d))) - adjustment factors
        val baseFactor = when (type) {
            "Rodillos Oscilantes" -> 1.0
            "Rodillos Cilíndricos" -> 5.0
            else -> 10.0 // Bolas
        }
        
        var baseHours = baseFactor * (1000000.0 / (rpm + 50.0))
        if (temp > 70.0) {
            // Half the life for every 15°C above 70°C
            val tempExcess = temp - 70.0
            val penaltyFactor = Math.pow(0.5, tempExcess / 15.0)
            baseHours *= penaltyFactor
        }
        
        val hoursRounded = Math.round(Math.max(baseHours, 50.0) / 50.0) * 50

        return RelubResult(
            quantityGrams = Math.max(quantityGrams, 2.0),
            intervalHours = hoursRounded.toInt(),
            recommendedGreaseType = when {
                temp > 100.0 -> "SKF LGHP 2 (Alta Temperatura / Alta Velocidad)"
                type.contains("Oscilantes") -> "SKF LGEP 2 (Cargas Elevadas / Extrema Presión)"
                else -> "SKF LGMT 2 (Multipropósito General)"
            }
        )
    }
}

data class FitResult(
    val fitClass: String,
    val description: String,
    val upperDevMicrons: Double,
    val lowerDevMicrons: Double,
    val recommendedLube: String
)

data class RelubResult(
    val quantityGrams: Double,
    val intervalHours: Int,
    val recommendedGreaseType: String
)
