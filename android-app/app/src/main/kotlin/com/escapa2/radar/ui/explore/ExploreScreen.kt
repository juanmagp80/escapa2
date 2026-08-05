package com.escapa2.radar.ui.explore

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
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
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.runtime.Composable
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
import com.escapa2.radar.data.model.Opportunity
import com.escapa2.radar.data.model.TransportMode
import com.escapa2.radar.ui.components.OpportunityCard
import com.escapa2.radar.ui.components.UiState

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ExploreScreen(
    onOpportunityClick: (String) -> Unit,
    viewModel: ExploreViewModel = hiltViewModel(),
) {
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()
    var budget by rememberSaveable { mutableStateOf("") }
    var minHours by rememberSaveable { mutableStateOf("") }
    var transportMode by rememberSaveable { mutableStateOf<TransportMode?>(null) }
    var destination by rememberSaveable { mutableStateOf("") }
    var duration by rememberSaveable { mutableStateOf(DurationFilter.ANY) }

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
            Button(
                onClick = {
                    viewModel.search(
                        maxTotalCostEur = budget.toDoubleOrNull(),
                        transportMode = transportMode,
                        minUsefulHours = minHours.toDoubleOrNull(),
                        destinationQuery = destination,
                        minNights = duration.minNights,
                        maxNights = duration.maxNights,
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
                    onRetry = {
                        viewModel.search(
                            maxTotalCostEur = budget.toDoubleOrNull(),
                            transportMode = transportMode,
                            minUsefulHours = minHours.toDoubleOrNull(),
                            destinationQuery = destination,
                            minNights = duration.minNights,
                            maxNights = duration.maxNights,
                        )
                    },
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
    androidx.compose.foundation.layout.Row(
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
    androidx.compose.foundation.layout.Row(
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
