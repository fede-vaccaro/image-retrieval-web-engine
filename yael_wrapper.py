import execnet
import numpy as np


def call_python_version(Version, Module, Function, ArgumentList):
    gw = execnet.makegateway("popen//python=python%s" % Version)
    channel = gw.remote_exec("""
        from %s import %s as the_function
        channel.send(the_function(*channel.receive()))
    """ % (Module, Function))
    channel.send(ArgumentList)
    return channel.receive()


def process_desc(signature):
    print("entering in yael_script.py")
    result = call_python_version("2.7", "yael_script", "process",
                                 [signature.tolist()])
    print("out of yael_script.py : descriptor processed")
    return np.array(result)
