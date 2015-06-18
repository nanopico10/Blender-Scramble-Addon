# メッシュオブジェクト > 「プロパティ」エリア > 「データ」タブ

import bpy

################
# オペレーター #
################

class CopyMeshDataName(bpy.types.Operator):
	bl_idname = "object.copy_mesh_data_name"
	bl_label = "データ名をコピー"
	bl_description = "データ名をクリップボードにコピーします"
	bl_options = {'REGISTER'}
	
	@classmethod
	def poll(cls, context):
		if (not context.object):
			return False
		if (not context.object.data):
			return False
		return True
	def execute(self, context):
		context.window_manager.clipboard = context.object.data.name
		self.report(type={'INFO'}, message=context.object.data.name)
		return {'FINISHED'}

class ObjectNameToDataName(bpy.types.Operator):
	bl_idname = "object.object_name_to_data_name"
	bl_label = "データ名をオブジェクト名に"
	bl_description = "データ名をリンクしているオブジェクト名に設定します"
	bl_options = {'REGISTER', 'UNDO'}
	
	@classmethod
	def poll(cls, context):
		if (not context.object):
			return False
		if (not context.object.data):
			return False
		return True
	def execute(self, context):
		context.object.data.name = context.object.name
		return {'FINISHED'}

################
# メニュー追加 #
################

# メニューのオン/オフの判定
def IsMenuEnable(self_id):
	for id in bpy.context.user_preferences.addons["Scramble Addon"].preferences.disabled_menu.split(','):
		if (id == self_id):
			return False
	else:
		return True

# メニューを登録する関数
def menu(self, context):
	if (IsMenuEnable(__name__.split('.')[-1])):
		row = self.layout.row(align=True)
		row.operator(CopyMeshDataName.bl_idname, icon='PLUGIN', text="名前をコピー")
		row.operator(ObjectNameToDataName.bl_idname, icon='PLUGIN', text="名前をオブジェクト名に")
	if (context.user_preferences.addons["Scramble Addon"].preferences.use_disabled_menu):
		self.layout.operator('wm.toggle_menu_enable', icon='CANCEL').id = __name__.split('.')[-1]