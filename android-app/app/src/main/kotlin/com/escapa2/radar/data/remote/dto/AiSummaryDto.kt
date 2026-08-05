package com.escapa2.radar.data.remote.dto

import kotlinx.serialization.Serializable

@Serializable
data class AiSummaryRequestDto(
    val destination: String,
    val travelers: Int,
    val totalCostEur: Double,
    val budgetEur: Double,
    val usefulHours: Double,
    val transportMode: String,
    val verifiedAt: String,
    val facts: List<String> = emptyList(),
)

@Serializable
data class AiSummaryDto(
    val headline: String,
    val summary: String,
    val pros: List<String> = emptyList(),
    val cons: List<String> = emptyList(),
    val confidence: String,
    val generatedByAi: Boolean,
)
