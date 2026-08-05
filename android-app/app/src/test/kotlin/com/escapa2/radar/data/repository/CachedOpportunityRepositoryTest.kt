package com.escapa2.radar.data.repository

import com.escapa2.radar.data.local.OpportunityDao
import com.escapa2.radar.data.local.OpportunityEntity
import com.escapa2.radar.data.model.Opportunity
import com.escapa2.radar.data.model.OpportunitySearchFilters
import com.escapa2.radar.data.model.TransportMode
import kotlinx.coroutines.runBlocking
import org.junit.Assert.assertEquals
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Test

class CachedOpportunityRepositoryTest {

    @Test
    fun getOpportunitiesCachesResults() = runBlocking {
        val dao = FakeDao()
        val repository = CachedOpportunityRepository(StaticSource(listOf(sample("opp-1"))), dao)

        val results = repository.getOpportunities()

        assertEquals(1, results.size)
        assertEquals(1, dao.stored.size)
        assertEquals("opp-1", dao.stored.first().id)
    }

    @Test
    fun getOpportunitiesFallsBackToCacheOnFailure() = runBlocking {
        val dao = FakeDao()
        dao.stored += sample("opp-1").toEntity()
        val repository = CachedOpportunityRepository(FailingSource(), dao)

        val results = repository.getOpportunities()

        assertEquals(1, results.size)
        assertEquals("opp-1", results.first().id)
    }

    @Test
    fun getOpportunityFallsBackToCacheOnFailure() = runBlocking {
        val dao = FakeDao()
        dao.stored += sample("opp-1").toEntity()
        val repository = CachedOpportunityRepository(FailingSource(), dao)

        val result = repository.getOpportunity("opp-1")

        assertEquals("opp-1", result?.id)
    }

    @Test
    fun getOpportunityReturnsNullWhenNotCachedAndSourceFails() = runBlocking {
        val dao = FakeDao()
        val repository = CachedOpportunityRepository(FailingSource(), dao)

        assertNull(repository.getOpportunity("missing"))
    }

    @Test
    fun searchCachesResults() = runBlocking {
        val dao = FakeDao()
        val repository = CachedOpportunityRepository(StaticSource(listOf(sample("opp-1"))), dao)

        val results = repository.search(OpportunitySearchFilters())

        assertEquals(1, results.size)
        assertEquals(1, dao.stored.size)
    }

    @Test
    fun searchFallsBackToCacheOnFailure() = runBlocking {
        val dao = FakeDao()
        dao.stored += sample("opp-1").toEntity()
        val repository = CachedOpportunityRepository(FailingSource(), dao)

        val results = repository.search(OpportunitySearchFilters())

        assertEquals(1, results.size)
        assertTrue(results.any { it.id == "opp-1" })
    }

    private fun sample(id: String) = Opportunity(
        id = id,
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

    private fun Opportunity.toEntity() = com.escapa2.radar.data.local.OpportunityEntity(
        id = id,
        destinationCode = destinationCode,
        destinationName = destinationName,
        transportMode = transportMode.name,
        startAt = startAt,
        endAt = endAt,
        usefulHours = usefulHours,
        totalCostEur = totalCostEur,
        costPerPersonEur = costPerPersonEur,
        costPerNightEur = costPerNightEur,
        costPerUsefulHourEur = costPerUsefulHourEur,
        verifiedAt = verifiedAt,
    )

    private class FakeDao : OpportunityDao {
        val stored = mutableListOf<OpportunityEntity>()

        override suspend fun upsertAll(items: List<OpportunityEntity>) {
            stored.clear()
            stored.addAll(items)
        }

        override suspend fun upsert(item: OpportunityEntity) {
            stored.removeAll { it.id == item.id }
            stored.add(item)
        }

        override suspend fun getAll(): List<OpportunityEntity> = stored.toList()

        override suspend fun getById(id: String): OpportunityEntity? =
            stored.firstOrNull { it.id == id }

        override suspend fun clearAll() {
            stored.clear()
        }
    }

    private class StaticSource(
        private val items: List<Opportunity>,
    ) : OpportunityRepository {
        override suspend fun getOpportunities(): List<Opportunity> = items
        override suspend fun getOpportunity(id: String): Opportunity? =
            items.firstOrNull { it.id == id }
        override suspend fun search(filters: OpportunitySearchFilters): List<Opportunity> = items
    }

    private class FailingSource : OpportunityRepository {
        override suspend fun getOpportunities(): List<Opportunity> =
            throw IllegalStateException("backend unavailable")
        override suspend fun getOpportunity(id: String): Opportunity? =
            throw IllegalStateException("backend unavailable")
        override suspend fun search(filters: OpportunitySearchFilters): List<Opportunity> =
            throw IllegalStateException("backend unavailable")
    }
}
