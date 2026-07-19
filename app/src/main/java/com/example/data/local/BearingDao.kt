package com.example.data.local

import androidx.room.*
import com.example.data.model.BearingSpec
import com.example.data.model.HousingSpec
import com.example.data.model.MountingReport
import kotlinx.coroutines.flow.Flow

@Dao
interface BearingDao {
    @Query("SELECT * FROM bearings ORDER BY designation ASC")
    fun getAllBearings(): Flow<List<BearingSpec>>

    @Query("SELECT * FROM bearings WHERE designation LIKE '%' || :query || '%' OR type LIKE '%' || :query || '%'")
    fun searchBearings(query: String): Flow<List<BearingSpec>>

    @Query("SELECT * FROM bearings WHERE id = :id")
    suspend fun getBearingById(id: String): BearingSpec?

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertBearings(bearings: List<BearingSpec>)

    // --- Soportes / Housings ---
    @Query("SELECT * FROM housings ORDER BY designation ASC")
    fun getAllHousings(): Flow<List<HousingSpec>>

    @Query("SELECT * FROM housings WHERE designation LIKE '%' || :query || '%' OR compatibleBearingsCsv LIKE '%' || :query || '%'")
    fun searchHousings(query: String): Flow<List<HousingSpec>>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertHousings(housings: List<HousingSpec>)

    // --- Reportes de Montaje ---
    @Query("SELECT * FROM mounting_reports ORDER BY id DESC")
    fun getAllReports(): Flow<List<MountingReport>>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertReport(report: MountingReport): Long

    @Delete
    suspend fun deleteReport(report: MountingReport)
}
