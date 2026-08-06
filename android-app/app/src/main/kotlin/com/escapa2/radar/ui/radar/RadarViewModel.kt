package com.escapa2.radar.ui.radar

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.escapa2.radar.data.model.SearchWatch
import com.escapa2.radar.data.model.WatchRunResult
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

    private val _runningWatchId = MutableStateFlow<String?>(null)
    val runningWatchId: StateFlow<String?> = _runningWatchId.asStateFlow()

    private val _runMessage = MutableStateFlow<RunMessage?>(null)
    val runMessage: StateFlow<RunMessage?> = _runMessage.asStateFlow()

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

    fun runWatch(watchId: String) {
        if (_runningWatchId.value != null) return
        viewModelScope.launch {
            _runningWatchId.value = watchId
            try {
                val result = repository.runWatch(watchId)
                _runMessage.value = RunMessage.Success(result)
                load()
            } catch (e: Exception) {
                _runMessage.value = RunMessage.Failure(e.message ?: "Unexpected error")
            } finally {
                _runningWatchId.value = null
            }
        }
    }

    fun consumeRunMessage() {
        _runMessage.value = null
    }
}

sealed interface RunMessage {
    data class Success(val result: WatchRunResult) : RunMessage
    data class Failure(val message: String) : RunMessage
}
