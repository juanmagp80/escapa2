package com.escapa2.radar.ui.detail

import com.escapa2.radar.data.model.AiSummary
import com.escapa2.radar.data.model.Opportunity
import com.escapa2.radar.data.model.OpportunitySearchFilters
import com.escapa2.radar.data.model.TransportMode
import com.escapa2.radar.data.repository.AiRepository
import com.escapa2.radar.data.repository.FakeAiRepository
import com.escapa2.radar.data.repository.OpportunityRepository
import com.escapa2.radar.data.repository.SearchWatchRepository
import com.escapa2.radar.data.model.SearchWatch
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
class OpportunityDetailViewModelTest {

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
    fun loadExposesContentForKnownOpportunity() = runTest(dispatcher.scheduler) {
        val viewModel = OpportunityDetailViewModel(
            SingleRepository(sampleOpportunity()),
            FakeAiRepository(),
            StaticWatchRepository(),
        )
        viewModel.load("opp-1")
        advanceUntilIdle()

        val state = viewModel.uiState.value
        assertTrue(state is UiState.Content)
        assertEquals("Santiago de Compostela", (state as UiState.Content).data.destinationName)
    }

    @Test
    fun loadExposesEmptyForUnknownOpportunity() = runTest(dispatcher.scheduler) {
        val viewModel = OpportunityDetailViewModel(
            SingleRepository(sampleOpportunity()),
            FakeAiRepository(),
            StaticWatchRepository(),
        )
        viewModel.load("opp-missing")
        advanceUntilIdle()

        assertTrue(viewModel.uiState.value is UiState.Empty)
    }

    @Test
    fun loadExposesErrorWhenRepositoryFails() = runTest(dispatcher.scheduler) {
        val viewModel = OpportunityDetailViewModel(
            FailingRepository(),
            FakeAiRepository(),
            StaticWatchRepository(),
        )
        viewModel.load("opp-1")
        advanceUntilIdle()

        val state = viewModel.uiState.value
        assertTrue(state is UiState.Error)
        assertTrue((state as UiState.Error).message.isNotBlank())
    }

    @Test
    fun loadLoadsAiSummaryForKnownOpportunity() = runTest(dispatcher.scheduler) {
        val viewModel = OpportunityDetailViewModel(
            SingleRepository(sampleOpportunity()),
            FakeAiRepository(),
            StaticWatchRepository(),
        )
        viewModel.load("opp-1")
        advanceUntilIdle()

        val summaryState = viewModel.summary.value
        assertTrue(summaryState is UiState.Content)
        val summary = (summaryState as UiState.Content).data
        assertEquals("Buena opción dentro del presupuesto", summary.headline)
        assertTrue(summary.generatedByAi.not())
    }

    @Test
    fun loadExposesSummaryErrorWithoutBlockingDetail() = runTest(dispatcher.scheduler) {
        val viewModel = OpportunityDetailViewModel(
            SingleRepository(sampleOpportunity()),
            FailingAiRepository(),
            StaticWatchRepository(),
        )
        viewModel.load("opp-1")
        advanceUntilIdle()

        assertTrue(viewModel.uiState.value is UiState.Content)
        assertTrue(viewModel.summary.value is UiState.Error)
    }

    @Test
    fun followCreatesWatchAndExposesContent() = runTest(dispatcher.scheduler) {
        val watchRepository = StaticWatchRepository()
        val viewModel = OpportunityDetailViewModel(
            SingleRepository(sampleOpportunity()),
            FakeAiRepository(),
            watchRepository,
        )
        viewModel.load("opp-1")
        advanceUntilIdle()

        viewModel.follow()
        advanceUntilIdle()

        assertTrue(viewModel.followState.value is UiState.Content)
        assertEquals(1, watchRepository.created.size)
        assertEquals("Santiago de Compostela", watchRepository.created[0].name)
    }

    @Test
    fun followExposesErrorWhenRepositoryFails() = runTest(dispatcher.scheduler) {
        val viewModel = OpportunityDetailViewModel(
            SingleRepository(sampleOpportunity()),
            FakeAiRepository(),
            FailingWatchRepository(),
        )
        viewModel.load("opp-1")
        advanceUntilIdle()

        viewModel.follow()
        advanceUntilIdle()

        assertTrue(viewModel.followState.value is UiState.Error)
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

    private class SingleRepository(
        private val opportunity: Opportunity,
    ) : OpportunityRepository {
        override suspend fun getOpportunities(): List<Opportunity> = listOf(opportunity)
        override suspend fun getOpportunity(id: String): Opportunity? =
            opportunity.takeIf { it.id == id }
        override suspend fun search(filters: OpportunitySearchFilters): List<Opportunity> =
            listOf(opportunity)
    }

    private class FailingRepository : OpportunityRepository {
        override suspend fun getOpportunities(): List<Opportunity> =
            throw IllegalStateException("backend unavailable")
        override suspend fun getOpportunity(id: String): Opportunity? =
            throw IllegalStateException("backend unavailable")
        override suspend fun search(filters: OpportunitySearchFilters): List<Opportunity> =
            throw IllegalStateException("backend unavailable")
    }

    private class FailingAiRepository : AiRepository {
        override suspend fun summarizeOpportunity(opportunity: Opportunity): AiSummary =
            throw IllegalStateException("ai unavailable")
    }

    private class StaticWatchRepository : SearchWatchRepository {
        val created = mutableListOf<SearchWatch>()

        override suspend fun getWatches(): List<SearchWatch> = created

        override suspend fun createWatch(name: String, initialPriceEur: Double): SearchWatch {
            val watch = SearchWatch(
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
            created.add(watch)
            return watch
        }
    }

    private class FailingWatchRepository : SearchWatchRepository {
        override suspend fun getWatches(): List<SearchWatch> =
            throw IllegalStateException("backend unavailable")

        override suspend fun createWatch(name: String, initialPriceEur: Double): SearchWatch =
            throw IllegalStateException("backend unavailable")
    }
}
