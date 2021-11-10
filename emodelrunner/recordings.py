"""Custom Recording class."""

import logging

from bluepyopt import ephys

logger = logging.getLogger(__name__)


class RecordingCustom(ephys.recordings.CompRecording):
    """Response to stimulus with recording every 0.1 ms.

    Attributes:
        name (str): name of this object
        location (Location): location in the model of the recording
        variable (str): which variable to record from (e.g. 'v')
        varvector (neuron Vector): vector recording the variable
        tvector (neuron Vector): vector recording the time (ms)
        instantiated (bool): whether the object has been instantiated or not

    Args of the parent constructor:

    - name (str): name of this object
    - location (Location): location in the model of the recording
    - variable (str): which variable to record from (e.g. 'v')
    """

    def instantiate(self, sim=None, icell=None):
        """Instantiate recording.

        Args:
            sim (bluepyopt.ephys.NrnSimulator): neuron simulator
            icell (neuron cell): cell instantiation in simulator
        """
        logger.debug(
            "Adding compartment recording of %s at %s", self.variable, self.location
        )

        self.varvector = sim.neuron.h.Vector()
        seg = self.location.instantiate(sim=sim, icell=icell)
        self.varvector.record(getattr(seg, f"_ref_{self.variable}"), 0.1)

        self.tvector = sim.neuron.h.Vector()
        self.tvector.record(sim.neuron.h._ref_t, 0.1)  # pylint: disable=W0212

        self.instantiated = True
