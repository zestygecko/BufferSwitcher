#============================================================================
# IMPORT
#============================================================================
import os
import sublime
import sublime_plugin


#============================================================================
# VEIW ITEM
#============================================================================
class ViewItem (object):
    def __init__ (self, view):
        self.view = view
        self.path = view.file_name()

        if self.path:
            self.name = os.path.basename(self.path)
        else:
            self.path = ''
            self.name = view.name() if view.name() else "<Untitled>"

        #self.name = "%s <%s>" % (self.name, view.name())
        self.lower = self.name.lower()

    def trimmed_path (self, base_paths):
        for bp in base_paths:
            if self.path and os.path.commonprefix([bp, self.path]) == bp:
                return os.path.relpath(self.path, bp)

        return self.path

    def __lt__ (self, other):
        return self.lower < other.lower


#============================================================================
# COMMAND
#============================================================================
class BufferSwitcherCommand (sublime_plugin.WindowCommand):
    # declarations
    open_files = []
    open_views = []
    window = []
    settings = []
    folders = []
    views = []

    def get_views (self):
        views = []

        file_paths = set()
        for vi in [ ViewItem(v) for v in self.window.views() ]:
            # Only show each file once
            if vi.path and vi.path in file_paths:
                continue

            file_paths.add(vi.path)
            views.append(vi)

        return views

    def run (self):
        # self.open_files = []
        # self.open_views = []
        # self.window = sublime.active_window()
        # self.settings = sublime.load_settings('BufferSwitcher.sublime-settings')
        #

        folders = self.window.folders()
        self.views = sorted(self.get_views())

        #items = [ [v.name, v.trimmed_path(folders)] for v in self.views ]
        items = [ v.name for v in self.views ]
        self.window.show_quick_panel(items, self.tab_selected, 0, -1)
        return

    def tab_selected (self, selected):
        if selected > -1:
            print(self.views[selected].name)
            sel_view_item = self.views[selected]

            # Is the view in the current group
            active_group = self.window.active_group()
            for view in self.window.views_in_group(active_group):
                view_item = ViewItem(view)
                if sel_view_item.path == view_item.path:
                    self.window.focus_view(view_item.view)
                    return selected

            # clone it over if not
            view_index = self.window.get_view_index(sel_view_item.view)
            other_active = self.window.active_view_in_group(view_index[0])

            self.window.focus_view(sel_view_item.view)
            self.window.run_command('clone_file')

            cloned_view = self.window.active_view()
            self.window.set_view_index(cloned_view, active_group, 0)
            self.window.focus_view(other_active)
            self.window.focus_view(cloned_view)

        return selected
