# Run the official cffdrs fbpRaster over the 100 m FBP input stack.
#
# Usage:
#   Rscript analysis/run_fbp.R data/processed/fbp_inputs_100m.tif data/processed/fbp_100m.tif 8

args <- commandArgs(trailingOnly = TRUE)
if (length(args) < 2) {
  stop("usage: Rscript analysis/run_fbp.R <input_tif> <output_tif> [cores]")
}
input_path <- args[[1]]
output_path <- args[[2]]
cores <- if (length(args) >= 3) as.integer(args[[3]]) else 4L

suppressPackageStartupMessages({
  library(terra)
  library(cffdrs)
})

bands <- c("FUEL", "FFMC", "BUI", "WS", "WD", "GS", "Aspect",
           "LAT", "LONG", "ELV", "Dj", "PC", "PDF", "cc", "CBH", "CFL")
input <- rast(input_path)
if (nlyr(input) != length(bands)) {
  stop(sprintf("expected %d bands, found %d", length(bands), nlyr(input)))
}
names(input) <- bands

message("running fbpRaster on ", ncell(input), " cells with ", cores, " cores")
started <- Sys.time()
out <- fbpRaster(input, output = "Primary", cores = cores)
message("elapsed ", round(difftime(Sys.time(), started, units = "mins"), 2), " minutes")
dir.create(dirname(output_path), recursive = TRUE, showWarnings = FALSE)
writeRaster(
  out,
  output_path,
  overwrite = TRUE,
  datatype = "FLT4S",
  NAflag = NaN,
  gdal = c("COMPRESS=DEFLATE", "PREDICTOR=2")
)
message("wrote ", output_path)
print(global(out, c("min", "max", "mean"), na.rm = TRUE))
