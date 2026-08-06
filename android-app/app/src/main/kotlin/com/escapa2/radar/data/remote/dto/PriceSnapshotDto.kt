package com.escapa2.radar.data.remote.dto

import com.escapa2.radar.data.model.PriceSnapshot
import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable
import kotlinx.serialization.json.JsonElement

@Serializable
data class PriceSnapshotDto(
    val id: String,
    @SerialName("travel_opportunity_id") val travelOpportunityId: String? = null,
    @SerialName("total_cost_eur") val totalCostEur: Double? = null,
    @SerialName("captured_at") val capturedAt: String? = null,
    @SerialName("source_summary_json") val sourceSummaryJson: Map<String, JsonElement> = emptyMap(),
)

fun PriceSnapshotDto.toDomain(): PriceSnapshot = PriceSnapshot(
    id = id,
    totalCostEur = totalCostEur,
    capturedAt = capturedAt ?: "",
    source = sourceSummaryJson["provider"]?.toString()?.trim('"') ?: "",
)
