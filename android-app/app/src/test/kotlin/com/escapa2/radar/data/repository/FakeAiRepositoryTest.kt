package com.escapa2.radar.data.repository

import com.escapa2.radar.data.model.Opportunity
import com.escapa2.radar.data.model.TransportMode
import kotlinx.coroutines.test.runTest
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

class FakeAiRepositoryTest {

    private val repository = FakeAiRepository()

    @Test
    fun withinBudgetProducesPositiveHeadline() = runTest {
        val summary = repository.summarizeOpportunity(sampleOpportunity(totalCostEur = 198.0))
        assertEquals("Buena opción dentro del presupuesto", summary.headline)
        assertTrue(summary.pros.any { it.contains("152,00") })
        assertTrue(summary.cons.isEmpty())
        assertFalse(summary.generatedByAi)
    }

    @Test
    fun overBudgetAddsCons() = runTest {
        val summary = repository.summarizeOpportunity(sampleOpportunity(totalCostEur = 400.0))
        assertEquals("Por encima del presupuesto", summary.headline)
        assertTrue(summary.cons.any { it.contains("50") })
    }

    private fun sampleOpportunity(totalCostEur: Double) = Opportunity(
        id = "opp-1",
        destinationCode = "GAL",
        destinationName = "Santiago de Compostela",
        transportMode = TransportMode.CAR,
        startAt = "2026-08-14T18:30:00+02:00",
        endAt = "2026-08-16T20:00:00+02:00",
        usefulHours = 34.0,
        totalCostEur = totalCostEur,
        costPerPersonEur = totalCostEur / 2,
        costPerNightEur = totalCostEur / 2,
        costPerUsefulHourEur = totalCostEur / 34.0,
        verifiedAt = "2026-08-05T12:00:00Z",
    )
}
