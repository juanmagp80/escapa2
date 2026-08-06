package com.escapa2.radar.data.model

/**
 * A time range during which the couple can travel.
 */
data class AvailabilityWindow(
    val id: String,
    val startAt: String,
    val endAt: String,
    val kind: String,
    val isFlexible: Boolean,
)
