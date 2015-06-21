# UV/画像エディター > 「画像」メニュー

import bpy
import os, numpy

################
# オペレーター #
################

class RenameImageFileName(bpy.types.Operator):
	bl_idname = "image.rename_image_file_name"
	bl_label = "画像名を使用するファイル名に"
	bl_description = "アクティブな画像の名前を、使用している外部画像のファイル名にします"
	bl_options = {'REGISTER', 'UNDO'}
	
	isExt = bpy.props.BoolProperty(name="拡張子も含む", default=True)
	
	@classmethod
	def poll(cls, context):
		if (not context.edit_image):
			return False
		if (context.edit_image.filepath == ""):
			return False
		return True
	def invoke(self, context, event):
		wm = context.window_manager
		return wm.invoke_props_dialog(self)
	def execute(self, context):
		img = context.edit_image
		name = bpy.path.basename(img.filepath_raw)
		if (not self.isExt):
			name, ext = os.path.splitext(name)
		try:
			img.name = name
		except: pass
		return {'FINISHED'}

class AllRenameImageFileName(bpy.types.Operator):
	bl_idname = "image.all_rename_image_file_name"
	bl_label = "全ての画像名を使用するファイル名に"
	bl_description = "全ての画像の名前を、使用している外部画像のファイル名にします"
	bl_options = {'REGISTER', 'UNDO'}
	
	isExt = bpy.props.BoolProperty(name="拡張子も含む", default=True)
	
	@classmethod
	def poll(cls, context):
		if (len(bpy.data.images) <= 0):
			return False
		for img in bpy.data.images:
			if (img.filepath != ""):
				return True
		return False
	def execute(self, context):
		for img in  bpy.data.images:
			name = bpy.path.basename(img.filepath_raw)
			if (not self.isExt):
				name, ext = os.path.splitext(name)
			try:
				img.name = name
			except: pass
		return {'FINISHED'}

class ReloadAllImage(bpy.types.Operator):
	bl_idname = "image.reload_all_image"
	bl_label = "全ての画像を再読み込み"
	bl_description = "外部ファイルを参照している画像データを全て読み込み直します"
	bl_options = {'REGISTER', 'UNDO'}
	
	@classmethod
	def poll(cls, context):
		if (len(bpy.data.images) <= 0):
			return False
		for img in bpy.data.images:
			if (img.filepath != ""):
				return True
		return False
	def execute(self, context):
		for img in bpy.data.images:
			if (img.filepath != ""):
				img.reload()
				try:
					img.update()
				except RuntimeError:
					pass
		for area in context.screen.areas:
			area.tag_redraw()
		return {'FINISHED'}

class FillColor(bpy.types.Operator):
	bl_idname = "image.fill_color"
	bl_label = "指定色で塗り潰し"
	bl_description = "アクティブな画像を指定した色で全て塗り潰します"
	bl_options = {'REGISTER', 'UNDO'}
	
	color = bpy.props.FloatVectorProperty(name="色", description="塗り潰す色", default=(1, 1, 1), min=0, max=1, soft_min=0, soft_max=1, step=10, precision=3, subtype='COLOR')
	alpha = bpy.props.FloatProperty(name="透明度", description="透明度", default=1, min=0, max=1, soft_min=0, soft_max=1, step=10, precision=3)
	
	@classmethod
	def poll(cls, context):
		if (not context.edit_image):
			return False
		if (len(context.edit_image.pixels) <= 0):
			return False
		return True
	def invoke(self, context, event):
		wm = context.window_manager
		return wm.invoke_props_dialog(self)
	def execute(self, context):
		img = context.edit_image
		pixel = list(self.color[:])
		if (4 <= img.channels):
			pixel.append(self.alpha)
		img.pixels = pixel * (img.size[0] * img.size[1])
		for area in context.screen.areas:
			area.tag_redraw()
		return {'FINISHED'}

