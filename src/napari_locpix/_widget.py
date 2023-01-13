"""
This module contains the main Widget plugin

It implements the Widget specification.
see: https://napari.org/stable/plugins/guides.html?#widgets

"""
from typing import TYPE_CHECKING

from qtpy.QtWidgets import QHBoxLayout, QVBoxLayout, QStackedLayout, QListWidget, QPushButton, QWidget, QComboBox, QFormLayout, QLabel, QLineEdit
from qtpy.QtGui import QIntValidator
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

        # main layout
        self.outer_layout = QVBoxLayout()

        # load data, write data v box
        io = QVBoxLayout()

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

        # bring together io
        io.addLayout(load_box)
        io.addLayout(write_box)


        #self.setLayout(self.form)
        #self.layout().addWidget(load_raw_btn)
        #self.layout().addWidget(load_annot_btn)
        #self.layout().addWidget(write_csv_btn)
        #self.layout().addWidget(write_parquet_btn)

        # link label button
        #self._link()

        # stacked layout for the options
        self.stackedLayout = QStackedLayout()

        # load raw data form
        load_raw_data_widget = QWidget()
        load_raw_data_form = QFormLayout()

        # load choices into widget and add render button
        load_raw_data_form.addRow(QLabel("File column selection"))

        self.channel_col_menu = QComboBox()
        load_raw_data_form.addRow("Channel: ", self.channel_col_menu)

        self.frame_col_menu = QComboBox()
        load_raw_data_form.addRow("Frame: ", self.frame_col_menu)

        self.x_col_menu = QComboBox()
        load_raw_data_form.addRow("x: ", self.x_col_menu)

        self.y_col_menu = QComboBox()
        load_raw_data_form.addRow("y: ", self.y_col_menu)

        #z_col_menu = QComboBox()
        #z_col_menu.addItems(df.columns)
        #load_raw_data_form.addRow("Channel col", self.z_col_menu)

        load_raw_data_form.addRow(QLabel("Channel labels"))

        self.channel_zero_label = QLineEdit("unk")
        self.channel_zero_label.setToolTip("Protein present in channel zero")
        load_raw_data_form.addRow("Chan 0 label: ", self.channel_zero_label)

        self.channel_one_label = QLineEdit("unk")
        self.channel_one_label.setToolTip("Protein present in channel one")
        load_raw_data_form.addRow("Chan 0 label: ", self.channel_one_label)

        self.channel_two_label = QLineEdit("unk")
        self.channel_two_label.setToolTip("Protein present in channel two")
        load_raw_data_form.addRow("Chan 0 label: ", self.channel_two_label)

        self.channel_three_label = QLineEdit("unk")
        self.channel_three_label.setToolTip("Protein present in channel three")
        load_raw_data_form.addRow("Chan 0 label: ", self.channel_three_label)

        load_raw_data_form.addRow(QLabel("Histogram settings"))

        self.x_bins_menu = QLineEdit("500")
        self.x_bins_menu.setValidator(QIntValidator())
        self.x_bins_menu.setToolTip("Number of bins in x dimension")
        load_raw_data_form.addRow("X bins", self.x_bins_menu)

        self.y_bins_menu = QLineEdit("500")
        self.y_bins_menu.setValidator(QIntValidator())
        self.y_bins_menu.setToolTip("Number of bins in y dimension")
        load_raw_data_form.addRow("Y bins", self.y_bins_menu)

        self.vis_interpolation_menu = QComboBox()
        self.vis_interpolation_menu.addItems(["log2", "log10", "linear"])
        self.vis_interpolation_menu.setToolTip(
            "Interpolation applied to the histogram when visualising"
            "the image of the histogram"
        )
        load_raw_data_form.addRow("Vis interpolation", self.vis_interpolation_menu)

        # render button
        self.render_button = QPushButton("Render")  
        load_raw_data_form.addRow(self.render_button)

        # format layout and add to stacked layout
        load_raw_data_widget.setLayout(load_raw_data_form)
        self.stackedLayout.addWidget(load_raw_data_widget)

        # add to main
        self.outer_layout.addLayout(io)
        self.outer_layout.addLayout(self.stackedLayout)
        self.setLayout(self.outer_layout)



    def _load_raw_data(self):

        # if user wants to change cmap let them do this in napari
        # post rendering -i.e. keep this as is
        self.cmap=["green", "red", "blue", "bop purple"]

        # this will change if allow for 3D
        self.dim=2
        self.z_col=None
        self.z_bins=None

        # load data into datastruc
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
            df = pl.scan_csv(path)
        elif path.endswith(".parquet"):
            file_type = 'parquet'
            df = pl.scan_parquet(path)

        # update form
        self.stackedLayout.setCurrentIndex(0)
        self.render_button.clicked.connect(lambda: self._render_button(path, file_type))
        self.channel_col_menu.addItems(df.columns)
        self.frame_col_menu.addItems(df.columns)
        self.x_col_menu.addItems(df.columns)
        self.y_col_menu.addItems(df.columns)


    def _link(self):
        
        #self.viewer.window.
        self.viewer.window.qt_viewer.QtLabelsControls.selectionSpinBox.valueChanged.connect(self._update_labels)

    def _update_labels(self, value):

        print('value', value)
        
        
    def _render_button(self, path, file_type):

        print('here 2')
        
        # will change
        z_col = None
        dim = 2

        # parse the options
        channel_col = self.channel_col_menu.currentText()
        frame_col = self.frame_col_menu.currentText()
        x_col = self.x_col_menu.currentText()
        y_col = self.y_col_menu.currentText()
        #self.z_col = self.z_col_menu.currentText()
        x_bins = int(self.x_bins_menu.text())
        y_bins = int(self.x_bins_menu.text())
        #self.z_bins =
        vis_interpolation =  self.vis_interpolation_menu.currentText()
        channel_label = [
            self.channel_zero_label.text(),
            self.channel_one_label.text(),
            self.channel_two_label.text(),
            self.channel_three_label.text(),
        ]

        self.datastruc = file_to_datastruc(path,
                                      file_type,
                                      dim,
                                      channel_col,
                                      frame_col,
                                      x_col,
                                      y_col,
                                      z_col,
                                      channel_label=channel_label,
                                      )

        # render histogram
        # generate histogram
        if self.datastruc.dim == 2:
            histo_size = (x_bins, y_bins)
        elif self.datastruc.dim ==3:
            raise ValueError("No 3D capability atm")
        #    histo_size = (x_bins, y_bins, z_bins)
        self._render_histo(histo_size, vis_interpolation)


    def _render_histo(self, histo_size, vis_interpolation):

        
        self.datastruc.coord_2_histo(
            histo_size,
            vis_interpolation=vis_interpolation
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

        # need to get histo_size and vis interpolation from user

        # 

        self.x_bins_menu = QLineEdit("500")
        self.x_bins_menu.setValidator(QIntValidator())
        self.x_bins_menu.setToolTip("Number of bins in x dimension")
        self.form.addRow("X bins", self.x_bins_menu)

        self.y_bins_menu = QLineEdit("500")
        self.y_bins_menu.setValidator(QIntValidator())
        self.y_bins_menu.setToolTip("Number of bins in y dimension")
        self.form.addRow("Y bins", self.y_bins_menu)

        self.vis_interpolation_menu = QComboBox()
        self.vis_interpolation_menu.addItems(["log2", "log10", "linear"])
        self.vis_interpolation_menu.setToolTip(
            "Interpolation applied to the histogram when visualising"
            "the image of the histogram"
        )
        self.form.addRow("Vis interpolation", self.vis_interpolation_menu)


        # render
        self._render_histo(histo_size, vis_interpolation)


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
