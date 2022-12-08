import bpy
import bmesh

bl_info = {
	"name": "Logo-Tracer",
	"category": "Mesh",
	"author": "Tim Crellin (Thatimst3r)",
	"blender": (3,1,0),
	"location": "3D View > Properties",
	"description": "Create a mesh out of any logo",
	"warning": "",
	"wiki_url":"",
	"tracker_url": "https://www.thatimster.com/contact.html",
	"version":('1', '21')
}

def prop_update(self, context):
	scn=context.scene
	props = scn.logo_tracer_props[0]
	if len(props.target_obj) > 0 and len(props.form_obj) > 0:
		target_obj = context.collection.objects[props.target_obj]
		form_obj = context.collection.objects[props.form_obj]

		subMod = form_obj.modifiers["Logo_tracer_res"]
		quality_ref = {"Low":2,"Medium":3, "High": 4}
		val = quality_ref[props.quality]
		subMod.render_levels=val
		subMod.levels=val

		dispMod = form_obj.modifiers["Logo_tracer_displace"]
		dispMod.mid_level = props.threshold

		smooth = form_obj.modifiers["Logo_tracer_smooth"]
		smooth.lambda_factor = props.smooth

		if "Logo_tracer_decimate" in target_obj.modifiers:
			moddec = target_obj.modifiers["Logo_tracer_decimate"]
			moddec.ratio = 1-props.optimize_factor
		
		if props.triangulate:
			if "Logo_tracer_tri" not in target_obj.modifiers:
				target_obj.modifiers.new("Logo_tracer_tri", type="TRIANGULATE")
			if "Logo_tracer_decimate" not in target_obj.modifiers:
				moddec = target_obj.modifiers.new("Logo_tracer_decimate", type="DECIMATE")
				moddec.decimate_type = "COLLAPSE"
				moddec.ratio = 1-props.optimize_factor
		else:
			if "Logo_tracer_tri" in target_obj.modifiers:
				target_obj.modifiers.remove(target_obj.modifiers["Logo_tracer_tri"])
			if "Logo_tracer_decimate" in target_obj.modifiers:
				target_obj.modifiers.remove(target_obj.modifiers["Logo_tracer_decimate"])
	else:
		cleanup(context, False)

def img_update(self, context):
	scn=context.scene
	if scn.logo_tracer_props:
		props = scn.logo_tracer_props[0]
		if len(props.target_obj) > 0 and len(props.form_obj) > 0 and scn.logo_tracer_img:
			form_obj = context.collection.objects[props.form_obj]
			target_obj = context.collection.objects[props.target_obj]

			tex = form_obj.modifiers["Logo_tracer_displace"].texture
			tex.image = scn.logo_tracer_img

			mat = target_obj.active_material
			if mat:
				for n in mat.node_tree.nodes:
					if n.type == "TEX_IMAGE":
						n.image = scn.logo_tracer_img
						break

			if scn.logo_tracer_img_alpha and not tex.use_alpha:
				tex.use_alpha = True
				tex.use_color_ramp = True

			elif not scn.logo_tracer_img_alpha and tex.use_alpha:
				tex.use_alpha = False
				tex.use_color_ramp = False
			
			target_img = scn.logo_tracer_img
			ratio_x = target_img.size[0] / target_img.size[1]
			ratio_y = target_img.size[1] / target_img.size[0]
			aspect_ratio_x = ratio_x if ratio_x > 1 else 1
			aspect_ratio_y = ratio_y if ratio_y > 1 else 1

			form_obj.scale = (aspect_ratio_x, aspect_ratio_y,1)
			target_obj.scale = (aspect_ratio_x, aspect_ratio_y,1)

		else:
			cleanup(context, False)

def cleanup(context, completed):
	scn = context.scene
	props = scn.logo_tracer_props[0]
	if props.target_obj in bpy.data.objects and not completed:
		bpy.data.objects.remove(bpy.data.objects[props.target_obj])
	if props.form_obj in bpy.data.objects:
		bpy.data.objects.remove(bpy.data.objects[props.form_obj])
	scn.logo_tracer_props.remove(0)
	
class LOGOTRACER_props(bpy.types.PropertyGroup):
	"""Maintain script properties"""
	threshold: bpy.props.FloatProperty(name="Threshold", default = 0.5, description = "Value Threshold for tracing", min=0, max =1, update=prop_update)
	smooth: bpy.props.FloatProperty(name="Smooth", default = 0.25, description = "Amount of Smoothing", min=0, update=prop_update)
	triangulate: bpy.props.BoolProperty(name="Triangulate", default = False, description = "Use Triangles for mesh", update=prop_update)
	optimize_factor: bpy.props.FloatProperty(name="Optimize", default = 0.5, min = 0,max=1, description = "How much optimization to apply", update=prop_update)
	target_obj: bpy.props.StringProperty(default="")
	form_obj: bpy.props.StringProperty(default="")
	quality: bpy.props.EnumProperty(name="Quality",items=[("Low", "Low", "Low"),("Medium", "Medium", "Medium"), ("High", "High", "High")], default="Medium", update=prop_update)

