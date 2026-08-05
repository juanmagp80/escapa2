package com.escapa2.radar.data.repository

import com.escapa2.radar.data.model.AiSummary
import com.escapa2.radar.data.model.Opportunity
import com.escapa2.radar.data.remote.Escapa2Api
import com.escapa2.radar.data.remote.dto.AiSummaryRequestDto

/**
 * Repository backed by the backend AI endpoint.
 *
 * Always sends structured data (never free text) and treats the response as
 * orientative. Falls back to rule-based summaries through the fallback wrapper.
 */
class RemoteAiRepository(
    private val api: Escapa2Api,
) : AiRepository {

    override suspend fun summarizeOpportunity(opportunity: Opportunity): AiSummary {
        val response = api.summarizeOpportunity(
            AiSummaryRequestDto(
                destination = opportunity.destinationName,
                travelers = AiRepository.DEFAULT_TRAVELERS,
                totalCostEur = opportunity.totalCostEur,
                budgetEur = AiRepository.DEFAULT_BUDGET_EUR,
                usefulHours = opportunity.usefulHours,
                transportMode = opportunity.transportMode.name,
                verifiedAt = opportunity.verifiedAt,
                facts = emptyList(),
            ),
        )
        return AiSummary(
            headline = response.headline,
            summary = response.summary,
            pros = response.pros,
            cons = response.cons,
            confidence = response.confidence,
            generatedByAi = response.generatedByAi,
        )
    }
}
