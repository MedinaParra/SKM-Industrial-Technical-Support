package com.example.data.repository

import com.example.data.local.BearingDao
import com.example.data.model.BearingSpec
import com.example.data.model.HousingSpec
import com.example.data.model.MountingReport
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.flow.onEach

class BearingRepository(private val bearingDao: BearingDao) {

    val allBearings: Flow<List<BearingSpec>> = bearingDao.getAllBearings()
    val allHousings: Flow<List<HousingSpec>> = bearingDao.getAllHousings()
    val allReports: Flow<List<MountingReport>> = bearingDao.getAllReports()

    fun searchBearings(query: String): Flow<List<BearingSpec>> = bearingDao.searchBearings(query)
    fun searchHousings(query: String): Flow<List<HousingSpec>> = bearingDao.searchHousings(query)

    suspend fun getBearingById(id: String): BearingSpec? = bearingDao.getBearingById(id)

    suspend fun insertReport(report: MountingReport): Long = bearingDao.insertReport(report)
    suspend fun deleteReport(report: MountingReport) = bearingDao.deleteReport(report)

    // Method to seed data if empty
    suspend fun seedDatabaseIfEmpty() {
        // Check bearings
        val currentBearings = bearingDao.getAllBearings().first()
        if (currentBearings.isEmpty()) {
            val seedBearings = listOf(
                BearingSpec(
                    id = "22209K",
                    designation = "22209 EK",
                    brand = "SKF",
                    boreDiameterMm = 45.0,
                    outerDiameterMm = 85.0,
                    widthMm = 23.0,
                    dynamicLoadKn = 102.0,
                    staticLoadKn = 98.0,
                    limitingSpeedRpm = 8500.0,
                    type = "Rodillos Oscilantes (Cono 1:12)",
                    clearanceMinNormal = 0.035,
                    clearanceMaxNormal = 0.050,
                    clearanceMinC3 = 0.050,
                    clearanceMaxC3 = 0.065,
                    clearanceMinC4 = 0.065,
                    clearanceMaxC4 = 0.080,
                    recommendedReductionMin = 0.025,
                    recommendedReductionMax = 0.030,
                    axialDriveUp1To12Min = 0.35,
                    axialDriveUp1To12Max = 0.40,
                    cadUrl = "https://www.skf.com/group/products/bearings-units-housings/spherical-roller-bearings/productid-22209%20EK"
                ),
                BearingSpec(
                    id = "22211K",
                    designation = "22211 EK",
                    brand = "SKF",
                    boreDiameterMm = 55.0,
                    outerDiameterMm = 100.0,
                    widthMm = 25.0,
                    dynamicLoadKn = 125.0,
                    staticLoadKn = 137.0,
                    limitingSpeedRpm = 7500.0,
                    type = "Rodillos Oscilantes (Cono 1:12)",
                    clearanceMinNormal = 0.040,
                    clearanceMaxNormal = 0.055,
                    clearanceMinC3 = 0.055,
                    clearanceMaxC3 = 0.075,
                    clearanceMinC4 = 0.075,
                    clearanceMaxC4 = 0.095,
                    recommendedReductionMin = 0.030,
                    recommendedReductionMax = 0.035,
                    axialDriveUp1To12Min = 0.40,
                    axialDriveUp1To12Max = 0.45,
                    cadUrl = "https://www.skf.com/group/products/bearings-units-housings/spherical-roller-bearings/productid-22211%20EK"
                ),
                BearingSpec(
                    id = "22213EK",
                    designation = "22213 EK",
                    brand = "SKF",
                    boreDiameterMm = 65.0,
                    outerDiameterMm = 120.0,
                    widthMm = 31.0,
                    dynamicLoadKn = 193.0,
                    staticLoadKn = 216.0,
                    limitingSpeedRpm = 6300.0,
                    type = "Rodillos Oscilantes (Cono 1:12)",
                    clearanceMinNormal = 0.040,
                    clearanceMaxNormal = 0.055,
                    clearanceMinC3 = 0.055,
                    clearanceMaxC3 = 0.075,
                    clearanceMinC4 = 0.075,
                    clearanceMaxC4 = 0.095,
                    recommendedReductionMin = 0.030,
                    recommendedReductionMax = 0.035,
                    axialDriveUp1To12Min = 0.40,
                    axialDriveUp1To12Max = 0.45,
                    cadUrl = "https://www.skf.com/group/products/bearings-units-housings/spherical-roller-bearings/productid-22213%20EK"
                ),
                BearingSpec(
                    id = "22215EK",
                    designation = "22215 EK",
                    brand = "SKF",
                    boreDiameterMm = 75.0,
                    outerDiameterMm = 130.0,
                    widthMm = 31.0,
                    dynamicLoadKn = 212.0,
                    staticLoadKn = 240.0,
                    limitingSpeedRpm = 5600.0,
                    type = "Rodillos Oscilantes (Cono 1:12)",
                    clearanceMinNormal = 0.050,
                    clearanceMaxNormal = 0.070,
                    clearanceMinC3 = 0.070,
                    clearanceMaxC3 = 0.095,
                    clearanceMinC4 = 0.095,
                    clearanceMaxC4 = 0.120,
                    recommendedReductionMin = 0.035,
                    recommendedReductionMax = 0.040,
                    axialDriveUp1To12Min = 0.45,
                    axialDriveUp1To12Max = 0.50,
                    cadUrl = "https://www.skf.com/group/products/bearings-units-housings/spherical-roller-bearings/productid-22215%20EK"
                ),
                BearingSpec(
                    id = "22218EK",
                    designation = "22218 EK",
                    brand = "SKF",
                    boreDiameterMm = 90.0,
                    outerDiameterMm = 160.0,
                    widthMm = 40.0,
                    dynamicLoadKn = 325.0,
                    staticLoadKn = 375.0,
                    limitingSpeedRpm = 4800.0,
                    type = "Rodillos Oscilantes (Cono 1:12)",
                    clearanceMinNormal = 0.060,
                    clearanceMaxNormal = 0.080,
                    clearanceMinC3 = 0.080,
                    clearanceMaxC3 = 0.110,
                    clearanceMinC4 = 0.110,
                    clearanceMaxC4 = 0.140,
                    recommendedReductionMin = 0.045,
                    recommendedReductionMax = 0.055,
                    axialDriveUp1To12Min = 0.50,
                    axialDriveUp1To12Max = 0.60,
                    cadUrl = "https://www.skf.com/group/products/bearings-units-housings/spherical-roller-bearings/productid-22218%20EK"
                ),
                BearingSpec(
                    id = "22220EK",
                    designation = "22220 EK",
                    brand = "SKF",
                    boreDiameterMm = 100.0,
                    outerDiameterMm = 180.0,
                    widthMm = 46.0,
                    dynamicLoadKn = 425.0,
                    staticLoadKn = 490.0,
                    limitingSpeedRpm = 4300.0,
                    type = "Rodillos Oscilantes (Cono 1:12)",
                    clearanceMinNormal = 0.060,
                    clearanceMaxNormal = 0.080,
                    clearanceMinC3 = 0.080,
                    clearanceMaxC3 = 0.110,
                    clearanceMinC4 = 0.110,
                    clearanceMaxC4 = 0.140,
                    recommendedReductionMin = 0.045,
                    recommendedReductionMax = 0.055,
                    axialDriveUp1To12Min = 0.50,
                    axialDriveUp1To12Max = 0.60,
                    cadUrl = "https://www.skf.com/group/products/bearings-units-housings/spherical-roller-bearings/productid-22220%20EK"
                ),
                BearingSpec(
                    id = "22222EK",
                    designation = "22222 EK",
                    brand = "SKF",
                    boreDiameterMm = 110.0,
                    outerDiameterMm = 200.0,
                    widthMm = 53.0,
                    dynamicLoadKn = 560.0,
                    staticLoadKn = 640.0,
                    limitingSpeedRpm = 3800.0,
                    type = "Rodillos Oscilantes (Cono 1:12)",
                    clearanceMinNormal = 0.075,
                    clearanceMaxNormal = 0.100,
                    clearanceMinC3 = 0.100,
                    clearanceMaxC3 = 0.135,
                    clearanceMinC4 = 0.135,
                    clearanceMaxC4 = 0.170,
                    recommendedReductionMin = 0.050,
                    recommendedReductionMax = 0.065,
                    axialDriveUp1To12Min = 0.65,
                    axialDriveUp1To12Max = 0.75,
                    cadUrl = "https://www.skf.com/group/products/bearings-units-housings/spherical-roller-bearings/productid-22222%20EK"
                ),
                // Other Brands: FAG, Timken, NSK, DODGE
                BearingSpec(
                    id = "FAG_22215",
                    designation = "22215-E1-K",
                    brand = "FAG",
                    boreDiameterMm = 75.0,
                    outerDiameterMm = 130.0,
                    widthMm = 31.0,
                    dynamicLoadKn = 216.0,
                    staticLoadKn = 245.0,
                    limitingSpeedRpm = 5700.0,
                    type = "Rodillos Oscilantes (Cono 1:12)",
                    clearanceMinNormal = 0.050,
                    clearanceMaxNormal = 0.070,
                    clearanceMinC3 = 0.070,
                    clearanceMaxC3 = 0.095,
                    clearanceMinC4 = 0.095,
                    clearanceMaxC4 = 0.120,
                    recommendedReductionMin = 0.035,
                    recommendedReductionMax = 0.040,
                    axialDriveUp1To12Min = 0.45,
                    axialDriveUp1To12Max = 0.50,
                    cadUrl = "https://www.schaeffler.com/en/products-and-solutions/"
                ),
                BearingSpec(
                    id = "TIMKEN_22218",
                    designation = "22218K YM",
                    brand = "Timken",
                    boreDiameterMm = 90.0,
                    outerDiameterMm = 160.0,
                    widthMm = 40.0,
                    dynamicLoadKn = 310.0,
                    staticLoadKn = 360.0,
                    limitingSpeedRpm = 4500.0,
                    type = "Rodillos Oscilantes (Cono 1:12)",
                    clearanceMinNormal = 0.060,
                    clearanceMaxNormal = 0.080,
                    clearanceMinC3 = 0.080,
                    clearanceMaxC3 = 0.110,
                    clearanceMinC4 = 0.110,
                    clearanceMaxC4 = 0.140,
                    recommendedReductionMin = 0.045,
                    recommendedReductionMax = 0.055,
                    axialDriveUp1To12Min = 0.50,
                    axialDriveUp1To12Max = 0.60,
                    cadUrl = "https://www.timken.com"
                ),
                BearingSpec(
                    id = "NSK_22220",
                    designation = "22220 EAKD1",
                    brand = "NSK",
                    boreDiameterMm = 100.0,
                    outerDiameterMm = 180.0,
                    widthMm = 46.0,
                    dynamicLoadKn = 415.0,
                    staticLoadKn = 485.0,
                    limitingSpeedRpm = 4200.0,
                    type = "Rodillos Oscilantes (Cono 1:12)",
                    clearanceMinNormal = 0.060,
                    clearanceMaxNormal = 0.080,
                    clearanceMinC3 = 0.080,
                    clearanceMaxC3 = 0.110,
                    clearanceMinC4 = 0.110,
                    clearanceMaxC4 = 0.140,
                    recommendedReductionMin = 0.045,
                    recommendedReductionMax = 0.055,
                    axialDriveUp1To12Min = 0.50,
                    axialDriveUp1To12Max = 0.60,
                    cadUrl = "https://www.nsk.com"
                ),
                BearingSpec(
                    id = "DODGE_22215",
                    designation = "SAF 22215",
                    brand = "DODGE",
                    boreDiameterMm = 75.0,
                    outerDiameterMm = 130.0,
                    widthMm = 31.0,
                    dynamicLoadKn = 205.0,
                    staticLoadKn = 230.0,
                    limitingSpeedRpm = 5400.0,
                    type = "Rodillos Oscilantes (Cono 1:12)",
                    clearanceMinNormal = 0.050,
                    clearanceMaxNormal = 0.070,
                    clearanceMinC3 = 0.070,
                    clearanceMaxC3 = 0.095,
                    clearanceMinC4 = 0.095,
                    clearanceMaxC4 = 0.120,
                    recommendedReductionMin = 0.035,
                    recommendedReductionMax = 0.040,
                    axialDriveUp1To12Min = 0.45,
                    axialDriveUp1To12Max = 0.50,
                    cadUrl = "https://www.dodgeindustrial.com"
                )
            )
            bearingDao.insertBearings(seedBearings)
        }

        // Check housings
        val currentHousings = bearingDao.getAllHousings().first()
        if (currentHousings.isEmpty()) {
            val seedHousings = listOf(
                HousingSpec(
                    designation = "SNL 511-609",
                    brand = "SKF",
                    L_mm = 255.0,
                    H_mm = 70.0,
                    H1_mm = 130.0,
                    W_mm = 95.0,
                    boltDistanceMm = 210.0,
                    weightKg = 4.4,
                    compatibleBearingsCsv = "22211 EK, 1211, 2211, C 2211 K",
                    compatibleSleevesCsv = "H 311, H 211, H 311 EC",
                    cadUrl = "https://www.skf.com/group/products/bearing-housings/split-plummer-block-housings-snl-2-3-5-6-series/productid-SNL%20511-609"
                ),
                HousingSpec(
                    designation = "SNL 513-611",
                    brand = "SKF",
                    L_mm = 275.0,
                    H_mm = 80.0,
                    H1_mm = 150.0,
                    W_mm = 110.0,
                    boltDistanceMm = 230.0,
                    weightKg = 6.5,
                    compatibleBearingsCsv = "22213 EK, 1213, 2213, C 2213 K",
                    compatibleSleevesCsv = "H 313, H 213",
                    cadUrl = "https://www.skf.com/group/products/bearing-housings/split-plummer-block-housings-snl-2-3-5-6-series/productid-SNL%20513-611"
                ),
                HousingSpec(
                    designation = "SNL 515-612",
                    brand = "SKF",
                    L_mm = 280.0,
                    H_mm = 80.0,
                    H1_mm = 155.0,
                    W_mm = 115.0,
                    boltDistanceMm = 230.0,
                    weightKg = 7.0,
                    compatibleBearingsCsv = "22215 EK, 22215-E1-K, SAF 22215, 1215, 2215, 2312K",
                    compatibleSleevesCsv = "H 315, H 215, H 2312",
                    cadUrl = "https://www.skf.com/group/products/bearing-housings/split-plummer-block-housings-snl-2-3-5-6-series/productid-SNL%20515-612"
                ),
                HousingSpec(
                    designation = "SNL 518-615",
                    brand = "SKF",
                    L_mm = 345.0,
                    H_mm = 100.0,
                    H1_mm = 194.0,
                    W_mm = 145.0,
                    boltDistanceMm = 290.0,
                    weightKg = 12.5,
                    compatibleBearingsCsv = "22218 EK, 22218K YM, 1218, 2218, 2315K",
                    compatibleSleevesCsv = "H 318, H 218, H 2315",
                    cadUrl = "https://www.skf.com/group/products/bearing-housings/split-plummer-block-housings-snl-2-3-5-6-series/productid-SNL%20518-615"
                ),
                HousingSpec(
                    designation = "SNL 520-617",
                    brand = "SKF",
                    L_mm = 380.0,
                    H_mm = 112.0,
                    H1_mm = 218.0,
                    W_mm = 160.0,
                    boltDistanceMm = 320.0,
                    weightKg = 17.6,
                    compatibleBearingsCsv = "22220 EK, 22220 EAKD1, 1220, 2220, 2317K",
                    compatibleSleevesCsv = "H 320, H 220, H 2317",
                    cadUrl = "https://www.skf.com/group/products/bearing-housings/split-plummer-block-housings-snl-2-3-5-6-series/productid-SNL%20520-617"
                ),
                HousingSpec(
                    designation = "SNL 522-619",
                    brand = "SKF",
                    L_mm = 410.0,
                    H_mm = 125.0,
                    H1_mm = 242.0,
                    W_mm = 175.0,
                    boltDistanceMm = 350.0,
                    weightKg = 22.0,
                    compatibleBearingsCsv = "22222 EK, 1222, 2222, 2319K",
                    compatibleSleevesCsv = "H 322, H 222, H 2319",
                    cadUrl = "https://www.skf.com/group/products/bearing-housings/split-plummer-block-housings-snl-2-3-5-6-series/productid-SNL%20522-619"
                ),
                HousingSpec(
                    designation = "FAG SAF 515",
                    brand = "FAG",
                    L_mm = 280.0,
                    H_mm = 82.5,
                    H1_mm = 160.0,
                    W_mm = 115.0,
                    boltDistanceMm = 230.0,
                    weightKg = 7.2,
                    compatibleBearingsCsv = "22215-E1-K, 22215 EK",
                    compatibleSleevesCsv = "H 315",
                    cadUrl = "https://www.schaeffler.com/en/products-and-solutions/"
                ),
                HousingSpec(
                    designation = "DODGE SAF 22215",
                    brand = "DODGE",
                    L_mm = 280.0,
                    H_mm = 82.5,
                    H1_mm = 162.0,
                    W_mm = 116.0,
                    boltDistanceMm = 230.0,
                    weightKg = 7.5,
                    compatibleBearingsCsv = "SAF 22215, 22215 EK",
                    compatibleSleevesCsv = "SN-15",
                    cadUrl = "https://www.dodgeindustrial.com"
                )
            )
            bearingDao.insertHousings(seedHousings)
        }
    }
}
