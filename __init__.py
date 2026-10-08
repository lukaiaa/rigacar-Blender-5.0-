# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 3
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

bl_info = {
    "name": "Rigacar",
    "author": "David Gayerie (fix by Mister Guide, patched for Blender 5.1.2)",
    "version": (1, 0, 4),
    "blender": (5, 0, 0),
    "location": "View3D > Add > Armature > Car (deformation rig)",
    "description": "Rigging, animation controls and baking tools for wheeled vehicles",
    "warning": "",
    "doc_url": "https://digicreatures.net/articles/rigacar.html",
    "category": "Rigging",
}

import bpy

if "bake_operators" in locals():
    import importlib
    importlib.reload(bake_operators)
    importlib.reload(car_rig)
    importlib.reload(widgets)
else:
    from . import bake_operators
    from . import car_rig
    from . import widgets


translations_dict = {
    "ru_RU": {
        ("*", "Rigacar"): "Rigacar",
        ("*", "Animation Rig"): "Риг анимации",
        ("*", "Wheels animation"): "Анимация колёс",
        ("*", "Ground Sensors"): "Датчики поверхности",
        ("*", "Ground projection"): "Проекция на поверхность",
        ("*", "Ground projection limitation"): "Ограничение проекции на поверхность",
        ("*", "Wheels on Y axis"): "Вращение колёс по оси Y",
        ("*", "Pitch factor"): "Фактор наклона (Pitch)",
        ("*", "Roll factor"): "Фактор крена (Roll)",
        ("*", "Ground"): "Поверхность",
        ("*", "Min local Z"): "Мин. локальный Z",
        ("*", "Max local Z"): "Макс. локальный Z",
        ("*", "Generate"): "Сгенерировать",
        ("*", "Car (deformation rig)"): "Автомобиль (деформационный риг)",
        ("*", "Add car deformation rig"): "Создать деформационный риг автомобиля",
        ("*", "Creates the base rig for a car."): "Создает базовый деформационный скелет для автомобиля.",
        ("*", "Generate car animation rig"): "Сгенерировать анимационный риг автомобиля",
        ("*", "Creates the complete armature for animating the car."): "Создает полную систему костей и элементов управления для анимации автомобиля.",
        ("*", "Bake wheels rotation"): "Запечь вращение колёс",
        ("*", "Automatically generates wheels animation based on Root bone animation."): "Автоматически рассчитывает и запекает вращение колёс на основе движения корневой кости (Root).",
        ("*", "Bake car steering"): "Запечь поворот руля",
        ("*", "Automatically generates steering animation based on Root bone animation."): "Автоматически рассчитывает и запекает поворот передних колёс и руля на основе траектории корневой кости.",
        ("*", "Clear baked animation"): "Очистить запечённую анимацию",
        ("*", "Clear generated rotation for steering and wheels"): "Очистить сгенерированные ключевые кадры для руля и вращения колёс.",
        ("*", "Add missing brake wheel bones"): "Добавить недостающие кости тормозов",
        ("*", "Generates missing brake wheel bones for each selected wheel widget."): "Генерирует недостающие кости тормозных суппортов для выбранных виджетов колёс.",
        ("*", "Start Frame"): "Начальный кадр",
        ("*", "End Frame"): "Конечный кадр",
        ("*", "Keyframe tolerance"): "Допуск ключевых кадров",
        ("*", "Rotation factor"): "Фактор поворота",
        ("*", "Clear generated keyframes for"): "Очистить ключевые кадры для:",
        ("*", "Steering"): "Рулевое управление",
        ("*", "Wheels"): "Колёса",
        ("*", "Body"): "Кузов",
        ("*", "Front wheels"): "Передние колёса",
        ("*", "Back wheels"): "Задние колёса",
        ("*", "Brakes"): "Тормоза",
        ("*", "Pairs"): "Пары",
        ("*", "Front Pairs"): "Передние пары",
        ("*", "Back Pairs"): "Задние пары",
        ("*", "Delta Location"): "Смещение позиции",
        ("*", "Front Delta Location"): "Переднее смещение",
        ("*", "Back Delta Location"): "Заднее смещение",
        ("*", "Number of front wheels pairs"): "Количество пар передних колёс",
        ("*", "Number of back wheels pairs"): "Количество пар задних колёс",
        ("*", "Number of front wheel brakes pairs"): "Количество пар передних тормозов",
        ("*", "Number of back wheel brakes pairs"): "Количество пар задних тормозов",
        ("*", "Extra translation added to location of the car body"): "Дополнительное смещение для кузова автомобиля",
        ("*", "Extra translation added to location of the front wheels"): "Дополнительное смещение для передних колёс",
        ("*", "Extra translation added to location of the back wheels"): "Дополнительное смещение для задних колёс",
        ("*", "Extra translation added to location of the front brakes"): "Дополнительное смещение для передних тормозов",
        ("*", "Extra translation added to location of the back brakes"): "Дополнительное смещение для задних тормозов",
        ("*", "Move origin"): "Переместить Origin",
        ("*", "Set origin of the armature at the same location as the root bone"): "Установить точку отсчета (Origin) скелета в позицию корневой кости Root",
        ("*", "Rig already generated"): "Риг уже сгенерирован",
        ("*", "No bone named DEF-Body. This is not a valid armature!"): "Кость DEF-Body не найдена. Это некорректный скелет!",
        ("*", "Cannot edit the new armature! Please make sure the active collection is visible and editable"): "Невозможно редактировать новый скелет! Убедитесь, что активная коллекция видима и доступна для редактирования.",
        ("*", "Activate wheels rotation when moving the root bone along the Y axis"): "Активировать вращение колёс при перемещении корневой кости вдоль оси Y",
        ("*", "Influence of the dampers over the pitch of the body"): "Влияние амортизаторов на продольный наклон кузова (Pitch)",
        ("*", "Influence of the dampers over the roll of the body"): "Влияние амортизаторов на поперечный крен кузова (Roll)",
        ("*", "Animation property for wheel spinning"): "Анимационное свойство для вращения колеса",
        ("*", "Animation property for steering"): "Анимационное свойство для поворота руля",
    }
}


