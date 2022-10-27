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
bl_info = {
    "name" : "Copy Dimensions",
    "author" : "Mox",
    "description" : "Copy active object Dimentions to selected, Only Mesh & Lattice now",
    "blender" : (3, 3, 1),
    "version" : (0, 0, 1),
    "location" : "View3D > Object Mode > Sidebar Tab > Context Menu",
    "warning" : "",
    "category" : "Object"
}

from xmlrpc.client import boolean
import bpy
from .operator import OBJECT_OT_CopyDimensions

def draw_menu(self, context):
    canCopy = True

    if context.object.mode == "OBJECT" and len(context.selected_objects) > 1:
        for o in context.selected_objects:
            if o.type != 'MESH' and o.type != 'LATTICE':
                canCopy = False
                break
    else: canCopy = False

    if canCopy == True:
        layout = self.layout
        layout.separator()
        layout.operator(OBJECT_OT_CopyDimensions.bl_idname)

def register():
    bpy.utils.register_class(OBJECT_OT_CopyDimensions)
    bpy.types.UI_MT_button_context_menu.append(draw_menu)

def unregister():
    bpy.types.UI_MT_button_context_menu.remove(draw_menu)
    bpy.utils.unregister_class(OBJECT_OT_CopyDimensions)

if __name__ == "__main__":
    register()