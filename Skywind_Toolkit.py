bl_info= {
    "name": "Skywind Toolkit",
    "description": "Scripts to assist with creating collision and LOD meshes for Skywind",
    "author": "Gamma_Metroid",
    "blender": (3,1,0),
    "version": (1, 2),
    "support": "COMMUNITY",
    "category": "Object",
}

import bpy
import time

class CreateCollision(bpy.types.Operator):
    """Create Collision Mesh"""

    # this script will assist with creating Collision meshes, which can then be exported using ck-cmd.
    # holes may still occur, so it is a good idea to check it over first.

    bl_idname = "object.create_collision"
    bl_label = "Create Collision Mesh"
    bl_options = {'REGISTER', 'UNDO'}

    coll_ratio: bpy.props.FloatProperty(name="Decimation Ratio", default=0.1, min=0.01, max=1)
    coll_weld: bpy.props.BoolProperty(name="Weld Vertices", default=True)
    coll_weld_distance: bpy.props.FloatProperty(name="Weld Distance", default=1.00, min=1e-06, max=50)
    coll_expand_distance: bpy.props.FloatProperty(name="Expand Distance", default=3, min=-1000, max=1000)

    def execute(self, context):
        # start timer
        time_start = time.time()

        # if a mesh is active, but no objects are selected, the active mesh
        # will be replaced by the collision mesh rather than creating a duplicate.
        # so first, check if this is the case and raise an error if so
        if bpy.context.selected_objects == []:
            raise TypeError("ERROR: no objects selected")
            return {'FINISHED'}
        
        # get active object name
        base_name = bpy.context.active_object.name
        
        # get active object collection
        collection = bpy.context.active_object.users_collection[0].name
        
        # duplicate objects
        bpy.ops.object.duplicate()

        # join objects
        bpy.ops.object.join()

        # name object
        bpy.context.active_object.name = base_name + "_rb_mopp_mesh"

        # remove materials and UV maps
        for uv_layers in bpy.context.active_object.data.uv_layers:
            bpy.ops.mesh.uv_texture_remove()

        # remove vertex colors
        for vertex_colors in bpy.context.active_object.data.vertex_colors:
            bpy.ops.mesh.vertex_color_remove()

        # remove custom split normals
        bpy.ops.mesh.customdata_custom_splitnormals_clear()

        # switch to edit mode
        bpy.ops.object.mode_set(mode='EDIT')

        if self.coll_weld == True:
            # merge vertices by distance
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.remove_doubles(threshold=self.coll_weld_distance, use_sharp_edge_from_normals=False)

        # turn off auto smooth
        bpy.context.active_object.data.use_auto_smooth = False

        # switch back to object mode
        bpy.ops.object.mode_set(mode='OBJECT')

        # decimate
        bpy.ops.object.modifier_add(type='DECIMATE')
        bpy.context.active_object.modifiers["Decimate"].ratio = self.coll_ratio
        bpy.context.active_object.modifiers["Decimate"].use_collapse_triangulate = True
        bpy.ops.object.modifier_apply(modifier="Decimate")
        
        if self.coll_expand_distance != 0:
            # expand
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.transform.shrink_fatten(value=self.coll_expand_distance)
            bpy.ops.object.mode_set(mode='OBJECT')
        
        need_rb = True
        need_mopp = True
        
        # check if either empty collision object exists
        for i in bpy.context.scene.objects:
            if i.name == base_name + "_rb":
                need_rb = False
            if i.name == base_name + "_rb_mopp":
                need_mopp = False
        
        # create rigid body mopp structure in empty nodes
        if need_mopp == True:
            bpy.ops.object.add(type='EMPTY')
            bpy.context.active_object.name = base_name + "_rb_mopp"
            bpy.data.collections[collection].objects.link(bpy.context.active_object) # add to our original object's collection
            bpy.ops.collection.objects_remove_active() # remove from active collection
        if need_rb == True:
            bpy.ops.object.add(type='EMPTY')
            bpy.context.active_object.name = base_name + "_rb"
            bpy.data.collections[collection].objects.link(bpy.context.active_object) # add to our original object's collection
            bpy.ops.collection.objects_remove_active() # remove from active collection
        
        # parent mopp node to rigid body
        bpy.ops.object.select_pattern(pattern=base_name + "_rb_mopp")
        bpy.ops.object.parent_set(keep_transform=True)
        
        # parent collision mesh to mopp node
        bpy.ops.object.select_pattern(pattern=base_name + "_rb_mopp",extend=False)
        bpy.context.view_layer.objects.active = bpy.context.selected_objects[0]
        bpy.ops.object.select_pattern(pattern=base_name + "_rb_mopp_mesh")
        bpy.ops.object.parent_set(keep_transform=True)
        
        print("Collision script finished in %.4f sec" % (time.time() - time_start))
        return {'FINISHED'}

