package com.escapa2.radar.data.repository

import com.escapa2.radar.data.model.AiSummary
import com.escapa2.radar.data.model.DailyReport
import com.escapa2.radar.data.model.DailyReportEntry
import com.escapa2.radar.data.model.DeviceRegistration
import com.escapa2.radar.data.model.Opportunity
import com.escapa2.radar.data.model.OpportunitySearchFilters
import com.escapa2.radar.data.model.PriceSnapshot
import com.escapa2.radar.data.model.SearchWatch
import com.escapa2.radar.data.model.TransportMode
import com.escapa2.radar.data.model.TravelProfile
import com.escapa2.radar.data.model.WatchRunResult
import java.io.IOException
import kotlinx.coroutines.runBlocking
import org.junit.Assert.assertEquals
import org.junit.Test

class FallbackRepositoriesTest {

    private val localOpportunities = listOf(
        sampleOpportunity.copy(id = "local-1", destinationName = "Fake"),
    )

    @Test
    fun opportunityRepositoryFallsBackOnIOException() {
        val remote = FailingOpportunityRepository(IOException("no network"))
        val fallback = FallbackOpportunityRepository(remote, FakeLocalOpportunityRepository())

        runBlocking {
            assertEquals("Fake", fallback.getOpportunities().first().destinationName)
            assertEquals("Fake", fallback.getOpportunity("local-1")?.destinationName)
            assertEquals("Fake", fallback.search(OpportunitySearchFilters()).first().destinationName)
        }
    }

    @Test
    fun opportunityRepositoryRethrowsNonNetworkErrors() {
        val remote = FailingOpportunityRepository(IllegalArgumentException("bad request"))
        val fallback = FallbackOpportunityRepository(remote, FakeLocalOpportunityRepository())

        assertThrows(IllegalArgumentException::class.java) {
            runBlocking { fallback.getOpportunities() }
        }
    }

    @Test
    fun aiRepositoryFallsBackOnIOException() {
        val remote = FailingAiRepository(IOException("no network"))
        val fallback = FallbackAiRepository(remote, LocalAiRepository())

        runBlocking {
            assertEquals("Local", fallback.summarizeOpportunity(sampleOpportunity).headline)
        }
    }

    @Test
    fun aiRepositoryReturnsRemoteResultWhenAvailable() {
        val remote = RemoteAiRepositoryStub()
        val fallback = FallbackAiRepository(remote, LocalAiRepository())

        runBlocking {
            assertEquals("Remote", fallback.summarizeOpportunity(sampleOpportunity).headline)
        }
    }

    @Test
    fun aiRepositoryDailyReportFallsBackOnIOException() {
        val remote = FailingAiRepository(IOException("no network"))
        val fallback = FallbackAiRepository(remote, LocalAiRepository())

        runBlocking {
            assertEquals("Local", fallback.generateDailyReport().headline)
        }
    }

    @Test
    fun aiRepositoryDailyReportReturnsRemoteResultWhenAvailable() {
        val remote = RemoteAiRepositoryStub()
        val fallback = FallbackAiRepository(remote, LocalAiRepository())

        runBlocking {
            assertEquals("Remote", fallback.generateDailyReport().headline)
        }
    }

    @Test
    fun profileRepositoryFallsBackOnIOException() {
        val remote = FailingProfileRepository(IOException("no network"))
        val fallback = FallbackProfileRepository(remote, LocalProfileRepository())

        runBlocking {
            assertEquals("FakeCity", fallback.getProfile().originCity)
        }
    }

    @Test
    fun searchWatchRepositoryFallsBackOnIOException() {
        val remote = FailingSearchWatchRepository(IOException("no network"))
        val fallback = FallbackSearchWatchRepository(remote, LocalSearchWatchRepository())

        runBlocking {
            assertEquals("FakeWatch", fallback.getWatches().first().name)
            assertEquals("created-1", fallback.createWatch("Nuevo", 300.0).id)
        }
    }

    @Test
    fun deviceRepositoryFallsBackOnIOException() {
        val remote = FailingDeviceRepository(IOException("no network"))
        val fallback = FallbackDeviceRepository(remote, LocalDeviceRepository())

        runBlocking {
            assertEquals("local-device", fallback.register("android-token-1").id)
            fallback.unregister("android-token-1")
        }
    }

    @Test
    fun deviceRepositoryRethrowsNonNetworkErrors() {
        val remote = FailingDeviceRepository(IllegalArgumentException("bad request"))
        val fallback = FallbackDeviceRepository(remote, LocalDeviceRepository())

        assertThrows(IllegalArgumentException::class.java) {
            runBlocking { fallback.register("android-token-1") }
        }
    }

    private fun assertThrows(expected: Class<out Throwable>, block: () -> Unit) {
        try {
            block()
        } catch (t: Throwable) {
            if (expected.isInstance(t)) return
            throw AssertionError("Expected ${expected.simpleName} but got $t", t)
        }
        throw AssertionError("Expected ${expected.simpleName} but nothing was thrown")
    }

    private inner class FailingOpportunityRepository(
        private val error: Throwable,
    ) : OpportunityRepository {
        override suspend fun getOpportunities(): List<Opportunity> = throw error
        override suspend fun getOpportunity(id: String): Opportunity? = throw error
        override suspend fun search(filters: OpportunitySearchFilters): List<Opportunity> = throw error
        override suspend fun getPriceHistory(id: String): List<PriceSnapshot> = throw error
    }

