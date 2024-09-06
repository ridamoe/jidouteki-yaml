from abc import ABC, abstractmethod
from jidouteki.spec import DictSpec
from jidouteki.spec.meta import Meta

class Fetcher(DictSpec, ABC):
    params: list
    type: str = Meta.REQUIRED
    
    @abstractmethod
    def fetch(self, *args, **kwargs):
        pass
    
from .network import NetworkFetcher
from .request import RequestFetcher