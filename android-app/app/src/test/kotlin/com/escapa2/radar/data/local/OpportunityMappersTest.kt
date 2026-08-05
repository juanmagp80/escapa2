package com.escapa2.radar.data.local

import com.escapa2.radar.data.model.Opportunity
import com.escapa2.radar.data.model.TransportMode
import org.junit.Assert.assertEquals
import org.junit.Test

class OpportunityMappersTest {

    @Test
    fun domainToEntityMapsAllFields() {
        val entity = sampleOpportunity().toEntity()

        assertEquals("opp-1", entity.id)
        assertEquals("GAL", entity.destinationCode)
        assertEquals("Santiago de Compostela", entity.destinationName)
        assertEquals("CAR", entity.transportMode)
        assertEquals(34.0, entity.usefulHours, 0.0)
        assertEquals(198.0, entity.totalCostEur, 0.0)
        assertEquals("2026-08-05T12:00:00Z", entity.verifiedAt)
    }

    @Test
    fun entityToDomainRestoresOriginal() {
        val original = sampleOpportunity()

        val restored = original.toEntity().toDomain()

        assertEquals(original, restored)
    }

    @Test
    fun unknownTransportModeFallsBackToEither() {
        val entity = sampleOpportunity().toEntity().copy(transportMode = "TRAIN")

        assertEquals(TransportMode.EITHER, entity.toDomain().transportMode)
    }

    private fun sampleOpportunity() = Opportunity(
        id = "opp-1",
        destinationCode = "GAL",
        destinationName = "Santiago de Compostela",
        transportMode = TransportMode.CAR,
        startAt = "2026-08-14T18:30:00+02:00",
        endAt = "2026-08-16T20:00:00+02:00",
        usefulHours = 34.0,
        totalCostEur = 198.0,
        costPerPersonEur = 99.0,
        costPerNightEur = 99.0,
        costPerUsefulHourEur = 5.82,
        verifiedAt = "2026-08-05T12:00:00Z",
    )
}
