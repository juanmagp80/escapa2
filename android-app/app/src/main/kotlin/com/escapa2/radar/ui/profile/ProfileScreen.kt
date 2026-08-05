package com.escapa2.radar.ui.profile

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.FilterChip
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Scaffold
import androidx.compose.material3.SnackbarHost
import androidx.compose.material3.SnackbarHostState
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.remember
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import com.escapa2.radar.R
import com.escapa2.radar.data.model.AirportPreference
import com.escapa2.radar.data.model.TransportMode
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

private val AVOID_OPTIONS = listOf(
    R.string.profile_avoid_nightlife to "vida nocturna",
    R.string.profile_avoid_tourists to "zonas turísticas",
    R.string.profile_avoid_driving to "conducción larga",
)

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ProfileScreen(
    viewModel: ProfileViewModel = hiltViewModel(),
) {
    val form by viewModel.form.collectAsStateWithLifecycle()
    val loadState by viewModel.loadState.collectAsStateWithLifecycle()
    val saveState by viewModel.saveState.collectAsStateWithLifecycle()
    val snackbarHostState = remember { SnackbarHostState() }

    LaunchedSaveFeedback(saveState, snackbarHostState)

    Scaffold(
        topBar = { TopAppBar(title = { Text(stringResource(R.string.profile_title)) }) },
        snackbarHost = { SnackbarHost(snackbarHostState) },
    ) { padding ->
        when (val state = loadState) {
            is UiState.Loading -> LoadingState(modifier = Modifier.padding(padding))
            is UiState.Error -> ErrorState(
                message = state.message,
                onRetry = viewModel::load,
                modifier = Modifier.padding(padding),
            )
            is UiState.Empty -> EmptyState(modifier = Modifier.padding(padding))
            is UiState.Content -> ProfileForm(
                form = form,
                onOriginCityChange = viewModel::updateOriginCity,
                onBudgetChange = viewModel::updateBudget,
                onMaxDriveChange = viewModel::updateMaxDriveMinutes,
                onTransportChange = viewModel::updateTransport,
                onToggleInterest = viewModel::toggleInterest,
                onToggleAvoid = viewModel::toggleAvoid,
                onSave = viewModel::save,
                modifier = Modifier.padding(padding),
            )
        }
    }
}

@Composable
private fun LaunchedSaveFeedback(
    saveState: UiState<Unit>?,
    snackbarHostState: SnackbarHostState,
) {
    val savedMessage = stringResource(R.string.profile_saved)
    val errorMessage = stringResource(R.string.profile_save_error)
    androidx.compose.runtime.LaunchedEffect(saveState) {
        when (saveState) {
            is UiState.Content -> snackbarHostState.showSnackbar(savedMessage)
            is UiState.Error -> snackbarHostState.showSnackbar(errorMessage)
            else -> Unit
        }
    }
}

@Composable
private fun ProfileForm(
    form: ProfileForm,
    onOriginCityChange: (String) -> Unit,
    onBudgetChange: (String) -> Unit,
    onMaxDriveChange: (String) -> Unit,
    onTransportChange: (TransportMode) -> Unit,
    onToggleInterest: (String) -> Unit,
    onToggleAvoid: (String) -> Unit,
    onSave: () -> Unit,
    modifier: Modifier = Modifier,
) {
    Column(
        modifier = modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState())
            .padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp),
    ) {
        OutlinedTextField(
            value = form.originCity,
            onValueChange = onOriginCityChange,
            label = { Text(stringResource(R.string.profile_origin_city)) },
            singleLine = true,
            modifier = Modifier.fillMaxWidth(),
        )
        OutlinedTextField(
            value = form.currency,
            onValueChange = {},
            label = { Text(stringResource(R.string.profile_currency)) },
            singleLine = true,
            readOnly = true,
            enabled = false,
            modifier = Modifier.fillMaxWidth(),
        )
        OutlinedTextField(
            value = form.budgetText,
            onValueChange = onBudgetChange,
            label = { Text(stringResource(R.string.profile_budget)) },
            singleLine = true,
            modifier = Modifier.fillMaxWidth(),
        )
        OutlinedTextField(
            value = form.maxDriveMinutesText,
            onValueChange = onMaxDriveChange,
            label = { Text(stringResource(R.string.profile_max_drive_minutes)) },
            singleLine = true,
            modifier = Modifier.fillMaxWidth(),
        )
        TransportSelector(
            selected = form.preferredTransport,
            onSelect = onTransportChange,
        )
        HorizontalDivider()
        ChipSelector(
            titleRes = R.string.profile_interests,
            options = INTEREST_OPTIONS,
            selected = form.interests,
            onToggle = onToggleInterest,
        )
        ChipSelector(
            titleRes = R.string.profile_avoid,
            options = AVOID_OPTIONS,
            selected = form.avoidPreferences,
            onToggle = onToggleAvoid,
        )
        AirportSection(airports = form.airports)
        Button(
            onClick = onSave,
            modifier = Modifier.fillMaxWidth(),
        ) {
            Text(stringResource(R.string.profile_save))
        }
    }
}

