package com.escapa2.radar.ui.explore

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.escapa2.radar.data.model.Opportunity
import com.escapa2.radar.data.model.OpportunitySearchFilters
import com.escapa2.radar.data.model.TransportMode
import com.escapa2.radar.data.repository.OpportunityRepository
import com.escapa2.radar.ui.components.UiState
import dagger.hilt.android.lifecycle.HiltViewModel
import javax.inject.Inject
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

@HiltViewModel
class ExploreViewModel @Inject constructor(
    private val repository: OpportunityRepository,
) : ViewModel() {

    private val _uiState = MutableStateFlow<UiState<List<Opportunity>>>(UiState.Empty)
    val uiState: StateFlow<UiState<List<Opportunity>>> = _uiState.asStateFlow()

    fun search(
        maxTotalCostEur: Double? = null,
        transportMode: TransportMode? = null,
        minUsefulHours: Double? = null,
        destinationQuery: String? = null,
        minNights: Int? = null,
        maxNights: Int? = null,
    ) {
        viewModelScope.launch {
            _uiState.value = UiState.Loading
            try {
                val filters = OpportunitySearchFilters(
                    maxTotalCostEur = maxTotalCostEur,
                    transportMode = transportMode,
                    minUsefulHours = minUsefulHours,
                    destinationQuery = destinationQuery?.trim()?.takeIf { it.isNotEmpty() },
                    minNights = minNights,
                    maxNights = maxNights,
                )
                val results = repository.search(filters)
                _uiState.value = if (results.isEmpty()) {
                    UiState.Empty
                } else {
                    UiState.Content(results)
                }
            } catch (e: Exception) {
                _uiState.value = UiState.Error(e.message ?: "Unexpected error")
            }
        }
    }

    fun clearResults() {
        _uiState.value = UiState.Empty
    }
}
