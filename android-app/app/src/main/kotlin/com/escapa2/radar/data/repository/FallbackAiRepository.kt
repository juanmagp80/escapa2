package com.escapa2.radar.data.repository

import com.escapa2.radar.data.model.AiSummary
import com.escapa2.radar.data.model.DailyReport
import com.escapa2.radar.data.model.Opportunity

/**
 * Tries the backend AI endpoint and falls back to deterministic rule-based
 * summaries when the service is unreachable, so explanations never block the
 * rest of the experience.
 */
class FallbackAiRepository(
    private val remote: AiRepository,
    private val local: AiRepository,
) : AiRepository {

    override suspend fun summarizeOpportunity(opportunity: Opportunity): AiSummary =
        try {
            remote.summarizeOpportunity(opportunity)
        } catch (throwable: Throwable) {
            if (NetworkFallback.shouldFallBack(throwable)) {
                local.summarizeOpportunity(opportunity)
            } else {
                throw throwable
            }
        }

    override suspend fun generateDailyReport(): DailyReport =
        try {
            remote.generateDailyReport()
        } catch (throwable: Throwable) {
            if (NetworkFallback.shouldFallBack(throwable)) {
                local.generateDailyReport()
            } else {
                throw throwable
            }
        }
}
