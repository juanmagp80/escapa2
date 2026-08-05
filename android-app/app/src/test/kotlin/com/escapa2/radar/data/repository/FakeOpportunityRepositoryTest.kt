package com.escapa2.radar.data.repository

import com.escapa2.radar.data.model.TransportMode
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test

class FakeOpportunityRepositoryTest {

    private val repository = FakeOpportunityRepository()

    @Test
    fun fakeRepositoryProvidesFourOpportunities() = runTest {
        val opportunities = repository.getOpportunities()
        assertEquals(4, opportunities.size)
    }

    @Test
    fun opportunitiesExposePositiveMetrics() = runTest {
        val opportunities = repository.getOpportunities()
        opportunities.forEach { opportunity ->
            assertTrue(opportunity.totalCostEur > 0)
            assertTrue(opportunity.costPerPersonEur > 0)
            assertTrue(opportunity.costPerNightEur > 0)
            assertTrue(opportunity.costPerUsefulHourEur > 0)
            assertTrue(opportunity.verifiedAt.isNotBlank())
        }
    }

    @Test
    fun cheaperOptionWithFewerUsefulHoursHasHigherCostPerUsefulHour() = runTest {
        val opportunities = repository.getOpportunities()
        val flexible = opportunities.first { it.id == "opp-avion-porto" }
        val cheaper = opportunities.first { it.id == "opp-avion-porto-barata" }

        assertTrue(cheaper.totalCostEur < flexible.totalCostEur)
        assertTrue(cheaper.usefulHours < flexible.usefulHours)
        assertTrue(cheaper.costPerUsefulHourEur > flexible.costPerUsefulHourEur)
    }

    @Test
    fun fakeRepositoryCoversExpectedTransportModes() = runTest {
        val modes = repository.getOpportunities().map { it.transportMode }.toSet()
        assertTrue(TransportMode.CAR in modes)
        assertTrue(TransportMode.FLIGHT in modes)
    }
}

private fun runTest(block: suspend () -> Unit) =
    kotlinx.coroutines.test.runTest { block() }
