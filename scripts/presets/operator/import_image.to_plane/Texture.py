import bpy
op = bpy.context.active_operator

op.align = 'WORLD'
op.location = (0.0, 0.0, 0.0)
op.rotation = (0.0, 0.0, 0.0)
op.force_reload = False
op.image_sequence = False
op.offset = True
op.offset_axis = 'X+'
op.offset_amount = 0.10000000149011612
op.align_axis = 'CAM_AX'
op.align_track = False
op.size_mode = 'ABSOLUTE'
op.fill_mode = 'FILL'
op.height = 1.0
op.factor = 600.0
op.shader = 'PRINCIPLED'
op.emit_strength = 1.0
op.overwrite_material = True
op.compositing_nodes = False
op.use_transparency = True
op.alpha_mode = 'STRAIGHT'
op.use_auto_refresh = True
op.relative = True
