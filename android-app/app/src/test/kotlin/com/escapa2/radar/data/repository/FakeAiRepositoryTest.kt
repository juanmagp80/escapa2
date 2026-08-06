package com.escapa2.radar.data.repository

import com.escapa2.radar.data.model.Opportunity
import com.escapa2.radar.data.model.OpportunitySearchFilters
import com.escapa2.radar.data.model.PriceSnapshot
import com.escapa2.radar.data.model.SearchWatch
import com.escapa2.radar.data.model.TransportMode
import com.escapa2.radar.data.model.WatchRunResult
import kotlinx.coroutines.test.runTest
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

class FakeAiRepositoryTest {

    private val repository = FakeAiRepository(StaticWatchRepository())

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

    @Test
    fun dailyReportWithoutWatchesExplainsHowToActivate() = runTest {
        val report = FakeAiRepository(StaticWatchRepository(emptyList())).generateDailyReport()

        assertTrue(report.entries.isEmpty())
        assertTrue(report.headline.contains("vigilados"))
        assertFalse(report.generatedByAi)
    }

    @Test
    fun dailyReportFlagsDropsAndNewLows() = runTest {
        val dropping = SearchWatch(
            id = "watch-drop",
            name = "Porto en avión",
            status = "ACTIVE",
            lastRunAt = "2026-08-05T12:00:00Z",
            nextRunAt = "2026-08-06T12:00:00Z",
            changeSinceYesterdayEur = -16.0,
            minRecordedEur = 312.0,
            alertRules = emptyList(),
            priceHistory = listOf(328.0, 312.0),
        )
        val report = FakeAiRepository(StaticWatchRepository(listOf(dropping))).generateDailyReport()

        assertEquals("Porto en avión bajó de precio hoy", report.headline)
        assertEquals(1, report.entries.size)
        val entry = report.entries[0]
        assertEquals(16.0, entry.changeEur!!, 0.001)
        assertTrue(entry.isNewLow)
        assertTrue(entry.recommendation.contains("mínimo"))
        assertFalse(report.generatedByAi)
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

    private class StaticWatchRepository(
        private val items: List<SearchWatch> = listOf(
            SearchWatch(
                id = "watch-porto",
                name = "Porto en avión",
                status = "ACTIVE",
                lastRunAt = "2026-08-05T12:00:00Z",
                nextRunAt = "2026-08-06T12:00:00Z",
                changeSinceYesterdayEur = -16.0,
                minRecordedEur = 312.0,
                alertRules = emptyList(),
                priceHistory = listOf(328.0, 312.0),
            ),
        ),
    ) : SearchWatchRepository {
        override suspend fun getWatches(): List<SearchWatch> = items

        override suspend fun createWatch(name: String, initialPriceEur: Double): SearchWatch =
            SearchWatch(
                id = "watch-new",
                name = name,
                status = "ACTIVE",
                lastRunAt = "2026-08-05T12:00:00Z",
                nextRunAt = "2026-08-06T12:00:00Z",
                changeSinceYesterdayEur = 0.0,
                minRecordedEur = initialPriceEur,
                alertRules = emptyList(),
                priceHistory = listOf(initialPriceEur),
            )

        override suspend fun runWatch(id: String): WatchRunResult =
            WatchRunResult(
                lastRunAt = "2026-08-06T12:00:00Z",
                nextRunAt = "2026-08-07T12:00:00Z",
                matchedCount = 0,
                alerts = emptyList(),
            )
    }
}
