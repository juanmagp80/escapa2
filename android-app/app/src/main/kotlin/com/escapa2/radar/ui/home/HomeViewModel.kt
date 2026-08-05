package com.escapa2.radar.ui.home

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.escapa2.radar.data.model.Opportunity
import com.escapa2.radar.data.model.SearchWatch
import com.escapa2.radar.data.repository.OpportunityRepository
import com.escapa2.radar.data.repository.SearchWatchRepository
import com.escapa2.radar.ui.components.UiState
import dagger.hilt.android.lifecycle.HiltViewModel
import javax.inject.Inject
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

/**
 * Home dashboard: the current best option, the biggest price drop, the
 * closest free dates and the watched trips.
 */
@HiltViewModel
class HomeViewModel @Inject constructor(
    private val repository: OpportunityRepository,
    private val watchRepository: SearchWatchRepository,
) : ViewModel() {

    private val _uiState = MutableStateFlow<UiState<HomeDashboard>>(UiState.Loading)
    val uiState: StateFlow<UiState<HomeDashboard>> = _uiState.asStateFlow()

    init {
        load()
    }

    fun load() {
        viewModelScope.launch {
            _uiState.value = UiState.Loading
            try {
                val opportunities = repository.getOpportunities()
                val watches = watchRepository.getWatches()
                _uiState.value = if (opportunities.isEmpty() && watches.isEmpty()) {
                    UiState.Empty
                } else {
                    UiState.Content(buildDashboard(opportunities, watches))
                }
            } catch (e: Exception) {
                _uiState.value = UiState.Error(e.message ?: "Unexpected error")
            }
        }
    }

    private fun buildDashboard(
        opportunities: List<Opportunity>,
        watches: List<SearchWatch>,
    ): HomeDashboard = HomeDashboard(
        opportunities = opportunities,
        bestOpportunity = bestOpportunity(opportunities),
        biggestDrop = biggestDrop(opportunities),
        watches = watches,
        nextFreeDates = opportunities
            .sortedBy { it.startAt }
            .take(NEXT_FREE_DATES_LIMIT),
        lastUpdateAt = opportunities.maxOfOrNull { it.verifiedAt },
    )

    private fun bestOpportunity(opportunities: List<Opportunity>): Opportunity? =
        opportunities.maxWithOrNull(
            compareBy<Opportunity>(
                { it.valueScore ?: Double.NEGATIVE_INFINITY },
                { -it.costPerUsefulHourEur },
            ),
        )

    private fun biggestDrop(opportunities: List<Opportunity>): Opportunity? =
        opportunities
            .mapNotNull { opportunity ->
                val previous = opportunity.previousTotalCostEur
                if (previous != null && previous > opportunity.totalCostEur) {
                    PriceDrop(opportunity = opportunity, amountEur = previous - opportunity.totalCostEur)
                } else {
                    null
                }
            }
            .maxByOrNull { it.amountEur }
            ?.opportunity

    private companion object {
        const val NEXT_FREE_DATES_LIMIT = 2
    }
}

data class HomeDashboard(
    val opportunities: List<Opportunity>,
    val bestOpportunity: Opportunity?,
    val biggestDrop: Opportunity?,
    val watches: List<SearchWatch>,
    val nextFreeDates: List<Opportunity>,
    val lastUpdateAt: String?,
)

data class PriceDrop(
    val opportunity: Opportunity,
    val amountEur: Double,
)
