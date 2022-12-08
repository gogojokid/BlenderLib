bl_info = {
    "name": "Import As Decal",
    "author": "Amandeep",
    "description": "Import Images as Decals/Stickers",
    "blender": (2, 83, 0),
    "version": (2, 1, 0),
    "location": "SHIFT+A > Image > Image as Decal",
    "warning": "",
    "category": "Object",
}
#region INFORMATION
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
import bpy
from bpy_extras.io_utils import ImportHelper
import os
preview_collections = {}
preview_list = {}
def preferences():
    return bpy.context.preferences.addons[__package__].preferences
class IADPrefs(bpy.types.AddonPreferences):
    bl_idname = __package__
    decals_path:bpy.props.StringProperty(default="Choose Path",name="Decal's Directory",subtype='DIR_PATH')
    def draw(self, context):
        layout=self.layout
        layout.prop(self,'decals_path')
def enum_previews_from_directory_items_iad(self, context):
    enum_items = []
    name = self.name
    if name in preview_list.keys():
        list = preview_list[name]
        #print(name,list)
        if context is None:
            return enum_items
        pcoll = preview_collections[name]
        if len(pcoll.my_previews) > 0:
            return pcoll.my_previews
        
        for i, name in enumerate(list):
            if name.endswith(".png") or name.endswith(".jpg"):
                #print("loading:",name)
                thumb = pcoll.load(name, name, 'IMAGE')
                enum_items.append(
                    (name, os.path.basename(name.replace(".png", "").replace(".jpg","")), "", thumb.icon_id, i))
        pcoll.my_previews = enum_items
        return pcoll.my_previews
    return []
class IAD_OT_Load_Previews(bpy.types.Operator):
    bl_idname = 'iad.refreshdecals'
    bl_label = 'Refresh'
    bl_description = "Refresh"
    bl_options = {'PRESET', 'UNDO'}
    def execute(self, context):
        bpy.context.scene.iad_decals.clear()
        for pcoll in preview_collections.values():
            bpy.utils.previews.remove(pcoll)
        preview_collections.clear()
        preview_list.clear()
        allfiles=[]
        alldirs=[]
        if os.path.isdir(preferences().decals_path):
            for path, dirs, files in os.walk(preferences().decals_path):
                    alldirs+= [os.path.join(path, dir) for dir in dirs]
            #print(allfiles)
            #print(alldirs)
            #print(os.path.dirname(preferences().decals_path))
            for a in alldirs+[os.path.dirname(preferences().decals_path),]:
                allfiles=[os.path.join(a,f) for f in os.listdir(a)]
                og_name=a
                i=1
                while os.path.basename(a) in bpy.context.scene.iad_decals.keys():
                    a=og_name+f"-{i}"
                    i=i+1
                #print(os.path.basename(a))
                temp = bpy.context.scene.iad_decals.add()
                temp.name = os.path.basename(a)
                preview_list[os.path.basename(a)] = allfiles
                pcoll = bpy.utils.previews.new()
                pcoll.my_previews = ()
                preview_collections[os.path.basename(a)] = pcoll
        return {'FINISHED'}
class IAD_DecalInfo(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name="name", default="Decals")
    preview: bpy.props.EnumProperty(
        items=enum_previews_from_directory_items_iad)
def iad_directories(self, context):
    if context.scene.iad_decals and [(a.name,a.name,a.name) for a in context.scene.iad_decals]:
        return [(a.name,a.name,a.name) for a in context.scene.iad_decals]
    else:
        return [("None","None","None")]
