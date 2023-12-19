#!python

import lx
import modo
import math
import lxifc
import lxu.attributes

class Balloon_Tool(lxifc.Tool, lxifc.Command, lxifc.ToolModel, lxu.attributes.DynamicAttributes, lx.object.Item):
"""
Simple python tool to 'inflate' target geometry, works with hauling.
"""
    def __init__(self):
        lxu.attributes.DynamicAttributes.__init__(self)
        self.dyna_Add('distance', lx.symbol.sTYPE_FLOAT)
        self.dyna_Add('strength', lx.symbol.sTYPE_FLOAT)

        self.attr_SetFlt(0,1.0)
        self.attr_SetFlt(1,0.0)
        self.scene = modo.Scene()
        pkt_svc = lx.service.Packet()
        self.vec_type = pkt_svc.CreateVectorType(lx.symbol.sCATEGORY_TOOL)

    def tool_Reset(self):
        self.attr_SetFlt(0, 1.0)
        self.attr_SetFlt(1, 0.0)

    def tool_Evaluate(self,vts):
        target_dist = self.attr_GetFlt(0)
        strength = self.attr_GetFlt(1)

        layer_svc = lx.service.Layer()
        layer_scan = lx.object.LayerScan(layer_svc.ScanAllocate(lx.symbol.f_LAYERSCAN_EDIT_VERTS))

        for n in range(0, layer_scan.Count()):
            mesh_loc = lx.object.Mesh(layer_scan.MeshEdit(n))

            mesh_bounds = mesh_loc.BoundingBox(lx.symbol.iMARK_ANY)
            mesh_center = ((mesh_bounds[0][0]+mesh_bounds[1][0])/2,(mesh_bounds[0][1]+mesh_bounds[1][1])/2,(mesh_bounds[0][2]+mesh_bounds[1][2])/2)

            for i in range(0, mesh_loc.PointCount()):

                point_loc = lx.object.Point(mesh_loc.PointAccessor())
                point_loc.SelectByIndex(i)

                point_pos = point_loc.Pos()
                #lx.out(strength)
                point_dist = (math.sqrt(math.pow((point_pos[0]-mesh_center[0]),(2))+math.pow((point_pos[1]-mesh_center[1]),(2))+math.pow((point_pos[2]-mesh_center[2]),(2))))
                lx.out(point_dist)

                scale = target_dist / point_dist
                point_newPos = ((point_pos[0]*scale),(point_pos[1]*scale),(point_pos[2]*scale))
                point_diff = ((point_newPos[0] - point_pos[0])*strength, (point_newPos[1] - point_pos[1])*strength, (point_newPos[2] - point_pos[2])*strength)
                new_points = ((point_diff[0] + point_pos[0]), (point_diff[1] + point_pos[1]), (point_diff[2] + point_pos[2]))

                point_loc.SetPos(new_points)

            layer_scan.SetMeshChange(n, lx.symbol.f_MESHEDIT_POINTS)

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
        adj_tool.SetFlt(1, 0.0)

    def tmod_Haul(self,index):
        if index == 0:
            return "strength"
        else:
            return 0
    
lx.bless(Balloon_Tool, "inflate")