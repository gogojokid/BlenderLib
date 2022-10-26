import bpy

class OBJECT_OT_CopyDimensions(bpy.types.Operator):
    bl_idname = "object.copy_dimensions"
    bl_label = "Copy Dimensions to slected"
    bl_description = "Copy active mesh dimensions to selected"
        
    def execute(self, context):
        for o in context.selectable_objects:
            if o != context.active_object:
                o.dimensions = context.active_object.dimensions
        return {'FINISHED'}