def enumerate_ground_sensors(bones):
    bone = bones.get('GroundSensor.Axle.Ft')
    if bone is not None:
        yield bone
        for b in bones:
            if b.name.startswith('GroundSensor.Ft'):
                yield b
    bone = bones.get('GroundSensor.Axle.Bk')
    if bone is not None:
        yield bone
        for b in bones:
            if b.name.startswith('GroundSensor.Bk'):
                yield b


class RIGACAR_PT_mixin:

    def __init__(self):
        self.layout.use_property_split = True
        self.layout.use_property_decorate = False

    @classmethod
    def is_car_rig(cls, context):
        return (context.object is not None and
                context.object.data is not None and
                'Car Rig' in context.object.data)

    @classmethod
    def is_car_rig_generated(cls, context):
        return cls.is_car_rig(context) and context.object.data.get('Car Rig', False)

    def display_generate_section(self, context):
        self.layout.operator(car_rig.POSE_OT_carAnimationRigGenerate.bl_idname, text='Generate')

    def display_bake_section(self, context):
        self.layout.operator(bake_operators.ANIM_OT_carSteeringBake.bl_idname)
        self.layout.operator(bake_operators.ANIM_OT_carWheelsRotationBake.bl_idname)
        self.layout.operator(bake_operators.ANIM_OT_carClearSteeringWheelsRotation.bl_idname)

    def display_rig_props_section(self, context):
        layout = self.layout.column()
        layout.prop(context.object, '["wheels_on_y_axis"]', text="Wheels on Y axis")
        layout.prop(context.object, '["suspension_factor"]', text="Pitch factor")
        layout.prop(context.object, '["suspension_rolling_factor"]', text="Roll factor")

    def display_ground_sensors_section(self, context):
        for ground_sensor in enumerate_ground_sensors(context.object.pose.bones):
            ground_projection_constraint = ground_sensor.constraints.get('Ground projection')
            self.layout.label(text=ground_sensor.name, icon='BONE_DATA')
            if ground_projection_constraint is not None:
                self.layout.prop(ground_projection_constraint, 'target', text='Ground')
                if ground_projection_constraint.target is not None:
                    self.layout.prop(ground_projection_constraint, 'shrinkwrap_type')
                    if ground_projection_constraint.shrinkwrap_type == 'PROJECT':
                        self.layout.prop(ground_projection_constraint, 'project_limit')
                    self.layout.prop(ground_projection_constraint, 'influence')
            ground_projection_limit_constraint = ground_sensor.constraints.get('Ground projection limitation')
            if ground_projection_limit_constraint is not None:
                self.layout.prop(ground_projection_limit_constraint, 'min_z', text='Min local Z')
                self.layout.prop(ground_projection_limit_constraint, 'max_z', text='Max local Z')
            self.layout.separator()