class RTOOLS_OT_Decal_Addon(bpy.types.Panel):
    bl_label = "Decals"
    bl_idname = "OBJECT_PT_DECAL"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Item"
    
    def draw(self, context):
        layout= self.layout
        #layout.operator("rtools.importasdecal")
        layout.operator("iad.refreshdecals",icon="FILE_REFRESH")
        layout.prop(context.scene,'iad_directories')
        if context.scene.iad_directories in context.scene.iad_decals.keys():
            layout.template_icon_view(
                        context.scene.iad_decals[context.scene.iad_directories], "preview", show_labels=True, scale=8, scale_popup=6)
            layout.operator("rtools.importasdecalfromenum")
        if context.active_object and context.active_object.type in {'MESH','CURVE','FONT','SURFACE'} and context.active_object.data.materials:
            mat=context.active_object.data.materials[0]
            if mat and "Decal Shader" in [a.name for a in mat.node_tree.nodes]:
                layout.prop(mat.node_tree.nodes['Decal Shader'].inputs[2],'default_value',text="Scale")
                
                layout.prop(mat.node_tree.nodes['Decal Shader'].inputs[3],'default_value',text="Worn Amount")
                row=layout.column(align=True)
                row.label(text="Offset:")
                row.prop(mat.node_tree.nodes['Decal Shader'].inputs[17],'default_value',text="")
                layout.prop(mat.node_tree.nodes['Decal Shader'].inputs[4],'default_value',text="Contrast")
                layout.prop(mat.node_tree.nodes['Decal Shader'].inputs[5],'default_value',text="Roughness")
                layout.prop(mat.node_tree.nodes['Decal Shader'].inputs[6],'default_value',text="Edge")
                layout.prop(mat.node_tree.nodes['Decal Shader'].inputs[7],'default_value',text="Damage Hue")
                layout.prop(mat.node_tree.nodes['Decal Shader'].inputs[8],'default_value',text="Damage Saturation")
                layout.prop(mat.node_tree.nodes['Decal Shader'].inputs[9],'default_value',text="Damage Brightness")
                layout.prop(mat.node_tree.nodes['Decal Shader'].inputs[10],'default_value',text="Bump Strength")
                layout.prop(mat.node_tree.nodes['Decal Shader'].inputs[11],'default_value',text="Scratches")
                #layout.prop(mat.node_tree.nodes['Decal Shader'].inputs[9],'default_value',text="Noise Seed")
                layout.prop(mat.node_tree.nodes['Decal Shader'].inputs[12],'default_value',text="Rotation")
                layout.prop(mat.node_tree.nodes['Decal Shader'].inputs[13],'default_value',text="Distortion")
                layout.prop(mat.node_tree.nodes['Decal Shader'].inputs[14],'default_value',text="Scale")
                layout.prop(mat.node_tree.nodes['Decal Shader'].inputs[15],'default_value',text="Thickness")
                layout.prop(mat.node_tree.nodes['Decal Shader'].inputs[16],'default_value',text="Scratches Strength")

def addToImageMenu(self, context):
    layout=self.layout
    layout.operator("rtools.importasdecal",icon='OUTLINER_OB_IMAGE')
class RTOOLS_OT_Import_As_Decal_From_Enum(bpy.types.Operator):
    bl_idname = 'rtools.importasdecalfromenum'
    bl_label = 'Image as Decal'
    bl_description = "Import image as a decal"
    bl_options = {'PRESET', 'UNDO'}
 
    
    def execute(self, context):
        path=context.scene.iad_decals[context.scene.iad_directories].preview
        #print(path)
        active=context.active_object if context.selected_objects else None

        plane=None
        if os.path.isfile(path):
            img=bpy.data.images.load(path)
            res_x=img.size[0]/1000
            res_y=img.size[1]/1000
            bpy.ops.mesh.primitive_plane_add()
            plane=context.active_object
            plane.scale.x=res_x
            plane.scale.y=res_y
            plane.rotation_euler=[1.5707,0,1.5707]
            plane.location=[0,0,0.01]
            bpy.ops.object.transform_apply(location=True, rotation=False, scale=True)
            mat=bpy.data.materials.new(img.name)
            mat.use_nodes=True
            mat.blend_method='CLIP'
            plane.data.materials.append(mat)
            nodes=mat.node_tree.nodes
            output_socket=None
            if "Principled BSDF" in [n.name for n in nodes]:
                output_socket=nodes['Principled BSDF'].outputs[0].links[0].to_socket
                nodes.remove(nodes['Principled BSDF'])
            if bpy.data.node_groups.get('Decal Shader') is None:
                path=os.path.join(os.path.join(os.path.dirname(os.path.abspath(__file__)),"Assets"),"Assets.blend","NodeTree")
            
        
                bpy.ops.wm.append(
                        directory=path,
                        filename='Decal Shader', autoselect=False
                    )
            DecalShaderGroup=nodes.new('ShaderNodeGroup')
            DecalShaderGroup.location=0,300
            DecalShaderGroup.name="Decal Shader"
            DecalShaderGroup.node_tree = bpy.data.node_groups.get('Decal Shader')
            if output_socket:
                mat.node_tree.links.new(DecalShaderGroup.outputs[0],output_socket)
            img_node=mat.node_tree.nodes.new('ShaderNodeTexImage')
            img_node.location=-300,300
            img_node.image=img
            mat.node_tree.links.new(img_node.outputs[0],DecalShaderGroup.inputs[0])
            mat.node_tree.links.new(img_node.outputs[1],DecalShaderGroup.inputs[1])
            subsurf_mod=plane.modifiers.new(type="SUBSURF",name="Subdivide")
            subsurf_mod.levels=6
            subsurf_mod.render_levels=6
            subsurf_mod.subdivision_type='SIMPLE'
        if active and plane:
            bpy.ops.object.shade_smooth()
            plane.data.use_auto_smooth=True
            shrink_mod=plane.modifiers.new(type="SHRINKWRAP",name="Shrinkwrap")
            shrink_mod.target=active
            shrink_mod.offset=0.003
            shrink_mod.wrap_method='PROJECT'
            shrink_mod.use_project_z=True
            shrink_mod.use_negative_direction=True
            bpy.context.scene.tool_settings.snap_elements = {'FACE'}
            bpy.context.scene.tool_settings.use_snap_align_rotation = True
            bpy.context.scene.tool_settings.snap_target = 'CENTER'

        return {'FINISHED'}