class FillTransparency(bpy.types.Operator):
	bl_idname = "image.fill_transparency"
	bl_label = "透明部分を塗り潰し"
	bl_description = "アクティブな画像の透明部分を指定色で塗り潰します"
	bl_options = {'REGISTER', 'UNDO'}
	
	color = bpy.props.FloatVectorProperty(name="埋める色", default=(1, 1, 1), min=0, max=1, soft_min=0, soft_max=1, step=10, precision=3, subtype='COLOR')
	
	@classmethod
	def poll(cls, context):
		if (not context.edit_image):
			return False
		if (len(context.edit_image.pixels) <= 0):
			return False
		if (context.edit_image.channels < 4):
			return False
		return True
	def invoke(self, context, event):
		return context.window_manager.invoke_props_dialog(self)
	def execute(self, context):
		img = context.edit_image
		color = self.color[:]
		img_width, img_height, img_channel = img.size[0], img.size[1], img.channels
		pixels = numpy.array(img.pixels).reshape(img_height, img_width, img_channel)
		for y in range(img_height):
			for x in range(img_width):
				alpha = pixels[y][x][3]
				unalpha = 1 - alpha
				pixels[y][x][0] = (pixels[y][x][0] * alpha) + (color[0] * unalpha)
				pixels[y][x][1] = (pixels[y][x][1] * alpha) + (color[1] * unalpha)
				pixels[y][x][2] = (pixels[y][x][2] * alpha) + (color[2] * unalpha)
				pixels[y][x][3] = 1.0
		img.pixels = pixels.flatten()
		for area in context.screen.areas:
			area.tag_redraw()
		return {'FINISHED'}

class Normalize(bpy.types.Operator):
	bl_idname = "image.normalize"
	bl_label = "画像の正規化"
	bl_description = "アクティブな画像を正規化します"
	bl_options = {'REGISTER', 'UNDO'}
	
	@classmethod
	def poll(cls, context):
		if (not context.edit_image):
			return False
		if (len(context.edit_image.pixels) <= 0):
			return False
		return True
	def execute(self, context):
		img = context.edit_image
		img_width, img_height, img_channel = img.size[0], img.size[1], img.channels
		pixels = numpy.array(img.pixels).reshape(img_height, img_width, img_channel)
		rs = pixels[:,:,0]
		gs = pixels[:,:,1]
		bs = pixels[:,:,2]
		values = (rs + gs + bs) / 3
		min = numpy.amin(values)
		max = numpy.amax(values)
		multi = 1 / (max - min)
		for c in range(3):
			pixels[:,:,c] = (pixels[:,:,c] - min) * multi
		img.pixels = pixels.flatten()
		for area in context.screen.areas:
			area.tag_redraw()
		return {'FINISHED'}

class RenameImageFile(bpy.types.Operator):
	bl_idname = "image.rename_image_file"
	bl_label = "画像ファイル名を変更"
	bl_description = "アクティブな画像のファイル名を変更します"
	bl_options = {'REGISTER'}
	
	new_name = bpy.props.StringProperty(name="新しいファイル名")
	
	@classmethod
	def poll(cls, context):
		if (not context.edit_image):
			return False
		if (context.edit_image.filepath == ""):
			return False
		return True
	def invoke(self, context, event):
		self.new_name = bpy.path.basename(context.edit_image.filepath_raw)
		if (self.new_name == ""):
			self.report(type={"ERROR"}, message="この画像には外部ファイルが存在しません")
			return {"CANCELLED"}
		return context.window_manager.invoke_props_dialog(self)
	def execute(self, context):
		pre_filepath = context.edit_image.filepath_raw
		dir = os.path.dirname(bpy.path.abspath(context.edit_image.filepath_raw))
		name = bpy.path.basename(context.edit_image.filepath_raw)
		if (self.new_name == name):
			self.report(type={"ERROR"}, message="画像ファイル名が元と同じです")
			return {"CANCELLED"}
		bpy.ops.image.save_as(filepath=os.path.join(dir, self.new_name))
		context.edit_image.name = self.new_name
		os.remove(bpy.path.abspath(pre_filepath))
		return {'FINISHED'}

