# Run cffdrs::fbp on the point table for the LiDAR fuel-type changes.
#
# Usage:
#   Rscript analysis/run_lidar_fbp_points.R <input_csv> <output_csv>

args <- commandArgs(trailingOnly = TRUE)
if (length(args) != 2) {
  stop("usage: Rscript analysis/run_lidar_fbp_points.R <input_csv> <output_csv>")
}
input_path <- args[[1]]
output_path <- args[[2]]

suppressPackageStartupMessages({
  library(cffdrs)
})

input <- read.csv(input_path, stringsAsFactors = FALSE, check.names = FALSE)
required <- c("ID", "FUELTYPE", "FFMC", "BUI", "WS", "WD", "GS", "ASPECT",
              "PC", "PDF", "CC", "CBH", "CFL", "LAT", "LONG", "ELV", "DJ")
missing <- setdiff(required, names(input))
if (length(missing) > 0) {
  stop(sprintf("missing columns: %s", paste(missing, collapse = ", ")))
}

out <- fbp(input, output = "Primary")
out$ID <- as.character(out$ID)
input$ID <- as.character(input$ID)
result <- merge(input[, c("ID", "ZONE", "FEATURE_ID", "SCENARIO", "FUELTYPE")],
                out, by = "ID", all.x = TRUE)

dir.create(dirname(output_path), recursive = TRUE, showWarnings = FALSE)
write.csv(result, output_path, row.names = FALSE)
message("wrote ", output_path)
print(result[, c("ZONE", "FEATURE_ID", "SCENARIO", "FUELTYPE", "ROS", "HFI", "CFB", "FD")])
