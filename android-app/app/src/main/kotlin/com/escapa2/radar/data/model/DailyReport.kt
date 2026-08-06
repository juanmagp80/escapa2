package com.escapa2.radar.data.model

/**
 * Personalized daily summary of watched trip prices.
 *
 * [generatedByAi] is false when produced by deterministic rules (fallback).
 * Values come from confirmed provider snapshots, never invented.
 */
data class DailyReport(
    val headline: String,
    val summary: String,
    val entries: List<DailyReportEntry>,
    val warnings: List<String>,
    val generatedByAi: Boolean,
)

/**
 * Per-watch result inside the daily report.
 *
 * [changeEur] is positive when the price dropped relative to the previous
 * recorded snapshot.
 */
data class DailyReportEntry(
    val watchName: String,
    val destination: String,
    val changeEur: Double?,
    val changePercent: Double?,
    val isNewLow: Boolean,
    val withinBudget: Boolean?,
    val recommendation: String,
    val confidence: String,
)
