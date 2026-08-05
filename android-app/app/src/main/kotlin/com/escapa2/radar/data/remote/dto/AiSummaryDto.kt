package com.escapa2.radar.data.remote.dto

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

@Serializable
data class AiSummaryRequestDto(
    val destination: String,
    val travelers: Int,
    @SerialName("total_cost_eur") val totalCostEur: Double,
    @SerialName("budget_eur") val budgetEur: Double,
    @SerialName("useful_hours") val usefulHours: Double,
    @SerialName("transport_mode") val transportMode: String,
    @SerialName("verified_at") val verifiedAt: String,
    val facts: List<String> = emptyList(),
)

@Serializable
data class AiSummaryDto(
    val headline: String,
    val summary: String,
    val pros: List<String> = emptyList(),
    val cons: List<String> = emptyList(),
    val confidence: String,
    @SerialName("generated_by_ai") val generatedByAi: Boolean,
)
