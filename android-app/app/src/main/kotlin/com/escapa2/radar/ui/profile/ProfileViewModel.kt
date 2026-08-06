package com.escapa2.radar.ui.profile

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.escapa2.radar.data.model.AirportPreference
import com.escapa2.radar.data.model.TravelProfile
import com.escapa2.radar.data.model.TransportMode
import com.escapa2.radar.data.repository.ProfileRepository
import com.escapa2.radar.ui.components.UiState
import dagger.hilt.android.lifecycle.HiltViewModel
import javax.inject.Inject
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

/**
 * Editable profile form with a separate [saveState] for explicit save feedback.
 */
@HiltViewModel
class ProfileViewModel @Inject constructor(
    private val repository: ProfileRepository,
) : ViewModel() {

    private val _form = MutableStateFlow(ProfileForm())
    val form: StateFlow<ProfileForm> = _form.asStateFlow()

    private val _loadState = MutableStateFlow<UiState<Unit>>(UiState.Loading)
    val loadState: StateFlow<UiState<Unit>> = _loadState.asStateFlow()

    private val _saveState = MutableStateFlow<UiState<Unit>?>(null)
    val saveState: StateFlow<UiState<Unit>?> = _saveState.asStateFlow()

    private var loadedProfileId: String? = null

    init {
        load()
    }

    fun load() {
        viewModelScope.launch {
            _loadState.value = UiState.Loading
            try {
                val profile = repository.getProfile()
                loadedProfileId = profile.id
                _form.value = ProfileForm.from(profile)
                _loadState.value = UiState.Content(Unit)
            } catch (e: Exception) {
                _loadState.value = UiState.Error(e.message ?: "Unexpected error")
            }
        }
    }

    fun updateOriginCity(value: String) {
        _form.value = _form.value.copy(originCity = value)
    }

    fun updateBudget(value: String) {
        _form.value = _form.value.copy(budgetText = value)
    }

    fun updateMaxDriveMinutes(value: String) {
        _form.value = _form.value.copy(maxDriveMinutesText = value)
    }

    fun updateTransport(value: TransportMode) {
        _form.value = _form.value.copy(preferredTransport = value)
    }

    fun toggleInterest(value: String) {
        val current = _form.value.interests
        _form.value = _form.value.copy(
            interests = if (value in current) current - value else current + value,
        )
    }

    fun toggleAvoid(value: String) {
        val current = _form.value.avoidPreferences
        _form.value = _form.value.copy(
            avoidPreferences = if (value in current) current - value else current + value,
        )
    }

    fun toggleAirportEnabled(iataCode: String) {
        _form.value = _form.value.copy(
            airports = _form.value.airports.map { airport ->
                if (airport.iataCode == iataCode) {
                    airport.copy(enabled = !airport.enabled)
                } else {
                    airport
                }
            },
        )
    }

    fun removeAirport(iataCode: String) {
        _form.value = _form.value.copy(
            airports = _form.value.airports.filterNot { it.iataCode == iataCode },
        )
    }

    fun addAirport(iataCode: String) {
        val code = iataCode.trim().uppercase()
        if (code.length != 3 || _form.value.airports.any { it.iataCode == code }) return
        _form.value = _form.value.copy(
            airports = _form.value.airports + AirportPreference(
                id = code,
                iataCode = code,
                enabled = true,
                transferCostEur = null,
                transferMinutes = null,
            ),
        )
    }

    fun save() {
        val profileId = loadedProfileId ?: return
        viewModelScope.launch {
            _saveState.value = UiState.Loading
            try {
                repository.saveProfile(_form.value.toProfile(profileId))
                _saveState.value = UiState.Content(Unit)
            } catch (e: Exception) {
                _saveState.value = UiState.Error(e.message ?: "Unexpected error")
            }
        }
    }
}

data class ProfileForm(
    val originCity: String = "",
    val currency: String = "EUR",
    val budgetText: String = "",
    val maxDriveMinutesText: String = "",
    val preferredTransport: TransportMode = TransportMode.EITHER,
    val interests: List<String> = emptyList(),
    val avoidPreferences: List<String> = emptyList(),
    val airports: List<AirportPreference> = emptyList(),
) {
    fun toProfile(id: String): TravelProfile = TravelProfile(
        id = id,
        originCity = originCity.trim().ifEmpty { "Madrid" },
        currency = currency,
        defaultBudgetEur = budgetText.toDoubleOrNull(),
        maxDriveMinutes = maxDriveMinutesText.toIntOrNull(),
        preferredTransport = preferredTransport,
        interests = interests,
        avoidPreferences = avoidPreferences,
        airports = airports,
    )

    companion object {
        fun from(profile: TravelProfile): ProfileForm = ProfileForm(
            originCity = profile.originCity,
            currency = profile.currency,
            budgetText = profile.defaultBudgetEur?.toString().orEmpty(),
            maxDriveMinutesText = profile.maxDriveMinutes?.toString().orEmpty(),
            preferredTransport = profile.preferredTransport,
            interests = profile.interests,
            avoidPreferences = profile.avoidPreferences,
            airports = profile.airports,
        )
    }
}
