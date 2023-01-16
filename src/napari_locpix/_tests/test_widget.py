import os

import polars as pl
import pyarrow.parquet as pq
import pytest
from polars.testing import assert_frame_equal

from napari_locpix import DatastrucWidget

# add label adds widget

# render button

# render button annotate


# test load raw
def test_load_raw_parquet(make_napari_viewer):

    # test file path
    test_file_path = "src/napari_locpix/_tests/raw_test.parquet"

    # make viewer and add an image layer using our fixture
    viewer = make_napari_viewer()

    # create our widget, passing in the viewer
    widget = DatastrucWidget(viewer)

    # call widget method
    widget._load_raw_data(test_file_path)


def test_load_raw_csv(make_napari_viewer):

    # test file path
    test_file_path = "src/napari_locpix/_tests/raw_test.csv"

    # make viewer and add an image layer using our fixture
    viewer = make_napari_viewer()

    # create our widget, passing in the viewer
    widget = DatastrucWidget(viewer)

    # call widget method
    widget._load_raw_data(test_file_path)


# test load annotate


def test_load_annot_parquet(make_napari_viewer):

    # test file path
    test_file_path = "src/napari_locpix/_tests/annot_test.parquet"

    # make viewer and add an image layer using our fixture
    viewer = make_napari_viewer()

    # create our widget, passing in the viewer
    widget = DatastrucWidget(viewer)

    # call widget method
    widget._load_annot_data(test_file_path)


# def test_load_annot_csv(make_napari_viewer):
#
#    # test file path
#    test_file_path = "src/napari_locpix/_tests/test.csv"
#
#    # make viewer and add an image layer using our fixture
#    viewer = make_napari_viewer()
#
#    # create our widget, passing in the viewer
#    widget = DatastrucWidget(viewer)
#
#    # call widget method
#    widget._load_annot_data(test_file_path)


@pytest.fixture
def setup_test_write_parquet(make_napari_viewer):

    # test file path
    in_test_file_path = "src/napari_locpix/_tests/annot_test.parquet"
    out_test_file_path = "src/napari_locpix/_tests/out_annot_test.parquet"

    # make viewer and add an image layer using our fixture
    viewer = make_napari_viewer()

    # create our widget, passing in the viewer
    widget = DatastrucWidget(viewer)

    # call widget method
    widget._load_annot_data(in_test_file_path)

    # render first
    widget._render_button_annot()

    # test write
    widget._write_parquet(out_test_file_path)

    # check two files same
    in_table = pq.read_table(in_test_file_path)
    out_table = pq.read_table(out_test_file_path)

    in_table_schema = in_table.schema
    out_table_schema = out_table.schema

    yield in_table_schema, out_table_schema, in_table, out_table,
    os.remove(out_test_file_path)


def test_write_parquet(setup_test_write_parquet):

    (
        in_table_schema,
        out_table_schema,
        in_table,
        out_table,
    ) = setup_test_write_parquet

    assert in_table_schema == out_table_schema

    in_table = pl.from_arrow(in_table)
    out_table = pl.from_arrow(out_table)

    assert_frame_equal(in_table, out_table, check_row_order=False)


@pytest.fixture
def setup_test_write_csv(make_napari_viewer):
    # test file path
    in_test_file_path = "src/napari_locpix/_tests/annot_test.csv"
    out_test_file_path = "src/napari_locpix/_tests/out_raw_test.csv"

    # make viewer and add an image layer using our fixture
    viewer = make_napari_viewer()

    # create our widget, passing in the viewer
    widget = DatastrucWidget(viewer)

    # call widget method
    widget._load_annot_data(in_test_file_path)

    # have to render for following to work
    widget._render_button(in_test_file_path, file_type="csv")

    # test write
    widget._write_csv(out_test_file_path)

    # check two files same
    in_table = pl.read_csv(in_test_file_path)
    out_table = pl.read_csv(out_test_file_path)

    yield in_table, out_table
    os.remove(out_test_file_path)


# def test_write_csv(setup_test_write_csv):

#    in_table, out_table = setup_test_write_csv

#    assert assert_frame_equal(in_table, out_table)


def test_add_labels(make_napari_viewer):

    # test file path
    test_file_path = "src/napari_locpix/_tests/annot_test.parquet"

    # make viewer and add an image layer using our fixture
    viewer = make_napari_viewer()

    # create our widget, passing in the viewer
    widget = DatastrucWidget(viewer)

    # call widget method
    widget._load_annot_data(test_file_path)

    # have to render first
    widget._render_button_annot()

    # test add labels button
    widget._wrap_labels()

    # test add label
    widget._add_label()


def test_render_button_parquet(make_napari_viewer):

    # test file path
    test_file_path = "src/napari_locpix/_tests/raw_test.parquet"

    # make viewer and add an image layer using our fixture
    viewer = make_napari_viewer()

    # create our widget, passing in the viewer
    widget = DatastrucWidget(viewer)

    # load data
    widget._load_raw_data(test_file_path)

    # render
    widget._render_button(test_file_path, file_type="parquet")


def test_render_button_csv(make_napari_viewer):

    # test file path
    test_file_path = "src/napari_locpix/_tests/raw_test.csv"

    # make viewer and add an image layer using our fixture
    viewer = make_napari_viewer()

    # create our widget, passing in the viewer
    widget = DatastrucWidget(viewer)

    # load data
    widget._load_raw_data(test_file_path)

    # render
    widget._render_button(test_file_path, file_type="csv")


def test_render_button_annot_parquet(make_napari_viewer):

    # test file path
    test_file_path = "src/napari_locpix/_tests/annot_test.parquet"

    # make viewer and add an image layer using our fixture
    viewer = make_napari_viewer()

    # create our widget, passing in the viewer
    widget = DatastrucWidget(viewer)

    # load data
    widget._load_annot_data(test_file_path)

    # render
    widget._render_button_annot()


# make_napari_viewer is a pytest fixture that returns a napari viewer object
# capsys is a pytest fixture that captures stdout and stderr output streams
# def test_write_parquet(make_napari_viewer, capsys):
#
#
#
#    # make viewer and add an image layer using our fixture
#    viewer = make_napari_viewer()
#
#    # create our widget, passing in the viewer
#    widget = DatastrucWidget(viewer)
#
#    # call widget method
#    widget._write_parquet()
#
#    assert 1 == 2
#
#    #viewer.add_image(np.random.random((100, 100)))
#
#    # create our widget, passing in the viewer
#    #my_widget = ExampleQWidget(viewer)
#
#    # call our widget method
#    #my_widget._on_click()
#
#    # read captured output and check that it's as we expected
#    #captured = capsys.readouterr()
#    #assert captured.out == "napari has 1 layers\n"
