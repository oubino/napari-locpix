"""
This module contains the main Widget plugin

It implements the Widget specification.
see: https://napari.org/stable/plugins/guides.html?#widgets

"""
from typing import TYPE_CHECKING

from qtpy.QtWidgets import QHBoxLayout, QVBoxLayout, QPushButton, QWidget, QComboBox, QFormLayout, QLabel
from qtpy.compat import getopenfilename, getsavefilename

from ._datastruc import file_to_datastruc, item
import polars as pl

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

        self.form = QFormLayout()

        # load data

        load_raw_btn = QPushButton("Load raw data")
        load_raw_btn.clicked.connect(self._load_raw_data)

        load_annot_btn = QPushButton("Load annotated data")
        load_annot_btn.clicked.connect(self._load_annot_data)

        load_box = QHBoxLayout()
        load_box.addWidget(load_raw_btn)
        load_box.addWidget(load_annot_btn)

        # write data

        write_csv_btn = QPushButton("Write to csv")
        write_csv_btn.clicked.connect(self._write_csv)

        write_parquet_btn = QPushButton("Write to parquet")
        write_parquet_btn.clicked.connect(self._write_parquet)

        write_box = QHBoxLayout()
        write_box.addWidget(write_csv_btn)
        write_box.addWidget(write_parquet_btn)

        # bring together
        self.form.addRow(load_box)
        self.form.addRow(write_box)

        self.setLayout(self.form)
        #self.layout().addWidget(load_raw_btn)
        #self.layout().addWidget(load_annot_btn)
        #self.layout().addWidget(write_csv_btn)
        #self.layout().addWidget(write_parquet_btn)

    def _load_raw_data(self):
        print("napari has", len(self.viewer.layers), "layers")

        # specify information want to generalise
        self.cmap=["green", "red", "blue", "bop purple"]
        self.dim=2
        self.channel_choice=[0,1,2,3]
        self.channel_label=['egfr','ereg','unk','unk']
        self.x_bins=500
        self.y_bins=500
        self.z_bins=None
        self.vis_interpolation='log2'

        # load data into datastruc
        path = getopenfilename(
            self,
            "Open file",
            "/home/some/folder",
            "Files (*.csv *.parquet)"
            )
        # first part is path; second part is path filter
        self.path = path[0]
        if self.path.endswith(".csv"):
            self.file_type = 'csv'
            df = pl.scan_csv(self.path)
        elif self.path.endswith(".parquet"):
            self.file_type = 'parquet'
            df = pl.scan_parquet(self.path)

        # load choices into widget and add render button
        #hbox = QHBoxLayout()

        self.form.addRow(QLabel("File column selection"))

        self.channel_col_menu = QComboBox()
        self.channel_col_menu.addItems(df.columns)
        #hbox.addWidget(QLabel("Channel col"))
        #hbox.addWidget(self.channel_col_menu)
        self.form.addRow("Channel: ", self.channel_col_menu)

        self.frame_col_menu = QComboBox()
        self.frame_col_menu.addItems(df.columns)
        self.form.addRow("Frame: ", self.frame_col_menu)

        self.x_col_menu = QComboBox()
        self.x_col_menu.addItems(df.columns)
        self.form.addRow("x: ", self.x_col_menu)

        self.y_col_menu = QComboBox()
        self.y_col_menu.addItems(df.columns)
        self.form.addRow("y: ", self.y_col_menu)

        #z_col_menu = QComboBox()
        #z_col_menu.addItems(df.columns)
        #self.form.addRow("Channel col", self.z_col_menu)

        # render button
        render_button = QPushButton("Render")
        render_button.clicked.connect(self._render_button)
        #render_box = QHBoxLayout()
        #render_box.addWidget(render_button)

        self.form.addRow(QLabel("Histogram settings"))


        # bring it all together
        self.form.addRow(render_button)
        
        
    def _render_button(self):

        # parse the options
        self.channel_col = self.channel_col_menu.currentText()
        self.frame_col = self.frame_col_menu.currentText()
        self.x_col = self.x_col_menu.currentText()
        self.y_col = self.y_col_menu.currentText()
        #self.z_col = self.z_col_menu.currentText()
        self.z_col = None


        self.datastruc = file_to_datastruc(self.path,
                                      self.file_type,
                                      self.dim,
                                      self.channel_col,
                                      self.frame_col,
                                      self.x_col,
                                      self.y_col,
                                      self.z_col,
                                      channel_choice=self.channel_choice,
                                      channel_label=self.channel_label,
                                      )

        # render histogram
        self._render_histo()


    def _render_histo(self):

        # generate histogram
        if self.dim == 2:
            histo_size = (self.x_bins, self.y_bins)
        elif self.dim ==3:
            raise ValueError("No 3D capability atm")
        #    histo_size = (x_bins, y_bins, z_bins)
        self.datastruc.coord_2_histo(
            histo_size,
            vis_interpolation=self.vis_interpolation
        )

        # clear images
        self.viewer.layers.clear()

        # render histogram
        if self.dim == 2:
                # overlay all channels for src
                if len(self.datastruc.channels) != 1:
                    # create the viewer and add each channel (first channel on own,
                    # then iterate through others)
                    colormap_list = self.cmap
                    # note image shape when plotted: [x, y]
                    for index, chan in enumerate(self.datastruc.channels):
                        self.viewer.add_image(
                            self.datastruc.histo[chan].T,
                            name=f"Channel {chan}/{self.datastruc.chan_2_label(chan)}",
                            rgb=False,
                            blending="additive",
                            colormap=colormap_list[index],
                            gamma=2,
                            contrast_limits=[0, 30],
                        )

                # only one channel
                else:
                    img = self.datastruc.histo[self.datastruc.channels[0]].T
                    # create the viewer and add the image
                    viewer = napari.add_image(
                        img,
                        name=f"Channel {self.datastruc.channels[0]}/{self.datastruc.chan_2_label(self.datastruc.channels[0])}",
                        rgb=False,
                        gamma=2,
                        contrast_limits=[0, 30],
                    )

        elif self.dim == 3:
            print("segment 3D image")

    def _load_annot_data(self):

        # get path
        path = getopenfilename(
            self,
            "Open file",
            "/home/some/folder",
            "Files (*.csv *.parquet)"
            )
        # first part is path; second part is path filter
        path = path[0]
        if path.endswith(".csv"):
            file_type = 'csv'
        elif path.endswith(".parquet"):
            file_type = 'parquet'

        # load in
        if file_type == '.parquet':
            self.datastruc = item.load_from_parquet(path)
        elif file_type == '.csv':
            raise ValueError('Not implemented yet!')

        # render
        self._render_histo()


    def _write_csv(self):

        # get path
        path = getsavefilename(
            self,
            "Save file",
            f"/home/some/folder/{self.datastruc.name}.csv",
            "Files (*.csv)"
            )
        # first part is path; second part is path filter
        path = path[0]

        # convert pixel labels to coordinate
        try:
            self.datastruc.histo_mask = self.viewer.layers["Labels"].data.T
            self.datastruc._manual_seg_pixel_2_coord()
        except KeyError:
            print("No labels saved")
        
        # save to this location
        self.datastruc.save_df_to_csv(
            path,
            drop_zero_label=False,
            drop_pixel_col=False,
            save_chan_label=True,
        )

    def _write_parquet(self):

        # specified but need to change
        gt_label_map = {0:'background', 1:'membrane'}

        # get path
        path = getsavefilename(
            self,
            "Save file",
            f"/home/some/folder/{self.datastruc.name}.parquet",
            "Files (*.parquet)"
            )
        # first part is path; second part is path filter
        path = path[0]

        # convert pixel labels to coordinate
        try:
            self.datastruc.histo_mask = self.viewer.layers["Labels"].data.T
            self.datastruc._manual_seg_pixel_2_coord()
        except KeyError:
            print("No labels saved")
        
        # save to this location
        self.datastruc.save_to_parquet(
            path,
            drop_zero_label=False,
            drop_pixel_col=False,
            gt_label_map=gt_label_map,
            overwrite=False,
        )
