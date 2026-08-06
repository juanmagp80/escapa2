package com.escapa2.radar.ui.radar

import com.escapa2.radar.data.model.SearchWatch
import com.escapa2.radar.data.model.WatchRunResult
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
class RadarViewModelTest {

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
    fun loadExposesContentWhenRepositoryReturnsWatches() = runTest(dispatcher.scheduler) {
        val viewModel = RadarViewModel(StaticWatchRepository(listOf(sampleWatch())))
        advanceUntilIdle()

        val state = viewModel.uiState.value
        assertTrue(state is UiState.Content)
        assertEquals(1, (state as UiState.Content).data.size)
        assertEquals("Porto en avión", (state as UiState.Content).data[0].name)
    }

    @Test
    fun loadExposesEmptyWhenRepositoryReturnsNothing() = runTest(dispatcher.scheduler) {
        val viewModel = RadarViewModel(StaticWatchRepository(emptyList()))
        advanceUntilIdle()

        assertTrue(viewModel.uiState.value is UiState.Empty)
    }

    @Test
    fun loadExposesErrorWhenRepositoryFails() = runTest(dispatcher.scheduler) {
        val viewModel = RadarViewModel(FailingWatchRepository())
        advanceUntilIdle()

        val state = viewModel.uiState.value
        assertTrue(state is UiState.Error)
        assertTrue((state as UiState.Error).message.isNotBlank())
    }

    @Test
    fun runWatchExposesAlertsAndReloadsWatches() = runTest(dispatcher.scheduler) {
        val repository = StaticWatchRepository(listOf(sampleWatch()))
        val viewModel = RadarViewModel(repository)
        advanceUntilIdle()

        viewModel.runWatch("watch-porto")
        advanceUntilIdle()

        assertNull(viewModel.runningWatchId.value)
        val message = viewModel.runMessage.value
        assertTrue(message is RunMessage.Success)
        assertEquals(listOf("Nuevo mínimo histórico: 296 EUR"), (message as RunMessage.Success).result.alerts)
        assertEquals(1, repository.runCount)
        assertTrue(viewModel.uiState.value is UiState.Content)
    }

    @Test
    fun runWatchExposesFailureMessage() = runTest(dispatcher.scheduler) {
        val viewModel = RadarViewModel(FailingWatchRepository())
        advanceUntilIdle()

        viewModel.runWatch("watch-porto")
        advanceUntilIdle()

        assertNull(viewModel.runningWatchId.value)
        val message = viewModel.runMessage.value
        assertTrue(message is RunMessage.Failure)
        assertTrue((message as RunMessage.Failure).message.isNotBlank())
    }

    private fun sampleWatch() = SearchWatch(
        id = "watch-porto",
        name = "Porto en avión",
        status = "ACTIVE",
        lastRunAt = "2026-08-05T12:00:00Z",
        nextRunAt = "2026-08-06T12:00:00Z",
        changeSinceYesterdayEur = -16.0,
        minRecordedEur = 312.0,
        alertRules = listOf("Nuevo mínimo histórico"),
        priceHistory = listOf(328.0, 312.0),
    )

    private class StaticWatchRepository(
        private val items: List<SearchWatch>,
    ) : SearchWatchRepository {
        var runCount = 0

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

        override suspend fun runWatch(id: String): WatchRunResult {
            runCount += 1
            return WatchRunResult(
                lastRunAt = "2026-08-06T12:00:00Z",
                nextRunAt = "2026-08-07T12:00:00Z",
                matchedCount = 1,
                alerts = listOf("Nuevo mínimo histórico: 296 EUR"),
            )
        }
    }

    private class FailingWatchRepository : SearchWatchRepository {
        override suspend fun getWatches(): List<SearchWatch> =
            throw IllegalStateException("backend unavailable")

        override suspend fun createWatch(name: String, initialPriceEur: Double): SearchWatch =
            throw IllegalStateException("backend unavailable")

        override suspend fun runWatch(id: String): WatchRunResult =
            throw IllegalStateException("backend unavailable")
    }
}
