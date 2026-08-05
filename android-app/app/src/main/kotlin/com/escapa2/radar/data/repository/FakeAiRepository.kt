package com.escapa2.radar.data.repository

import com.escapa2.radar.data.model.AiSummary
import com.escapa2.radar.data.model.Opportunity
import java.util.Locale
import javax.inject.Inject
import javax.inject.Singleton

/**
 * Deterministic rule-based AI summary for development and offline usage.
 *
 * Mirrors the backend fallback: never invents prices, always reports the
 * verified time and treats the budget comparison as the main signal.
 */
@Singleton
class FakeAiRepository @Inject constructor() : AiRepository {

    override suspend fun summarizeOpportunity(opportunity: Opportunity): AiSummary {
        val budget = AiRepository.DEFAULT_BUDGET_EUR
        val difference = budget - opportunity.totalCostEur
        val travelers = AiRepository.DEFAULT_TRAVELERS

        val headline: String
        val pros = mutableListOf<String>()
        val cons = mutableListOf<String>()
        if (difference >= 0) {
            headline = "Buena opción dentro del presupuesto"
            pros += "Está ${formatEur(difference)} por debajo del presupuesto"
            pros += "$travelers viajeros, ${formatHours(opportunity.usefulHours)} horas útiles"
        } else {
            headline = "Por encima del presupuesto"
            pros += "$travelers viajeros, ${formatHours(opportunity.usefulHours)} horas útiles"
            cons += "Excede el presupuesto en ${formatEur(-difference)}"
        }

        val summary = buildString {
            append(
                "Oportunidad para ${opportunity.destinationName} con coste total de " +
                    "${formatEur(opportunity.totalCostEur)} para $travelers viajeros."
            )
            append(" Los precios están verificados a la hora indicada y pueden cambiar.")
        }

        return AiSummary(
            headline = headline,
            summary = summary,
            pros = pros,
            cons = cons,
            confidence = "MEDIUM",
            generatedByAi = false,
        )
    }

    private fun formatEur(value: Double): String =
        String.format(Locale("es", "ES"), "%.2f EUR", value)

    private fun formatHours(value: Double): String =
        String.format(Locale("es", "ES"), "%.1f", value)
}
