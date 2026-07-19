package com.example.util

import android.content.Context
import android.content.Intent
import androidx.core.content.FileProvider
import java.io.File

object AssetPdfOpener {
    fun open(context: Context, assetPath: String, outputName: String) {
        val directory = File(context.cacheDir, "manuales").apply { mkdirs() }
        val output = File(directory, outputName)
        if (!output.exists() || output.length() == 0L) {
            context.assets.open(assetPath).use { input ->
                output.outputStream().use { target -> input.copyTo(target) }
            }
        }
        val uri = FileProvider.getUriForFile(
            context,
            "${context.packageName}.fileprovider",
            output
        )
        context.startActivity(
            Intent(Intent.ACTION_VIEW).apply {
                setDataAndType(uri, "application/pdf")
                addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
            }
        )
    }
}
