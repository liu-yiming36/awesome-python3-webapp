#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Configuration
读取配置文件: 优先从config_override.py读取，并将config_default.py合并进来
"""

import test_config_default

class Dict(dict):
    """
    simple dict but support access as x.y style.
    """
    def __init__(self, names=(), values=(), **kw):
        super(Dict, self).__init__(**kw)
        for k, v in zip(names, values):
            self[k] = v

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(r"'Dict' object has no attribute '%s'" % key)

    def __setattr__(self, key, value):
        self[key] = value

def merge(defaults, override):
    r = {}
    for k, v in defaults.items():
        if k in override:
            if isinstance(v, dict):
                r[k] = merge(v, override[k])
            else:
                r[k] = override[k]
        else:
            r[k] = v  # 如果k不在override里，则无论v是否为字典，都直接赋值于r
    return r
# 用来将字典d转化为能调用x.y的新字典Dict
def toDict(d):
    D = Dict()
    for k, v in d.items():
        D[k] = toDict(v) if isinstance(v, dict) else v
    return D

configs = test_config_default.configs
# 如果不存在test_config_override，则不导入
try:
    import test_config_override
    configs = merge(configs, test_config_override.configs)
except ImportError:
    pass
# 转变为新Dict
configs = toDict(configs)




