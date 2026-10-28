# Run the official cffdrs fwiRaster over the 62-day mean-summer weather sequence.
#
# Usage:
#   Rscript analysis/run_fwi.R data/interim/weather data/processed/fwi_800m.tif
#
# The caller must set PROJ_DATA and GDAL_DATA when using the conda R
# environment; analysis/run_fwi.sh does that automatically.

args <- commandArgs(trailingOnly = TRUE)
if (length(args) != 2) {
  stop("usage: Rscript analysis/run_fwi.R <weather_dir> <output_tif>")
}
weather_dir <- args[[1]]
output_path <- args[[2]]

suppressPackageStartupMessages({
  library(terra)
  library(cffdrs)
})

files <- sort(list.files(weather_dir, pattern = "^weather_day_[0-9]{3}\\.tif$", full.names = TRUE))
if (length(files) != 62) {
  stop(sprintf("expected 62 weather days, found %d", length(files)))
}

init <- c(ffmc = 85, dmc = 6, dc = 15)
final <- NULL
july_end <- NULL
for (index in seq_along(files)) {
  day <- rast(files[[index]])
  names(day) <- c("temp", "rh", "ws", "prec", "lat")
  month <- if (index <= 31) 7 else 8
  if (index == 1) {
    day_out <- fwiRaster(day, init = init, mon = month, out = "fwi", lat.adjust = TRUE)
  } else {
    init_stack <- c(day_out[["FFMC"]], day_out[["DMC"]], day_out[["DC"]])
    names(init_stack) <- c("ffmc", "dmc", "dc")
    day_out <- fwiRaster(day, init = init_stack, mon = month, out = "fwi", lat.adjust = TRUE)
  }
  if (index == 31) {
    july_end <- day_out
  }
  if (index %% 10 == 0 || index == length(files)) {
    message(sprintf("day %02d/%d  FFMC mean %.1f  BUI mean %.1f  FWI mean %.1f",
                    index, length(files),
                    global(day_out[["FFMC"]], "mean", na.rm = TRUE)[[1]],
                    global(day_out[["BUI"]], "mean", na.rm = TRUE)[[1]],
                    global(day_out[["FWI"]], "mean", na.rm = TRUE)[[1]]))
  }
  final <- day_out
}

dir.create(dirname(output_path), recursive = TRUE, showWarnings = FALSE)
writeRaster(final, output_path, overwrite = TRUE, gdal = c("COMPRESS=DEFLATE", "PREDICTOR=2"))
writeRaster(july_end, sub("\\.tif$", "_july_end.tif", output_path), overwrite = TRUE,
            gdal = c("COMPRESS=DEFLATE", "PREDICTOR=2"))
message("wrote ", output_path)