class RIGACAR_PT_rigProperties(bpy.types.Panel, RIGACAR_PT_mixin):
    bl_label = "Rigacar"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "data"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return RIGACAR_PT_mixin.is_car_rig(context)

    def draw(self, context):
        if RIGACAR_PT_mixin.is_car_rig_generated(context):
            self.display_rig_props_section(context)
            self.layout.separator()
            self.display_bake_section(context)
        else:
            self.display_generate_section(context)


class RIGACAR_PT_groundSensorsProperties(bpy.types.Panel, RIGACAR_PT_mixin):
    bl_label = "Ground Sensors"
    bl_parent_id = "RIGACAR_PT_rigProperties"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "data"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return RIGACAR_PT_mixin.is_car_rig_generated(context)

    def draw(self, context):
        self.display_ground_sensors_section(context)


class RIGACAR_PT_animationRigView(bpy.types.Panel, RIGACAR_PT_mixin):
    bl_category = "Rigacar"
    bl_label = "Animation Rig"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

    @classmethod
    def poll(cls, context):
        return RIGACAR_PT_mixin.is_car_rig(context)

    def draw(self, context):
        if RIGACAR_PT_mixin.is_car_rig_generated(context):
            self.display_rig_props_section(context)
        else:
            self.display_generate_section(context)


class RIGACAR_PT_wheelsAnimationView(bpy.types.Panel, RIGACAR_PT_mixin):
    bl_category = "Rigacar"
    bl_label = "Wheels animation"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

    @classmethod
    def poll(cls, context):
        return RIGACAR_PT_mixin.is_car_rig_generated(context)

    def draw(self, context):
        self.display_bake_section(context)


class RIGACAR_PT_groundSensorsView(bpy.types.Panel, RIGACAR_PT_mixin):
    bl_category = "Rigacar"
    bl_label = "Ground Sensors"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return RIGACAR_PT_mixin.is_car_rig_generated(context)

    def draw(self, context):
        self.display_ground_sensors_section(context)


def menu_entries(menu, context):
    menu.layout.operator(car_rig.OBJECT_OT_armatureCarDeformationRig.bl_idname, text="Car (deformation rig)", icon='AUTO')


classes = (
    RIGACAR_PT_rigProperties,
    RIGACAR_PT_groundSensorsProperties,
    RIGACAR_PT_animationRigView,
    RIGACAR_PT_wheelsAnimationView,
    RIGACAR_PT_groundSensorsView,
)


def register():
    try:
        bpy.app.translations.register(__name__, translations_dict)
    except Exception:
        pass

    if menu_entries not in bpy.types.VIEW3D_MT_armature_add._dyn_ui_initialize():
        bpy.types.VIEW3D_MT_armature_add.append(menu_entries)

    for c in classes:
        try:
            bpy.utils.register_class(c)
        except ValueError:
            pass
    car_rig.register()
    bake_operators.register()


def unregister():
    bake_operators.unregister()
    car_rig.unregister()
    for c in classes:
        bpy.utils.unregister_class(c)
    bpy.types.VIEW3D_MT_armature_add.remove(menu_entries)

    try:
        bpy.app.translations.unregister(__name__)
    except Exception:
        pass


if __name__ == "__main__":
    register()
