package com.escapa2.radar.ui.detail

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.escapa2.radar.data.model.AiSummary
import com.escapa2.radar.data.model.Opportunity
import com.escapa2.radar.data.model.PriceSnapshot
import com.escapa2.radar.data.repository.AiRepository
import com.escapa2.radar.data.repository.OpportunityRepository
import com.escapa2.radar.data.repository.SearchWatchRepository
import com.escapa2.radar.ui.components.UiState
import dagger.hilt.android.lifecycle.HiltViewModel
import javax.inject.Inject
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

@HiltViewModel
class OpportunityDetailViewModel @Inject constructor(
    private val repository: OpportunityRepository,
    private val aiRepository: AiRepository,
    private val watchRepository: SearchWatchRepository,
) : ViewModel() {

    private val _uiState = MutableStateFlow<UiState<Opportunity>>(UiState.Loading)
    val uiState: StateFlow<UiState<Opportunity>> = _uiState.asStateFlow()

    private val _summary = MutableStateFlow<UiState<AiSummary>?>(null)
    val summary: StateFlow<UiState<AiSummary>?> = _summary.asStateFlow()

    private val _priceHistory = MutableStateFlow<UiState<List<PriceSnapshot>>?>(null)
    val priceHistory: StateFlow<UiState<List<PriceSnapshot>>?> = _priceHistory.asStateFlow()

    private val _followState = MutableStateFlow<UiState<Unit>?>(null)
    val followState: StateFlow<UiState<Unit>?> = _followState.asStateFlow()

    private var currentOpportunity: Opportunity? = null

    fun load(opportunityId: String) {
        viewModelScope.launch {
            _uiState.value = UiState.Loading
            _summary.value = null
            _priceHistory.value = null
            _followState.value = null
            try {
                val opportunity = repository.getOpportunity(opportunityId)
                if (opportunity == null) {
                    _uiState.value = UiState.Empty
                } else {
                    currentOpportunity = opportunity
                    _uiState.value = UiState.Content(opportunity)
                    loadSummary(opportunity)
                    loadPriceHistory(opportunityId)
                }
            } catch (e: Exception) {
                _uiState.value = UiState.Error(e.message ?: "Unexpected error")
            }
        }
    }

    fun follow() {
        val opportunity = currentOpportunity ?: return
        viewModelScope.launch {
            _followState.value = UiState.Loading
            _followState.value = try {
                watchRepository.createWatch(
                    name = opportunity.destinationName,
                    initialPriceEur = opportunity.totalCostEur,
                )
                UiState.Content(Unit)
            } catch (e: Exception) {
                UiState.Error(e.message ?: "Unexpected error")
            }
        }
    }

    private fun loadSummary(opportunity: Opportunity) {
        viewModelScope.launch {
            _summary.value = UiState.Loading
            _summary.value = try {
                UiState.Content(aiRepository.summarizeOpportunity(opportunity))
            } catch (e: Exception) {
                UiState.Error(e.message ?: "Unexpected error")
            }
        }
    }

    private fun loadPriceHistory(opportunityId: String) {
        viewModelScope.launch {
            _priceHistory.value = UiState.Loading
            _priceHistory.value = try {
                val history = repository.getPriceHistory(opportunityId)
                if (history.isEmpty()) {
                    UiState.Empty
                } else {
                    UiState.Content(history.sortedBy { it.capturedAt })
                }
            } catch (e: Exception) {
                UiState.Error(e.message ?: "Unexpected error")
            }
        }
    }
}
