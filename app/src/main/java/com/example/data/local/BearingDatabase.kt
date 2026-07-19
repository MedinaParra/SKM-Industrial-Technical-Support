package com.example.data.local

import android.content.Context
import androidx.room.Database
import androidx.room.Room
import androidx.room.RoomDatabase
import com.example.data.model.BearingSpec
import com.example.data.model.HousingSpec
import com.example.data.model.MountingReport

@Database(
    entities = [BearingSpec::class, HousingSpec::class, MountingReport::class],
    version = 1,
    exportSchema = false
)
abstract class BearingDatabase : RoomDatabase() {
    abstract fun bearingDao(): BearingDao

    companion object {
        @Volatile
        private var INSTANCE: BearingDatabase? = null

        fun getDatabase(context: Context): BearingDatabase {
            return INSTANCE ?: synchronized(this) {
                val instance = Room.databaseBuilder(
                    context.applicationContext,
                    BearingDatabase::class.java,
                    "skm_bearings_database"
                )
                .fallbackToDestructiveMigration()
                .build()
                INSTANCE = instance
                instance
            }
        }
    }
}
