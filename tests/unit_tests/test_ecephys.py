from unittest import TestCase

from uuid import uuid4
from datetime import datetime

import numpy as np
from pynwb import NWBFile
from pynwb.misc import Units
from pynwb.ecephys import ElectricalSeries

from nwbinspector.checks.ecephys import check_negative_spike_times, check_electrical_series_dims
from nwbinspector.register_checks import InspectorMessage, Importance, Severity


def test_check_negative_spike_times_all_positive():
    units_table = Units()
    units_table.add_unit(spike_times=[0.0, 0.1])
    units_table.add_unit(spike_times=[1.0])
    assert check_negative_spike_times(units_table=units_table) is None


def test_check_negative_spike_times_empty():
    units_table = Units()
    assert check_negative_spike_times(units_table=units_table) is None


def test_check_negative_spike_times_some_negative():
    units_table = Units()
    units_table.add_unit(spike_times=[0.0, 0.1])
    units_table.add_unit(spike_times=[-1.0])
    assert check_negative_spike_times(units_table=units_table) == InspectorMessage(
        severity=Severity.NO_SEVERITY,
        message=(
            "This Units table contains negative spike times. Time should generally be aligned to the earliest time "
            "reference in the NWBFile."
        ),
        importance=Importance.BEST_PRACTICE_VIOLATION,
        check_function_name="check_negative_spike_times",
        object_type="Units",
        object_name="Units",
        location="/",
    )


class TestCheckElectricalSeries(TestCase):
    def setUp(self):

        nwbfile = NWBFile(
            session_description="", identifier=str(uuid4()), session_start_time=datetime.now().astimezone()
        )

        device = nwbfile.create_device(name="dev")
        group = nwbfile.create_electrode_group(
            name="electrode_group", description="desc", location="loc", device=device
        )

        for _ in range(5):
            nwbfile.add_electrode(
                x=3.0,
                y=3.0,
                z=3.0,
                imp=-1.0,
                location="unknown",
                filtering="unknown",
                group=group,
            )

        self.nwbfile = nwbfile

    def test_check_electrical_series_wrong_dims(self):

        electrodes = self.nwbfile.create_electrode_table_region(region=[1, 2, 3], description="three elecs")

        electrical_series = ElectricalSeries(
            name="elec_series",
            description="desc",
            data=np.zeros((100, 10)),
            electrodes=electrodes,
            rate=30.0,
        )

        self.nwbfile.add_acquisition(electrical_series)

        assert check_electrical_series_dims(self.nwbfile.acquisition["elec_series"]) == InspectorMessage(
            severity=Severity.NO_SEVERITY,
            message="The second dimension of data does not match the length of electrodes. Your data may be transposed.",
            importance=Importance.CRITICAL,
            check_function_name="check_electrical_series_dims",
            object_type="ElectricalSeries",
            object_name="elec_series",
            location="/acquisition/",
        )

    def test_check_electrical_series_flipped(self):

        electrodes = self.nwbfile.create_electrode_table_region(region=[0, 1, 2, 3, 4], description="all")

        electrical_series = ElectricalSeries(
            name="elec_series",
            description="desc",
            data=np.zeros((5, 100)),
            electrodes=electrodes,
            rate=30.0,
        )

        self.nwbfile.add_acquisition(electrical_series)

        assert check_electrical_series_dims(self.nwbfile.acquisition["elec_series"]) == InspectorMessage(
            severity=Severity.NO_SEVERITY,
            message="The second dimension of data does not match the length of electrodes, but instead the first does. Data is oriented incorrectly and should be transposed.",
            importance=Importance.CRITICAL,
            check_function_name="check_electrical_series_dims",
            object_type="ElectricalSeries",
            object_name="elec_series",
            location="/acquisition/",
        )