class PREVIEW_OT_trace(bpy.types.Operator):
	"""set up trace"""

	bl_idname = 'preview.trace'
	bl_label = "Preview"

	@classmethod
	def poll(cls, context):
		return context.scene.logo_tracer_img

	def execute(self, context):
		scn = context.scene
		props = scn.logo_tracer_props
		if not props:
			props.add()
		props = props[0]
		bpy.ops.mesh.primitive_plane_add(size=2)
		target_img = scn.logo_tracer_img
		ratio_x = target_img.size[0] / target_img.size[1]
		ratio_y = target_img.size[1] / target_img.size[0]
		aspect_ratio_x = ratio_x if ratio_x > 1 else 1
		aspect_ratio_y = ratio_y if ratio_y > 1 else 1
		form_obj = context.selected_objects[0]
		form_obj.scale = (aspect_ratio_x, aspect_ratio_y, 1)

		mesh = form_obj.data
		bm = bmesh.new()
		bm.from_mesh(mesh)
		bmesh.ops.subdivide_edges(bm,
			edges=bm.edges,
			cuts=10,
			use_grid_fill=True,
		)
		bm.to_mesh(mesh)
		mesh.update()

		#subsurf
		subMod = form_obj.modifiers.new("Logo_tracer_res", type='SUBSURF')
		subMod.subdivision_type = "SIMPLE"
		quality_ref = {"Medium":3, "High": 4}
		val = quality_ref[props.quality]
		subMod.render_levels=val
		subMod.levels=val
		subMod.quality=1
		subMod.uv_smooth = "NONE"
		subMod.show_only_control_edges = True
		subMod.use_creases = False

		#add texture
		heightTex = bpy.data.textures.new('Logo_tracer_img', type = 'IMAGE')
		heightTex.image = scn.logo_tracer_img
		if scn.logo_tracer_img_alpha:
			heightTex.use_alpha = True
			heightTex.use_color_ramp = True
		else:
			heightTex.use_alpha = False
			heightTex.use_color_ramp = False

		dispMod = form_obj.modifiers.new("Logo_tracer_displace", type='DISPLACE')
		dispMod.texture = heightTex
		dispMod.direction = "Z"
		dispMod.mid_level = props.threshold

		smooth = form_obj.modifiers.new("Logo_tracer_smooth", type = "LAPLACIANSMOOTH")
		smooth.iterations = 5
		smooth.lambda_factor = props.smooth
		smooth.lambda_border = 0.01

		form_obj.hide_viewport = True
		form_obj.hide_render = True
		form_obj.hide_select = True

		props.form_obj = form_obj.name

		bpy.ops.mesh.primitive_plane_add(size=2)
		target_obj = context.selected_objects[0]
		target_obj.scale = (aspect_ratio_x, aspect_ratio_y, 1)
		mat = bpy.data.materials.new(name=scn.logo_tracer_img.name + "_mesh")
		target_obj.data.materials.append(mat)
		
		mat.use_nodes = True
		nt = mat.node_tree
		out = [n for n in nt.nodes if n.type == "OUTPUT_MATERIAL"][0]
		target_node = out.inputs[0].links[0].from_node
		new_img = nt.nodes.new(type="ShaderNodeTexImage")
		new_img.location.x = target_node.location.x - 200
		new_img.location.y = target_node.location.y
		new_img.image = bpy.data.images[scn.logo_tracer_img.name]
		nt.links.new(new_img.outputs[0], target_node.inputs[0])

		modbool = target_obj.modifiers.new("bool", type="BOOLEAN")
		if hasattr(modbool, "solver"):
			modbool.solver = "FAST"
		modbool.operation = "INTERSECT"
		modbool.object = form_obj

		if (props.triangulate):
			target_obj.modifiers.new("Logo_tracer_tri", type="TRIANGULATE")
			moddec = target_obj.modifiers.new("Logo_tracer_decimate", type="DECIMATE")
			moddec.decimate_type = "COLLAPSE"
			moddec.ratio = 1-props.optimize_factor
		
		target_obj.show_wire=True
		props.target_obj = target_obj.name
		return{'FINISHED'}

