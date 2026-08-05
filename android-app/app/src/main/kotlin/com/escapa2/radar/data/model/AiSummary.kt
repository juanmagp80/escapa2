package com.escapa2.radar.data.model

/**
 * Structured, orientative AI explanation for a travel opportunity.
 *
 * [generatedByAi] is false when produced by deterministic rules (fallback).
 */
data class AiSummary(
    val headline: String,
    val summary: String,
    val pros: List<String>,
    val cons: List<String>,
    val confidence: String,
    val generatedByAi: Boolean,
)
