package com.escapa2.radar.ui.explore

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.Button
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.FilterChip
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import com.escapa2.radar.R
import com.escapa2.radar.data.model.AvailabilityWindow
import com.escapa2.radar.data.model.Opportunity
import com.escapa2.radar.data.model.TransportMode
import com.escapa2.radar.ui.components.OpportunityCard
import com.escapa2.radar.ui.components.UiState

private val INTEREST_OPTIONS = listOf(
    R.string.profile_interest_city to "ciudad",
    R.string.profile_interest_beach to "playa",
    R.string.profile_interest_nature to "naturaleza",
    R.string.profile_interest_mountain to "montaña",
    R.string.profile_interest_food to "gastronomía",
    R.string.profile_interest_quiet to "tranquilidad",
    R.string.profile_interest_nightlife to "vida nocturna",
)

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ExploreScreen(
    onOpportunityClick: (String) -> Unit,
    viewModel: ExploreViewModel = hiltViewModel(),
) {
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()
    val windows by viewModel.windows.collectAsStateWithLifecycle()
    val defaultOrigin by viewModel.defaultOrigin.collectAsStateWithLifecycle()
    var origin by rememberSaveable { mutableStateOf("") }
    var budget by rememberSaveable { mutableStateOf("") }
    var minHours by rememberSaveable { mutableStateOf("") }
    var transportMode by rememberSaveable { mutableStateOf<TransportMode?>(null) }
    var destination by rememberSaveable { mutableStateOf("") }
    var duration by rememberSaveable { mutableStateOf(DurationFilter.ANY) }
    var interest by rememberSaveable { mutableStateOf<String?>(null) }
    var windowId by rememberSaveable { mutableStateOf<String?>(null) }

    LaunchedEffect(defaultOrigin) {
        val currentDefault = defaultOrigin
        if (origin.isBlank() && !currentDefault.isNullOrBlank()) {
            origin = currentDefault
        }
    }

    fun runSearch() {
        viewModel.search(
            maxTotalCostEur = budget.toDoubleOrNull(),
            transportMode = transportMode,
            minUsefulHours = minHours.toDoubleOrNull(),
            destinationQuery = destination,
            minNights = duration.minNights,
            maxNights = duration.maxNights,
            originCity = origin,
            interest = interest,
            window = windows.firstOrNull { it.id == windowId },
        )
    }

    Scaffold(
        topBar = { TopAppBar(title = { Text(stringResource(R.string.explore_title)) }) },
    ) { padding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
                .padding(horizontal = 16.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp),
        ) {
            Text(
                text = stringResource(R.string.explore_filters_title),
                style = MaterialTheme.typography.titleMedium,
                modifier = Modifier.padding(top = 12.dp),
            )
            OutlinedTextField(
                value = origin,
                onValueChange = { origin = it },
                label = { Text(stringResource(R.string.explore_origin_label)) },
                singleLine = true,
                modifier = Modifier.fillMaxWidth(),
            )
            OutlinedTextField(
                value = budget,
                onValueChange = { budget = it },
                label = { Text(stringResource(R.string.explore_budget_label)) },
                singleLine = true,
                modifier = Modifier.fillMaxWidth(),
            )
            OutlinedTextField(
                value = minHours,
                onValueChange = { minHours = it },
                label = { Text(stringResource(R.string.explore_min_hours_label)) },
                singleLine = true,
                modifier = Modifier.fillMaxWidth(),
            )
            OutlinedTextField(
                value = destination,
                onValueChange = { destination = it },
                label = { Text(stringResource(R.string.explore_destination_label)) },
                singleLine = true,
                modifier = Modifier.fillMaxWidth(),
            )
            Text(
                text = stringResource(R.string.explore_transport_label),
                style = MaterialTheme.typography.labelLarge,
            )
            RowChips(
                selected = transportMode,
                onSelect = { transportMode = it },
            )
            Text(
                text = stringResource(R.string.explore_duration_label),
                style = MaterialTheme.typography.labelLarge,
            )
            DurationChips(
                selected = duration,
                onSelect = { duration = it },
            )
            Text(
                text = stringResource(R.string.explore_interests_label),
                style = MaterialTheme.typography.labelLarge,
            )
            InterestChips(
                selected = interest,
                onSelect = { interest = it },
            )
            if (windows.isNotEmpty()) {
                Text(
                    text = stringResource(R.string.explore_free_dates_label),
                    style = MaterialTheme.typography.labelLarge,
                )
                WindowChips(
                    windows = windows,
                    selectedId = windowId,
                    onSelect = { windowId = it },
                )
            }
            Button(
                onClick = { runSearch() },
                modifier = Modifier.fillMaxWidth(),
            ) {
                Text(stringResource(R.string.explore_search_button))
            }
            OutlinedButton(
                onClick = {
                    viewModel.search(
                        maxTotalCostEur = null,
                        transportMode = null,
                        minUsefulHours = null,
                        destinationQuery = null,
                        minNights = null,
                        maxNights = null,
                        originCity = null,
                        interest = null,
                        window = null,
                    )
                },
                modifier = Modifier.fillMaxWidth(),
            ) {
                Text(stringResource(R.string.explore_surprise_button))
            }
            when (val state = uiState) {
                is UiState.Loading -> LoadingState(modifier = Modifier.weight(1f))
                is UiState.Empty -> ResultsHint(modifier = Modifier.weight(1f))
                is UiState.Error -> ErrorState(
                    message = state.message,
                    onRetry = { runSearch() },
                    modifier = Modifier.weight(1f),
                )
                is UiState.Content -> ResultsList(
                    opportunities = state.data,
                    onOpportunityClick = onOpportunityClick,
                    modifier = Modifier.weight(1f),
                )
            }
        }
    }
}