@Composable
private fun AirportSection(airports: List<AirportPreference>) {
    if (airports.isEmpty()) return
    Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
        Text(
            text = stringResource(R.string.profile_airports),
            style = MaterialTheme.typography.labelLarge,
            fontWeight = FontWeight.SemiBold,
        )
        airports.forEach { airport ->
            Row(
                modifier = Modifier.fillMaxWidth(),
                verticalAlignment = Alignment.CenterVertically,
            ) {
                Column(modifier = Modifier.weight(1f)) {
                    Text(
                        text = airport.iataCode,
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.Bold,
                    )
                    airport.transferCostEur?.let { cost ->
                        airport.transferMinutes?.let { minutes ->
                            Text(
                                text = stringResource(
                                    R.string.profile_airport_transfer,
                                    cost.toString().replace(".", ","),
                                    minutes,
                                ),
                                style = MaterialTheme.typography.bodySmall,
                                color = MaterialTheme.colorScheme.outline,
                            )
                        }
                    }
                }
                Text(
                    text = if (airport.enabled) {
                        stringResource(R.string.profile_airport_enabled)
                    } else {
                        ""
                    },
                    style = MaterialTheme.typography.labelMedium,
                    color = MaterialTheme.colorScheme.primary,
                )
            }
        }
    }
}

@Composable
private fun TransportSelector(
    selected: TransportMode,
    onSelect: (TransportMode) -> Unit,
) {
    Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
        Text(
            text = stringResource(R.string.profile_transport),
            style = MaterialTheme.typography.labelLarge,
        )
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            TransportMode.entries.forEach { mode ->
                FilterChip(
                    selected = selected == mode,
                    onClick = { onSelect(mode) },
                    label = { Text(stringResource(transportLabel(mode))) },
                )
            }
        }
    }
}

@Composable
private fun ChipSelector(
    titleRes: Int,
    options: List<Pair<Int, String>>,
    selected: List<String>,
    onToggle: (String) -> Unit,
) {
    Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
        Text(
            text = stringResource(titleRes),
            style = MaterialTheme.typography.labelLarge,
            fontWeight = FontWeight.SemiBold,
        )
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            options.forEach { (labelRes, value) ->
                FilterChip(
                    selected = value in selected,
                    onClick = { onToggle(value) },
                    label = { Text(stringResource(labelRes)) },
                )
            }
        }
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
private fun EmptyState(modifier: Modifier = Modifier) {
    Column(
        modifier = modifier.fillMaxSize(),
        verticalArrangement = Arrangement.Center,
        horizontalAlignment = Alignment.CenterHorizontally,
    ) {
        Text(stringResource(R.string.content_empty), style = MaterialTheme.typography.bodyLarge)
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

private fun transportLabel(mode: TransportMode): Int = when (mode) {
    TransportMode.FLIGHT -> R.string.transport_flight
    TransportMode.CAR -> R.string.transport_car
    TransportMode.EITHER -> R.string.transport_either
}
