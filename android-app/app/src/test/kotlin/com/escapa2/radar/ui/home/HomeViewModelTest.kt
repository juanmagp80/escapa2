package com.escapa2.radar.ui.home

import com.escapa2.radar.data.model.AvailabilityWindow
import com.escapa2.radar.data.model.Opportunity
import com.escapa2.radar.data.model.OpportunitySearchFilters
import com.escapa2.radar.data.model.PriceSnapshot
import com.escapa2.radar.data.model.SearchWatch
import com.escapa2.radar.data.model.TransportMode
import com.escapa2.radar.data.model.WatchRunResult
import com.escapa2.radar.data.repository.AvailabilityRepository
import com.escapa2.radar.data.repository.OpportunityRepository
import com.escapa2.radar.data.repository.SearchWatchRepository
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
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Before
import org.junit.Test

@OptIn(ExperimentalCoroutinesApi::class)
class HomeViewModelTest {

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
    fun loadExposesContentWhenRepositoryReturnsData() = runTest(dispatcher.scheduler) {
        val viewModel = HomeViewModel(
            StaticRepository(listOf(sampleOpportunity())),
            StaticWatchRepository(emptyList()),
            StaticAvailabilityRepository(listOf(sampleWindow())),
        )
        advanceUntilIdle()

        val state = viewModel.uiState.value
        assertTrue(state is UiState.Content)
        val dashboard = (state as UiState.Content).data
        assertEquals(1, dashboard.opportunities.size)
        assertEquals("Santiago de Compostela", dashboard.opportunities[0].destinationName)
        assertEquals("Santiago de Compostela", dashboard.bestOpportunity?.destinationName)
        assertEquals("2026-08-05T12:00:00Z", dashboard.lastUpdateAt)
        assertEquals(1, dashboard.availabilityWindows.size)
    }

    @Test
    fun loadExposesEmptyWhenRepositoryReturnsNothing() = runTest(dispatcher.scheduler) {
        val viewModel = HomeViewModel(
            StaticRepository(emptyList()),
            StaticWatchRepository(emptyList()),
            StaticAvailabilityRepository(emptyList()),
        )
        advanceUntilIdle()

        assertTrue(viewModel.uiState.value is UiState.Empty)
    }

    @Test
    fun loadExposesErrorWhenRepositoryFails() = runTest(dispatcher.scheduler) {
        val viewModel = HomeViewModel(
            FailingRepository(),
            StaticWatchRepository(emptyList()),
            StaticAvailabilityRepository(emptyList()),
        )
        advanceUntilIdle()

        val state = viewModel.uiState.value
        assertTrue(state is UiState.Error)
        assertTrue((state as UiState.Error).message.isNotBlank())
    }

    @Test
    fun bestOpportunityPrefersHigherValueScore() = runTest(dispatcher.scheduler) {
        val lowScore = sampleOpportunity().copy(
            id = "low",
            destinationName = "Bajo",
            valueScore = 60.0,
            costPerUsefulHourEur = 4.0,
        )
        val highScore = sampleOpportunity().copy(
            id = "high",
            destinationName = "Alto",
            valueScore = 90.0,
            costPerUsefulHourEur = 9.0,
        )
        val viewModel = HomeViewModel(
            StaticRepository(listOf(lowScore, highScore)),
            StaticWatchRepository(emptyList()),
            StaticAvailabilityRepository(emptyList()),
        )
        advanceUntilIdle()

        val dashboard = (viewModel.uiState.value as UiState.Content).data
        assertEquals("Alto", dashboard.bestOpportunity?.destinationName)
    }

    @Test
    fun biggestDropPicksLargestPreviousDelta() = runTest(dispatcher.scheduler) {
        val smallDrop = sampleOpportunity().copy(
            id = "small",
            destinationName = "Pequeña",
            totalCostEur = 190.0,
            previousTotalCostEur = 200.0,
        )
        val bigDrop = sampleOpportunity().copy(
            id = "big",
            destinationName = "Grande",
            totalCostEur = 150.0,
            previousTotalCostEur = 260.0,
        )
        val viewModel = HomeViewModel(
            StaticRepository(listOf(smallDrop, bigDrop)),
            StaticWatchRepository(emptyList()),
            StaticAvailabilityRepository(emptyList()),
        )
        advanceUntilIdle()

        val dashboard = (viewModel.uiState.value as UiState.Content).data
        assertEquals("Grande", dashboard.biggestDrop?.destinationName)
    }

    @Test
    fun biggestDropIsNullWithoutPreviousPrices() = runTest(dispatcher.scheduler) {
        val noPrevious = sampleOpportunity().copy(previousTotalCostEur = null)
        val viewModel = HomeViewModel(
            StaticRepository(listOf(noPrevious)),
            StaticWatchRepository(emptyList()),
            StaticAvailabilityRepository(emptyList()),
        )
        advanceUntilIdle()

        val dashboard = (viewModel.uiState.value as UiState.Content).data
        assertNull(dashboard.biggestDrop)
    }

    @Test
    fun watchesAreExposedInDashboard() = runTest(dispatcher.scheduler) {
        val watch = SearchWatch(
            id = "watch-1",
            name = "Porto en avión",
            status = "ACTIVE",
            lastRunAt = "2026-08-05T12:00:00Z",
            nextRunAt = "2026-08-06T12:00:00Z",
            changeSinceYesterdayEur = -16.0,
            minRecordedEur = 312.0,
            alertRules = emptyList(),
            priceHistory = emptyList(),
        )
        val viewModel = HomeViewModel(
            StaticRepository(listOf(sampleOpportunity())),
            StaticWatchRepository(listOf(watch)),
            StaticAvailabilityRepository(emptyList()),
        )
        advanceUntilIdle()

        val dashboard = (viewModel.uiState.value as UiState.Content).data
        assertEquals(1, dashboard.watches.size)
        assertEquals("Porto en avión", dashboard.watches[0].name)
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
        previousTotalCostEur = 212.0,
        valueScore = 100.0,
    )

    private fun sampleWindow() = AvailabilityWindow(
        id = "avail-1",
        startAt = "2026-08-14T18:00:00+02:00",
        endAt = "2026-08-16T22:00:00+02:00",
        kind = "WEEKEND",
        isFlexible = true,
    )

    private class StaticAvailabilityRepository(
        private val items: List<AvailabilityWindow>,
    ) : AvailabilityRepository {
        override suspend fun getWindows(): List<AvailabilityWindow> = items
    }

    private class StaticRepository(
        private val items: List<Opportunity>,
    ) : OpportunityRepository {
        override suspend fun getOpportunities(): List<Opportunity> = items
        override suspend fun getOpportunity(id: String): Opportunity? =
            items.firstOrNull { it.id == id }
        override suspend fun search(filters: OpportunitySearchFilters): List<Opportunity> = items
        override suspend fun getPriceHistory(id: String): List<PriceSnapshot> = emptyList()
    }

    private class FailingRepository : OpportunityRepository {
        override suspend fun getOpportunities(): List<Opportunity> =
            throw IllegalStateException("backend unavailable")
        override suspend fun getOpportunity(id: String): Opportunity? =
            throw IllegalStateException("backend unavailable")
        override suspend fun search(filters: OpportunitySearchFilters): List<Opportunity> =
            throw IllegalStateException("backend unavailable")
        override suspend fun getPriceHistory(id: String): List<PriceSnapshot> =
            throw IllegalStateException("backend unavailable")
    }

    private class StaticWatchRepository(
        private val items: List<SearchWatch>,
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