private enum class DurationFilter(
    val minNights: Int?,
    val maxNights: Int?,
) {
    ANY(null, null),
    WEEKEND(1, 2),
    VACATION(3, null),
}

@Composable
private fun DurationChips(
    selected: DurationFilter,
    onSelect: (DurationFilter) -> Unit,
) {
    Row(
        horizontalArrangement = Arrangement.spacedBy(8.dp),
    ) {
        FilterChip(
            selected = selected == DurationFilter.ANY,
            onClick = { onSelect(DurationFilter.ANY) },
            label = { Text(stringResource(R.string.explore_duration_any)) },
        )
        FilterChip(
            selected = selected == DurationFilter.WEEKEND,
            onClick = { onSelect(DurationFilter.WEEKEND) },
            label = { Text(stringResource(R.string.explore_duration_weekend)) },
        )
        FilterChip(
            selected = selected == DurationFilter.VACATION,
            onClick = { onSelect(DurationFilter.VACATION) },
            label = { Text(stringResource(R.string.explore_duration_vacation)) },
        )
    }
}

@Composable
private fun RowChips(
    selected: TransportMode?,
    onSelect: (TransportMode?) -> Unit,
) {
    Row(
        horizontalArrangement = Arrangement.spacedBy(8.dp),
    ) {
        FilterChip(
            selected = selected == null,
            onClick = { onSelect(null) },
            label = { Text(stringResource(R.string.explore_transport_any)) },
        )
        FilterChip(
            selected = selected == TransportMode.CAR,
            onClick = { onSelect(TransportMode.CAR) },
            label = { Text(stringResource(R.string.transport_car)) },
        )
        FilterChip(
            selected = selected == TransportMode.FLIGHT,
            onClick = { onSelect(TransportMode.FLIGHT) },
            label = { Text(stringResource(R.string.transport_flight)) },
        )
    }
}

@Composable
private fun InterestChips(
    selected: String?,
    onSelect: (String?) -> Unit,
) {
    Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
        FilterChip(
            selected = selected == null,
            onClick = { onSelect(null) },
            label = { Text(stringResource(R.string.explore_interest_any)) },
        )
        INTEREST_OPTIONS.forEach { (labelRes, value) ->
            FilterChip(
                selected = selected == value,
                onClick = { onSelect(value) },
                label = { Text(stringResource(labelRes)) },
            )
        }
    }
}

@Composable
private fun WindowChips(
    windows: List<AvailabilityWindow>,
    selectedId: String?,
    onSelect: (String?) -> Unit,
) {
    Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
        FilterChip(
            selected = selectedId == null,
            onClick = { onSelect(null) },
            label = { Text(stringResource(R.string.explore_free_dates_any)) },
        )
        windows.forEach { window ->
            FilterChip(
                selected = selectedId == window.id,
                onClick = { onSelect(window.id) },
                label = { Text(windowKindShortLabel(window.kind)) },
            )
        }
    }
}

private fun windowKindShortLabel(kind: String): String = when (kind) {
    "WEEKEND" -> "Fin de semana"
    "VACATION" -> "Vacaciones"
    else -> kind
}

@Composable
private fun LoadingState(modifier: Modifier = Modifier) {
    Column(
        modifier = modifier.fillMaxSize(),
        verticalArrangement = Arrangement.Center,
        horizontalAlignment = Alignment.CenterHorizontally,
    ) {
        CircularProgressIndicator()
    }
}

@Composable
private fun ResultsHint(modifier: Modifier = Modifier) {
    Column(
        modifier = modifier
            .fillMaxSize()
            .padding(top = 24.dp),
    ) {
        Text(
            text = stringResource(R.string.explore_results_hint),
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.outline,
        )
    }
}

@Composable
private fun ErrorState(message: String, onRetry: () -> Unit, modifier: Modifier = Modifier) {
    Column(
        modifier = modifier
            .fillMaxSize()
            .padding(24.dp),
        verticalArrangement = Arrangement.Center,
        horizontalAlignment = Alignment.CenterHorizontally,
    ) {
        Text(
            text = "${stringResource(R.string.content_error)} $message",
            style = MaterialTheme.typography.bodyLarge,
        )
        Button(onClick = onRetry, modifier = Modifier.padding(top = 12.dp)) {
            Text(stringResource(R.string.content_retry))
        }
    }
}

@Composable
private fun ResultsList(
    opportunities: List<Opportunity>,
    onOpportunityClick: (String) -> Unit,
    modifier: Modifier = Modifier,
) {
    if (opportunities.isEmpty()) {
        Column(
            modifier = modifier.fillMaxSize(),
            verticalArrangement = Arrangement.Center,
            horizontalAlignment = Alignment.CenterHorizontally,
        ) {
            Text(stringResource(R.string.explore_results_empty))
        }
        return
    }
    LazyColumn(
        modifier = modifier.fillMaxSize(),
        contentPadding = PaddingValues(top = 8.dp, bottom = 16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp),
    ) {
        items(opportunities, key = { it.id }) { opportunity ->
            OpportunityCard(
                opportunity = opportunity,
                onClick = { onOpportunityClick(opportunity.id) },
            )
        }
    }
}
