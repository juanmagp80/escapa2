package com.escapa2.radar.data.remote.dto

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

/**
 * Response of POST /watches/daily-report. Empty by default so new fields from
 * the backend do not break decoding.
 */
@Serializable
data class DailyReportResponseDto(
    val headline: String,
    val summary: String,
    val entries: List<DailyReportOpportunityEntryDto> = emptyList(),
    val warnings: List<String> = emptyList(),
    @SerialName("generated_by_ai") val generatedByAi: Boolean,
)

@Serializable
data class DailyReportOpportunityEntryDto(
    @SerialName("watch_name") val watchName: String,
    val destination: String,
    @SerialName("change_eur") val changeEur: Double? = null,
    @SerialName("change_percent") val changePercent: Double? = null,
    @SerialName("is_new_low") val isNewLow: Boolean,
    @SerialName("within_budget") val withinBudget: Boolean? = null,
    val recommendation: String,
    val confidence: String,
)
