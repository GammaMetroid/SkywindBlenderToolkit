bl_info= {
    "name": "Skywind Toolkit",
    "description": "Scripts to assist with Skywind 3D and Implementation",
    "author": "Gamma_Metroid",
    "blender": (3,4,0),
    "version": (1,4,2),
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

    def nif_materials():
        items=[
            ("SKY_HAV_MAT_BROKEN_STONE", "SKY_HAV_MAT_BROKEN_STONE", "Broken Stone"),
            ("SKY_HAV_MAT_LIGHT_WOOD", "SKY_HAV_MAT_LIGHT_WOOD", "Light Wood"),
            ("SKY_HAV_MAT_ASH", "SKY_HAV_MAT_ASH", "Ash"),
            ("SKY_HAV_MAT_GRAVEL", "SKY_HAV_MAT_GRAVEL", "Gravel"),
            ("SKY_HAV_MAT_MATERIAL_CHAIN_METAL", "SKY_HAV_MAT_MATERIAL_CHAIN_METAL", "Material Chain Metal"),
            ("SKY_HAV_MAT_BOTTLE", "SKY_HAV_MAT_BOTTLE", "Bottle"),
            ("SKY_HAV_MAT_WOOD", "SKY_HAV_MAT_WOOD", "Wood"),
            ("SKY_HAV_MAT_SKIN", "SKY_HAV_MAT_SKIN", "Skin"),
            ("SKY_HAV_MAT_UNKNOWN_617099282", "SKY_HAV_MAT_UNKNOWN_617099282", "Unknown in Creation Kit v1.9.32.0. Found in Dawnguard DLC in meshes\dlc01\clutter\dlc01deerskin.nif."),
            ("SKY_HAV_MAT_BARREL", "SKY_HAV_MAT_BARREL", "Barrel"),
            ("SKY_HAV_MAT_MATERIAL_CERAMIC_MEDIUM", "SKY_HAV_MAT_MATERIAL_CERAMIC_MEDIUM", "Material Ceramic Medium"),
            ("SKY_HAV_MAT_MATERIAL_BASKET", "SKY_HAV_MAT_MATERIAL_BASKET", "Material Basket"),
            ("SKY_HAV_MAT_SHIELD_ALTERNATE", "SKY_HAV_MAT_SHIELD_ALTERNATE", "Ice"),
            ("SKY_HAV_MAT_STAIRS_STONE", "SKY_HAV_MAT_STAIRS_STONE", "Stairs Stone"),
            ("SKY_HAV_MAT_WATER", "SKY_HAV_MAT_WATER", "Water"),
            ("SKY_HAV_MAT_UNKNOWN_1028101969", "SKY_HAV_MAT_UNKNOWN_1028101969", "Unknown in Creation Kit v1.6.89.0. Found in actors\draugr\character assets\skeletons.nif."),
            ("SKY_HAV_MAT_MATERIAL_BLADE_1HAND", "SKY_HAV_MAT_MATERIAL_BLADE_1HAND", "Material Blade 1 Hand"),
            ("SKY_HAV_MAT_MATERIAL_BOOK", "SKY_HAV_MAT_MATERIAL_BOOK", "Material Book"),
            ("SKY_HAV_MAT_MATERIAL_CARPET", "SKY_HAV_MAT_MATERIAL_CARPET", "Material Carpet"),
            ("SKY_HAV_MAT_LIGHT_METAL", "SKY_HAV_MAT_LIGHT_METAL", "Light Metal"),
            ("SKY_HAV_MAT_MATERIAL_AXE_1HAND", "SKY_HAV_MAT_MATERIAL_AXE_1HAND", "Material Axe 1Hand"),
            ("SKY_HAV_MAT_UNKNOWN_1440721808", "SKY_HAV_MAT_UNKNOWN_1440721808", "Unknown in Creation Kit v1.6.89.0. Found in armor\draugr\draugrbootsfemale_go.nif or armor\amuletsandrings\amuletgnd.nif."),
            ("SKY_HAV_MAT_STAIRS_WOOD", "SKY_HAV_MAT_STAIRS_WOOD", "Stairs Wood"),
            ("SKY_HAV_MAT_BLADE1HAND_ALTERNATE", "SKY_HAV_MAT_BLADE1HAND_ALTERNATE", "Blade 1Hand Alternate"),
            ("SKY_HAV_MAT_MATERIAL_ARMOR_ALTERNATE", "SKY_HAV_MAT_MATERIAL_ARMOR_ALTERNATE", "Armor Alternate"),
            ("SKY_HAV_MAT_STAIRS_ASH", "SKY_HAV_MAT_STAIRS_ASH", "Stairs Ash"),
            ("SKY_HAV_MAT_PLASTER", "SKY_HAV_MAT_PLASTER", "Plaster"),
            ("SKY_HAV_MAT_UNKNOWN_1574477864", "SKY_HAV_MAT_UNKNOWN_1574477864", "Unknown in Creation Kit v1.6.89.0. Found in actors\dragon\character assets\skeleton.nif."),
            ("SKY_HAV_MAT_UNKNOWN_1591009235", "SKY_HAV_MAT_UNKNOWN_1591009235", "Unknown in Creation Kit v1.6.89.0. Found in trap objects or clutter\displaycases\displaycaselgangled01.nif or actors\deer\character assets\skeleton.nif."),
            ("SKY_HAV_MAT_MATERIAL_BOWS_STAVES_POLEARMS_LIGHT", "SKY_HAV_MAT_MATERIAL_BOWS_STAVES_POLEARMS_LIGHT", "Material Bows Staves and Polearms (Light)"),
            ("SKY_HAV_MAT_MATERIAL_WOOD_AS_STAIRS", "SKY_HAV_MAT_MATERIAL_WOOD_AS_STAIRS", "Material Wood As Stairs"),
            ("SKY_HAV_MAT_GRASS", "SKY_HAV_MAT_GRASS", "Grass"),
            ("SKY_HAV_MAT_MATERIAL_BOWS_STAVES_POLEARMS_HEAVY", "SKY_HAV_MAT_MATERIAL_BOWS_STAVES_POLEARMS_HEAVY", "Bows, Staves, and Polearms (Heavy)"),
            ("SKY_HAV_MAT_MATERIAL_STONE_AS_STAIRS", "SKY_HAV_MAT_MATERIAL_STONE_AS_STAIRS", "Material Stone As Stairs"),
            ("SKY_HAV_MAT_MATERIAL_BLADE_2HAND", "SKY_HAV_MAT_MATERIAL_BLADE_2HAND", "Material Blade 2Hand"),
            ("SKY_HAV_MAT_MATERIAL_BOTTLE_SMALL", "SKY_HAV_MAT_MATERIAL_BOTTLE_SMALL", "Material Bottle Small"),
            ("SKY_HAV_MAT_SAND", "SKY_HAV_MAT_SAND", "Sand"),
            ("SKY_HAV_MAT_HEAVY_METAL", "SKY_HAV_MAT_HEAVY_METAL", "Heavy Metal"),
            ("SKY_HAV_MAT_UNKNOWN_2290050264", "SKY_HAV_MAT_UNKNOWN_2290050264", "Unknown in Creation Kit v1.9.32.0. Found in Dawnguard DLC in meshes\dlc01\clutter\dlc01sabrecatpelt.nif."),
            ("SKY_HAV_MAT_DRAGON", "SKY_HAV_MAT_DRAGON", "Dragon"),
            ("SKY_HAV_MAT_MATERIAL_BLADE_1HAND_SMALL", "SKY_HAV_MAT_MATERIAL_BLADE_1HAND_SMALL", "Material Blade 1Hand Small"),
            ("SKY_HAV_MAT_MATERIAL_SKIN_SMALL", "SKY_HAV_MAT_MATERIAL_SKIN_SMALL", "Material Skin Small"),
            ("SKY_HAV_MAT_STAIRS_BROKEN_STONE", "SKY_HAV_MAT_STAIRS_BROKEN_STONE", "Stairs Broken Stone"),
            ("SKY_HAV_MAT_MATERIAL_SKIN_LARGE", "SKY_HAV_MAT_MATERIAL_SKIN_LARGE", "Material Skin Large"),
            ("SKY_HAV_MAT_ORGANIC", "SKY_HAV_MAT_ORGANIC", "Organic"),
            ("SKY_HAV_MAT_MATERIAL_BONE", "SKY_HAV_MAT_MATERIAL_BONE", "Material Bone"),
            ("SKY_HAV_MAT_HEAVY_WOOD", "SKY_HAV_MAT_HEAVY_WOOD", "Heavy Wood"),
            ("SKY_HAV_MAT_MATERIAL_CHAIN", "SKY_HAV_MAT_MATERIAL_CHAIN", "Material Chain"),
            ("SKY_HAV_MAT_DIRT", "SKY_HAV_MAT_DIRT", "Dirt"),
            ("SKY_HAV_MAT_MATERIAL_ARMOR_LIGHT", "SKY_HAV_MAT_MATERIAL_ARMOR_LIGHT", "Material Armor Light"),
            ("SKY_HAV_MAT_MATERIAL_SHIELD_LIGHT", "SKY_HAV_MAT_MATERIAL_SHIELD_LIGHT", "Material Shield Light"),
            ("SKY_HAV_MAT_MATERIAL_COIN", "SKY_HAV_MAT_MATERIAL_COIN", "Material Coin"),
            ("SKY_HAV_MAT_MATERIAL_SHIELD_HEAVY", "SKY_HAV_MAT_MATERIAL_SHIELD_HEAVY", "Material Shield Heavy"),
            ("SKY_HAV_MAT_MATERIAL_ARMOR_HEAVY", "SKY_HAV_MAT_MATERIAL_ARMOR_HEAVY", "Material Armor Heavy"),
            ("SKY_HAV_MAT_MATERIAL_ARROW", "SKY_HAV_MAT_MATERIAL_ARROW", "Material Arrow"),
            ("SKY_HAV_MAT_GLASS", "SKY_HAV_MAT_GLASS", "Glass"),
            ("SKY_HAV_MAT_STONE", "SKY_HAV_MAT_STONE", "Stone"),
            ("SKY_HAV_MAT_CLOTH", "SKY_HAV_MAT_CLOTH", "Cloth"),
            ("SKY_HAV_MAT_MATERIAL_BLUNT_2HAND", "SKY_HAV_MAT_MATERIAL_BLUNT_2HAND", "Material Blunt 2Hand"),
            ("SKY_HAV_MAT_UNKNOWN_4239621792", "SKY_HAV_MAT_UNKNOWN_4239621792", "Unknown in Creation Kit v1.9.32.0. Found in Dawnguard DLC in meshes\dlc01\prototype\dlc1protoswingingbridge.nif."),
            ("SKY_HAV_MAT_MATERIAL_STAIRS_PLASTER", "SKY_HAV_MAT_MATERIAL_STAIRS_PLASTER", "Plaster Stairs")
        ]
        return items

    coll_ratio: bpy.props.FloatProperty(name="Decimation Ratio", default=0.1, min=0.01, max=1)
    coll_weld: bpy.props.BoolProperty(name="Weld Vertices", default=True)
    coll_weld_distance: bpy.props.FloatProperty(name="Weld Distance", default=1.00, min=1e-06, max=50)
    coll_expand_distance: bpy.props.FloatProperty(name="Expand Distance", default=3, min=-1000, max=1000)
    coll_single_material: bpy.props.BoolProperty(name="Single Material", default=True)
    coll_material: bpy.props.EnumProperty(items=nif_materials(), name="Material", default="SKY_HAV_MAT_WOOD")
        
    def execute(self, context):
        # start timer
        time_start = time.time()

        # if a mesh is active, but no objects are selected, the active mesh
        # will be replaced by the collision mesh rather than creating a duplicate.
        # so first, check if this is the case and raise an error if so
        if bpy.context.selected_objects == []:
            raise TypeError("ERROR: no objects selected")
            return {'FINISHED'}
        
        # if none of the selected objects are active, make the first one active
        if bpy.context.view_layer.objects.active == None:
            bpy.context.view_layer.objects.active = bpy.context.selected_objects[0]
        
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

        # remove UV maps
        for uv_layers in bpy.context.active_object.data.uv_layers:
            bpy.ops.mesh.uv_texture_remove()
        # if a single material is desired
        if self.coll_single_material:
            # remove the existing materials
            for material_slots in bpy.context.active_object.material_slots.values():
                bpy.ops.object.material_slot_remove()
            # replace them with a single material
            mat = bpy.data.materials.get(self.coll_material)
            if mat == None:
                mat = bpy.data.materials.new(name=self.coll_material)
            bpy.context.active_object.data.materials.append(mat)
        # remove vertex colors
        for vertex_colors in bpy.context.active_object.data.color_attributes:
            bpy.ops.geometry.color_attribute_remove()
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
        
        # select collision mesh object
        bpy.ops.object.select_pattern(pattern=base_name + "_rb_mopp_mesh",extend=False)
        bpy.context.view_layer.objects.active = bpy.context.selected_objects[0]
        
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

        print("\nAnalyzing current names...")
        
        # first rename them to unique values to prevent any conflicts
        n = 0
        for i in objArray:
            if hasattr(i.data,"name"): # only if the data has a name (empties don't)
                if i.data.name != (i.name + ":data"):
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
                print("SKIP: OBJ {:>03}".format(str(n)) + ": " + i.name + " has no named data!")
                skipArray.append(i) # add this obj to the skip array
            n += 1

        print("\nAssigning final names...")

        # rename all data blocks to match their parent objects
        for i in objArray:
            if hasattr(i.data,"name") and skipArray.count(i) == 0: # only if the data has a name (empties don't) and if it's not in the skip array
                print("OBJ: " + i.name + " > DATA: " + i.data.name)
                i.data.name = i.name + ":data"
                print("\trenamed to: " + i.data.name)
        
        print("SyncNames script finished in %.4f sec" % (time.time() - time_start))
        return {'FINISHED'}
        
class VColorCopy(bpy.types.Operator):
    """Copy Vertex Color Channel"""
    
    # copy vertex color values from one channel to another
    
    bl_idname = "object.vcolorcopy"
    bl_label = "Copy Vertex Colors"
    bl_options = {'REGISTER', 'UNDO'}
    
    def channels():
        items = [
            ("0", "Red", "Red"),
            ("1", "Green", "Green"),
            ("2", "Blue", "Blue"),
            ("3", "Alpha", "Alpha")
        ]
        return items
    
    src_chan: bpy.props.EnumProperty(items=channels(), name="Source Channel", default=0)
    dst_chan: bpy.props.EnumProperty(items=channels(), name="Destination Channel", default=0)
    
    sta: bpy.props.BoolProperty(name="Selected to Active", default=False)
    
    def execute(self, context):
        time_start = time.time()
        print("Beginning vertex color copy...")
        
        # check that an object is active
        if bpy.context.active_object == None:
            raise TypeError("ERROR: no active object")
            return {'FINISHED'}
        
        # check that the object has vertex colors
        if list(bpy.context.active_object.data.color_attributes) == []:
            raise TypeError("ERROR: active object has no vertex colors")
            return {'FINISHED'}        
        
        # try to predict whether to enable "Selected to Active"
        if len(bpy.context.selected_objects) == 1:
            self.sta = False
        else:
            self.sta = True
        
        # if "Selected to Active" is not ticked
        if not self.sta:
            # access color attribute
            # this just grabs the first one. how can i grab the active one?
            color_attr = bpy.context.active_object.data.color_attributes[0].data
            
            # cast to int
            src_chan = int(self.src_chan)
            dst_chan = int(self.dst_chan)
            
            # copy values from channel "src" to channel "dst"
            for attr in color_attr:
                color = attr.color_srgb
                color[dst_chan] = color[src_chan]
            
        elif self.sta: # if "Selected to Active" is ticked
            act_obj = bpy.context.active_object
            
            selection = bpy.context.selected_objects
            selection.remove(act_obj)
            
            if len(selection) > 1:
                raise TypeError("ERROR: more than one source object selected")
                return {"FINISHED"}
            
            sel_obj = selection[0]
            
            print("src obj: " + sel_obj.name)
            print("src channel: " + self.src_chan)
            print("dest obj: " + act_obj.name)
            print("dest channel: " + self.dst_chan)
            
            # check to make sure the two objects have the same number of vertices
            if len(act_obj.data.vertices) != len(sel_obj.data.vertices):
                raise TypeError("ERROR: Objects do not have the same number of vertices")
                return {'FINISHED'}
            
            # access color attributes
            # this just grabs the first one. how can i grab the active one?
            src_color_attr = sel_obj.data.color_attributes[0].data
            dst_color_attr = act_obj.data.color_attributes[0].data
            
            # cast to int
            src_chan = int(self.src_chan)
            dst_chan = int(self.dst_chan)
            
            # copy values from channel "src" to channel "dst"
            for src_attr, dst_attr in zip(src_color_attr,dst_color_attr):
                src_color = src_attr.color_srgb
                dst_color = dst_attr.color_srgb
                dst_color[dst_chan] = src_color[src_chan]
                
        print("VColorCopy script finished in %.4f sec" % (time.time() - time_start))
        return {'FINISHED'}

def menu_func(self, context):
    self.layout.operator(CreateLOD.bl_idname)
    self.layout.operator(CreateCollision.bl_idname)
    self.layout.operator(SyncNames.bl_idname)
    self.layout.operator(VColorCopy.bl_idname)

# store keymaps here to access after registration
addon_keymaps = []

def register():
    bpy.utils.register_class(CreateLOD)
    bpy.utils.register_class(CreateCollision)
    bpy.utils.register_class(SyncNames)
    bpy.utils.register_class(VColorCopy)
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
        
        km = wm.keyconfigs.addon.keymaps.new(name='Object Mode', space_type='EMPTY')
        kmi = km.keymap_items.new(VColorCopy.bl_idname, 'V', 'PRESS', ctrl=True, alt=True)
        addon_keymaps.append((km, kmi))

def unregister():
    # handle the keymap
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()

    bpy.utils.unregister_class(CreateLOD)
    bpy.utils.unregister_class(CreateCollision)
    bpy.utils.unregister_class(SyncNames)
    bpy.utils.unregister_class(VColorCopy)
    bpy.types.VIEW3D_MT_object.remove(menu_func)

if __name__ == "__main__":
    register()
