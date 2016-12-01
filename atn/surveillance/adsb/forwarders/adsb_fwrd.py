from abc import ABCMeta, abstractmethod


class AdsbForwarder(object):

    __metaclass__ = ABCMeta

    @abstractmethod
    def forward(self, message, time_of_arrival, tx_id, rx_id):
        raise NotImplementedError()

    @abstractmethod
    def __str__(self):
        raise NotImplementedError()
