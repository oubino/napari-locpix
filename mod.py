import polars as pl

path = "../../../data/c15_cells/egfr_568_ereg_647_output/egfr_568_ereg_647_fov1.parquet"

# test data
test_df = pl.read_parquet(path, columns=["x (nm)", "y (nm)", "channelIndex ()", "frameIndex ()"])

test_df = test_df.sample(20)

test_df = test_df.with_column(pl.col("channelIndex ()").cast(pl.Int64))

test_df.write_csv("src/napari_locpix/_tests/raw_test.csv")
test_df.write_parquet("src/napari_locpix/_tests/raw_test.parquet")