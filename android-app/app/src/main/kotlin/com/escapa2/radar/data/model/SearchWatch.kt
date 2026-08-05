package com.escapa2.radar.data.model

/**
 * A watched trip search shown in the Radar screen.
 *
 * Price values are orientative and derived from tracked snapshots.
 */
data class SearchWatch(
    val id: String,
    val name: String,
    val status: String,
    val lastRunAt: String,
    val nextRunAt: String,
    val changeSinceYesterdayEur: Double?,
    val minRecordedEur: Double?,
    val alertRules: List<String>,
    val priceHistory: List<Double>,
)
