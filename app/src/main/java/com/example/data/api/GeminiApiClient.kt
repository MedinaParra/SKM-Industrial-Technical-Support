package com.example.data.api

import com.example.BuildConfig
import com.example.data.model.BearingSpec
import com.squareup.moshi.Moshi
import com.squareup.moshi.kotlin.reflect.KotlinJsonAdapterFactory
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import okhttp3.OkHttpClient
import retrofit2.Retrofit
import retrofit2.converter.moshi.MoshiConverterFactory
import retrofit2.http.Body
import retrofit2.http.POST
import retrofit2.http.Query
import java.util.concurrent.TimeUnit

data class Part(val text: String? = null)

data class Content(val parts: List<Part>)

data class GenerateContentRequest(
    val contents: List<Content>,
    val systemInstruction: Content? = null
)

data class Candidate(val content: Content)

data class GenerateContentResponse(val candidates: List<Candidate>?)

interface GeminiApiService {
    @POST("v1beta/models/gemini-3.5-flash:generateContent")
    suspend fun generateContent(
        @Query("key") apiKey: String,
        @Body request: GenerateContentRequest
    ): GenerateContentResponse
}

object GeminiApiClient {
    private const val BASE_URL = "https://generativelanguage.googleapis.com/"

    private val okHttpClient = OkHttpClient.Builder()
        .connectTimeout(60, TimeUnit.SECONDS)
        .readTimeout(60, TimeUnit.SECONDS)
        .writeTimeout(60, TimeUnit.SECONDS)
        .build()

    private val moshi = Moshi.Builder()
        .addLast(KotlinJsonAdapterFactory())
        .build()

    val service: GeminiApiService by lazy {
        val retrofit = Retrofit.Builder()
            .baseUrl(BASE_URL)
            .client(okHttpClient)
            .addConverterFactory(MoshiConverterFactory.create(moshi))
            .build()
        retrofit.create(GeminiApiService::class.java)
    }

    suspend fun askAssistant(prompt: String, bearingInfo: BearingSpec? = null): String = withContext(Dispatchers.IO) {
        val apiKey = BuildConfig.GEMINI_API_KEY
        if (apiKey.isEmpty() || apiKey == "MY_GEMINI_API_KEY") {
            return@withContext "Error: API Key no configurada. Por favor, configúrela en el panel de secretos de AI Studio."
        }

        // Context system instructions
        val systemInstructionText = """
            Eres el Asistente Técnico de SKM Industrial, un ingeniero experto en montaje de rodamientos de alta precisión según los manuales oficiales de SKF, FAG, Timken, DODGE y NSK.
            Tu objetivo es dar recomendaciones técnicas precisas de montaje, tolerancias de ejes, alojamiento, métodos de lubricación o causas de fallas de rodamientos.
            Habla en español, mantén un tono profesional, técnico y servicial.
            ${if (bearingInfo != null) "El usuario está trabajando actualmente con el rodamiento: ${bearingInfo.designation} (${bearingInfo.brand}), que tiene un diámetro interior de ${bearingInfo.boreDiameterMm} mm, diámetro exterior de ${bearingInfo.outerDiameterMm} mm y un juego radial inicial normal de ${bearingInfo.clearanceMinNormal}-${bearingInfo.clearanceMaxNormal} mm." else ""}
        """.trimIndent()

        val request = GenerateContentRequest(
            contents = listOf(Content(parts = listOf(Part(text = prompt)))),
            systemInstruction = Content(parts = listOf(Part(text = systemInstructionText)))
        )

        try {
            val response = service.generateContent(apiKey, request)
            response.candidates?.firstOrNull()?.content?.parts?.firstOrNull()?.text 
                ?: "No se obtuvo respuesta del Asistente Técnico SKM."
        } catch (e: Exception) {
            "No se pudo conectar con el Asistente AI de SKM Industrial: ${e.localizedMessage}. Verifique su conexión o la API Key."
        }
    }
}
