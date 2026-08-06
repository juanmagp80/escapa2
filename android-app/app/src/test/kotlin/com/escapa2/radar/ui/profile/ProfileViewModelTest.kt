package com.escapa2.radar.ui.profile

import com.escapa2.radar.data.model.AirportPreference
import com.escapa2.radar.data.model.TravelProfile
import com.escapa2.radar.data.model.TransportMode
import com.escapa2.radar.data.repository.ProfileRepository
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
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Before
import org.junit.Test

@OptIn(ExperimentalCoroutinesApi::class)
class ProfileViewModelTest {

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
    fun loadFillsFormFromRepository() = runTest(dispatcher.scheduler) {
        val repository = InMemoryProfileRepository(
            profile = sampleProfile().copy(originCity = "Valencia"),
        )
        val viewModel = ProfileViewModel(repository)
        advanceUntilIdle()

        assertEquals(UiState.Content(Unit), viewModel.loadState.value)
        assertEquals("Valencia", viewModel.form.value.originCity)
        assertEquals("198.0", viewModel.form.value.budgetText)
    }

    @Test
    fun toggleInterestAddsAndRemovesValue() = runTest(dispatcher.scheduler) {
        val viewModel = ProfileViewModel(InMemoryProfileRepository(sampleProfile()))
        advanceUntilIdle()

        viewModel.toggleInterest("playa")
        assertTrue("playa" in viewModel.form.value.interests)

        viewModel.toggleInterest("playa")
        assertTrue("playa" !in viewModel.form.value.interests)
    }

    @Test
    fun savePersistsEditedProfile() = runTest(dispatcher.scheduler) {
        val repository = InMemoryProfileRepository(sampleProfile())
        val viewModel = ProfileViewModel(repository)
        advanceUntilIdle()

        viewModel.updateOriginCity("Bilbao")
        viewModel.updateTransport(TransportMode.CAR)
        viewModel.save()
        advanceUntilIdle()

        assertEquals(UiState.Content(Unit), viewModel.saveState.value)
        val saved = repository.lastSaved!!
        assertEquals("Bilbao", saved.originCity)
        assertEquals(TransportMode.CAR, saved.preferredTransport)
    }

    @Test
    fun saveExposesErrorWhenRepositoryFails() = runTest(dispatcher.scheduler) {
        val viewModel = ProfileViewModel(FailingSaveRepository(sampleProfile()))
        advanceUntilIdle()

        viewModel.save()
        advanceUntilIdle()

        assertTrue(viewModel.saveState.value is UiState.Error)
    }

    @Test
    fun toggleAirportEnabledFlipsFlag() = runTest(dispatcher.scheduler) {
        val profile = sampleProfile().copy(
            airports = listOf(
                AirportPreference("airport-mad", "MAD", true, 12.0, 45),
            ),
        )
        val viewModel = ProfileViewModel(InMemoryProfileRepository(profile))
        advanceUntilIdle()

        viewModel.toggleAirportEnabled("MAD")
        assertFalse(viewModel.form.value.airports.single().enabled)

        viewModel.toggleAirportEnabled("MAD")
        assertTrue(viewModel.form.value.airports.single().enabled)
    }

    @Test
    fun removeAirportDropsFromList() = runTest(dispatcher.scheduler) {
        val profile = sampleProfile().copy(
            airports = listOf(
                AirportPreference("airport-mad", "MAD", true, 12.0, 45),
                AirportPreference("airport-bcn", "BCN", true, 20.0, 60),
            ),
        )
        val viewModel = ProfileViewModel(InMemoryProfileRepository(profile))
        advanceUntilIdle()

        viewModel.removeAirport("MAD")
        assertEquals(listOf("BCN"), viewModel.form.value.airports.map { it.iataCode })
    }

    @Test
    fun addAirportAppendsEnabledAirport() = runTest(dispatcher.scheduler) {
        val viewModel = ProfileViewModel(InMemoryProfileRepository(sampleProfile()))
        advanceUntilIdle()

        viewModel.addAirport(" bcn ")
        val added = viewModel.form.value.airports.single()
        assertEquals("BCN", added.iataCode)
        assertTrue(added.enabled)
    }

    @Test
    fun addAirportRejectsInvalidOrDuplicateCode() = runTest(dispatcher.scheduler) {
        val profile = sampleProfile().copy(
            airports = listOf(AirportPreference("airport-mad", "MAD", true, 12.0, 45)),
        )
        val viewModel = ProfileViewModel(InMemoryProfileRepository(profile))
        advanceUntilIdle()

        viewModel.addAirport("MAD")
        viewModel.addAirport("X")
        assertEquals(1, viewModel.form.value.airports.size)
    }

    private class FailingSaveRepository(
        private val profile: TravelProfile,
    ) : ProfileRepository {
        override suspend fun getProfile(): TravelProfile = profile

        override suspend fun saveProfile(updated: TravelProfile): TravelProfile =
            throw IllegalStateException("profile unavailable")
    }

    private fun sampleProfile() = TravelProfile(
        id = "dev-profile",
        originCity = "Madrid",
        currency = "EUR",
        defaultBudgetEur = 198.0,
        maxDriveMinutes = 240,
        preferredTransport = TransportMode.EITHER,
        interests = listOf("ciudad"),
        avoidPreferences = emptyList(),
        airports = emptyList(),
    )

    private class InMemoryProfileRepository(
        private var profile: TravelProfile,
    ) : ProfileRepository {
        var lastSaved: TravelProfile? = null
            private set

        override suspend fun getProfile(): TravelProfile = profile

        override suspend fun saveProfile(updated: TravelProfile): TravelProfile {
            lastSaved = updated
            profile = updated
            return updated
        }
    }
}
