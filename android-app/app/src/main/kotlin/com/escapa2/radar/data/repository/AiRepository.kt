package com.escapa2.radar.data.repository

import com.escapa2.radar.data.model.AiSummary
import com.escapa2.radar.data.model.Opportunity

/**
 * Contract for AI-generated explanations consumed by the UI.
 */
interface AiRepository {

    /**
     * Generate an orientative summary for an [opportunity].
     */
    suspend fun summarizeOpportunity(opportunity: Opportunity): AiSummary

    companion object {
        const val DEFAULT_BUDGET_EUR = 350.0
        const val DEFAULT_TRAVELERS = 2
    }
}
