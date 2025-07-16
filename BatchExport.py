import bpy
import os
import traceback

bl_info = {
    "name": "Batch Export FBX",
    "author": "Your Name",
    "version": (1, 1),
    "blender": (2, 80, 0),
    "location": "View3D > Tools",
    "description": "Batch export selected objects as FBX with object names",
    "warning": "",
    "wiki_url": "",
    "category": "Import-Export",
}

def get_export_directories_file_path():
    scripts_dir = bpy.utils.user_resource('SCRIPTS')
    if not os.path.exists(scripts_dir):
        try:
            os.makedirs(scripts_dir)
        except Exception as e:
            print(f"无法创建SCRIPTS目录: {e}")
            return None
    return os.path.join(scripts_dir, "export_directories.txt")

def select_only(obj, selected_objects):
    for other_obj in selected_objects:
        other_obj.select_set(False)
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj

def export_fbx(obj, directory):
    if not os.path.exists(directory):
        try:
            os.makedirs(directory)
        except Exception as e:
            print(f"无法创建导出目录: {e}")
            return False
    fbx_path = os.path.join(directory, obj.name + ".fbx")
    try:
        bpy.ops.export_scene.fbx(filepath=fbx_path, use_selection=True, axis_forward='-Z', axis_up='Y')
        return True
    except Exception as e:
        print(f"导出FBX失败: {e}\n{traceback.format_exc()}")
        return False

class BatchExportFBXOperator(bpy.types.Operator):
    bl_idname = "export.batch_fbx"
    bl_label = "Batch Export FBX"
    bl_description = "Batch export selected objects as FBX with object names"
    bl_options = {'REGISTER'}

    def execute(self, context):
        scene = context.scene
        selected_objects = bpy.context.selected_objects
        if not selected_objects:
            self.report({'ERROR'}, "没有选中任何对象！")
            return {'CANCELLED'}
        original_locations = {obj: obj.location.copy() for obj in selected_objects}
        original_parents = {obj: obj.parent for obj in selected_objects}
        for obj in selected_objects:
            obj.location = (0, 0, 0)
            select_only(obj, selected_objects)
            success = export_fbx(obj, scene.manual_directory)
            obj.location = original_locations[obj]
            try:
                obj.parent = original_parents[obj]
            except Exception as e:
                print(f"恢复父子关系失败: {e}")
            if not success:
                self.report({'WARNING'}, f"导出 {obj.name} 失败")
        for obj in selected_objects:
            obj.select_set(True)
        file_path = get_export_directories_file_path()
        if file_path and (not os.path.exists(file_path) or scene.manual_directory not in open(file_path).read()):
            try:
                with open(file_path, 'a') as file:
                    file.write(scene.manual_directory + '\n')
                update_enum(None, bpy.context)
            except Exception as e:
                print(f"写入导出目录文件失败: {e}")
        self.report({'INFO'}, "批量导出完成")
        return {'FINISHED'}

def update_enum(self, context):
    file_path = get_export_directories_file_path()
    if file_path and os.path.exists(file_path):
        with open(file_path, 'r') as file:
            items = [(line.strip(), line.strip(), '') for line in file]
        bpy.types.Scene.text_file_enum = bpy.props.EnumProperty(items=items, update=update_manual_directory)

def update_manual_directory(self, context):
    context.scene.manual_directory = self.text_file_enum

class SimplePanel(bpy.types.Panel):
    bl_label = "Batch FBX Export"
    bl_idname = "OBJECT_PT_simple"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Tools'

    def draw(self, context):
        layout = self.layout
        row = layout.row(align=True)

        row.prop(context.scene, 'manual_directory',text='')
        if hasattr(bpy.types.Scene, 'text_file_enum'):
            row.prop_menu_enum(context.scene, 'text_file_enum',text='', icon='DOWNARROW_HLT')
        layout.operator("export.batch_fbx")

def register():
    bpy.utils.register_class(BatchExportFBXOperator)
    bpy.utils.register_class(SimplePanel)
    bpy.types.Scene.manual_directory = bpy.props.StringProperty(subtype='DIR_PATH')
    update_enum(None, bpy.context)

def unregister():
    bpy.utils.unregister_class(BatchExportFBXOperator)
    bpy.utils.unregister_class(SimplePanel)
    del bpy.types.Scene.manual_directory
    if hasattr(bpy.types.Scene, 'text_file_enum'):
        del bpy.types.Scene.text_file_enum

if __name__ == "__main__":
    register()
