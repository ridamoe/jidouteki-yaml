from abc import ABC, abstractmethod
from jidouteki.spec import DictSpec
from jidouteki.spec.meta import Meta
import time

class Fetcher(DictSpec, ABC):
    params: list
    type: str = Meta.REQUIRED
    
    def fetch(self, **kwargs):
        cache = self._context._cache
        cache_key = self.key(**kwargs)
        print(self.type, cache_key in cache.keys())

        if cache_key in cache.keys():
            cache_hit = cache[cache_key]
            if time.time() - cache_hit[1] <= cache_hit[2]:
                 return cache_hit[0]
        
        value = self._fetch(**kwargs)
        cache[cache_key] = (value, time.time(), self._context.cache_ttl)
        
        return cache[cache_key][0]
    
    def key(self, **kwargs):
        return hash(str((self.type,self.params,self._key(),kwargs)))
    
    @abstractmethod
    def _key(self):
        pass
        
    @abstractmethod
    def _fetch(**kwargs):
        pass
    
from .network import NetworkFetcher
from .request import RequestFetcher