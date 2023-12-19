#!python

import lx
import modo
import math
import lxifc
import lxu.attributes

class Cage_Tool(lxifc.Tool, lxifc.Command, lxifc.ToolModel, lxu.attributes.DynamicAttributes, lx.object.Item):
    """
    This tool duplicates the current layer, offsets polygons and applies a transparent material. Works with hauling. 
    """
    def __init__(self):
        lxu.attributes.DynamicAttributes.__init__(self)

        # Add Dynamic Attributes and set init values
        self.dyna_Add('offset', lx.symbol.sTYPE_FLOAT)
        self.dyna_Add('smooth_angle', lx.symbol.sTYPE_ANGLE)
        self.dyna_Add('transparency', lx.symbol.sTYPE_PERCENT)
        self.dyna_Add('color', lx.symbol.sTYPE_COLOR)
        self.attr_SetFlt(0,0.0)
        self.attr_SetFlt(1,180.0)
        self.attr_SetFlt(2,0.75)
        self.attr_SetString(3, "0.0 0.2 0.0")

        pkt_svc = lx.service.Packet()
        self.vec_type = pkt_svc.CreateVectorType(lx.symbol.sCATEGORY_TOOL)

    def create_mask(self, color = (0.0, 0.2, 0.0), transparency = 0.75):
        scene = modo.Scene()
        mesh = scene.selected[0]
        geo = mesh.geometry

        # Adding a vmap as it fails without one (BUG)
        geo.vmaps.addMap(name='Null')
        scene.select(mesh)
        mask = scene.addItem('mask', name='Cage Mask')
        mat = scene.addMaterial(name='Cage')
        mat.channel('diffCol').set(color)
        mat.channel('tranAmt').set(transparency)
        mask.channel('ptag').set('Cage')

        # Parent the material to the mask
        mat.setParent(mask, index=1)
        # This places the mask item below the base shader in the hierarchy of the Shader Tree
        mask.setParent(scene.renderItem, index=1)
        geo.setMeshEdits()


    def offset_points(self, scale, normals, points):
        new_points = []
        print(points)
        for x in range(0, 3):
            if normals[x] > 0 and points[x] < 0:
                diff = abs((points[x]+(points[x]*(scale))/2) - points[x])
                new_points.append(points[x] + (diff*2))
            elif normals[x] < 0 and points[x] > 0:
                diff = abs((points[x]+(points[x]*(scale))/2) - points[x])
                new_points.append(points[x] - (diff*2))
            else:
                result = (points[x]+(points[x]*(scale))/2)
                new_points.append(result)
                
        return tuple(new_points)

    def tool_Reset(self):
        self.attr_SetFlt(0,0.0)
        self.attr_SetFlt(1,180.0)
        self.attr_SetFlt(2,0.75)
        self.attr_SetString(3, "0.0 0.2 0.0")

    def tool_Evaluate(self, vts):
        # Grab attributes
        offset = self.attr_GetFlt(0)
        angle = self.attr_GetFlt(1)
        transparency = self.attr_GetFlt(2)
        color = self.attr_GetString(3)
        rgb = tuple(map(float, color.split(' ')))
        self.create_mask(rgb, transparency)

        # Setup Layer Scan for Mesh Edit
        layer_svc = lx.service.Layer()
        layer_scan = lx.object.LayerScan(layer_svc.ScanAllocate(lx.symbol.f_LAYERSCAN_EDIT))

        og_mesh_loc = lx.object.Mesh(layer_scan.MeshEdit(0)) # Current Mesh
        og_point_loc = lx.object.Point(og_mesh_loc.PointAccessor())

        normals = []
        for i in range(0, og_mesh_loc.PointCount()):
            og_point_loc.SelectByIndex(i)
            normals.append(og_point_loc.Normal(0))
	
        layer_scan.SetMeshChange(0, lx.symbol.f_MESHEDIT_GEOMETRY)
        lx.eval("item.duplicate false locator false true")

        mesh_loc = lx.object.Mesh(layer_scan.MeshEdit(0))
        point_loc = lx.object.Point(mesh_loc.PointAccessor())
        poly_loc = lx.object.Polygon(mesh_loc.PolygonAccessor())

        for i in range(0, mesh_loc.PointCount()):
            point_loc.SelectByIndex(i)
            point_pos = point_loc.Pos()
            normal = normals[i]
            point_loc.SetPos(self.offset_points(offset, normal, point_pos))

        poly_count = mesh_loc.PolygonCount()
        for id in reversed(range(0, poly_count)):
            poly_loc.SelectByIndex(id)
            loc = lx.object.StringTag(poly_loc)
            loc.Set(lx.symbol.i_POLYTAG_MATERIAL, 'Cage')

        layer_scan.SetMeshChange(0, lx.symbol.f_MESHEDIT_GEOMETRY)
        layer_scan.Apply()

    def tool_VectorType(self):
        return self.vec_type

    def tool_Order(self):
        return lx.symbol.s_ORD_ACTR

    def tool_Task(self):
        return lx.symbol.i_TASK_ACTR

    def tmod_Flags(self):
        '''
            This sets how we intend to interact with the tool. The symbol
            "fTMOD_I0_ATTRHAUL" basically says that we expect to haul an
            attribute when clicking and dragging with the left mouse button.
        '''
        return lx.symbol.fTMOD_I0_ATTRHAUL

    def tmod_Initialize(self,vts,adjust,flags):
        '''
            This is called when the tool is activated. We use it to simply
            set the attribute that we hauling back to the default.
        '''
        adj_tool = lx.object.AdjustTool(adjust)
        adj_tool.SetFlt(0, 0.0)

    def tmod_Haul(self,index):
        '''
            Hauling is dependent on the direction of the haul. So a vertical
            haul can drive a different parameter to a horizontal haul. The
            direction of the haul is represented by an index, with 0
            representing horizontal and 1 representing vertical. The function
            simply returns the name of the attribute to drive, given it's index.
            As we only have one attribute, we'll set horizontal hauling to
            control it and vertical hauling to do nothing.
        '''
        if index == 0:
            return "offset"
        else:
            return 0
    
lx.bless(Cage_Tool, "quick.cage")