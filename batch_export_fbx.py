import bpy
import os
import traceback

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
    bl_description = "Batch export selected objects as FBX with object names\n\n操作方法:\n• 普通点击: 导出时移动到原点\n• 按住Shift点击: 原地导出保持位置"
    bl_options = {'REGISTER'}

    def invoke(self, context, event):
        # Store whether Shift is held down
        self.shift_held = event.shift
        return self.execute(context)

    def execute(self, context):
        scene = context.scene
        selected_objects = bpy.context.selected_objects
        if not selected_objects:
            self.report({'ERROR'}, "没有选中任何对象！")
            return {'CANCELLED'}
        
        # Store original locations and parents only if we need to move objects
        if not self.shift_held:
            original_locations = {obj: obj.location.copy() for obj in selected_objects}
            original_parents = {obj: obj.parent for obj in selected_objects}
        
        for obj in selected_objects:
            # Only move to origin if Shift is not held
            if not self.shift_held:
                obj.location = (0, 0, 0)
            
            select_only(obj, selected_objects)
            success = export_fbx(obj, scene.manual_directory)
            
            # Restore original location and parent only if we moved the object
            if not self.shift_held:
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
        
        # Show appropriate message based on whether Shift was held
        if self.shift_held:
            self.report({'INFO'}, "批量导出完成 (原地导出模式)")
        else:
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
    bl_category = 'CC'

    def draw(self, context):
        layout = self.layout
        row = layout.row(align=True)

        row.prop(context.scene, 'manual_directory',text='')
        if hasattr(bpy.types.Scene, 'text_file_enum'):
            row.prop_menu_enum(context.scene, 'text_file_enum',text='', icon='DOWNARROW_HLT')
        
        # No text hints in UI - operation methods are shown in tooltip only
        
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
    # 当直接运行脚本时，自动注册插件
    register()
    print("Batch Export FBX 插件已注册")
    print("请在Blender的3D视图中查看 'CC' 标签页")