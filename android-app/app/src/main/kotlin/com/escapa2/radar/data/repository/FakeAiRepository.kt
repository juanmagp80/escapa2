package com.escapa2.radar.data.repository

import com.escapa2.radar.data.model.AiSummary
import com.escapa2.radar.data.model.DailyReport
import com.escapa2.radar.data.model.DailyReportEntry
import com.escapa2.radar.data.model.Opportunity
import com.escapa2.radar.data.model.SearchWatch
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
class FakeAiRepository @Inject constructor(
    private val watchRepository: SearchWatchRepository,
) : AiRepository {

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

    override suspend fun generateDailyReport(): DailyReport {
        val watches = watchRepository.getWatches()
        if (watches.isEmpty()) {
            return DailyReport(
                headline = "Sin viajes vigilados",
                summary = "Activa un seguimiento para recibir el informe diario de precios.",
                entries = emptyList(),
                warnings = defaultWarnings(),
                generatedByAi = false,
            )
        }
        return buildReport(watches)
    }

    private fun buildReport(watches: List<SearchWatch>): DailyReport {
        val entries = watches.map { watch ->
            val current = watch.priceHistory.lastOrNull()
            val previous = watch.priceHistory.getOrNull(watch.priceHistory.size - 2)
            val changeEur = if (previous != null && current != null) {
                previous - current
            } else {
                null
            }
            val changePercent = if (changeEur != null && previous != null && previous > 0) {
                changeEur / previous * 100
            } else {
                null
            }
            val isNewLow = current != null && watch.minRecordedEur != null &&
                current <= watch.minRecordedEur + NEW_LOW_EUR
            DailyReportEntry(
                watchName = watch.name,
                destination = watch.name,
                changeEur = round2(changeEur),
                changePercent = round1(changePercent),
                isNewLow = isNewLow,
                withinBudget = null,
                recommendation = recommendation(
                    changeEur = changeEur,
                    isNewLow = isNewLow,
                ),
                confidence = "HIGH",
            )
        }

        val drops = entries.filter { (it.changeEur ?: 0.0) > 0.0 }
        val newLows = entries.filter { it.isNewLow }

        val headline: String
        val summary: String
        when {
            drops.isNotEmpty() -> {
                headline = if (drops.size > 1) {
                    "${drops.size} de ${entries.size} viajes vigilados bajaron de precio"
                } else {
                    "${drops[0].destination} bajó de precio hoy"
                }
                summary = "Los precios verificados hoy bajan respecto al registro anterior en " +
                    drops.joinToString { "${it.destination} (-${formatEur(it.changeEur ?: 0.0)})" } +
                    ". Verifica la disponibilidad antes de reservar; los precios pueden cambiar."
            }
            newLows.isNotEmpty() -> {
                headline = "${newLows[0].destination} marca un nuevo mínimo registrado"
                summary = "Algunos viajes vigilados están en su mínimo registrado según las " +
                    "fuentes consultadas. Confirma horarios y disponibilidad antes de tomar una decisión."
            }
            else -> {
                headline = "Sin cambios importantes en tus viajes vigilados"
                summary = "Los precios verificados hoy no presentan bajadas significativas frente " +
                    "al registro anterior. Mantener el seguimiento activo permite detectar cambios."
            }
        }

        return DailyReport(
            headline = headline,
            summary = summary,
            entries = entries,
            warnings = defaultWarnings(),
            generatedByAi = false,
        )
    }

    private fun recommendation(changeEur: Double?, isNewLow: Boolean): String = when {
        isNewLow -> "Nuevo mínimo registrado: es un buen momento para verificar y valorar la reserva."
        changeEur != null && changeEur > 0 -> "Ha bajado ${formatEur(changeEur)} respecto al registro anterior."
        changeEur != null && changeEur < 0 -> "El precio ha subido respecto al registro anterior."
        else -> "Sin cambios significativos; se mantiene el seguimiento."
    }

    private fun defaultWarnings(): List<String> = listOf(
        "Informe orientativo basado en datos verificados a la hora indicada.",
        "Los precios y la disponibilidad pueden cambiar sin previo aviso.",
    )

    private fun round2(value: Double?): Double? = value?.let {
        (Math.round(it * 100) / 100.0)
    }

    private fun round1(value: Double?): Double? = value?.let {
        (Math.round(it * 10) / 10.0)
    }

    private fun formatEur(value: Double): String =
        String.format(Locale("es", "ES"), "%.2f EUR", value)

    private fun formatHours(value: Double): String =
        String.format(Locale("es", "ES"), "%.1f", value)

    private companion object {
        const val NEW_LOW_EUR = 0.0
    }
}
