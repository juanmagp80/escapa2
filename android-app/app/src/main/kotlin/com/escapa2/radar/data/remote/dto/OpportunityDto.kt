package com.escapa2.radar.data.remote.dto

import com.escapa2.radar.data.model.Opportunity
import com.escapa2.radar.data.model.TransportMode
import kotlinx.serialization.Serializable

@Serializable
data class OpportunityDto(
    val id: String,
    val destinationCode: String,
    val destinationName: String,
    val transportMode: String,
    val startAt: String,
    val endAt: String,
    val usefulHours: Double,
    val totalCostEur: Double,
    val costPerPersonEur: Double,
    val costPerNightEur: Double,
    val costPerUsefulHourEur: Double,
    val providerVerifiedAt: String? = null,
)

fun OpportunityDto.toDomain(): Opportunity = Opportunity(
    id = id,
    destinationCode = destinationCode,
    destinationName = destinationName,
    transportMode = runCatching { TransportMode.valueOf(transportMode) }
        .getOrDefault(TransportMode.EITHER),
    startAt = startAt,
    endAt = endAt,
    usefulHours = usefulHours,
    totalCostEur = totalCostEur,
    costPerPersonEur = costPerPersonEur,
    costPerNightEur = costPerNightEur,
    costPerUsefulHourEur = costPerUsefulHourEur,
    verifiedAt = providerVerifiedAt ?: "",
)
