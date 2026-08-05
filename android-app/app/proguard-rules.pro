# Keep line numbers for stack traces in release builds.
-keepattributes SourceFile,LineNumberTable
-renamesourcefileattribute SourceFile

# Retrofit
-dontwarn retrofit2.**
-keepattributes Signature, InnerClasses, EnclosingMethod, *Annotation*
-keepclassmembers,allowshrinking,allowobfuscation interface * {
    @retrofit2.http.* <methods>;
}

# kotlinx.serialization
-keepattributes *Annotation*, InnerClasses
-dontnote kotlinx.serialization.AnnotationsKt
-keep,includedescriptorclasses class com.escapa2.radar.**$$serializer { *; }
-keepclassmembers class com.escapa2.radar.** {
    *** Companion;
}
-keepclasseswithmembers class com.escapa2.radar.** {
    kotlinx.serialization.KSerializer serializer(...);
}