# ながとさんに協力して頂きました、感謝！
class BlurImage(bpy.types.Operator):
	bl_idname = "image.blur_image"
	bl_label = "画像をぼかす (重いので注意)"
	bl_description = "アクティブな画像をぼかします"
	bl_options = {'REGISTER', 'UNDO'}
	
	strength = bpy.props.IntProperty(name="ぼかし量", default=10, min=1, max=100, soft_min=1, soft_max=100)
	
	@classmethod
	def poll(cls, context):
		if (not context.edit_image):
			return False
		if (len(context.edit_image.pixels) <= 0):
			return False
		return True
	def invoke(self, context, event):
		return context.window_manager.invoke_props_dialog(self)
	def execute(self, context):
		img = context.edit_image
		if (not img):
			self.report(type={'ERROR'}, message="アクティブな画像が見つかりません")
			return {'CANCELLED'}
		w, h, c = img.size[0], img.size[1], img.channels
		ps = numpy.array(img.pixels)
		lengthes = []
		for i in range(999):
			length = 2 ** i
			lengthes.append(length)
			if (self.strength < sum(lengthes)):
				lengthes[-1] -= sum(lengthes) - self.strength
				if (2 <= len(lengthes)):
					if (lengthes[-1] == 0):
						lengthes = lengthes[:-1]
					elif (lengthes[-1] <= lengthes[-2] / 2):
						lengthes[-2] += lengthes[-1]
						lengthes = lengthes[:-1]
				break
		divisor = 16 ** len(lengthes)
		for length in lengthes:
			for (dx, dy, endX, endY) in [(w*c, c, h, w), (c, w*c, w, h)]:
				for (start, end, sign) in [(0, endX, 1), (endX-1, -1, -1)]:
					dir  = sign * dx
					diff = dir * length
					for y in range(0, dy*endY, dy):
						for x in range(start*dx, end*dx - diff, dir):
							for i in range(y + x, y + x + c):
								ps[i] = ps[i] + ps[i + diff]
						for x in range(end*dx - diff, end*dx, dir):
							for i in range(y + x, y + x + c):
								ps[i] = ps[i] * 2
		for y in range(0, h*w*c, w*c):
			for x in range(0, w*c, c):
				for i in range(y + x, y + x + c):
					ps[i] = ps[i] / divisor
		img.pixels = ps.tolist()
		for area in context.screen.areas:
			area.tag_redraw()
		return {'FINISHED'}

class ReverseWidthImage(bpy.types.Operator):
	bl_idname = "image.reverse_width_image"
	bl_label = "水平反転"
	bl_description = "アクティブな画像を水平方向に反転します"
	bl_options = {'REGISTER', 'UNDO'}
	
	@classmethod
	def poll(cls, context):
		if (not context.edit_image):
			return False
		if (len(context.edit_image.pixels) <= 0):
			return False
		return True
	def execute(self, context):
		img = context.edit_image
		if (not img):
			self.report(type={'ERROR'}, message="アクティブな画像が見つかりません")
			return {'CANCELLED'}
		img_width, img_height, img_channel = img.size[0], img.size[1], img.channels
		pixels = numpy.array(img.pixels).reshape(img_height, img_width, img_channel)
		for i in range(img_height):
			pixels[i] = pixels[i][::-1]
		img.pixels = pixels.flatten()
		for area in context.screen.areas:
			area.tag_redraw()
		return {'FINISHED'}

class ReverseHeightImage(bpy.types.Operator):
	bl_idname = "image.reverse_height_image"
	bl_label = "垂直反転"
	bl_description = "アクティブな画像を垂直方向に反転します"
	bl_options = {'REGISTER', 'UNDO'}
	
	@classmethod
	def poll(cls, context):
		if (not context.edit_image):
			return False
		if (len(context.edit_image.pixels) <= 0):
			return False
		return True
	def execute(self, context):
		img = context.edit_image
		if (not img):
			self.report(type={'ERROR'}, message="アクティブな画像が見つかりません")
			return {'CANCELLED'}
		img_width, img_height, img_channel = img.size[0], img.size[1], img.channels
		pixels = numpy.array(img.pixels).reshape(img_height, img_width, img_channel)
		pixels = pixels[::-1]
		img.pixels = pixels.flatten()
		for area in context.screen.areas:
			area.tag_redraw()
		return {'FINISHED'}

class Rotate180Image(bpy.types.Operator):
	bl_idname = "image.rotate_180_image"
	bl_label = "180°回転"
	bl_description = "アクティブな画像を180°回転します"
	bl_options = {'REGISTER', 'UNDO'}
	
	@classmethod
	def poll(cls, context):
		if (not context.edit_image):
			return False
		if (len(context.edit_image.pixels) <= 0):
			return False
		return True
	def execute(self, context):
		img = context.edit_image
		if (not img):
			self.report(type={'ERROR'}, message="アクティブな画像が見つかりません")
			return {'CANCELLED'}
		img_width, img_height, img_channel = img.size[0], img.size[1], img.channels
		pixels = numpy.array(img.pixels).reshape(img_height, img_width, img_channel)
		for i in range(img_height):
			pixels[i] = pixels[i][::-1]
		pixels = pixels[::-1]
		img.pixels = pixels.flatten()
		for area in context.screen.areas:
			area.tag_redraw()
		return {'FINISHED'}