class RTOOLS_OT_Import_As_Decal(bpy.types.Operator, ImportHelper):
    bl_idname = 'rtools.importasdecal'
    bl_label = 'Image as Decal'
    bl_description = "Import image as a decal"
    bl_options = {'PRESET', 'UNDO'}
 
    
    filter_glob: bpy.props.StringProperty(
        default='*.jpg;*.jpeg;*.png;*.tif;*.tiff;*.bmp',
        options={'HIDDEN'}
    )
    def execute(self, context):
        path=self.filepath
        active=context.active_object if context.selected_objects else None

        plane=None
        if os.path.isfile(path):
            img=bpy.data.images.load(path)
            res_x=img.size[0]/1000
            res_y=img.size[1]/1000
            bpy.ops.mesh.primitive_plane_add()
            plane=context.active_object
            plane.scale.x=res_x
            plane.scale.y=res_y
            plane.rotation_euler=[1.5707,0,1.5707]
            plane.location=[0,0,0.01]
            bpy.ops.object.transform_apply(location=True, rotation=False, scale=True)
            mat=bpy.data.materials.new(img.name)
            mat.use_nodes=True
            mat.blend_method='CLIP'
            plane.data.materials.append(mat)
            nodes=mat.node_tree.nodes
            output_socket=None
            if "Principled BSDF" in [n.name for n in nodes]:
                output_socket=nodes['Principled BSDF'].outputs[0].links[0].to_socket
                nodes.remove(nodes['Principled BSDF'])
            if bpy.data.node_groups.get('Decal Shader') is None:
                path=os.path.join(os.path.join(os.path.dirname(os.path.abspath(__file__)),"Assets"),"Assets.blend","NodeTree")
            
        
                bpy.ops.wm.append(
                        directory=path,
                        filename='Decal Shader', autoselect=False
                    )
            DecalShaderGroup=nodes.new('ShaderNodeGroup')
            DecalShaderGroup.location=0,300
            DecalShaderGroup.name="Decal Shader"
            DecalShaderGroup.node_tree = bpy.data.node_groups.get('Decal Shader')
            if output_socket:
                mat.node_tree.links.new(DecalShaderGroup.outputs[0],output_socket)
            img_node=mat.node_tree.nodes.new('ShaderNodeTexImage')
            img_node.location=-300,300
            img_node.image=img
            mat.node_tree.links.new(img_node.outputs[0],DecalShaderGroup.inputs[0])
            mat.node_tree.links.new(img_node.outputs[1],DecalShaderGroup.inputs[1])
            subsurf_mod=plane.modifiers.new(type="SUBSURF",name="Subdivide")
            subsurf_mod.levels=6
            subsurf_mod.render_levels=6
            subsurf_mod.subdivision_type='SIMPLE'
        if active and plane:
            bpy.ops.object.shade_smooth()
            plane.data.use_auto_smooth=True
            shrink_mod=plane.modifiers.new(type="SHRINKWRAP",name="Shrinkwrap")
            shrink_mod.target=active
            shrink_mod.offset=0.003
            shrink_mod.wrap_method='PROJECT'
            shrink_mod.use_project_z=True
            shrink_mod.use_negative_direction=True
            bpy.context.scene.tool_settings.snap_elements = {'FACE'}
            bpy.context.scene.tool_settings.use_snap_align_rotation = True
            bpy.context.scene.tool_settings.snap_target = 'CENTER'

        return {'FINISHED'}
classes = (
    RTOOLS_OT_Import_As_Decal,RTOOLS_OT_Decal_Addon,IAD_OT_Load_Previews,IAD_DecalInfo,RTOOLS_OT_Import_As_Decal_From_Enum,IADPrefs
)

icon_collection={}
addon_keymaps = []

def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)
    
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    kmaps = [
    ]

    km = kc.keymaps.new(name="3D View", space_type="VIEW_3D")
    if kc:
        for (op, k, sp) in kmaps:

            kmi = km.keymap_items.new(
                op,
                type=k,
                value="PRESS",
                alt="alt" in sp,
                shift="shift" in sp,
                ctrl="ctrl" in sp,
            )
            addon_keymaps.append((km, kmi))
    
    bpy.types.VIEW3D_MT_image_add.append(addToImageMenu)
    bpy.types.Scene.iad_decals = bpy.props.CollectionProperty(type=IAD_DecalInfo)
    bpy.types.Scene.iad_directories= bpy.props.EnumProperty(items=iad_directories,name="Folder")

def unregister():

    from bpy.utils import unregister_class

    for cls in reversed(classes):
        unregister_class(cls)
    for (km, kmi) in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()
    bpy.types.VIEW3D_MT_image_add.remove(addToImageMenu)
    for pcoll in preview_collections.values():
        bpy.utils.previews.remove(pcoll)
    preview_collections.clear()
    preview_list.clear()
if __name__ == "__main__":
    register()