class CreateLOD(bpy.types.Operator):
    """Create LOD Meshes"""

    # this script will assist with creating LOD meshes. however, if you want your LOD
    # textures to be atlased, the UVs must all be in the 0..1 range. this must be done
    # manually, either before or after decimation.

    bl_idname = "object.create_lod"
    bl_label = "Create LOD"
    bl_options = {'REGISTER', 'UNDO'}

    ratio0: bpy.props.FloatProperty(name="LOD0 Ratio", default=0.2, min=0.01, max=1)
    ratio1: bpy.props.FloatProperty(name="LOD1 Ratio", default=0.1, min=0.01, max=1)

    def execute(self, context):
        # start timer
        time_start = time.time()

        def create_lod(level,ratio):
            # duplicate selection
            bpy.ops.object.duplicate()

            # join selected objects
            bpy.ops.object.join()

            # name the object
            bpy.context.active_object.name = level

            # switch to edit mode
            bpy.ops.object.mode_set(mode='EDIT')

            # merge vertices by distance
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.remove_doubles(threshold=0.01, use_sharp_edge_from_normals=True)

            # switch to object mode
            bpy.ops.object.mode_set(mode='OBJECT')

            # decimate
            bpy.ops.object.modifier_add(type='DECIMATE')
            bpy.context.active_object.modifiers["Decimate"].ratio = ratio
            bpy.context.active_object.modifiers["Decimate"].use_collapse_triangulate = True
            bpy.ops.object.modifier_apply(modifier="Decimate")

        # rename all UV maps to "UVMap" for the join
        for obj in bpy.context.selected_objects:
            obj.data.uv_layers.active.name = "UVMap"

        # create lod0
        create_lod("lod0",self.ratio0)

        # select the originals again
        bpy.ops.object.select_all(action='INVERT')

        # make one of them active
        bpy.context.view_layer.objects.active = bpy.context.selected_objects[0]

        # create lod1
        create_lod("lod1",self.ratio1)

        print("LOD script finished in %.4f sec" % (time.time() - time_start))
        return {'FINISHED'}

class AutoShrink(bpy.types.Operator):
    """Import FBX, Shrink and Re-Export"""
    
    # made this to shrink LOD meshes to prevent z fighting when they're loading in
    # (not done)
    
    bl_idname = "object.auto_shrink"
    bl_label = "AutoShrink"
    bl_options = {'REGISTER', 'UNDO'}
    
    shrink_value: bpy.props.FloatProperty()
    working_dir: bpy.props.StringProperty()
    
    def execute(self, context):
        time_start = time.time()
        
        # foo
        
        print("AutoShrink script finished in %.4f sec" % (time.time() - time_start))
        return {'FINISHED'}

def menu_func(self, context):
    self.layout.operator(CreateLOD.bl_idname)
    self.layout.operator(CreateCollision.bl_idname)

# store keymaps here to access after registration
addon_keymaps = []

def register():
    bpy.utils.register_class(CreateLOD)
    bpy.utils.register_class(CreateCollision)
    bpy.types.VIEW3D_MT_object.append(menu_func)

    # handle the keymap
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        km = wm.keyconfigs.addon.keymaps.new(name='Object Mode', space_type='EMPTY')
        kmi = km.keymap_items.new(CreateLOD.bl_idname, 'L', 'PRESS', ctrl=True, alt=True)
        kmi.properties.ratio0 = 0.2
        kmi.properties.ratio1 = 0.1
        addon_keymaps.append((km, kmi))

        km = wm.keyconfigs.addon.keymaps.new(name='Object Mode', space_type='EMPTY')
        kmi = km.keymap_items.new(CreateCollision.bl_idname, 'C', 'PRESS', ctrl=True, alt=True)
        kmi.properties.coll_ratio = 0.1
        kmi.properties.coll_weld = True
        kmi.properties.coll_weld_distance = 1.00
        kmi.properties.coll_expand_distance = 3
        addon_keymaps.append((km, kmi))

def unregister():
    # handle the keymap
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()

    bpy.utils.unregister_class(CreateLOD)
    bpy.utils.unregister_class(CreateCollision)
    bpy.types.VIEW3D_MT_object.remove(menu_func)

if __name__ == "__main__":
    register()