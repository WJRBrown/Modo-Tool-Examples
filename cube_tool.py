#!python

import lx
import modo
import math
import lxifc
import lxu.attributes

class Cube_Tool(lxifc.Tool, lxifc.Command, lxifc.ToolModel, lxu.attributes.DynamicAttributes, lx.object.Item):
"""
Simple python tool to create a Cube with hauling to adjust the size
"""
    def __init__(self):
        lxu.attributes.DynamicAttributes.__init__(self)

        # Add Dynamic Attribute 'size' of type float + set default value to 1.0
        self.dyna_Add('size', lx.symbol.sTYPE_FLOAT)
        self.attr_SetFlt(0,1.0)
        self.scene = modo.Scene()


        # Cube vert positions
        self.vertices = [
            (-0.5, -0.5, -0.5), # 0
            (-0.5, -0.5,  0.5), # 1
            ( 0.5, -0.5, -0.5), # 2
            ( 0.5, -0.5,  0.5), # 3
            (-0.5,  0.5, -0.5), # 4
            (-0.5,  0.5,  0.5), # 5
            ( 0.5,  0.5, -0.5), # 6
            ( 0.5,  0.5,  0.5), # 7
        ]

        # Polygon vert order
        self.polygons = [
            (0, 2, 3, 1), # -Y
            (4, 5, 7, 6), # +Y
            (2, 6, 7, 3), # +X
            (0, 1, 5, 4), # -X
            (1, 3, 7, 5), # +Z
            (0, 4, 6, 2)  # -Z
        ]

        pkt_svc = lx.service.Packet()
        self.vec_type = pkt_svc.CreateVectorType(lx.symbol.sCATEGORY_TOOL)

    def tool_Reset(self):
        self.attr_SetFlt(0, 1.0)

    def tool_Evaluate(self,vts):
        # Grab size attribute
        size = self.attr_GetFlt(0)

        # Setup Layer Scan for Mesh Edit
        layer_svc = lx.service.Layer()
        layer_scan = lx.object.LayerScan(layer_svc.ScanAllocate(lx.symbol.f_LAYERSCAN_EDIT))

        # Access and create points
        mesh_loc = lx.object.Mesh(layer_scan.MeshEdit(0)) # Current Mesh
        point_loc = lx.object.Point(mesh_loc.PointAccessor())
        poly_loc = lx.object.Polygon(mesh_loc.PolygonAccessor())
        points = ()
        for vert in self.vertices:
            vert = tuple([size*x for x in vert]) #Applying scale to verts
            new_point = point_loc.New(vert)
            points = points + (new_point,)

        # Setup Point Storage for polygon
        points_storage = lx.object.storage()
        points_storage.setType('p')

        # Loop through polygon order tuple and create polygons
        for poly in self.polygons:
            polys = (points[poly[0]],points[poly[1]],points[poly[2]],points[poly[3]])
            points_storage.setSize(len(self.vertices))
            points_storage.set(polys)
            poly_loc.New(lx.symbol.iPTYP_FACE,points_storage,4,0)

        # Apply Mesh Edits and cleanup Layer Scan obj
        lx.out(size)
        layer_scan.SetMeshChange(0, lx.symbol.f_MESHEDIT_GEOMETRY)
        layer_scan.Apply()

    def tool_VectorType(self):
        return self.vec_type

    def tool_Order(self):
        return lx.symbol.s_ORD_ACTR

    def tool_Task(self):
        return lx.symbol.i_TASK_ACTR
    
    def tmod_Flags(self):
        return lx.symbol.fTMOD_I0_ATTRHAUL

    def tmod_Initialize(self,vts,adjust,flags):
        adj_tool = lx.object.AdjustTool(adjust)
        adj_tool.SetFlt(0, 1.0)

    def tmod_Haul(self,index):
        # 0 index represents horizontal haul
        if index == 0:
            return "size"
        else:
            return 0
    
lx.bless(Cube_Tool, "py.cube")