bl_info= {
    "name": "Skywind Toolkit",
    "description": "Scripts to assist with Skywind 3D and Implementation",
    "author": "Gamma_Metroid",
    "blender": (3,3,0),
    "version": (1,3,1),
    "support": "COMMUNITY",
    "category": "Object",
}

import bpy
import time
import re # regex

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
        
        # recursively traverse layer_collection for a particular name
        def recurLayerCollection(layerColl, collName):
            found = None
            if (layerColl.name == collName):
                return layerColl
            for layer in layerColl.children:
                found = recurLayerCollection(layer, collName)
                if found:
                    return found
        
        # get active object collection
        collection = bpy.context.active_object.users_collection[0].name
        # set this as the active collection
        layer_collection = bpy.context.view_layer.layer_collection
        layerColl = recurLayerCollection(layer_collection, collection)
        bpy.context.view_layer.active_layer_collection = layerColl
        
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
        # mark all edges as not sharp
        bpy.ops.mesh.mark_sharp(clear=True)

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
            if collection != bpy.context.active_object.users_collection[0].name: # is the original object not in the active collection?
                bpy.data.collections[collection].objects.link(bpy.context.active_object) # add to our original object's collection
                bpy.ops.collection.objects_remove_active() # remove from active collection
        if need_rb == True:
            bpy.ops.object.add(type='EMPTY')
            bpy.context.active_object.name = base_name + "_rb"
            if collection != bpy.context.active_object.users_collection[0].name:
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

class SyncNames(bpy.types.Operator):
    """Sync Object/Mesh Names"""
    
    # rename meshes to match their parent objects
    
    bl_idname = "object.syncnames"
    bl_label = "Sync Object/Mesh Names"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        time_start = time.time()
        print("Beginning name sync...")
        
        objArray = bpy.context.selected_objects
        
        skipArray = list()

        # first rename them to unique values to prevent any conflicts
        n = 0
        for i in objArray:
            if hasattr(i.data,"name"): # only if the data has a name (empties don't)
                if i.name != i.data.name:
                    if not re.search("^STK[0-9][0-9][0-9]$",i.data.name): # make sure the data name has not already been changed--this can happen with linked objects
                        print("OBJ {:>03}".format(str(n)) + ": " + i.name + " > DATA: " + i.data.name)
                        i.data.name = "STK{:>03}".format(str(n))
                        print("\trenamed to: " + i.data.name)
                    else:
                        print("SKIP: OBJ {:>03}".format(str(n)) + ": " + i.name + " has suspected linked data!")
                        skipArray.append(i) # add this obj to the skip array
                else:
                    print("SKIP: OBJ {:>03}".format(str(n)) + ": " + i.name + " already has synced names!")
                    skipArray.append(i) # add this obj to the skip array
            else:
                print("SKIP: OBJ " + "{:>03}".format(str(n)) + ": " + i.name + " has no named data!")
                skipArray.append(i) # add this obj index to the skip array
            n += 1

        # rename all data blocks to match their parent objects
        for i in objArray:
            if hasattr(i.data,"name") and skipArray.count(i) == 0: # only if the data has a name (empties don't) and if it's not in the skip array
                print("OBJ: " + i.name + " > DATA: " + i.data.name)
                i.data.name = i.name
                print("\trenamed to: " + i.data.name)
        
        print("SyncNames script finished in %.4f sec" % (time.time() - time_start))
        return {'FINISHED'}

def menu_func(self, context):
    self.layout.operator(CreateLOD.bl_idname)
    self.layout.operator(CreateCollision.bl_idname)
    self.layout.operator(SyncNames.bl_idname)

# store keymaps here to access after registration
addon_keymaps = []

def register():
    bpy.utils.register_class(CreateLOD)
    bpy.utils.register_class(CreateCollision)
    bpy.utils.register_class(SyncNames)
    bpy.types.VIEW3D_MT_object.append(menu_func)

    # handle the keymap
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        km = wm.keyconfigs.addon.keymaps.new(name='Object Mode', space_type='EMPTY')
        kmi = km.keymap_items.new(CreateLOD.bl_idname, 'L', 'PRESS', ctrl=True, alt=True)
        addon_keymaps.append((km, kmi))

        km = wm.keyconfigs.addon.keymaps.new(name='Object Mode', space_type='EMPTY')
        kmi = km.keymap_items.new(CreateCollision.bl_idname, 'C', 'PRESS', ctrl=True, alt=True)
        addon_keymaps.append((km, kmi))
        
        km = wm.keyconfigs.addon.keymaps.new(name='Object Mode', space_type='EMPTY')
        kmi = km.keymap_items.new(SyncNames.bl_idname, 'N', 'PRESS', ctrl=True, alt=True)
        addon_keymaps.append((km, kmi))

def unregister():
    # handle the keymap
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()

    bpy.utils.unregister_class(CreateLOD)
    bpy.utils.unregister_class(CreateCollision)
    bpy.utils.unregister_class(SyncNames)
    bpy.types.VIEW3D_MT_object.remove(menu_func)

if __name__ == "__main__":
    register()
