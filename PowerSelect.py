import re
import sublime
import sublime_plugin

class PowerSelectCommand(sublime_plugin.TextCommand):
	def __init__(self, *vargs, **kwargs):
		super().__init__(*vargs, **kwargs)
		self.prev_deselect_pattern = r"^\s*$"

	def run(self, edit, mode="none", args=None):
		if args == None:
			args = []

		if mode == "none":
			print("hello, world!")

		if mode == "clear-all":
			sel = self.view.sel()
			last = sel[-1]
			self.view.sel().clear()
			self.view.sel().add(last)

		if mode == "deselect-lines":
			# get the pattern to deselect by
			self.view.window().show_input_panel(caption="Deselect Regex Pattern", initial_text=self.prev_deselect_pattern, on_done=lambda s: self.deselect_lines(s), on_change=None, on_cancel=None)

		if mode == "split-lines":
			# get the cursor locations
			regs = self.view.sel()

			# create the list of locations to add cursors at
			locs = []
			for reg in regs:
				loc_start = reg.begin()
				loc_end = reg.end()
				for i in range(loc_start, loc_end+1):
					loc = self.view.line(i).begin()
					if loc not in locs:
						locs.append(loc)

			# create the list of regions to add cursors at
			new_regs = []
			for loc in locs:
				new_regs.append(sublime.Region(loc, loc))

			# set the regions
			regs.clear()
			regs.add_all(new_regs)

	def deselect_lines(self, deselect_pattern):
		p = re.compile(deselect_pattern)

		sel = self.view.sel()
		new_sel = []
		for reg in sel:
			start = reg.a
			curr_reg = None
			has_curr = False

			while True:
				line = self.view.line(start)
				sline = self.view.substr(line)
				print(sline)

				m = p.search(sline)
				print(m)
				if m == None:
					if not has_curr:
						curr_reg = sublime.Region(max(reg.a, line.a), min(reg.b, line.b))
					else:
						curr_reg = sublime.Region(curr_reg.a, min(reg.b, line.b))
					has_curr = True
				else:
					if has_curr:
						new_sel.append(curr_reg)
					curr_reg = None
					has_curr = False

				if line.b >= reg.b:
					break
				else:
					start = line.b+1

			if has_curr:
				new_sel.append(curr_reg)
				curr_reg = None
				has_curr = False

		self.view.sel().clear()
		self.view.sel().add_all(new_sel)
