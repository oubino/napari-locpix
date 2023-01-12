"""
This module is an example of a barebones QWidget plugin for napari

It implements the Widget specification.
see: https://napari.org/stable/plugins/guides.html?#widgets

Replace code below according to your needs.
"""
from typing import TYPE_CHECKING

from magicgui import magic_factory
from qtpy.QtWidgets import QHBoxLayout, QPushButton, QWidget
from qtpy.compat import getopenfilename

from ._datastruc import file_to_datastruc

if TYPE_CHECKING:
    import napari


class DatastrucWidget(QWidget):
    # your QWidget.__init__ can optionally request the napari viewer instance
    # in one of two ways:
    # 1. use a parameter called `napari_viewer`, as done here
    # 2. use a type annotation of 'napari.viewer.Viewer' for any parameter
    def __init__(self, napari_viewer):
        super().__init__()
        self.viewer = napari_viewer

        load_raw_btn = QPushButton("Load raw data")
        load_raw_btn.clicked.connect(self._load_raw_data)

        load_annot_btn = QPushButton("Load annotated data")
        load_annot_btn.clicked.connect(self._load_annot_data)

        write_csv_btn = QPushButton("Write to csv")
        write_csv_btn.clicked.connect(self._write_csv)

        write_parquet_btn = QPushButton("Write to parquet")
        write_parquet_btn.clicked.connect(self._write_parquet)

        self.setLayout(QHBoxLayout())
        self.layout().addWidget(load_raw_btn)
        self.layout().addWidget(load_annot_btn)
        self.layout().addWidget(write_csv_btn)
        self.layout().addWidget(write_parquet_btn)

    def _load_raw_data(self):
        print("napari has", len(self.viewer.layers), "layers")

        # specify information want to generalise
        cmap=["green", "red", "blue", "bop purple"]
        dim=2
        channel_col="Channel"
        frame_col="Frame"
        x_col="X (nm)"
        y_col="Y (nm)"
        z_col=None
        channel_choice=[0,1,2,3]
        channel_label=['egfr','ereg','unk','unk']
        x_bins=500
        y_bins=500
        z_bins=None
        vis_interpolation='log2'

        # load data into datastruc
        path = getopenfilename(
            self,
            "Open file",
            "/home/some/folder",
            "Files (*.csv, *.parquet)"
            )
        # first part is path; second part is path filter
        path = path[0]
        if path.endswith(".csv"):
            file_type = 'csv'
        elif path.endswith(".parquet"):
            file_type = 'parquet'
        datastruc = file_to_datastruc(path,
                                      file_type,
                                      dim,
                                      channel_col,
                                      frame_col,
                                      x_col,
                                      y_col,
                                      z_col,
                                      channel_choice=channel_choice,
                                      channel_label=channel_label,
                                      )

        # assign datastruc to the widget
        self.datastruc = datastruc

        # generate histogram
        if dim == 2:
            histo_size = (x_bins, y_bins)
        elif dim ==3:
            raise ValueError("No 3D capability atm")
        #    histo_size = (x_bins, y_bins, z_bins)
        datastruc.coord_2_histo(
            histo_size,
            vis_interpolation=vis_interpolation
        )

        # render histogram
        if dim == 2:
                # overlay all channels for src
                if len(datastruc.channels) != 1:
                    # create the viewer and add each channel (first channel on own,
                    # then iterate through others)
                    colormap_list = cmap
                    # note image shape when plotted: [x, y]
                    for index, chan in enumerate(datastruc.channels):
                        self.viewer.add_image(
                            datastruc.histo[chan].T,
                            name=f"Channel {chan}/{datastruc.chan_2_label(chan)}",
                            rgb=False,
                            blending="additive",
                            colormap=colormap_list[index],
                            gamma=2,
                            contrast_limits=[0, 30],
                        )

                # only one channel
                else:
                    img = datastruc.histo[datastruc.channels[0]].T
                    # create the viewer and add the image
                    viewer = napari.add_image(
                        img,
                        name=f"Channel {datastruc.channels[0]}/{datastruc.chan_2_label(datastruc.channels[0])}",
                        rgb=False,
                        gamma=2,
                        contrast_limits=[0, 30],
                    )

        elif dim == 3:
            print("segment 3D image")


    def _write_data(self):
        
        # write datastruc to file



@magic_factory
def example_magic_widget(img_layer: "napari.layers.Image"):
    print(f"you have selected {img_layer}")


# Uses the `autogenerate: true` flag in the plugin manifest
# to indicate it should be wrapped as a magicgui to autogenerate
# a widget.
def example_function_widget(img_layer: "napari.layers.Image"):
    print(f"you have selected {img_layer}")
