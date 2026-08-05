package com.escapa2.radar.ui.components

import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Card
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.escapa2.radar.R
import com.escapa2.radar.data.model.Opportunity
import java.util.Locale

@Composable
fun OpportunityCard(
    opportunity: Opportunity,
    modifier: Modifier = Modifier,
    onClick: (() -> Unit)? = null,
) {
    Card(modifier = modifier.fillMaxWidth(), onClick = { onClick?.invoke() }) {
        Column(modifier = Modifier.padding(16.dp)) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Text(
                    text = opportunity.destinationName,
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold,
                    modifier = Modifier.weight(1f),
                )
                Text(
                    text = stringResource(transportLabel(opportunity.transportMode.name)),
                    style = MaterialTheme.typography.labelMedium,
                    color = MaterialTheme.colorScheme.primary,
                )
            }
            Text(
                text = "${opportunity.startAt} → ${opportunity.endAt}",
                style = MaterialTheme.typography.bodySmall,
            )
            Column(modifier = Modifier.padding(top = 12.dp)) {
                Text(
                    text = "${opportunity.totalCostEur.formatEur()} ${stringResource(R.string.opportunity_total_for_two)}",
                    style = MaterialTheme.typography.titleLarge,
                    fontWeight = FontWeight.Bold,
                )
                Text(
                    text = "${opportunity.costPerUsefulHourEur.formatEur()}/h útil · " +
                        "${opportunity.usefulHours.toString().replace(".", ",")} h",
                    style = MaterialTheme.typography.bodyMedium,
                )
                Text(
                    text = "${stringResource(R.string.opportunity_verified)} ${opportunity.verifiedAt}",
                    style = MaterialTheme.typography.labelSmall,
                    color = MaterialTheme.colorScheme.outline,
                )
            }
        }
    }
}

private fun transportLabel(value: String): Int = when (value) {
    "FLIGHT" -> R.string.transport_flight
    "CAR" -> R.string.transport_car
    else -> R.string.transport_either
}

private fun Double.formatEur(): String =
    String.format(Locale("es", "ES"), "%.2f €", this)
