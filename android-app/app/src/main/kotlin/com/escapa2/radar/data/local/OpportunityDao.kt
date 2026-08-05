package com.escapa2.radar.data.local

import androidx.room.Dao
import androidx.room.Insert
import androidx.room.OnConflictStrategy
import androidx.room.Query

@Dao
interface OpportunityDao {

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun upsertAll(items: List<OpportunityEntity>)

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun upsert(item: OpportunityEntity)

    @Query("SELECT * FROM opportunities ORDER BY cost_per_useful_hour_eur ASC")
    suspend fun getAll(): List<OpportunityEntity>

    @Query("SELECT * FROM opportunities WHERE id = :id LIMIT 1")
    suspend fun getById(id: String): OpportunityEntity?

    @Query("DELETE FROM opportunities")
    suspend fun clearAll()
}