class ExternalEditEX(bpy.types.Operator):
	bl_idname = "image.external_edit_ex"
	bl_label = "外部エディターで編集 (拡張)"
	bl_description = "ユーザー設定のファイルタブで設定した追加の外部エディターで画像を開きます"
	bl_options = {'REGISTER', 'UNDO'}
	
	index = bpy.props.IntProperty(name="使用する番号", default=1, min=1, max=3, soft_min=1, soft_max=3)
	
	@classmethod
	def poll(cls, context):
		if (not context.edit_image):
			return False
		if (context.edit_image.filepath == ""):
			return False
		return True
	def execute(self, context):
		img = context.edit_image
		if (not img):
			self.report(type={'ERROR'}, message="画像が見つかりません")
			return {'CANCELLED'}
		if (img.filepath == ""):
			self.report(type={'ERROR'}, message="画像パスが見つかりません")
			return {'CANCELLED'}
		path = bpy.path.abspath(img.filepath)
		pre_path = context.user_preferences.filepaths.image_editor
		if (self.index == 1):
			context.user_preferences.filepaths.image_editor = context.user_preferences.addons['Scramble Addon'].preferences.image_editor_path_1
		elif (self.index == 2):
			context.user_preferences.filepaths.image_editor = context.user_preferences.addons['Scramble Addon'].preferences.image_editor_path_2
		elif (self.index == 3):
			context.user_preferences.filepaths.image_editor = context.user_preferences.addons['Scramble Addon'].preferences.image_editor_path_3
		bpy.ops.image.external_edit(filepath=path)
		context.user_preferences.filepaths.image_editor = pre_path
		return {'FINISHED'}

################
# サブメニュー #
################

class TransformMenu(bpy.types.Menu):
	bl_idname = "IMAGE_MT_image_transform"
	bl_label = "変形"
	bl_description = "画像の変形処理メニューです"
	
	def draw(self, context):
		self.layout.operator(ReverseWidthImage.bl_idname, icon='PLUGIN')
		self.layout.operator(ReverseHeightImage.bl_idname, icon='PLUGIN')
		self.layout.operator(Rotate180Image.bl_idname, icon='PLUGIN')

################
# メニュー追加 #
################

# メニューのオン/オフの判定
def IsMenuEnable(self_id):
	for id in bpy.context.user_preferences.addons['Scramble Addon'].preferences.disabled_menu.split(','):
		if (id == self_id):
			return False
	else:
		return True

# メニューを登録する関数
def menu(self, context):
	if (IsMenuEnable(__name__.split('.')[-1])):
		if (context.user_preferences.addons['Scramble Addon'].preferences.image_editor_path_1):
			self.layout.separator()
			path = os.path.basename(context.user_preferences.addons['Scramble Addon'].preferences.image_editor_path_1)
			name, ext = os.path.splitext(path)
			self.layout.operator(ExternalEditEX.bl_idname, icon='PLUGIN', text=name+" で開く").index = 1
		if (context.user_preferences.addons['Scramble Addon'].preferences.image_editor_path_2):
			path = os.path.basename(context.user_preferences.addons['Scramble Addon'].preferences.image_editor_path_2)
			name, ext = os.path.splitext(path)
			self.layout.operator(ExternalEditEX.bl_idname, icon='PLUGIN', text=name+" で開く").index = 2
		if (context.user_preferences.addons['Scramble Addon'].preferences.image_editor_path_3):
			path = os.path.basename(context.user_preferences.addons['Scramble Addon'].preferences.image_editor_path_3)
			name, ext = os.path.splitext(path)
			self.layout.operator(ExternalEditEX.bl_idname, icon='PLUGIN', text=name+" で開く").index = 3
		self.layout.separator()
		self.layout.operator(FillColor.bl_idname, icon='PLUGIN')
		self.layout.operator(FillTransparency.bl_idname, icon='PLUGIN')
		self.layout.separator()
		self.layout.operator(Normalize.bl_idname, icon='PLUGIN')
		self.layout.operator(BlurImage.bl_idname, icon='PLUGIN')
		self.layout.menu(TransformMenu.bl_idname, icon='PLUGIN')
		self.layout.separator()
		self.layout.operator(RenameImageFile.bl_idname, icon='PLUGIN')
		self.layout.operator(RenameImageFileName.bl_idname, icon='PLUGIN')
		self.layout.separator()
		self.layout.operator(AllRenameImageFileName.bl_idname, icon='PLUGIN')
		self.layout.operator(ReloadAllImage.bl_idname, icon='PLUGIN')
	if (context.user_preferences.addons['Scramble Addon'].preferences.use_disabled_menu):
		self.layout.separator()
		self.layout.operator('wm.toggle_menu_enable', icon='CANCEL').id = __name__.split('.')[-1]
