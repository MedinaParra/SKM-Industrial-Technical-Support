package com.example.data.model

import androidx.room.Entity
import androidx.room.PrimaryKey
import androidx.room.TypeConverter
import com.squareup.moshi.JsonClass
import com.squareup.moshi.Moshi
import com.squareup.moshi.Types

@Entity(tableName = "bearings")
@JsonClass(generateAdapter = true)
data class BearingSpec(
    @PrimaryKey val id: String,
    val designation: String,
    val brand: String, // SKF, Timken, FAG, DODGE, NSK
    val boreDiameterMm: Double, // d (mm)
    val outerDiameterMm: Double, // D (mm)
    val widthMm: Double, // B (mm)
    val dynamicLoadKn: Double, // C
    val staticLoadKn: Double, // C0
    val limitingSpeedRpm: Double,
    val type: String, // e.g., "Oscilante de Rodillos" (Spherical Roller), "Bolas", etc.
    // Radial Internal Clearance limits (in mm) for Normal and C3
    val clearanceMinNormal: Double,
    val clearanceMaxNormal: Double,
    val clearanceMinC3: Double,
    val clearanceMaxC3: Double,
    val clearanceMinC4: Double,
    val clearanceMaxC4: Double,
    // Mounting specifications for Tapered Bore (Cono 1:12 or 1:30)
    val recommendedReductionMin: Double, // mm
    val recommendedReductionMax: Double, // mm
    val axialDriveUp1To12Min: Double, // mm (for taper 1:12)
    val axialDriveUp1To12Max: Double, // mm
    val axialDriveUp1To30Min: Double = 0.0, // mm (for taper 1:30)
    val axialDriveUp1To30Max: Double = 0.0, // mm
    val minLockingAngleDegrees: Double = 0.0,
    val maxLockingAngleDegrees: Double = 0.0,
    val cadUrl: String = ""
)

@Entity(tableName = "housings")
@JsonClass(generateAdapter = true)
data class HousingSpec(
    @PrimaryKey val designation: String,
    val brand: String, // SKF, FAG, DODGE, NSK
    val L_mm: Double,  // Length
    val H_mm: Double,  // Shaft center height
    val H1_mm: Double, // Overall height
    val W_mm: Double,  // Width
    val boltDistanceMm: Double,
    val weightKg: Double,
    val compatibleBearingsCsv: String, // Comma-separated list of bearing designations
    val compatibleSleevesCsv: String,  // Comma-separated list of sleeve designations (e.g. H311, H315)
    val cadUrl: String
)

@Entity(tableName = "mounting_reports")
data class MountingReport(
    @PrimaryKey(autoGenerate = true) val id: Long = 0,
    val clientName: String,
    val machineTag: String,
    val technicianName: String,
    val date: String,
    val bearingDesignation: String,
    val brand: String,
    val sleeveType: String, // e.g. "H 315", "Eje Cónico"
    val initialClearanceMm: Double,
    val targetReductionMinMm: Double,
    val targetReductionMaxMm: Double,
    val finalClearanceMm: Double,
    val clearanceReductionMm: Double,
    val axialDriveUpMm: Double,
    val lockNutAngleDegrees: Double,
    val status: String, // "Aprobado", "Fuera de Tolerancia"
    val notes: String
)
