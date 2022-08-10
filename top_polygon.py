import random

import bpy

from bpy.types import Mesh

bl_info = {
    'name': 'Top Polygon',
    'blender': (2, 80, 0),
    'category': 'Object',
    'author': 'Zenker'
}


def update(self, context):
    scene = context.scene

    b = context.scene.top_object[context.scene.top_object_active]
    bpy.ops.object.select_all(action='DESELECT')

    ob = bpy.data.objects[b.name]
    bpy.context.view_layer.objects.active = ob
    ob.select_set(True)


class TopObject(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty()
    polycount: bpy.props.IntProperty(default=0)


class TopSettings(bpy.types.PropertyGroup):
    modify: bpy.props.BoolProperty(default=True)


class BasePanel:
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'TOP'
    bl_context = 'objectmode'


class TOP_UL_top_props(bpy.types.UIList):

    def filter_items(self, context, data, propname):
        helper_funcs = bpy.types.UI_UL_list

        o = getattr(data, propname).values()

        ordered = [(index, item.polycount) for index, item in enumerate(o)]
        ordered = helper_funcs.sort_items_helper(ordered, lambda e: e[1], True)

        return [], ordered

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            row = layout.row()
            row.label(text=item.name)
            row.label(text=str(item.polycount))


class TOP_OT_top(bpy.types.Operator):
    bl_idname: str = 'top.calc_top'
    bl_label: str = 'Calc top'
    count: bpy.props.IntProperty()

    def calc_count(self, context, count):
        scene = context.scene
        scene.top_object.clear()
        dg = context.evaluated_depsgraph_get()

        for i in bpy.data.objects:
            if not isinstance(i.data, Mesh):
                continue

            if scene.top_settings.modify:
                i = i.evaluated_get(dg)

            item = scene.top_object.add()
            item.name = i.name
            counter = 0
            for p in i.data.polygons:
                if len(p.vertices) == self.count:
                    counter += 1

            item.polycount = counter

    def calc_polygon(self, context):
        scene = context.scene
        scene.top_object.clear()
        dg = context.evaluated_depsgraph_get()

        for i in bpy.data.objects:
            if not isinstance(i.data, Mesh):
                continue

            if scene.top_settings.modify:
                i = i.evaluated_get(dg)

            item = scene.top_object.add()
            item.name = i.name
            item.polycount = len(i.data.polygons)

    def execute(self, context: bpy.types.Context):
        self.calc_count(context, self.count)
        return {'FINISHED'}


class TOP_PT_object_list(BasePanel, bpy.types.Panel):
    bl_label = 'Топ'

    def draw(self, context):
        scene = context.scene
        layout = self.layout
        layout.prop(scene.top_settings, 'modify', text='Учесть Модификаторы')
        layout.template_list('TOP_UL_top_props', '',
                             scene, 'top_object', scene, 'top_object_active')

        o = layout.operator(TOP_OT_top.bl_idname,
                            text='Посчитать Треугольники')
        o.count = 3

        o = layout.operator(TOP_OT_top.bl_idname,
                            text='Посчитать Полигоны')
        o.count = 4


reg, unreg = bpy.utils.register_classes_factory((
    TOP_OT_top,
    TOP_PT_object_list,
    TOP_UL_top_props,
    TopObject,
    TopSettings
))


def register():
    reg()
    bpy.types.Scene.top_settings = bpy.props.PointerProperty(type=TopSettings)
    bpy.types.Scene.top_object = bpy.props.CollectionProperty(type=TopObject)
    bpy.types.Scene.top_object_active = bpy.props.IntProperty(update=update)


def unregister():
    unreg()


if __name__ == '__main__':
    register()
