bl_info = {
    "name": "Batch Export FBX",
    "author": "Your Name",
    "version": (1, 2),
    "blender": (2, 80, 0),
    "location": "View3D > CC",
    "description": "Batch export selected objects as FBX with object names, supports in-place export with Shift+click",
    "warning": "",
    "wiki_url": "",
    "category": "Import-Export",
}

# 支持重新加载模块
if "bpy" in locals():
    import importlib
    if "batch_export_fbx" in locals():
        importlib.reload(batch_export_fbx)

import bpy
from . import batch_export_fbx

def register():
    batch_export_fbx.register()

def unregister():
    batch_export_fbx.unregister()

if __name__ == "__main__":
    register()