class APPLY_OT_logotrace(bpy.types.Operator):

	bl_idname = 'apply.logotrace'
	bl_label = "Apply"

	output_mode: bpy.props.IntProperty()

	def execute(self, context):
		scn = context.scene
		props = scn.logo_tracer_props[0]
		obj = context.collection.objects[props.target_obj]
		obj.hide_select = False
		obj.show_wire = False
		context.view_layer.objects.active = obj
		obj.select_set(True)

		for mod in obj.modifiers:
			bpy.ops.object.modifier_apply(modifier=mod.name)

		bpy.data.objects.remove(context.collection.objects[props.form_obj])

		if self.output_mode == 1:
			bpy.ops.object.convert(target="CURVE")
			
		cleanup(context, True)
		return{'FINISHED'}

class CANCEL_OT_logotrace(bpy.types.Operator):
	bl_idname = 'cancel.logotrace'
	bl_label = "Cancel"

	def execute(self, context):
		cleanup(context, False)
		return{'FINISHED'}

class LOGOTRACE_PT_panel(bpy.types.Panel):
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'UI'
	bl_category = 'Logo-Tracer'
	bl_label = 'Logo-Tracer'

	def draw(self, context):
		layout = self.layout
		row = layout.row()
		row.label(text="Image to Trace:")
		row = layout.row()
		row.template_ID(context.scene, "logo_tracer_img", open="image.open")
		row = layout.row()
		row.prop(context.scene, "logo_tracer_img_alpha")
		if not context.scene.logo_tracer_props:
			row = layout.row()
			row.scale_y = 1.5
			row.operator(PREVIEW_OT_trace.bl_idname, icon="IMAGE_PLANE")
		else:
			box = layout.box()
			row = box.row(align=True).split(factor=0.333333)
			row.label(text="Quality:")
			row.prop(context.scene.logo_tracer_props[0], "quality", text="")
			row = box.row()
			row.prop(context.scene.logo_tracer_props[0], "threshold", slider=True)
			row = box.row()
			row.prop(context.scene.logo_tracer_props[0], "smooth")
			box2 = box.box()
			row = box2.row()
			row.prop(context.scene.logo_tracer_props[0], "triangulate")
			if context.scene.logo_tracer_props[0].triangulate:
				row = box2.row()
				row.prop(context.scene.logo_tracer_props[0], "optimize_factor", slider=True)
			row = layout.row()
			row.label(text="Output Format:")
			row = layout.row(align = True)
			row.scale_y = 1.5
			meshtrace = row.operator(APPLY_OT_logotrace.bl_idname, text="Mesh", icon="MESH_DATA")
			meshtrace.output_mode = 0
			curvetrace = row.operator(APPLY_OT_logotrace.bl_idname, text="Curve", icon="CURVE_DATA")
			curvetrace.output_mode = 1
			row = layout.row()
			row.operator(CANCEL_OT_logotrace.bl_idname, icon="CANCEL")

class LOGOTRACE_PR_preferences(bpy.types.AddonPreferences):
    bl_idname = __name__

    def draw(self, context):
        layout = self.layout
        col = layout.column(align = True)
        row = col.row(align = True)
        row.scale_y = 1.5
        row.label(text=" ")
        row.operator(
                "wm.url_open", 
                text="YouTube Channel", 
                icon='TRIA_RIGHT',
        ).url = "https://www.youtube.com/channel/UCoMnKDkb9_v12qC_QMaZuSA"
        
        row.operator(
                "wm.url_open", 
                text="Support Me", 
                icon='SOLO_ON',
        ).url = "https://blendermarket.com/creators/thatimst3r"
        row.label(text=" ")
        row = layout.row()
classes=(PREVIEW_OT_trace,LOGOTRACE_PT_panel, LOGOTRACER_props, APPLY_OT_logotrace,CANCEL_OT_logotrace,LOGOTRACE_PR_preferences)
def register():
	
	from bpy.utils import register_class
	for cls in classes:
		register_class(cls)
	bpy.types.Scene.logo_tracer_img = bpy.props.PointerProperty(name="Logo", description = "Image to trace", type=bpy.types.Image, update=img_update)
	bpy.types.Scene.logo_tracer_img_alpha = bpy.props.BoolProperty(name="Use Alpha Channel", default = False, update=img_update)
	bpy.types.Scene.logo_tracer_props = bpy.props.CollectionProperty(type=LOGOTRACER_props)

def unregister():
	from bpy.utils import unregister_class
	for cls in classes:
		unregister_class(cls)
	del bpy.types.Scene.logo_tracer_img
	del bpy.types.Scene.logo_tracer_img_alpha
	del bpy.types.Scene.logo_tracer_props
