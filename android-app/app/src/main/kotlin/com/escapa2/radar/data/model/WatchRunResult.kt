package com.escapa2.radar.data.model

/**
 * Result of running a watch once. Alerts are already evaluated by the backend
 * against the price history recorded during the run.
 */
data class WatchRunResult(
    val lastRunAt: String,
    val nextRunAt: String,
    val matchedCount: Int,
    val alerts: List<String>,
)
