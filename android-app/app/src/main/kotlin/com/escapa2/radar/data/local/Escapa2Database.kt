package com.escapa2.radar.data.local

import androidx.room.Database
import androidx.room.RoomDatabase

@Database(
    entities = [OpportunityEntity::class],
    version = 1,
    exportSchema = false,
)
abstract class Escapa2Database : RoomDatabase() {
    abstract fun opportunityDao(): OpportunityDao
}
