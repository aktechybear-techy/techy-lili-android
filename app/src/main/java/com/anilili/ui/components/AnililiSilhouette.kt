package com.anilili.ui.components

import androidx.compose.ui.geometry.Rect
import androidx.compose.ui.geometry.Size
import androidx.compose.ui.graphics.Canvas
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.ImageBitmap
import androidx.compose.ui.graphics.Paint
import androidx.compose.ui.graphics.Path
import androidx.compose.ui.graphics.vector.PathParser
import kotlin.math.max
import kotlin.math.min
import kotlin.math.roundToInt

/**
 * The TechyLili mark as vector geometry, for the loaders that fill it: the brush
 * hiragana te (Yuji Syuku) that the fork's launcher icons carry, traced off the same
 * render with potrace onto a 1254-unit canvas, centred, ~900 units tall. It replaced
 * the OG's a-with-play-cutout pair, which went with the OG's logo; exact at every size
 * the same way they were, and [silhouetteFrame] still frames it by its bounds.
 */
private const val SilhouetteBody =
    "M929.80 179.00c-1.40 0.40 -4.60 2.10 -7.00 3.80 -5.80 4.00 -22.20 12.20 -32.80 16.60 -24.10 9.70 -45.90 14.80 -104.50 24.10 -13.40 2.20 -44.80 6.00 -74.00 9.00 -7.70 0.80 -18.30 1.90 -23.50 2.50 -27.70 2.90 -74.20 9.60 -128.00 18.50 -9.90 1.70 -46.70 6.90 -59.00 8.50 -64.30 8.10 -105.10 11.60 -168.00 14.10 -45.70 1.80 -105.90 -1.30 -143.80 -7.50 -4.50 -0.70 -8.40 -1.00 -8.70 -0.60 -1.20 2.00 6.50 23.60 12.20 34.00 12.10 22.20 34.10 44.40 59.60 60.20 20.80 13.00 54.10 27.40 75.20 32.60 18.80 4.70 29.50 5.70 59.50 5.60 27.70 -0.00 47.80 -1.70 67.00 -5.40 2.50 -0.50 9.20 -1.60 15.00 -2.50 5.80 -0.90 15.50 -2.50 21.50 -3.60 6.10 -1.10 14.80 -2.60 19.50 -3.50 11.70 -2.10 42.60 -8.20 47.50 -9.40 2.20 -0.60 11.40 -2.60 20.50 -4.50 9.10 -1.90 19.40 -4.20 23.00 -4.90 16.90 -3.70 22.70 -4.90 39.00 -8.10 28.10 -5.50 48.80 -8.90 61.50 -10.00 3.90 -0.30 8.00 -0.80 9.30 -1.10 1.20 -0.20 2.20 -0.00 2.20 0.50 0.00 0.50 -3.60 8.40 -8.00 17.50 -4.40 9.10 -8.80 18.50 -9.90 20.90 -1.10 2.30 -3.60 7.80 -5.60 12.20 -5.20 11.30 -23.20 52.40 -29.90 68.50 -3.10 7.40 -6.10 14.40 -6.60 15.50 -3.30 7.30 -9.20 22.00 -14.70 36.50 -2.40 6.30 -10.30 29.80 -13.80 41.00 -9.70 31.00 -18.40 77.30 -23.10 122.00 -2.70 25.70 -2.50 81.50 0.40 105.50 2.20 17.40 4.20 30.70 6.20 39.00 9.70 42.10 19.00 66.20 39.50 103.00 23.50 42.00 49.20 76.20 82.50 109.70 14.90 15.00 18.50 18.10 24.50 21.10 22.00 10.80 42.40 16.00 63.50 16.10 13.10 0.10 19.50 -1.20 29.00 -5.70 6.10 -2.80 15.20 -12.10 17.90 -18.20 5.00 -11.40 4.70 -26.50 -1.00 -43.00 -4.90 -14.00 -6.00 -15.70 -11.60 -17.90 -46.70 -18.10 -85.20 -54.80 -111.00 -105.60 -16.20 -31.90 -25.60 -62.50 -32.40 -105.00 -14.00 -88.00 1.40 -190.40 41.10 -272.60 22.50 -46.80 48.80 -82.00 79.50 -106.30 20.30 -16.10 48.40 -31.10 79.50 -42.40 13.90 -5.00 15.50 -5.50 42.50 -12.80 10.50 -2.80 22.80 -6.20 27.50 -7.60 4.70 -1.40 10.50 -3.10 13.00 -3.80 30.10 -8.60 49.80 -18.10 72.40 -34.90 10.90 -8.10 -0.60 -8.50c-0.60 -8.40 -3.10 -21.00 -6.10 -30.10 -6.30 -20.00 -24.00 -43.00 -42.30 -55.20 -14.80 -9.80 -33.60 -16.40 -54.80 -19.10 -12.40 -1.70 -37.10 -2.00 -41.70 -0.60"

/** The mark in SVG units. Parsed once; nothing mutates it. */
private val silhouette: Path by lazy {
    PathParser().parsePathString(SilhouetteBody).toPath()
}
private val silhouetteBounds: Rect by lazy { silhouette.getBounds() }

/**
 * Where the mark lands inside a canvas of [canvas] size: centred, aspect kept, filling
 * [fraction] of the shorter side. The 0.9 default matches the margin the old bitmaps carried.
 */
internal fun silhouetteFrame(canvas: Size, fraction: Float = 0.9f): Rect {
    val source = silhouetteBounds
    val scale = min(canvas.width, canvas.height) * fraction / max(source.width, source.height)
    val width = source.width * scale
    val height = source.height * scale
    val left = (canvas.width - width) / 2f
    val top = (canvas.height - height) / 2f
    return Rect(left, top, left + width, top + height)
}

/**
 * The mark rasterised once, opaque white on transparent, at exactly [canvas] pixels and placed at
 * [silhouetteFrame]. Tinted and used as an alpha source by the loader, so per frame there is no
 * path to fill and no clip to rasterise — only bitmap sampling.
 */
internal fun silhouetteMask(canvas: Size, fraction: Float = 0.9f): ImageBitmap {
    val width = canvas.width.roundToInt().coerceAtLeast(1)
    val height = canvas.height.roundToInt().coerceAtLeast(1)
    val bitmap = ImageBitmap(width, height)
    val frame = silhouetteFrame(Size(width.toFloat(), height.toFloat()), fraction)
    val source = silhouetteBounds
    val scale = frame.width / source.width
    Canvas(bitmap).apply {
        translate(frame.left, frame.top)
        scale(scale, scale)
        translate(-source.left, -source.top)
        drawPath(silhouette, Paint().apply { color = Color.White })
    }
    return bitmap
}
