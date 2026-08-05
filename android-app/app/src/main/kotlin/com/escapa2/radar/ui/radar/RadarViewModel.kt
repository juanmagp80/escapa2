package com.escapa2.radar.ui.radar

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.escapa2.radar.data.model.SearchWatch
import com.escapa2.radar.data.repository.SearchWatchRepository
import com.escapa2.radar.ui.components.UiState
import dagger.hilt.android.lifecycle.HiltViewModel
import javax.inject.Inject
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

@HiltViewModel
class RadarViewModel @Inject constructor(
    private val repository: SearchWatchRepository,
) : ViewModel() {

    private val _uiState = MutableStateFlow<UiState<List<SearchWatch>>>(UiState.Loading)
    val uiState: StateFlow<UiState<List<SearchWatch>>> = _uiState.asStateFlow()

    init {
        load()
    }

    fun load() {
        viewModelScope.launch {
            _uiState.value = UiState.Loading
            try {
                val watches = repository.getWatches()
                _uiState.value = if (watches.isEmpty()) {
                    UiState.Empty
                } else {
                    UiState.Content(watches)
                }
            } catch (e: Exception) {
                _uiState.value = UiState.Error(e.message ?: "Unexpected error")
            }
        }
    }
}
