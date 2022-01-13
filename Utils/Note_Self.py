import os
class Note_Self(object):
	def __init__(self, pitch, offset, quarterLength, velocity=90):
		self.pitch = pitch
		self.offset = offset
		self.quarterLength = quarterLength
		self.velocity = velocity
	def __repr__(self):
		return 'Note(pitch={}, offset={}, quarterLength={}, velocity={})'.format(
			self.pitch, self.offset, self.quarterLength, self.velocity)
class Rest_Self(object):
	def __init__(self, offset, quarterLength):
		self.pitch = '0'
		self.offset = offset
		self.quarterLength = quarterLength
		self.velocity = 0
	def __repr__(self):
		return 'Rest(pitch={}, offset={}, quarterLength={}, velocity={})'.format(
			self.pitch, self.offset, self.quarterLength, self.velocity)
