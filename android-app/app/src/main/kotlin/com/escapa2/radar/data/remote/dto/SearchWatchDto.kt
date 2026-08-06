package com.escapa2.radar.data.remote.dto

import com.escapa2.radar.data.model.SearchWatch
import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable
import kotlinx.serialization.json.JsonArray
import kotlinx.serialization.json.JsonElement
import kotlinx.serialization.json.JsonPrimitive
import kotlinx.serialization.json.buildJsonArray
import kotlinx.serialization.json.buildJsonObject
import kotlinx.serialization.json.contentOrNull
import kotlinx.serialization.json.doubleOrNull
import kotlinx.serialization.json.jsonArray
import kotlinx.serialization.json.jsonPrimitive
import kotlinx.serialization.json.put

@Serializable
data class SearchWatchDto(
    val id: String,
    @SerialName("couple_id") val coupleId: String? = null,
    val name: String,
    val status: String,
    @SerialName("criteria_json") val criteriaJson: Map<String, JsonElement> = emptyMap(),
    @SerialName("alert_rules_json") val alertRulesJson: Map<String, JsonElement> = emptyMap(),
    @SerialName("last_run_at") val lastRunAt: String? = null,
    @SerialName("next_run_at") val nextRunAt: String? = null,
    @SerialName("created_at") val createdAt: String? = null,
    @SerialName("updated_at") val updatedAt: String? = null,
)

@Serializable
data class SearchWatchCreateDto(
    val name: String,
    val status: String = "ACTIVE",
    val criteria: Map<String, JsonElement> = emptyMap(),
    @SerialName("alert_rules") val alertRules: Map<String, JsonElement> = emptyMap(),
)

fun SearchWatchDto.toDomain(): SearchWatch = SearchWatch(
    id = id,
    name = name,
    status = status,
    lastRunAt = lastRunAt ?: "",
    nextRunAt = nextRunAt ?: "",
    changeSinceYesterdayEur = null,
    minRecordedEur = criteriaJson[CRITERIA_INITIAL_PRICE_KEY]?.jsonPrimitive?.doubleOrNull,
    alertRules = alertRulesJson[ALERT_RULES_KEY]
        ?.jsonArray
        ?.mapNotNull { it.jsonPrimitive.contentOrNull }
        ?: emptyList(),
    priceHistory = emptyList(),
)

internal fun initialPriceCriteria(initialPriceEur: Double): Map<String, JsonElement> =
    buildJsonObject {
        put(CRITERIA_INITIAL_PRICE_KEY, JsonPrimitive(initialPriceEur))
    }

internal fun defaultAlertRules(): Map<String, JsonElement> =
    buildJsonObject {
        put(ALERT_RULES_KEY, JsonArray(listOf(JsonPrimitive("Nuevo mínimo histórico"))))
    }

private const val CRITERIA_INITIAL_PRICE_KEY = "initial_price_eur"
private const val ALERT_RULES_KEY = "rules"
