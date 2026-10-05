from pygame import *
import factory as fac
import decodeFactory as dec

def placeComponent(factory, component, worldPos: list[int, int], orientation: fac.Directions):
    """validates and encodes components based on how they were placed"""
    
    # check component type
    if isinstance(component, dec.Transport):
        validateTransport(factory, component)
        
    elif isinstance(component, dec.Producer):
        ...
    elif isinstance(component, dec.Machine):
        ... 
    elif isinstance(component, dec.Transport):
        ...

def validateTransport(factory, transport):
    ...

def encodeTransport(factory):
    # check possible connections and set flags
    
    # encode into the factory
    ...
    

def encodeMachine(factory):...
    

def encodeProducer(factory):...
    

def encodeInventory(factory):...
    