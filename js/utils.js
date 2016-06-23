function rgba(red, green, blue, alpha) {
    if (typeof alpha === 'undefined') { alpha = 1.0 }
    return "rgba("+red+","+green+","+blue+","+alpha+")"
}
