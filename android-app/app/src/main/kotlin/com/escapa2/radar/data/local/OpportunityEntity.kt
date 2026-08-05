package com.escapa2.radar.data.local

import androidx.room.ColumnInfo
import androidx.room.Entity
import androidx.room.PrimaryKey

@Entity(tableName = "opportunities")
data class OpportunityEntity(
    @PrimaryKey val id: String,
    @ColumnInfo(name = "destination_code") val destinationCode: String,
    @ColumnInfo(name = "destination_name") val destinationName: String,
    @ColumnInfo(name = "transport_mode") val transportMode: String,
    @ColumnInfo(name = "start_at") val startAt: String,
    @ColumnInfo(name = "end_at") val endAt: String,
    @ColumnInfo(name = "useful_hours") val usefulHours: Double,
    @ColumnInfo(name = "total_cost_eur") val totalCostEur: Double,
    @ColumnInfo(name = "cost_per_person_eur") val costPerPersonEur: Double,
    @ColumnInfo(name = "cost_per_night_eur") val costPerNightEur: Double,
    @ColumnInfo(name = "cost_per_useful_hour_eur") val costPerUsefulHourEur: Double,
    @ColumnInfo(name = "verified_at") val verifiedAt: String,
)