    private inner class FakeLocalOpportunityRepository : OpportunityRepository {
        override suspend fun getOpportunities(): List<Opportunity> = localOpportunities
        override suspend fun getOpportunity(id: String): Opportunity? =
            localOpportunities.firstOrNull { it.id == id }
        override suspend fun search(filters: OpportunitySearchFilters): List<Opportunity> = localOpportunities
        override suspend fun getPriceHistory(id: String): List<PriceSnapshot> = emptyList()
    }

    private inner class FailingAiRepository(
        private val error: Throwable,
    ) : AiRepository {
        override suspend fun summarizeOpportunity(opportunity: Opportunity): AiSummary = throw error
        override suspend fun generateDailyReport(): DailyReport = throw error
    }

    private inner class RemoteAiRepositoryStub : AiRepository {
        override suspend fun summarizeOpportunity(opportunity: Opportunity): AiSummary =
            localSummary.copy(headline = "Remote", generatedByAi = true)
        override suspend fun generateDailyReport(): DailyReport =
            localReport.copy(headline = "Remote", generatedByAi = true)
    }

    private inner class LocalAiRepository : AiRepository {
        override suspend fun summarizeOpportunity(opportunity: Opportunity): AiSummary = localSummary
        override suspend fun generateDailyReport(): DailyReport = localReport
    }

    private inner class FailingProfileRepository(
        private val error: Throwable,
    ) : ProfileRepository {
        override suspend fun getProfile(): TravelProfile = throw error
        override suspend fun saveProfile(profile: TravelProfile): TravelProfile = throw error
    }

    private inner class LocalProfileRepository : ProfileRepository {
        override suspend fun getProfile(): TravelProfile = TravelProfile(
            id = "local-profile",
            originCity = "FakeCity",
            currency = "EUR",
            defaultBudgetEur = 350.0,
            maxDriveMinutes = 240,
            preferredTransport = TransportMode.EITHER,
            interests = emptyList(),
            avoidPreferences = emptyList(),
            airports = emptyList(),
        )

        override suspend fun saveProfile(profile: TravelProfile): TravelProfile = profile
    }

    private inner class FailingSearchWatchRepository(
        private val error: Throwable,
    ) : SearchWatchRepository {
        override suspend fun getWatches(): List<SearchWatch> = throw error
        override suspend fun createWatch(name: String, initialPriceEur: Double): SearchWatch = throw error
        override suspend fun runWatch(id: String): WatchRunResult = throw error
    }

    private inner class FailingDeviceRepository(
        private val error: Throwable,
    ) : DeviceRepository {
        override suspend fun register(token: String): DeviceRegistration = throw error
        override suspend fun unregister(token: String) = throw error
    }

    private inner class LocalDeviceRepository : DeviceRepository {
        override suspend fun register(token: String): DeviceRegistration =
            DeviceRegistration(
                id = "local-device",
                userId = "dev-user",
                token = token,
                platform = "android",
            )

        override suspend fun unregister(token: String) = Unit
    }

    private inner class LocalSearchWatchRepository : SearchWatchRepository {
        override suspend fun getWatches(): List<SearchWatch> =
            listOf(localWatch)

        override suspend fun createWatch(name: String, initialPriceEur: Double): SearchWatch =
            localWatch.copy(id = "created-1", name = name)

        override suspend fun runWatch(id: String): WatchRunResult =
            WatchRunResult(
                lastRunAt = "2026-08-06T12:00:00Z",
                nextRunAt = "2026-08-07T12:00:00Z",
                matchedCount = 1,
                alerts = emptyList(),
            )
    }

    companion object {
        private val sampleOpportunity = Opportunity(
            id = "opp-1",
            destinationCode = "SVQ",
            destinationName = "Sevilla",
            transportMode = TransportMode.FLIGHT,
            startAt = "2026-08-14T19:45:00+02:00",
            endAt = "2026-08-16T21:10:00+02:00",
            usefulHours = 30.0,
            totalCostEur = 246.0,
            costPerPersonEur = 123.0,
            costPerNightEur = 123.0,
            costPerUsefulHourEur = 8.2,
            verifiedAt = "2026-08-05T12:00:00Z",
        )

        private val localSummary = AiSummary(
            headline = "Local",
            summary = "Local summary",
            pros = emptyList(),
            cons = emptyList(),
            confidence = "LOW",
            generatedByAi = false,
        )

        private val localReport = DailyReport(
            headline = "Local",
            summary = "Local report",
            entries = listOf(
                DailyReportEntry(
                    watchName = "Porto",
                    destination = "Porto",
                    changeEur = 16.0,
                    changePercent = 4.9,
                    isNewLow = false,
                    withinBudget = null,
                    recommendation = "Ha bajado 16.00 EUR",
                    confidence = "HIGH",
                )
            ),
            warnings = emptyList(),
            generatedByAi = false,
        )

        private val localWatch = SearchWatch(
            id = "watch-local",
            name = "FakeWatch",
            status = "ACTIVE",
            lastRunAt = "2026-08-05T12:00:00Z",
            nextRunAt = "2026-08-06T12:00:00Z",
            changeSinceYesterdayEur = null,
            minRecordedEur = 300.0,
            alertRules = emptyList(),
            priceHistory = emptyList(),
        )
    }
}
