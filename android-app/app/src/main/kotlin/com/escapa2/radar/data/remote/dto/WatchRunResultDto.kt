package com.escapa2.radar.data.remote.dto

import com.escapa2.radar.data.model.WatchRunResult
import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

@Serializable
data class WatchRunResultDto(
    @SerialName("last_run_at") val lastRunAt: String? = null,
    @SerialName("next_run_at") val nextRunAt: String? = null,
    @SerialName("matched_opportunities") val matchedOpportunities: List<MatchedOpportunityDto> = emptyList(),
    val alerts: List<WatchRunAlertDto> = emptyList(),
)

@Serializable
data class MatchedOpportunityDto(
    val id: String,
    @SerialName("destination_code") val destinationCode: String? = null,
    @SerialName("destination_name") val destinationName: String? = null,
    @SerialName("transport_mode") val transportMode: String? = null,
    @SerialName("total_cost_eur") val totalCostEur: Double? = null,
)

@Serializable
data class WatchRunAlertDto(
    val rule: String? = null,
    val message: String? = null,
)

fun WatchRunResultDto.toDomain(): WatchRunResult = WatchRunResult(
    lastRunAt = lastRunAt ?: "",
    nextRunAt = nextRunAt ?: "",
    matchedCount = matchedOpportunities.size,
    alerts = alerts.mapNotNull { it.message },
)
