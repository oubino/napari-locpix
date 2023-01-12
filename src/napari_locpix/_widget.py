"""
This module contains the main Widget plugin

It implements the Widget specification.
see: https://napari.org/stable/plugins/guides.html?#widgets

"""
from typing import TYPE_CHECKING

from qtpy.QtWidgets import QHBoxLayout, QPushButton, QWidget
from qtpy.compat import getopenfilename, getsavefilename

from ._datastruc import file_to_datastruc, item

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
        self.cmap=["green", "red", "blue", "bop purple"]
        self.dim=2
        self.channel_col="Channel"
        self.frame_col="Frame"
        self.x_col="X (nm)"
        self.y_col="Y (nm)"
        self.z_col=None
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
            "Files (*.csv, *.parquet)"
            )
        # first part is path; second part is path filter
        path = path[0]
        if path.endswith(".csv"):
            file_type = 'csv'
        elif path.endswith(".parquet"):
            file_type = 'parquet'
        self.datastruc = file_to_datastruc(path,
                                      file_type,
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
            "Files (*.csv, *.parquet)"
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
