package com.escapa2.radar.data.remote.dto

import com.escapa2.radar.data.model.Opportunity
import com.escapa2.radar.data.model.TransportMode
import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

@Serializable
data class OpportunityDto(
    val id: String,
    @SerialName("destination_code") val destinationCode: String,
    @SerialName("destination_name") val destinationName: String,
    @SerialName("transport_mode") val transportMode: String,
    @SerialName("start_at") val startAt: String,
    @SerialName("end_at") val endAt: String,
    @SerialName("useful_hours") val usefulHours: Double? = null,
    @SerialName("total_cost_eur") val totalCostEur: Double? = null,
    @SerialName("cost_per_person_eur") val costPerPersonEur: Double? = null,
    @SerialName("cost_per_night_eur") val costPerNightEur: Double? = null,
    @SerialName("cost_per_useful_hour_eur") val costPerUsefulHourEur: Double? = null,
    @SerialName("provider_verified_at") val providerVerifiedAt: String? = null,
    @SerialName("value_score") val valueScore: Double? = null,
)

fun OpportunityDto.toDomain(): Opportunity = Opportunity(
    id = id,
    destinationCode = destinationCode,
    destinationName = destinationName,
    transportMode = runCatching { TransportMode.valueOf(transportMode) }
        .getOrDefault(TransportMode.EITHER),
    startAt = startAt,
    endAt = endAt,
    usefulHours = usefulHours ?: 0.0,
    totalCostEur = totalCostEur ?: 0.0,
    costPerPersonEur = costPerPersonEur ?: 0.0,
    costPerNightEur = costPerNightEur ?: 0.0,
    costPerUsefulHourEur = costPerUsefulHourEur ?: 0.0,
    valueScore = valueScore ?: 0.0,
    verifiedAt = providerVerifiedAt ?: "",
)
