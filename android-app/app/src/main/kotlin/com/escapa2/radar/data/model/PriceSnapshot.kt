package com.escapa2.radar.data.model

/**
 * A price point captured for an opportunity at a given time. Snapshots grow
 * with each radar run.
 */
data class PriceSnapshot(
    val id: String,
    val totalCostEur: Double?,
    val capturedAt: String,
    val source: String,
)
