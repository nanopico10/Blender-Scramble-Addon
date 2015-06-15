# 「プロパティ」エリア > 「オブジェクト」タブ

import bpy

################
# オペレーター #
################

class CopyObjectName(bpy.types.Operator):
	bl_idname = "object.copy_object_name_2"
	bl_label = "オブジェクト名をコピー"
	bl_description = "オブジェクト名をクリップボードにコピーします"
	bl_options = {'REGISTER'}
	
	@classmethod
	def poll(cls, context):
		if (not context.object):
			return False
		return True
	def execute(self, context):
		context.window_manager.clipboard = context.object.name
		self.report(type={'INFO'}, message=context.object.name)
		return {'FINISHED'}

class DataNameToObjectName(bpy.types.Operator):
	bl_idname = "object.data_name_to_object_name"
	bl_label = "オブジェクト名をデータ名に"
	bl_description = "オブジェクト名をリンクしているデータ名に設定します"
	bl_options = {'REGISTER', 'UNDO'}
	
	@classmethod
	def poll(cls, context):
		if (not context.object):
			return False
		if (not context.object.data):
			return False
		return True
	def execute(self, context):
		context.object.name = context.object.data.name
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
		row.operator(CopyObjectName.bl_idname, icon='PLUGIN', text="名前をコピー")
		row.operator(DataNameToObjectName.bl_idname, icon='PLUGIN', text="名前をデータ名に")
	if (context.user_preferences.addons["Scramble Addon"].preferences.use_disabled_menu):
		self.layout.operator('wm.toggle_menu_enable', icon='CANCEL').id = __name__.split('.')[-1]
