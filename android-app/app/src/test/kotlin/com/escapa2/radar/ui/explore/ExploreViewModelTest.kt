package com.escapa2.radar.ui.explore

import com.escapa2.radar.data.model.Opportunity
import com.escapa2.radar.data.model.OpportunitySearchFilters
import com.escapa2.radar.data.model.TransportMode
import com.escapa2.radar.data.repository.OpportunityRepository
import com.escapa2.radar.data.repository.filterOpportunities
import com.escapa2.radar.ui.components.UiState
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.test.StandardTestDispatcher
import kotlinx.coroutines.test.advanceUntilIdle
import kotlinx.coroutines.test.resetMain
import kotlinx.coroutines.test.runTest
import kotlinx.coroutines.test.setMain
import org.junit.After
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Before
import org.junit.Test

@OptIn(ExperimentalCoroutinesApi::class)
class ExploreViewModelTest {

    private val dispatcher = StandardTestDispatcher()

    @Before
    fun setUp() {
        Dispatchers.setMain(dispatcher)
    }

    @After
    fun tearDown() {
        Dispatchers.resetMain()
    }

    @Test
    fun searchExposesContentWhenResultsExist() = runTest(dispatcher.scheduler) {
        val viewModel = ExploreViewModel(FakeSearchRepository())
        advanceUntilIdle()

        viewModel.search(
            maxTotalCostEur = 300.0,
            transportMode = null,
            minUsefulHours = null,
        )
        advanceUntilIdle()

        val state = viewModel.uiState.value
        assertTrue(state is UiState.Content)
        assertEquals(2, (state as UiState.Content).data.size)
    }

    @Test
    fun searchExposesEmptyWhenNoResultsMatch() = runTest(dispatcher.scheduler) {
        val viewModel = ExploreViewModel(FakeSearchRepository())
        advanceUntilIdle()

        viewModel.search(
            maxTotalCostEur = 1.0,
            transportMode = null,
            minUsefulHours = null,
        )
        advanceUntilIdle()

        assertTrue(viewModel.uiState.value is UiState.Empty)
    }

    @Test
    fun searchExposesErrorWhenRepositoryFails() = runTest(dispatcher.scheduler) {
        val viewModel = ExploreViewModel(FailingSearchRepository())
        advanceUntilIdle()

        viewModel.search(
            maxTotalCostEur = null,
            transportMode = null,
            minUsefulHours = null,
        )
        advanceUntilIdle()

        val state = viewModel.uiState.value
        assertTrue(state is UiState.Error)
        assertTrue((state as UiState.Error).message.isNotBlank())
    }

    @Test
    fun searchWithDestinationQueryFiltersResults() = runTest(dispatcher.scheduler) {
        val viewModel = ExploreViewModel(FakeSearchRepository())
        advanceUntilIdle()

        viewModel.search(
            destinationQuery = "sevilla",
        )
        advanceUntilIdle()

        val state = viewModel.uiState.value
        assertTrue(state is UiState.Content)
        assertEquals(1, (state as UiState.Content).data.size)
        assertEquals("Sevilla", state.data[0].destinationName)
    }

    @Test
    fun clearResultsResetsToEmpty() = runTest(dispatcher.scheduler) {
        val viewModel = ExploreViewModel(FakeSearchRepository())
        advanceUntilIdle()

        viewModel.search(maxTotalCostEur = null, transportMode = null, minUsefulHours = null)
        advanceUntilIdle()
        assertTrue(viewModel.uiState.value is UiState.Content)

        viewModel.clearResults()
        assertTrue(viewModel.uiState.value is UiState.Empty)
    }

    private class FakeSearchRepository : OpportunityRepository {
        private val items = listOf(
            sampleOpportunity("opp-1", "Santiago de Compostela", TransportMode.CAR, 198.0),
            sampleOpportunity("opp-2", "Sevilla", TransportMode.FLIGHT, 246.0),
        )

        override suspend fun getOpportunities(): List<Opportunity> = items
        override suspend fun getOpportunity(id: String): Opportunity? =
            items.firstOrNull { it.id == id }
        override suspend fun search(filters: OpportunitySearchFilters): List<Opportunity> =
            filterOpportunities(items, filters)
    }

    private class FailingSearchRepository : OpportunityRepository {
        override suspend fun getOpportunities(): List<Opportunity> =
            throw IllegalStateException("backend unavailable")
        override suspend fun getOpportunity(id: String): Opportunity? =
            throw IllegalStateException("backend unavailable")
        override suspend fun search(filters: OpportunitySearchFilters): List<Opportunity> =
            throw IllegalStateException("backend unavailable")
    }
}

private fun sampleOpportunity(
    id: String,
    name: String,
    mode: TransportMode,
    total: Double,
) = Opportunity(
    id = id,
    destinationCode = id.uppercase(),
    destinationName = name,
    transportMode = mode,
    startAt = "2026-08-14T18:30:00+02:00",
    endAt = "2026-08-16T20:00:00+02:00",
    usefulHours = 30.0,
    totalCostEur = total,
    costPerPersonEur = total / 2,
    costPerNightEur = total / 2,
    costPerUsefulHourEur = total / 30,
    verifiedAt = "2026-08-05T12:00:00Z",
)
